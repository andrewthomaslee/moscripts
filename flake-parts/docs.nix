# Docs settings that differ from the org defaults (flakeModules.docs). This
# repo lives on a personal account, not in external-systems, so `docs.repo`
# (which points every URL at external-systems) stays unset and the URLs are
# set directly.
_: {
  perSystem.docs = {
    settings = {
      site_name = "moscripts";
      site_url = "https://andrewthomaslee.github.io/moscripts/";
      repo_url = "https://github.com/andrewthomaslee/moscripts";
      repo_name = "andrewthomaslee/moscripts";
      edit_uri = "edit/main/documentation/docs/";
      nav = [
        {Home = "index.md";}
        {
          Commands = [
            "cli/motmp.md"
            "cli/mpv_playlists.md"
            "cli/password_generator.md"
            "cli/human_timestamp.md"
          ];
        }
        {Development = "development.md";}
      ];
    };
    slides.title = "moscripts";
  };
}
