from pathlib import Path
from ai_audiobooks.git import git_create_working_dir


def test_git_create_working_dir():
    # Test that the function creates the correct working directory.
    # Doesn't really matter what file you use
    out = git_create_working_dir(input_file=Path("examples/YellowWallpaper.pdf"))
    assert out.working_dir.exists()
    assert (out.working_dir / ".git").exists()
    assert out.input_file_copy.exists()
    assert Path(out.input_file_copy) == Path(
        "output/YellowWallpaper/YellowWallpaper.pdf"
    )
    out.delete()
