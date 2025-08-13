{
  description = "Using Nix Flake apps to run scripts with uv2nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    nixpkgs,
    uv2nix,
    pyproject-nix,
    pyproject-build-systems,
    ...
  }: let
    inherit (nixpkgs) lib;
    inherit (lib) filterAttrs hasSuffix;

    # System configuration
    pkgs = nixpkgs.legacyPackages.x86_64-linux;
    python = pkgs.python313;

    # Workspace and package setup
    workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;};

    overlay = workspace.mkPyprojectOverlay {
      sourcePreference = "wheel";
    };

    # Build the Python package set
    baseSet = pkgs.callPackage pyproject-nix.build.packages {
      inherit python;
    };

    pytestOverlay = final: prev: {
      moscripts = prev.moscripts.overrideAttrs (old: {
        passthru =
          (old.passthru or {})
          // {
            tests = let
              virtualenv = final.mkVirtualEnv "moscripts-pytest-env" {
                moscripts = ["dev"];
              };
            in
              (old.tests or {})
              // {
                pytest = pkgs.stdenv.mkDerivation {
                  name = "${final.moscripts.name}-pytest";
                  inherit (final.moscripts) src;
                  nativeBuildInputs = [virtualenv];
                  dontConfigure = true;
                  buildPhase = ''
                    runHook preBuild
                    pytest --junit-xml=pytest.xml
                    runHook postBuild
                  '';
                  installPhase = ''
                    runHook preInstall
                    mv pytest.xml $out
                    runHook postInstall
                  '';
                };
              };
          };
      });
    };

    pythonSet = baseSet.overrideScope (
      lib.composeManyExtensions [
        pyproject-build-systems.overlays.default
        overlay
        pytestOverlay
      ]
    );

    venv = pythonSet.mkVirtualEnv "moscripts-default-env" workspace.deps.default;
    # Dev shell helpers
    editableOverlay = workspace.mkEditablePyprojectOverlay {
      root = "$REPO_ROOT";
    };

    editablePythonSet = pythonSet.overrideScope (
      lib.composeManyExtensions [
        editableOverlay
        (final: prev: {
          moscripts = prev.moscripts.overrideAttrs (old: {
            src = lib.fileset.toSource {
              root = old.src;
              fileset = lib.fileset.unions [
                (old.src + "/pyproject.toml")
                (old.src + "/README.md")
                (old.src + "/src/moscripts/__init__.py")
              ];
            };
            nativeBuildInputs =
              old.nativeBuildInputs
              ++ final.resolveBuildSystem {
                editables = [];
              };
          });
        })
      ]
    );

    virtualenvDev = editablePythonSet.mkVirtualEnv "moscripts-dev-env" workspace.deps.all;
    # ------------------------------------------------------------------------------ #
    # App discovery and creation
    appsBasedir = ./apps;
    appFiles = filterAttrs (name: type: type == "regular" && hasSuffix ".py" name) (
      builtins.readDir appsBasedir
    );
    appNames = lib.mapAttrsToList (name: _: lib.removeSuffix ".py" name) appFiles;

    # Shared build logic for creating executable scripts
    makeExecutable = appName: ''
      mkdir -p $out/bin
      cp ${appsBasedir}/${appName}.py $out/bin/${appName}
      chmod +x $out/bin/${appName}
      patchShebangs $out/bin/${appName}
    '';

    makePatchedScript = appName:
      pkgs.runCommand appName {buildInputs = [venv];} (makeExecutable appName);

    makeApp = appName: {
      type = "app";
      program = "${makePatchedScript appName}/bin/${appName}";
      meta = {
        name = appName;
        description = "Python script ${appName} from moscripts";
      };
    };

    makeDockerImage = appName: imageName:
      pkgs.dockerTools.buildLayeredImage {
        name = "${imageName}";
        contents = [(makePatchedScript appName)];
        config = {
          Cmd = ["/bin/${appName}"];
        };
      };

    makeStandalonePackage = appName:
      pkgs.stdenv.mkDerivation {
        name = appName;
        buildCommand = makeExecutable appName;
        buildInputs = [venv];
      };
  in {
    # Create individual packages for each app and their container variants
    packages.x86_64-linux = let
      # Helper function to create container images for bundled package
      makeBundledDockerImage = appName: makeDockerImage appName "${appName}-container";

      bundledPackages = {
        # Standalone packages in /bin/appsName
        default = pkgs.symlinkJoin {
          name = "moscripts-bundled-apps";
          paths = map makePatchedScript appNames;
          meta = {
            description = "Bundled moscripts applications";
            longDescription = "A collection of Python scripts from the apps directory, packaged as executable binaries with patched shebangs";
          };
        };
        # Container images in a single directory
        containers = pkgs.stdenv.mkDerivation {
          name = "moscripts-bundled-container-apps";
          buildCommand = ''
            mkdir -p $out
            ${lib.concatMapStrings (appName: ''
                cp ${(makeBundledDockerImage appName)} $out/${appName}-container.tar.gz
              '')
              appNames}
          '';
          meta = {
            description = "Bundled moscripts container applications";
            longDescription = "A collection of Python scripts from the apps directory, packaged as container images in a single output directory";
          };
        };
      };
      # Standalone packages (named after the app)
      standalonePackages = lib.genAttrs appNames makeStandalonePackage;

      # Container packages (named after the app-container)
      containerPackages =
        if pkgs.stdenv.isLinux
        then
          lib.foldl' (acc: appName:
            acc
            // {
              "${appName}-container" = makeDockerImage appName "${appName}-container";
            })
          {}
          appNames
        else {};
    in
      bundledPackages // standalonePackages // containerPackages;

    # Create apps that are runnable with `nix run .#<app>`
    apps.x86_64-linux = lib.genAttrs appNames makeApp;

    devShells.x86_64-linux = {
      # It is of course perfectly OK to keep using an impure virtualenv workflow and only use uv2nix to build packages.
      # This devShell simply adds Python and undoes the dependency leakage done by Nixpkgs Python infrastructure.
      impure = pkgs.mkShell {
        buildInputs = [pkgs.bashInteractive];
        packages = [
          python
          pkgs.uv
        ];
        env =
          {
            UV_PYTHON_DOWNLOADS = "never";
            UV_PYTHON = python.interpreter;
          }
          // lib.optionalAttrs pkgs.stdenv.isLinux {
            LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
          };
        shellHook = ''
          unset PYTHONPATH
          uv sync
          source .venv/bin/activate
        '';
      };

      # This devShell uses uv2nix to construct a virtual environment purely from Nix, using the same dependency specification as the application.
      uv2nix = pkgs.mkShell {
        buildInputs = [pkgs.bashInteractive];
        packages = [
          virtualenvDev
          pkgs.uv
        ];
        env = {
          UV_NO_SYNC = "1";
          UV_PYTHON = python.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
        };
        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel)
          source ${virtualenvDev}/bin/activate
        '';
      };
    };

    # Construct flake checks from Python set
    checks.x86_64-linux = {
      inherit (pythonSet.moscripts.passthru.tests) pytest;
    };
  };
}
