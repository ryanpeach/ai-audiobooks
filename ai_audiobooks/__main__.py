from pathlib import Path
from dotenv import load_dotenv
from typer import Typer, Option

from ai_audiobooks.git import git_create_working_dir
from ai_audiobooks.llm import LLM, split_chapters
from ai_audiobooks.pandoc import pandoc_convert_to_text

load_dotenv()  # take environment variables from .env.

app = Typer()

@app.command()
def main(
    input_file: Path = Option(..., help="The input file to process."),
    working_directory_root: Path = Option(
        Path("working_dir"), help="The root directory for ai working directories. This should be in your .gitignore."
    ),
):
    git_repo = git_create_working_dir(input_file=input_file, working_directory_root=working_directory_root)
    pandoc_convert_to_text(git_repo)
    split_chapters(llm=LLM(), wd=git_repo)

if __name__ == "__main__":
    app()