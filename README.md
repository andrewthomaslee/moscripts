# moscripts
A collection of Python scripts managed by Nix



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
To run apps ( easy way ):
```bash
nix run github:andrewthomaslee/moscripts#motmp
```
To build package ( recommended ):
```bash
nix build github:andrewthomaslee/moscripts
```
To build docker image ( not recommended ):
```bash
nix build .#password_generator-container
```


# Apps
## motmp
MOTMP is a simple CLI that allows you to create and edit temporary marimo notbook files with a managed virtual environment. It's a great way to quickly create notebooks for testing or prototyping. Under the hood uses nix package manager to execute `uv` to manage the fallback virtual environment. MOTMP uses a directory in `~/.cache/marimo/motmp` to store temporary notebooks by default. If `.` is passed as the destination argument the notebook will be created inplace and will search for `.venv` in the current working directory.


```bash
nix run github:andrewthomaslee/moscripts#motmp -- --help
```
![MOTMP Help](screenshots/motmp--help.png)


## mpv_playlists
Launches mpv with a playlist from `~/Music/Playlists`.


```bash
nix run github:andrewthomaslee/moscripts#mpv_playlists -- --help
```
![mpv_playlists Example](screenshots/mpv_playlists--scan.png)


## password_generator
A secure, customizable password generator.


```bash
nix run github:andrewthomaslee/moscripts#password_generator -- --help
```
![password_generator Run](screenshots/password_generator--run.png)


## human_timestamp
A simple human-readable timestamp. Defaults to `America/Chicago` because Texas is the only time zone I recognize.
```bash
nix run github:andrewthomaslee/moscripts#human_timestamp -- --help
```