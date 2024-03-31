from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from guidance import models, user, assistant, system, gen
import tiktoken
import guidance
import re
import typer

from ai_audiobooks.git import GitWorkingDirectory


load_dotenv()  # take environment variables from .env.


@dataclass
class LLM:
    name = "gpt-4-turbo-preview"
    guidance_model = models.OpenAIChat("gpt-4-turbo-preview")
    max_tokens = 128_000
    output_tokens = 8_000
    enc = tiktoken.encoding_for_model("gpt-4-turbo-preview")


def sample_text(*, llm: LLM, file: Path) -> str:
    # Get the text from the file.
    text = file.read_text()

    # Tokenize the text.
    tokens = llm.enc.encode(text)

    # Sample the first max_tokens - output_tokens tokens.
    tokens = tokens[: llm.max_tokens - llm.output_tokens]

    # Decode the tokens.
    return llm.enc.decode(tokens)


@dataclass
class LLMResponse:
    plan: str
    regex: str


REGEX = "```regex\n(.*)\n```"
PROMPT = (
    "Generate a regex that matches the very beginning of each chapter for given text. "
    f"Wrap the regex in something which matches the pattern {REGEX}. "
    "Begin your response with a plan for what the regex will accomplish. "
    "It will end with the regex itself. "
)


@guidance
def split_chapters_regex(*, llm: LLM, file: Path) -> LLMResponse:
    text = sample_text(llm=llm, file=file)
    lm = llm.guidance_model
    done = False
    with system():
        lm += PROMPT
    with user():
        lm += text
    while not done:
        with assistant():
            lm += gen("plan") + gen("regex", regex=REGEX)
        # Validate the regex.
        if lm.get("regex") is None:
            with user():
                lm += "Your output did not include a regex. Please try again. "
        try:
            re.compile(lm["regex"])
            done = True
        except re.error as e:
            with user():
                lm += f"Your regex was invalid. {e}. Please try again. "
    return LLMResponse(plan=lm.get("plan"), regex=lm.get("regex"))


@guidance
def try_again(
    *, llm: LLM, response: LLMResponse, wd: GitWorkingDirectory
) -> LLMResponse:
    text = sample_text(llm=llm, file=wd.text_file_path)
    lm = llm.guidance_model
    done = False
    with system():
        lm += PROMPT
    with user():
        lm += text
        lm += f"The regex you generated last was {response.regex}. "
        lm += f"Your plan was {response.plan}. "
        lm += "Here are some chapter splits you generated: "
        for chapter in (wd.working_dir / "chapters").glob("chapter_*.txt"):
            lm += "```\n"
            lm += "\n".join(chapter.read_text().split("\n", 10))
            lm += "```\n"
        lm += "I don't believe this is correct. Please try again. "
    while not done:
        with assistant():
            lm += gen("plan") + gen("regex", regex=REGEX)
        # Validate the regex.
        if lm.get("regex") is None:
            with user():
                lm += "Your output did not include a regex. Please try again. "
        try:
            re.compile(lm["regex"])
            done = True
        except re.error as e:
            with user():
                lm += f"Your regex was invalid. {e}. Please try again. "
    return LLMResponse(plan=lm.get("plan"), regex=lm.get("regex"))


def split_chapters(
    *, llm: LLM, wd: GitWorkingDirectory, response: Optional[LLMResponse] = None
) -> None:
    if response is None:
        response = split_chapters_regex(llm=llm, file=wd.text_file_path)
    regex = re.compile(response.regex)
    text = wd.text_file_path.read_text()
    # Split the text by the regex.
    chapters = regex.split(text)
    # Save the chapters to files.
    for i, chapter in enumerate(chapters):
        chapter_path = wd.working_dir / "chapters" / f"chapter_{i}.txt"
        chapter_path.write_text(chapter)
        wd.repo.index.add([chapter_path.relative_to(wd.working_dir)])

    # Commit the new chapters.
    wd.repo.commit("Split chapters")

    if typer.prompt("Please check the chapters. Are they correct? (yes/no)") != "yes":
        for chapter in (wd.working_dir / "chapters").glob("chapter_*.txt"):
            wd.repo.index.remove([chapter], working_tree=True)
        split_chapters(
            llm=llm, wd=wd, response=try_again(llm=llm, response=response, wd=wd)
        )
