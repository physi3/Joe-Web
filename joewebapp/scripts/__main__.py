from . import *

def compileMancino():
    script_directory = Path(__file__).parent
    source_path = script_directory / "mancino.thmd"
    compiled_path = script_directory / "mancino.thmc"

    with source_path.open(encoding="utf-8") as source_file:
        compiled_path.write_bytes(CompileTHMD(source_file))


if __name__ == "__main__":
    print("Compiling Mancino script...")
    compileMancino()