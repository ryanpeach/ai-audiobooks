from pathlib import Path
from ai_audiobooks.git import GitWorkingDirectory
from ai_audiobooks.pandoc import convert_to_text
import pytest


def test_pandoc_convert_to_text(git_working_directory: GitWorkingDirectory):
    # Test that the function writes the correct text to the correct file.
    convert_to_text(git_working_directory)
    assert Path(git_working_directory.text_file_path).exists()
    assert git_working_directory.text_file_path == Path(
        "output/YellowWallpaper/YellowWallpaper.txt"
    )


@pytest.mark.slow()
def test_pandoc_convert_to_text_pdf_ocred(git_working_directory: GitWorkingDirectory):
    if git_working_directory.input_file_copy.suffixes[-1].replace(".", "") != "pdf":
        pytest.skip("Only PDF files can be OCR'd.")
    # Test that the function writes the correct text to the correct file.
    convert_to_text(git_working_directory, force_ocr=True)
    assert Path(git_working_directory.text_file_path).exists()
    assert git_working_directory.text_file_path == Path(
        "output/YellowWallpaper/YellowWallpaper.txt"
    )
