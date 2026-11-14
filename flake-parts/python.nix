# Packages, apps and checks from the uv workspace (flake-parts/_python/).
{inputs, ...}: {
  perSystem = {
    pkgs,
    lib,
    ...
  }: let
    py = import ./_python/python-set.nix {
      inherit pkgs lib;
      inherit (inputs) uv2nix pyproject-nix pyproject-build-systems;
    };
    inherit (pkgs.callPackages inputs.pyproject-nix.build.util {}) mkApplication;

    # The [project.scripts] entry points, one `nix run .#NAME` app each.
    clis = lib.attrNames (lib.importTOML ../pyproject.toml).project.scripts;

    # Tools the CLIs exec. Appended to PATH (--suffix), so a user's own copy
    # wins and the pinned one is the fallback; nothing calls `nix run` at
    # runtime.
    runtimeTools = [pkgs.gum pkgs.uv pkgs.mpv];

    app = mkApplication {
      inherit (py) venv;
      package = py.pythonSet.moscripts;
    };

    # makeWrapper, not wrapProgram: the wrapper execs the script under its
    # own name, so Typer's usage line says `motmp`, not `.motmp-wrapped`.
    moscripts =
      pkgs.runCommand "moscripts-${py.pythonSet.moscripts.version}" {
        nativeBuildInputs = [pkgs.makeWrapper];
        passthru = {inherit app clis;};
        meta = {
          description = "Small Python CLIs: ${lib.concatStringsSep ", " clis}";
          homepage = "https://github.com/andrewthomaslee/moscripts";
          license = lib.licenses.mit;
          platforms = lib.platforms.linux;
        };
      } ''
        mkdir -p $out/bin
        for cli in ${lib.escapeShellArgs clis}; do
          makeWrapper ${app}/bin/$cli $out/bin/$cli --suffix PATH : ${lib.makeBinPath runtimeTools}
        done
      '';

    # Only what the checks read, so docs or Nix edits do not rerun them.
    checkSrc = lib.fileset.toSource {
      root = ../.;
      fileset = lib.fileset.unions [
        ../pyproject.toml
        ../uv.lock
        ../README.md
        ../LICENSE
        ../src
        ../tests
      ];
    };

    # Runs a command in a writable copy of checkSrc with the test venv.
    pyCheck = name: script:
      pkgs.runCommand "moscripts-${name}" {nativeBuildInputs = [py.testVenv pkgs.gum pkgs.which];} ''
        cp -r ${checkSrc}/. src && chmod -R u+w src && cd src
        export HOME=$TMPDIR
        ${script}
        touch $out
      '';
  in {
    packages = {
      default = moscripts;
      inherit moscripts;
      moscripts-venv = py.venv;
    };

    apps = lib.genAttrs clis (cli: {
      type = "app";
      program = "${moscripts}/bin/${cli}";
      meta.description = "Run ${cli} from moscripts";
    });

    checks = {
      # Tests the installed package (not editable), so it tests what ships.
      pytest = pyCheck "pytest" "pytest -p no:cacheprovider tests";
      pyrefly = pyCheck "pyrefly" "pyrefly check --config pyproject.toml";
      ruff = pyCheck "ruff" ''
        export RUFF_NO_CACHE=true
        ruff check src tests
        ruff format --check src tests
      '';
      # uv.lock still matches pyproject.toml. uv2nix builds a stale lock
      # without complaint, silently missing new dependencies.
      uv-lock = pkgs.runCommand "moscripts-uv-lock" {nativeBuildInputs = [pkgs.uv];} ''
        cp -r ${checkSrc}/. . && chmod -R u+w .
        export HOME=$TMPDIR UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=never
        uv lock --check --offline --python ${py.python.interpreter}
        touch $out
      '';
    };

    # For inspection: nix eval .#legacyPackages.x86_64-linux.pythonSet.typer.version
    legacyPackages.pythonSet = py.pythonSet;
  };
}
