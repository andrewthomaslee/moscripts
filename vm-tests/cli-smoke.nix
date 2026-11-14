# The installed moscripts package on an offline NixOS machine: every command
# runs as a normal user, and the tools the commands exec (gum, uv, mpv) come
# from the package's own closure, never from `nix run`.
{self, ...}: {
  nodes.machine = {pkgs, ...}: {
    environment.systemPackages = [self.packages.${pkgs.stdenv.hostPlatform.system}.default];
    users.users.alice = {
      isNormalUser = true;
      uid = 1000;
    };
    virtualisation = {
      memorySize = 1024;
      cores = 1;
    };
  };

  testScript = ''
    import re

    def as_alice(cmd):
        # Wide COLUMNS: rich must not wrap the printed mpv command line.
        return f"su - alice -c 'COLUMNS=400 {cmd}'"

    start_all()
    machine.wait_for_unit("multi-user.target", timeout=300)

    with subtest("every command answers --help without side effects"):
        for cli in ["motmp", "mpv_playlists", "password_generator", "human_timestamp"]:
            out = machine.succeed(as_alice(f"{cli} --help"))
            assert "Usage" in out, out

    with subtest("pinned gum, uv and mpv are on the wrapper's PATH"):
        wrapper = machine.succeed("cat \"$(command -v motmp)\"")
        bins = set(re.findall(r"/nix/store/[^:'\"\s]+/bin", wrapper))
        for tool in ["gum", "uv", "mpv"]:
            assert any(f"-{tool}" in b for b in bins), (tool, bins)
        for b in bins:
            machine.succeed(f"test -d {b}")

    with subtest("password_generator"):
        pw = machine.succeed(as_alice("password_generator -l 40 --cli")).strip()
        assert len(pw) == 40, pw
        custom = machine.succeed(as_alice("password_generator -l 32 -c ab --cli")).strip()
        assert len(custom) == 32 and set(custom) <= {"a", "b"}, custom
        out = machine.succeed(as_alice("password_generator --length 24"))
        assert "length=24" in out, out

    with subtest("human_timestamp"):
        ts = machine.succeed(as_alice("human_timestamp -t UTC")).strip()
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} (AM|PM)", ts), ts
        machine.fail(as_alice("human_timestamp -t Not/AZone"))

    with subtest("mpv_playlists"):
        machine.fail(as_alice("mpv_playlists --directory /nonexistent"))
        # A playlist whose only entry is missing: mpv starts, fails the entry
        # and exits, which is all the test needs (no audio device in the VM).
        # Created as alice: tmpfiles refuses root writes into a user's home.
        machine.succeed(as_alice(
            "mkdir -p ~/Music/Playlists && echo /nonexistent/song.ogg > ~/Music/Playlists/road-trip.m3u"
        ))
        machine.fail(as_alice("mpv_playlists missing.m3u"))
        # Default directory and first playlist; execs the pinned mpv.
        _, out = machine.execute(as_alice("timeout 60 mpv_playlists --no-shuffle") + " 2>&1")
        print(out)
        assert "road-trip.m3u" in out, out
        assert re.search(r"/nix/store/[^']+-mpv[^']*/bin/mpv", out), out
  '';
}
