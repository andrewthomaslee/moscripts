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

    forAllSystems = lib.genAttrs lib.systems.flakeExposed;

    # Load a uv workspace from a workspace root.
    # Uv2nix treats all uv projects as workspace projects.
    workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;};

    # Create package overlay from workspace.
    overlay = workspace.mkPyprojectOverlay {
      sourcePreference = "wheel"; # or sourcePreference = "sdist";
    };

    pyprojectOverrides = _final: _prev: {
      # Implement build fixups here.
      # Note that uv2nix is _not_ using Nixpkgs buildPythonPackage.
      # It's using https://pyproject-nix.github.io/pyproject.nix/build.html
    };

    pkgs = nixpkgs.legacyPackages.x86_64-linux;

    python = pkgs.python313;

    pythonSet = let
      inherit (pkgs) stdenv;

      baseSet = pkgs.callPackage pyproject-nix.build.packages {
        inherit python;
      };

      # An overlay of build fixups & test additions.
      pyprojectOverrides = final: prev: {
        # moscripts is the name of our example package
        moscripts = prev.moscripts.overrideAttrs (old: {
          passthru =
            old.passthru
            // {
              # Put all tests in the passthru.tests attribute set.
              # Nixpkgs also uses the passthru.tests mechanism for ofborg test discovery.
              #
              # For usage with Flakes we will refer to the passthru.tests attributes to construct the flake checks attribute set.
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
                    nativeBuildInputs = [
                      virtualenv
                    ];
                    dontConfigure = true;

                    # Because this package is running tests, and not actually building the main package
                    # the build phase is running the tests.
                    #
                    # In this particular example we also output a HTML coverage report, which is used as the build output.
                    buildPhase = ''
                      runHook preBuild
                      pytest --junit-xml=pytest.xml
                      runHook postBuild
                    '';

                    # Install the HTML coverage report into the build output.
                    #
                    # If you wanted to install multiple test output formats such as TAP outputs
                    # you could make this derivation a multiple-output derivation.
                    #
                    # See https://nixos.org/manual/nixpkgs/stable/#chap-multiple-output for more information on multiple outputs.
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
    in
      baseSet.overrideScope
      (
        lib.composeManyExtensions [
          pyproject-build-systems.overlays.default
          overlay
          pyprojectOverrides
        ]
      );

    venv = pythonSet.mkVirtualEnv "moscripts-default-env" workspace.deps.default;
  in {
    apps.x86_64-linux = let
      # Example base directory
      basedir = ./apps;

      # Get a list of regular Python files in example directory
      files = filterAttrs (name: type: type == "regular" && hasSuffix ".py" name) (
        builtins.readDir basedir
      );
    in
      # Map over files to:
      # - Rewrite script shebangs as shebangs pointing to the virtualenv
      # - Strip .py suffixes from attribute names
      #   Making a script "greet.py" runnable as "nix run .#greet"
      lib.mapAttrs' (
        name: _:
          lib.nameValuePair (lib.removeSuffix ".py" name) (
            let
              script = basedir + "/${name}";

              # Patch script shebang
              program = pkgs.runCommand name {buildInputs = [venv];} ''
                cp ${script} $out
                chmod +x $out
                patchShebangs $out
              '';
            in {
              type = "app";
              program = "${program}";
              meta = let
                app = lib.removeSuffix ".py" name;
              in {
                name = app;
                description = "A app named ${app}";
              };
            }
          )
      )
      files;

    devShells.x86_64-linux = {
      # It is of course perfectly OK to keep using an impure virtualenv workflow and only use uv2nix to build packages.
      # This devShell simply adds Python and undoes the dependency leakage done by Nixpkgs Python infrastructure.
      impure = pkgs.mkShell {
        packages = [
          python
          pkgs.uv
        ];
        env =
          {
            # Prevent uv from managing Python downloads
            UV_PYTHON_DOWNLOADS = "never";
            # Force uv to use nixpkgs Python interpreter
            UV_PYTHON = python.interpreter;
          }
          // lib.optionalAttrs pkgs.stdenv.isLinux {
            # Python libraries often load native shared objects using dlopen(3).
            # Setting LD_LIBRARY_PATH makes the dynamic library loader aware of libraries without using RPATH for lookup.
            LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
          };
        shellHook = ''
          unset PYTHONPATH
        '';
      };

      # This devShell uses uv2nix to construct a virtual environment purely from Nix, using the same dependency specification as the application.
      # The notable difference is that we also apply another overlay here enabling editable mode ( https://setuptools.pypa.io/en/latest/userguide/development_mode.html ).
      #
      # This means that any changes done to your local files do not require a rebuild.
      #
      # Note: Editable package support is still unstable and subject to change.
      uv2nix = let
        # Create an overlay enabling editable mode for all local dependencies.
        editableOverlay = workspace.mkEditablePyprojectOverlay {
          # Use environment variable
          root = "$REPO_ROOT";
          # Optional: Only enable editable for these packages
          # members = [ "moscripts" ];
        };

        # Override previous set with our overrideable overlay.
        editablePythonSet = pythonSet.overrideScope (
          lib.composeManyExtensions [
            editableOverlay

            # Apply fixups for building an editable package of your workspace packages
            (final: prev: {
              moscripts = prev.moscripts.overrideAttrs (old: {
                # It's a good idea to filter the sources going into an editable build
                # so the editable package doesn't have to be rebuilt on every change.
                src = lib.fileset.toSource {
                  root = old.src;
                  fileset = lib.fileset.unions [
                    (old.src + "/pyproject.toml")
                    (old.src + "/README.md")
                    (old.src + "/src/moscripts/__init__.py")
                  ];
                };

                # Hatchling (our build system) has a dependency on the `editables` package when building editables.
                #
                # In normal Python flows this dependency is dynamically handled, and doesn't need to be explicitly declared.
                # This behaviour is documented in PEP-660.
                #
                # With Nix the dependency needs to be explicitly declared.
                nativeBuildInputs =
                  old.nativeBuildInputs
                  ++ final.resolveBuildSystem {
                    editables = [];
                  };
              });
            })
          ]
        );

        # Build virtual environment, with local packages being editable.
        #
        # Enable all optional dependencies for development.
        virtualenv = editablePythonSet.mkVirtualEnv "moscripts-dev-env" workspace.deps.all;
      in
        pkgs.mkShell {
          packages = [
            virtualenv
            pkgs.uv
          ];

          env = {
            # Don't create venv using uv
            UV_NO_SYNC = "1";

            # Force uv to use nixpkgs Python interpreter
            UV_PYTHON = python.interpreter;

            # Prevent uv from downloading managed Python's
            UV_PYTHON_DOWNLOADS = "never";
          };

          shellHook = ''
            # Undo dependency propagation by nixpkgs.
            unset PYTHONPATH

            # Get repository root using git. This is expanded at runtime by the editable `.pth` machinery.
            export REPO_ROOT=$(git rev-parse --show-toplevel)
          '';
        };
    };

    # Construct flake checks from Python set
    checks.x86_64-linux = {
      inherit (pythonSet.moscripts.passthru.tests) pytest;
    };
  };
}
