# The editable venv, uv, ruff and ty come from org-pkgs/devenv/python
# (devenv.yaml). The tools the CLIs exec (gum, mpv) come from the same
# nixpkgs as the package.
{pkgs, ...}: {
  packages = [pkgs.gum pkgs.mpv];
}
