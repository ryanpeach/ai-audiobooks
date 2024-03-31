from pathlib import Path
from typing import Generator

from ai_audiobooks.git import GitWorkingDirectory, git_create_working_dir
import pytest


@pytest.fixture(
    params=[Path("examples/YellowWallpaper.pdf"), Path("examples/YellowWallpaper.epub")]
)
def git_working_directory(request) -> Generator[GitWorkingDirectory, None, None]:
    # Create a working directory for the input file.
    wd = git_create_working_dir(input_file=request.param)
    yield wd
    wd.delete()
