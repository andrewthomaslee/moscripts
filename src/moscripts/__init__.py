from .utilities import which_nix
from pathlib import Path


# Globals
HOME: Path = Path.home()
NIX: Path = which_nix()





def greet() -> None:
    print("Hello from moscripts!")

