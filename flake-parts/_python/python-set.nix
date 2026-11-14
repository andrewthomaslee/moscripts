# The uv workspace at the repo root as a pyproject.nix Python set. A plain
# function (the `_` keeps import-tree out), shared by flake-parts/python.nix
# (packages, checks) and devenv.nix (the editable dev venv), so both build
# one set.
{
  pkgs,
  lib,
  uv2nix,
  pyproject-nix,
  pyproject-build-systems,
}: let
  workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ../..;};

  # The first nixpkgs interpreter inside the lock's requires-python.
  python = lib.head (pyproject-nix.lib.util.filterPythonInterpreters {
    inherit (workspace) requires-python;
    inherit (pkgs) pythonInterpreters;
  });

  pythonSet =
    (pkgs.callPackage pyproject-nix.build.packages {inherit python;}).overrideScope
    (lib.composeManyExtensions [
      pyproject-build-systems.overlays.wheel
      (workspace.mkPyprojectOverlay {sourcePreference = "wheel";})
      (import ./overrides.nix {inherit pkgs;})
    ]);

  # moscripts installed as a pointer into $DEVENV_ROOT/src, expanded by
  # Python at import time: edits apply without a rebuild.
  editableSet = pythonSet.overrideScope (workspace.mkEditablePyprojectOverlay {
    root = "$DEVENV_ROOT";
  });
in {
  inherit workspace python pythonSet editableSet;
  venv = pythonSet.mkVirtualEnv "moscripts-env" workspace.deps.default;
  testVenv = pythonSet.mkVirtualEnv "moscripts-test-env" workspace.deps.all;
  devVenv = editableSet.mkVirtualEnv "moscripts-dev-env" workspace.deps.all;
}
