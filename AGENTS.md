# AGENTS.md

moscripts: small Python CLIs (`motmp`, `mpv_playlists`, `password_generator`, `human_timestamp`) in one uv workspace, built with uv2nix into `packages.default`. A personal repo (github.com/andrewthomaslee/moscripts) that follows the external-systems org standard. external-systems/pkgs consumes it as `pkgs.moscripts` (overlays.third-party), so pkgs, modules and home all lock it.

## Layout
- `pyproject.toml`, `uv.lock`: the uv workspace (backend `uv_build`). Each `[project.scripts]` entry becomes a binary in `packages.default` and an `apps.<system>.<name>`.
- `src/moscripts/`: the package, one module per command plus `gum.py` and `utilities.py`. `tests/`: pytest.
- `flake.nix`: the org inputs plus `pyproject-nix`, `uv2nix`, `pyproject-build-systems`, all following `org-pkgs`; imports `org-pkgs.flakeModules.default`.
- `flake-parts/python.nix`: packages (`default`/`moscripts`, `moscripts-venv`), apps, checks (`pytest`, `pyrefly`, `ruff`, `uv-lock`), `legacyPackages.pythonSet`.
- `flake-parts/_python/`: plain functions, not modules (import-tree skips `_`). `python-set.nix` is shared by `python.nix` and `devenv.nix`; `overrides.nix` holds build fixups.
- `flake-parts/docs.nix`: docs settings. URLs point at andrewthomaslee (not `docs.repo`, which assumes the external-systems org).
- `devenv.yaml` + `devenv.lock` + `devenv.nix`: the org shell plus the editable venv (`$DEVENV_ROOT/src`), `uv`, `gum`, `mpv`.
- `vm-tests/cli-smoke.nix`: offline NixOS VM test of the installed package.
- `documentation/`: MkDocs site (`docs/`, screenshots in `docs/assets/`) and reveal.js deck (`slides/slides.md`).
- `.github/workflows/ci.yml`: the org CI caller (`major: 0`, `minor: 2`). `.github/rulesets/default.json`: the ruleset; bypass is `RepositoryRole` admin (id 5) because a personal repo has no `OrganizationAdmin`.

## Tool loop
- The shell is devenv. If `DEVENV_ROOT` is unset, run commands with `devenv shell -- <cmd>`.
- `git add` new files before any `nix` command.
- `uv add PKG` or edit `pyproject.toml` then `uv lock`; `UV_NO_SYNC=1`, so call `pytest`/the commands directly, never `uv run`.
- `fmt`, then `check`. Both must pass before a change is done.
- After `nix flake update org-pkgs`, run `sync-locks` in the same commit.
- VM test: `vm-test cli-smoke --remote --rebuild` (or local KVM without `--remote`). Exit code is the result.

## Rules
- Load the `nix-style` skill before editing `.nix` files and the `uv2nix` skill before touching the Python build.
- One nixpkgs and one uv2nix: never add an input URL that org-pkgs already pins; a newer uv2nix is a pkgs PR.
- The consumer contract: pkgs declares `moscripts = {url = "github:andrewthomaslee/moscripts"; inputs.org-pkgs.follows = "";}`, so everything here resolves to pkgs' own pins. Keep every input a `follows` of `org-pkgs` and `packages.<system>.default` the full CLI bundle.
- The commands never call `nix run` for their tools: `utilities.tool_prefix` looks on PATH first, and the package appends pinned `gum`, `uv`, `mpv`. No import-time side effects (no asserts on `nix` or `~/Music`): `--help` must work anywhere.
- Ruff rules are pinned in `pyproject.toml` (`[tool.ruff.lint] select`); widen them deliberately, not through a ruff bump.
- Work on a branch and open a PR; never push to `main`. The ruleset requires a green `ci / flake-check`.
- VM tests run only by hand, never in CI or `checks`, and stay hermetic.
- Never commit build output (`result*`, `_site/`, `site/`).
