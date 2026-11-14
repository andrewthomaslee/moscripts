{
  description = "moscripts: small Python CLIs (motmp, mpv_playlists, password_generator, human_timestamp) built with uv2nix";

  inputs = {
    # Shared-input authority: every pin below comes from external-systems/pkgs,
    # so a consumer that already follows it locks nothing new. pkgs itself
    # consumes this flake with `inputs.org-pkgs.follows = ""` (see AGENTS.md).
    org-pkgs.url = "github:external-systems/pkgs";
    nixpkgs.follows = "org-pkgs/nixpkgs";
    flake-parts.follows = "org-pkgs/flake-parts";
    import-tree.follows = "org-pkgs/import-tree";
  };

  outputs = inputs:
    inputs.flake-parts.lib.mkFlake {inherit inputs;} {
      # Exposes debug.options / currentSystem.options, which nixd
      # (.vscode/settings.json) reads for flake-parts option hints.
      debug = true;

      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      imports = [
        # treefmt, docs + slides, lock-sync, vm-tests: everything from pkgs.
        inputs.org-pkgs.flakeModules.default
        (inputs.import-tree ./flake-parts)
      ];
    };
}
