# Development

Needs Nix and [devenv](https://devenv.sh). The shell is the org shell from
external-systems/pkgs plus an editable uv2nix venv: `moscripts`, its four
commands, pytest, ruff and pyrefly on PATH, importing straight from `src/`.

```sh
devenv allow        # auto-activates the shell on cd (after `devenv hook`)
fmt                 # treefmt: Nix, shell, Markdown
check               # nix flake check
docs-build          # this site to ./result-docs; open index.html from disk
devenv up           # live docs on :8981, slides on :8982
```

## Layout

```
pyproject.toml uv.lock         the uv workspace (uv_build backend)
src/moscripts/                 the package; one module per command
tests/                         pytest
flake-parts/python.nix         packages, apps, checks
flake-parts/_python/           the Python set, shared with devenv.nix
vm-tests/cli-smoke.nix         NixOS VM test of the installed package
documentation/                 this site and the deck
```

## Python loop

```sh
uv add httpx                   # or edit pyproject.toml, then: uv lock
uv lock --upgrade              # bump every dependency
git add -A                     # Nix only sees tracked files
pytest && ruff check src tests && ruff format src tests
check                          # pytest, pyrefly, ruff, uv-lock, treefmt, docs
```

`UV_NO_SYNC=1`: uv edits the lock only and never creates `.venv`; call
`pytest` and the commands directly, not through `uv run`. A new command is a
`[project.scripts]` entry; the flake turns each one into
`apps.<system>.<name>` and a binary in `packages.default`.

## Checks

| Check | Fails when |
| --- | --- |
| `pytest` | a test fails (runs against the installed package) |
| `pyrefly` | a type error |
| `ruff` | a lint error or unformatted file (rules pinned in `pyproject.toml`) |
| `uv-lock` | `uv.lock` is stale against `pyproject.toml` |
| `treefmt`, `lock-sync`, `documentation`, `slides` | from org-pkgs |

## VM test

`vm-tests/cli-smoke.nix` installs the package in an offline NixOS VM and runs
every command. It never runs in CI; run it by hand:

```sh
vm-test cli-smoke --remote --rebuild    # on the remote builder
vm-test cli-smoke                       # local KVM
```

## Updating

nixpkgs and uv2nix come from external-systems/pkgs:

```sh
nix flake update org-pkgs && sync-locks   # one commit
```

CI (`ci / flake-check`) runs `nix flake check` on every PR; on `main` it
deploys this site to GitHub Pages and tags a `0.2.<commits>` release.
