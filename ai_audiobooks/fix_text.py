import re
from ai_audiobooks.git import GitWorkingDirectory
from rich.prompt import Console, Confirm, Prompt
import guidance
from guidance import gen, system, user, assistant
from guidance.models import OpenAIChat
from IPython import display
from ai_audiobooks.llm import LLM, sample_text

console = Console()


@guidance
def fix_text(llm: OpenAIChat, sample_text: str, user_in: str) -> dict[str, str]:
    with system():
        llm += "You process the following sample text:\n"
        llm += "```\n"
        llm += sample_text
        llm += "```\n"
        llm += "You describe what you are going to do based on the users query\n"
        llm += (
            "and then output a 'pattern' and a 'replacement' regex to fix the text.\n"
        )
        llm += "The pattern could be like:\n"
        llm += "```pattern\n"
        llm += "\d(.*)\n"
        llm += "```\n\n"
        llm += "The replacement could be like:\n"
        llm += "```replacement\n"
        llm += "$1\n"
        llm += "```\n"
        llm += "Always give the plan, pattern, and replacement in that order."
        llm += "Be sure to put the pattern and replacement in the correct markdown code block exactly as shown."
    with user():
        llm += user_in
    with assistant():
        llm += gen("plan", temperature=0.5)
        llm += "```pattern\n" + gen("pattern", stop="\n", temperature=0) + "```\n"
        llm += gen()
        llm += "```replacement\n" + gen("replacement", stop="\n", temperature=0) + "```"
    return {
        "plan": llm["plan"],
        "pattern": llm["pattern"],
        "replacement": llm["replacement"],
    }


def iterative_fix_text(*, llm: LLM, git: GitWorkingDirectory) -> None:
    console.print(f"Please check the file at {git.text_file_path} for errors.")
    yn = Confirm().ask("Does the current text need any editing?")
    while yn:
        # Prompt the user for string input.
        user_in = (
            Prompt()
            .ask(
                "What would you like me to fix? Type \\undo to undo the last fix. Type enter to skip."
            )
            .strip()
        )

        # Commands:
        # The undo command.
        if user_in == "\\undo":
            git.repo.git.revert("HEAD", no_edit=True)
            console.print("Last fix has been undone.")
            continue

        # The skip command.
        elif user_in == "":
            break

        # Query the LLM
        out = llm.guidance_model + fix_text(
            sample_text(file=git.text_file_path, llm=llm), user_in
        )
        display(out["plan"])

        # Confirm the fix.
        yn = Confirm().ask(
            f"Would you like to execute the following regex: `s/{out['pattern']}/{out['replacement']}/g`"
        )
        if yn:
            text = git.text_file_path.read_text()
            text = re.sub(out["pattern"], out["replacement"], text)
            git.text_file_path.write_text(text)
            git.repo.index.add([git.text_file_path.relative_to(git.working_dir)])
            git.repo.commit("User asked: " + user_in)
            console.print("Text has been fixed.")
            console.print(f"Please check the file at {git.text_file_path} for errors.")
