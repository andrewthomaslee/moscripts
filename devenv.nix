# The editable uv2nix venv: moscripts, its CLIs and the dev group on PATH,
# sources live from $DEVENV_ROOT/src. uv only edits uv.lock. The tools the
# CLIs exec (gum, uv, mpv) come from the same nixpkgs as the package.
{
  pkgs,
  lib,
  inputs,
  ...
}: let
  py = import ./flake-parts/_python/python-set.nix {
    inherit pkgs lib;
    inherit (inputs) uv2nix pyproject-nix pyproject-build-systems;
  };
in {
  packages = [py.devVenv pkgs.uv pkgs.gum pkgs.mpv];

  env = {
    UV_NO_SYNC = "1";
    UV_PYTHON = py.python.interpreter;
    UV_PYTHON_DOWNLOADS = "never";
  };

  # nixpkgs Python setup hooks leak PYTHONPATH; it beats the venv.
  enterShell = "unset PYTHONPATH";
}
