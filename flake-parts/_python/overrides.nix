# Build fixups uv.lock cannot express: native libraries for wheels, build
# systems for sdists. Plain overlay over the Python set, called with
# {inherit pkgs;}; empty while every locked package ships a wheel that needs
# nothing extra. When adding one, take `{pkgs}:` and `final: prev:`.
_: _final: _prev: {}
