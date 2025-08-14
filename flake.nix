{
  description = "Using Nix Flake apps to run scripts with uv2nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";

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
    self,
    nixpkgs,
    uv2nix,
    pyproject-nix,
    pyproject-build-systems,
    systems,
    ...
  }: let
    inherit (nixpkgs) lib;
    inherit (lib) filterAttrs hasSuffix;

    # Create attrset for each system
    forAllSystems = lib.genAttrs (import systems);

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

    # use uv2nix to load workspace and discover pyproject.toml
    workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;};

    overlay = workspace.mkPyprojectOverlay {
      sourcePreference = "wheel";
    };

    # Python sets grouped per system
    pythonSets = forAllSystems (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (pkgs) stdenv;

        baseSet = pkgs.callPackage pyproject-nix.build.packages {
          python = pkgs.python313;
        };

        # An overlay of build fixups & test additions.
        pyprojectOverrides = final: prev: {
          moscripts = prev.moscripts.overrideAttrs (old: {
            passthru =
              old.passthru
              // {
                # Put all tests in the passthru.tests attribute set.
                tests = let
                  # Construct a virtual environment with only the test dependency-group enabled for testing.
                  virtualenv = final.mkVirtualEnv "moscripts-pytest-env" {
                    moscripts = ["dev"];
                  };
                in
                  (old.tests or {})
                  // {
                    pytest = stdenv.mkDerivation {
                      name = "${final.moscripts.name}-pytest";
                      inherit (final.moscripts) src;
                      nativeBuildInputs = [virtualenv];
                      dontConfigure = true;
                      # the build phase runs the tests.
                      buildPhase = ''
                        runHook preBuild
                        pytest --junit-xml=pytest.xml
                        runHook postBuild
                      '';
                      # Install the test output
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

        # Editable overlay for development
        editableOverlay = lib.composeManyExtensions [
          (workspace.mkEditablePyprojectOverlay {root = "$REPO_ROOT";})
          (final: prev: {
            moscripts = prev.moscripts.overrideAttrs (old: {
              src = lib.fileset.toSource {
                root = old.src;
                fileset = lib.fileset.unions [
                  (old.src + "/pyproject.toml")
                  (old.src + "/README.md")
                  (old.src + "/src/")
                  (old.src + "/tests/")
                  (old.src + "/apps/")
                ];
              };
              nativeBuildInputs =
                old.nativeBuildInputs
                ++ final.resolveBuildSystem {editables = [];};
            });
          })
        ];
      in {
        # Standard Python set
        standard = baseSet.overrideScope (
          lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
            pyprojectOverrides
          ]
        );
        # Editable Python set for development
        editable = baseSet.overrideScope (
          lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
            pyprojectOverrides
            editableOverlay
          ]
        );
      }
    );
  in {
    # Create individual packages for each app and their container variants
    packages = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      pythonSet = pythonSets.${system}.standard;
      venv = pythonSet.mkVirtualEnv "moscripts-default-env" (uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;}).deps.default;

      makePatchedScript = appName:
        pkgs.runCommand appName {buildInputs = [venv];} (makeExecutable appName);

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
        bundledContainers = pkgs.stdenv.mkDerivation {
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
      bundledPackages // standalonePackages // containerPackages);

    # Create apps that are runnable with `nix run .#<app>`
    apps = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      pythonSet = pythonSets.${system}.standard;
      venv = pythonSet.mkVirtualEnv "moscripts-default-env" (uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;}).deps.default;

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
    in
      lib.genAttrs appNames makeApp);

    devShells = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python313;
      editablePythonSet = pythonSets.${system}.editable;
      virtualenvDev = editablePythonSet.mkVirtualEnv "moscripts-dev-env" (uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;}).deps.all;
    in {
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
    });

    # Construct flake checks from Python set
    checks = forAllSystems (system: let
      pythonSet = pythonSets.${system}.standard;
    in {
      inherit (pythonSet.moscripts.passthru.tests) pytest;
    });
  };
}
