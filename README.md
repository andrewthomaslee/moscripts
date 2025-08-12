# moscripts
A collection of Python scripts


# Installation
## Determinate Systems Nix installer
Determinate Nix Installer is the easiest and most reliable way to install Nix on your system. This will enable flakes by default.
1. Download [Determinate Systems Nix installer](https://github.com/DeterminateSystems/nix-installer)
```bash
curl -fsSL https://install.determinate.systems/nix | sh -s -- install --determinate
```
## Standalone Nix
1. Download [Nix](https://nixos.org/download/)
2. For Nix standalone (without NixOS or Home Manager):
    Add the following line to your Nix configuration file, located at either ~/.config/nix/nix.conf or /etc/nix/nix.conf:
```
experimental-features = nix-command flakes
```


# Usage
To run apps:
```bash
nix run github:andrewthomaslee/moscripts#greet
```
To build package:
```bash
nix build github:andrewthomaslee/moscripts
```
To build docker image:
```bash
nix build github:andrewthomaslee/moscripts#packages.x86_64-linux.docker
```