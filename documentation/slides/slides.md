<!-- .slide: class="title-slide" -->

<p class="kicker">andrewthomaslee</p>

# moscripts

Small Python CLIs, one uv lock, built by Nix.

Note: Press `S` for the speaker view, `F` for fullscreen, `Esc` for the
overview.

---

## Four commands

| Command | Does |
| --- | --- |
| `motmp` | temporary marimo notebooks with a managed venv |
| `mpv_playlists` | play `~/Music/Playlists` with mpv |
| `password_generator` | secure, customizable passwords |
| `human_timestamp` | the time, readable, in any zone |

<p class="hint">nix run github:andrewthomaslee/moscripts#&lt;command&gt;</p>

---

## From uv.lock to a binary

<div class="diagram">
<svg class="sketch" viewBox="0 0 1200 300">
  <rect x="20" y="90" width="250" height="120" stroke="#d97757" fill="#d97757" />
  <text x="145" y="145" text-anchor="middle">pyproject.toml</text>
  <text x="145" y="180" text-anchor="middle">uv.lock</text>
  <g class="fragment fade-in">
    <line x1="280" y1="150" x2="430" y2="150" stroke="#faf9f5" data-arrow />
    <rect x="440" y="90" width="300" height="120" stroke="#6a9bcc" fill="none" />
    <text x="590" y="145" text-anchor="middle">uv2nix Python set</text>
    <text x="590" y="180" text-anchor="middle" class="mono">one drv per wheel</text>
  </g>
  <g class="fragment fade-in">
    <line x1="750" y1="150" x2="900" y2="150" stroke="#faf9f5" data-arrow />
    <rect x="910" y="90" width="270" height="120" stroke="#8fa876" fill="#8fa876" />
    <text x="1045" y="145" text-anchor="middle">packages.default</text>
    <text x="1045" y="180" text-anchor="middle" class="mono">4 wrapped CLIs</text>
  </g>
</svg>
</div>

- Each `[project.scripts]` entry becomes a binary and a `nix run` app
- `gum`, `uv`, `mpv` are pinned and appended to `PATH`: no `nix run` at runtime

---

## One pin for the org

<div class="layer"><span>external-systems/pkgs</span><span>nixpkgs, flake-parts, uv2nix, pyproject.nix, build systems</span></div>
<div class="layer"><span>moscripts</span><span>follows all of them: declares no URL of its own</span></div>
<div class="layer"><span>pkgs consumes it</span><span><code>inputs.org-pkgs.follows = ""</code>: points back at pkgs itself</span></div>

<div class="takeaway fragment fade-up">moscripts costs its consumers one lock node: no second nixpkgs, no second uv2nix.</div>

Note: Before, pkgs, modules and home each locked moscripts' own uv2nix,
pyproject.nix, build-system-pkgs and nix-systems at older revisions.

---

## Develop

```sh
devenv allow   # editable venv: src/ is live, no rebuilds
uv add httpx   # uv edits uv.lock only
fmt && check   # pytest, pyrefly, ruff, uv-lock, treefmt, docs
vm-test cli-smoke --remote --rebuild
```

<ul class="ticks">
  <li>CI: the org <code>ci / flake-check</code></li>
  <li>Docs and this deck: GitHub Pages on <code>main</code></li>
  <li>Releases: <code>0.2.&lt;commits&gt;</code></li>
</ul>

---

<!-- .slide: class="title-slide" -->

# Thanks

<p class="muted">github.com/andrewthomaslee/moscripts</p>
