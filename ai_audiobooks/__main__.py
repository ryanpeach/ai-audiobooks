from pathlib import Path
from dotenv import load_dotenv
from typer import Argument, Typer, Option

from ai_audiobooks.fix_text import iterative_fix_text
from ai_audiobooks.git import GitWorkingDirectory, git_create_working_dir
from ai_audiobooks.pandoc import convert_to_text

load_dotenv()  # take environment variables from .env.

app = Typer()


@app.command()
def main(
    input_file: Path = Argument(..., help="The input file to process."),
    working_directory_root: Path = Option(
        Path("output"),
        help="The root directory for ai working directories. This should be in your .gitignore.",
    ),
    force_ocr: bool = Option(
        False,
        help="Force OCR on the input file. Only works with PDF files.",
    ),
    just_edit: bool = Option(
        False,
        help="Just edit the text file. Don't convert the input file to text.",
    ),
):
    if not just_edit:
        git_repo = git_create_working_dir(
            input_file=input_file, working_directory_root=working_directory_root
        )
        convert_to_text(git_repo, force_ocr=force_ocr)
    else:
        git_repo = GitWorkingDirectory.from_file(input_file)
    iterative_fix_text(git_repo)


if __name__ == "__main__":
    app()
