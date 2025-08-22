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

    # Load standalone Python scripts from ./scripts directory (with inline metadata)
    loadStandaloneScripts = dir:
      lib.mapAttrs
      (name: _: uv2nix.lib.scripts.loadScript {script = dir + "/${name}";})
      (lib.filterAttrs (name: type: type == "regular" && lib.hasSuffix ".py" name)
        (builtins.readDir dir));

    # Load Python apps from ./apps directory (simple files, no inline metadata)
    loadApps = dir:
      lib.mapAttrs
      (name: _: dir + "/${name}")
      (lib.filterAttrs (name: type: type == "regular" && lib.hasSuffix ".py" name)
        (builtins.readDir dir));

    standaloneScripts = loadStandaloneScripts ./scripts;
    apps = loadApps ./apps;

    # Create derivations for standalone scripts
    standaloneScriptDerivations = forAllSystems (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python313;
        baseSet = pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        };
        pyprojectOverrides = _final: _prev: {};
      in
        lib.mapAttrs (
          name: script: let
            overlay = script.mkOverlay {
              sourcePreference = "wheel";
            };
            pythonSet = baseSet.overrideScope (
              lib.composeManyExtensions [
                pyproject-build-systems.overlays.default
                overlay
                pyprojectOverrides
              ]
            );
          in
            pkgs.writeScript script.name (
              script.renderScript {
                venv = script.mkVirtualEnv {
                  inherit pythonSet;
                };
              }
            )
        )
        standaloneScripts
    );

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
                      nativeBuildInputs = [virtualenv pkgs.which pkgs.nix];
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
    packages = forAllSystems (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonSet = pythonSets.${system}.standard;
        venv = pythonSet.mkVirtualEnv "moscripts-venv" workspace.deps.default;
        # alpine base docker image
        alpine = pkgs.dockerTools.pullImage {
          imageName = "alpine";
          imageDigest = "sha256:4bcff63911fcb4448bd4fdacec207030997caf25e9bea4045fa6c8c44de311d1";
          finalImageName = "alpine";
          finalImageTag = "latest";
          sha256 = "sha256-1Af8p6cYQs8sxlowz4BC6lC9eAOpNWYnIhCN7BSDKL0=";
          os = "linux";
          arch =
            if system == "x86_64-linux"
            then "amd64"
            else if system == "aarch64-linux"
            then "arm64"
            else system;
        };

        # Helper to create executable scripts (for standalone scripts)
        makeStandaloneExecutable = scriptName: scriptDrv:
          pkgs.stdenv.mkDerivation {
            name = "${scriptName}-in-bin";
            buildCommand = ''
              mkdir -p $out/bin
              cp ${scriptDrv} $out/bin/${scriptName}
              chmod +x $out/bin/${scriptName}
            '';
          };

        # Helper to create executable apps (for apps that need moscripts venv)
        makeAppExecutable = appName: appPath:
          pkgs.stdenv.mkDerivation {
            name = "${appName}-in-bin";
            buildCommand = ''
              mkdir -p $out/bin
              cp ${appPath} $out/bin/${appName}
              chmod +x $out/bin/${appName}
              patchShebangs $out/bin/${appName}
            '';
            buildInputs = [venv];
          };

        # Helper to create docker images for standalone scripts
        makeDockerImage = scriptName: scriptDrv:
          pkgs.dockerTools.buildLayeredImage {
            name = "${scriptName}-container";
            fromImage = alpine;
            contents = [(makeStandaloneExecutable scriptName scriptDrv) pkgs.curl pkgs.nix];
            config = {
              Cmd = ["/bin/${scriptName}"];
            };
          };

        # Helper to create docker images for apps
        makeAppDockerImage = appName: appPath:
          pkgs.dockerTools.buildLayeredImage {
            name = "${appName}-container";
            fromImage = alpine;
            contents = [(makeAppExecutable appName appPath) pkgs.curl pkgs.nix];
            config = {
              Cmd = ["/bin/${appName}"];
            };
          };

        # Create binary packages for standalone scripts
        standaloneBinaryPackages =
          lib.mapAttrs' (
            name: drv:
              lib.nameValuePair (lib.removeSuffix ".py" name)
              (makeStandaloneExecutable (lib.removeSuffix ".py" name) drv)
          )
          standaloneScriptDerivations.${system};

        # Create container packages for standalone scripts
        standaloneContainerPackages =
          if pkgs.stdenv.isLinux
          then
            lib.mapAttrs' (
              name: drv:
                lib.nameValuePair "${lib.removeSuffix ".py" name}-container"
                (makeDockerImage (lib.removeSuffix ".py" name) drv)
            )
            standaloneScriptDerivations.${system}
          else {};

        # Create binary packages for apps
        appBinaryPackages =
          lib.mapAttrs' (
            name: appPath: let
              appName = lib.removeSuffix ".py" name;
            in
              lib.nameValuePair appName (makeAppExecutable appName appPath)
          )
          apps;

        # Create container packages for apps
        appContainerPackages =
          if pkgs.stdenv.isLinux
          then
            lib.mapAttrs' (
              name: appPath: let
                appName = lib.removeSuffix ".py" name;
              in
                lib.nameValuePair "${appName}-container" (makeAppDockerImage appName appPath)
            )
            apps
          else {};

        # Create a default package that bundles all binary packages
        default = pkgs.symlinkJoin {
          name = "moscripts-bundled-apps";
          paths = lib.attrValues standaloneBinaryPackages ++ lib.attrValues appBinaryPackages;
          meta = {
            description = "Bundled moscripts applications and scripts";
            longDescription = "A collection of Python scripts from the apps and scripts directories, packaged as executable binaries";
          };
        };
      in
        {
          inherit default;
        }
        // standaloneBinaryPackages
        // standaloneContainerPackages
        // appBinaryPackages
        // appContainerPackages
    );

    # Create apps that are runnable with `nix run .#<app>`
    apps = forAllSystems (
      system: let
        pkgs = nixpkgs.legacyPackages.${system};
        # Helper to create runnable apps
        makeRunnableApp = appName: {
          type = "app";
          program = "${self.packages.${system}.${appName}}/bin/${appName}";
          meta = {
            description = "Run ${appName} script";
          };
        };
        # Filter out the 'default' package from the runnable apps
        runnablePackages = lib.filterAttrs (name: _: name != "default" && !lib.hasSuffix "-container" name) self.packages.${system};
      in
        lib.mapAttrs' (name: _: lib.nameValuePair name (makeRunnableApp name))
        runnablePackages
    );

    devShells = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python313;
      editablePythonSet = pythonSets.${system}.editable;
      virtualenvDev = editablePythonSet.mkVirtualEnv "moscripts-dev-venv" workspace.deps.all;
      devPackages = [
        pkgs.bash
        pkgs.jq
        pkgs.uv
      ];
    in {
      # This devShell simply adds Python and undoes the dependency leakage done by Nixpkgs Python infrastructure.
      impure = pkgs.mkShell {
        packages =
          [
            python
          ]
          ++ devPackages;
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
      default = pkgs.mkShell {
        packages =
          [
            virtualenvDev
          ]
          ++ devPackages;
        env = {
          UV_NO_SYNC = "1";
          UV_PYTHON = python.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
        };
        shellHook = ''
          unset PYTHONPATH
          export REPO_ROOT=$(git rev-parse --show-toplevel)
          source ${virtualenvDev}/bin/activate
          export VIRTUAL_ENV=${virtualenvDev} # Export VIRTUAL_ENV for the script

          # Configure VS Code
          source ${./scripts/configure-vscode.sh}
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
