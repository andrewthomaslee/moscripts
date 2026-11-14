# moscripts

[![ci](https://img.shields.io/github/actions/workflow/status/andrewthomaslee/moscripts/ci.yml?branch=main&label=ci&logo=github)](https://github.com/andrewthomaslee/moscripts/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/andrewthomaslee/moscripts?label=release&color=d97757)](https://github.com/andrewthomaslee/moscripts/releases/latest)
[![docs](https://img.shields.io/website?url=https%3A%2F%2Fandrewthomaslee.github.io%2Fmoscripts%2F&label=docs&up_message=online&down_message=offline)](https://andrewthomaslee.github.io/moscripts/)
[![license](https://img.shields.io/github/license/andrewthomaslee/moscripts)](https://github.com/andrewthomaslee/moscripts/blob/main/LICENSE)
[![built with Nix](https://img.shields.io/badge/built_with-Nix-5277C3?logo=nixos&logoColor=white)](https://nixos.org)

Small Python CLIs packaged with Nix: one uv workspace built by uv2nix into one
package. Docs and slides: <https://andrewthomaslee.github.io/moscripts/>.

| Command | Does |
| --- | --- |
| `motmp` | create and edit temporary marimo notebooks with a managed venv |
| `mpv_playlists` | play a playlist from `~/Music/Playlists` with mpv |
| `password_generator` | secure, customizable passwords |
| `human_timestamp` | a human-readable timestamp in any time zone |

## Use

Needs [Nix](https://nixos.org/download/) with flakes enabled.

```sh
nix run github:andrewthomaslee/moscripts#password_generator -- --help
nix profile add github:andrewthomaslee/moscripts   # all four on PATH
```

In a flake that follows [external-systems/pkgs](https://github.com/external-systems/pkgs):

```nix
inputs.moscripts = {
  url = "github:andrewthomaslee/moscripts";
  inputs.org-pkgs.follows = "org-pkgs";
};
```

## Develop

Needs Nix and devenv.

```sh
devenv allow     # editable venv, auto-activates on cd (after `devenv hook`)
fmt              # format and lint
check            # nix flake check: pytest, pyrefly, ruff, uv-lock, docs
docs-build       # static docs to ./result-docs; open index.html from disk
devenv up        # live docs on :8981 and slides on :8982
```

CI is the [external-systems org CI](https://github.com/external-systems/pkgs):
`nix flake check` on PRs; on `main`, the docs deploy to GitHub Pages and a
`0.2.<commits>` release is tagged. See
[Development](https://andrewthomaslee.github.io/moscripts/development.html).

## License

[MIT](LICENSE)
