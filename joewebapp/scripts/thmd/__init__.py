from .compiled import Compile, Parse as ParseTHMC
from .parser import Script
from .thmdtokenizer import Tokenise

__all__ = [
    "CompileTHMD",
    "ParseTHMC",
    "ParseTHMD",
    "Script",
]


def parse_thmd(script):
    tokens = list(Tokenise(script.read()))
    return Script.Parse(tokens)


def compile_thmd(script):
    return Compile(Script.Parse(Tokenise(script.read())))


def parse_thmc(data):
    return ParseTHMC(data)


# Keep the original names available for existing callers.
ParseTHMD = parse_thmd
CompileTHMD = compile_thmd