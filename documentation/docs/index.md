# moscripts

[![ci](https://img.shields.io/github/actions/workflow/status/andrewthomaslee/moscripts/ci.yml?branch=main&label=ci&logo=github)](https://github.com/andrewthomaslee/moscripts/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/andrewthomaslee/moscripts?label=release&color=d97757)](https://github.com/andrewthomaslee/moscripts/releases/latest)
[![docs](https://img.shields.io/website?url=https%3A%2F%2Fandrewthomaslee.github.io%2Fmoscripts%2F&label=docs&up_message=online&down_message=offline)](https://andrewthomaslee.github.io/moscripts/)
[![license](https://img.shields.io/github/license/andrewthomaslee/moscripts)](https://github.com/andrewthomaslee/moscripts/blob/main/LICENSE)
[![built with Nix](https://img.shields.io/badge/built_with-Nix-5277C3?logo=nixos&logoColor=white)](https://nixos.org)

Small Python CLIs packaged with Nix. One uv workspace (`pyproject.toml` +
`uv.lock`) is built by [uv2nix](https://github.com/pyproject-nix/uv2nix) into
one package with four commands:

| Command | Does |
| --- | --- |
| [`motmp`](cli/motmp.md) | create and edit temporary marimo notebooks |
| [`mpv_playlists`](cli/mpv_playlists.md) | play a playlist from `~/Music/Playlists` with mpv |
| [`password_generator`](cli/password_generator.md) | secure, customizable passwords |
| [`human_timestamp`](cli/human_timestamp.md) | a human-readable timestamp in any time zone |

## Install

Needs [Nix](https://nixos.org/download/) with flakes enabled
(`experimental-features = nix-command flakes` in `nix.conf`).

```sh
nix run github:andrewthomaslee/moscripts#password_generator -- --help
nix profile add github:andrewthomaslee/moscripts   # all four on PATH
nix flake show github:andrewthomaslee/moscripts
```

The tools the commands call (`gum`, `uv`, `mpv`) are pinned in the package
and appended to `PATH`, so your own copies win and nothing runs `nix run` at
runtime.

## In a flake

moscripts follows [external-systems/pkgs](https://github.com/external-systems/pkgs)
for nixpkgs and uv2nix, so a flake that already follows pkgs locks one extra
node for it:

```nix
inputs.moscripts = {
  url = "github:andrewthomaslee/moscripts";
  inputs.org-pkgs.follows = "org-pkgs";
};
# packages.${system}.default: every command; apps.${system}.<command>
```

external-systems/pkgs ships it as `pkgs.moscripts` in its default overlay.

## Slides

<iframe src="slides/index.html" title="Slide deck"
  style="width: 100%; aspect-ratio: 16 / 9; border: 0;"
  allowfullscreen></iframe>
