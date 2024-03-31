import re
from ai_audiobooks.git import GitWorkingDirectory
from rich.prompt import Console, Confirm, Prompt
import guidance
from guidance import gen

from ai_audiobooks.llm import LLM, sample_text

console = Console()


@guidance
def iterative_fix_text(llm: LLM, git: GitWorkingDirectory) -> None:
    console.print(f"Please check the file at {git.text_file_path} for errors.")
    yn = Confirm("Does the current text need any editing?").ask()
    while yn:
        # Redescribe the task.
        with llm.system():
            llm += "You process the following sample text:"
            llm += "```"
            llm += sample_text(file=git.text_file_path, llm=llm)
            llm += "```"
            llm += "You describe what you are going to do based on the users query"
            llm += (
                "and then output a 'pattern' and a 'replacement' regex to fix the text."
            )
            llm += "The pattern could be like:"
            llm += "```pattern"
            llm += "\d(.*)"
            llm += "```"
            llm += "The replacement could be like:"
            llm += "```replacement"
            llm += "$1"
            llm += "```"

        # Prompt the user for string input.
        user_in = (
            Prompt(
                "What would you like me to fix? Type \\undo to undo the last fix. Type enter to skip."
            )
            .ask()
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
        with llm.user():
            llm += user_in
        with llm.assistant():
            llm += gen("plan")
            llm += "```pattern\n" + gen("pattern", stop="\n") + "```"
            llm += "```replacement\n" + gen("replacement", stop="\n") + "```"
        console.print(llm["plan"])

        # Confirm the fix.
        yn = Confirm(
            f"Would you like to execute the following regex: `s/{llm['pattern']}/{llm['replacement']}/g`"
        ).ask()
        if yn:
            text = git.text_file_path.read_text()
            text = re.sub(llm["pattern"], llm["replacement"], text)
            git.text_file_path.write_text(text)
            git.repo.index.add([git.text_file_path.relative_to(git.working_dir)])
            git.repo.commit("User asked: " + user_in)
            console.print("Text has been fixed.")
            console.print(f"Please check the file at {git.text_file_path} for errors.")
