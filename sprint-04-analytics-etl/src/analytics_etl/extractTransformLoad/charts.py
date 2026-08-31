from pathlib import Path

from .dashboard import OUTPUT_FILE, create_dashboard


OUTPUT_DIR = OUTPUT_FILE.parent


def create_charts(database_file: Path = None, output_dir: Path = OUTPUT_DIR) -> list[Path]:
    """Generate the self-contained interactive analytics dashboard."""
    arguments = {"output_file": output_dir / OUTPUT_FILE.name}
    if database_file is not None:
        arguments["database_file"] = database_file
    return [create_dashboard(**arguments)]


if __name__ == "__main__":
    print(create_charts()[0])
