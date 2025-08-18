# moscripts
A collection of Python scripts


## Determinate Systems Nix installer
Determinate Nix Installer is the easiest and most reliable way to install Nix on your system. This will enable flakes by default.
1. Download [Determinate Systems Nix installer](https://github.com/DeterminateSystems/nix-installer) with one command:
```bash
curl -fsSL https://install.determinate.systems/nix | sh -s -- install --determinate
```


## Discover flake options
```bash
nix flake show github:andrewthomaslee/moscripts
```

## Usage
To run apps:
```bash
nix run github:andrewthomaslee/moscripts#motmp
```
To build package:
```bash
nix build github:andrewthomaslee/moscripts
```
To build docker image:
```bash
nix build github:andrewthomaslee/moscripts#packages.x86_64-linux.greet-container
```


# Apps
## motmp
MOTMP is a simple CLI that allows you to create and edit temporary marimo notbook files with a managed virtual environment.
```bash
nix run github:andrewthomaslee/moscripts#motmp -- --help
```
## mpv_playlists
Launches mpv with a playlist.
```bash
nix run github:andrewthomaslee/moscripts#mpv_playlists -- --help
```
## password_generator
A secure, customizable password generator.
```bash
nix run github:andrewthomaslee/moscripts#password_generator -- --help
```
## human_timestamp
A simple human-readable timestamp.
```bash
nix run github:andrewthomaslee/moscripts#human_timestamp -- --help
```