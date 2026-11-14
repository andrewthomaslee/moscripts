# Python: flakeModules.python (from org-pkgs flakeModules.default) builds
# the uv workspace: packages, apps, checks and the python-cli VM test.
# Only what is specific to moscripts lives here.
_: {
  perSystem = {pkgs, ...}: {
    python = {
      # The programs the CLIs exec, appended to their PATH.
      runtimeInputs = [pkgs.gum pkgs.uv pkgs.mpv];
      # tests look the programs up with `which`.
      checkInputs = [pkgs.which];
    };
  };
}
