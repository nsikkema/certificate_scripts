from pathlib import Path

__all__ = ["root_path", "scripts_folder", "scratch_path", "templates_folder"]

scripts_folder = Path(__file__).parent.parent
templates_folder = scripts_folder / "templates"
root_path = scripts_folder.parent
scratch_path = root_path / "scratch"
