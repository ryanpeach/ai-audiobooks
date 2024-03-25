from ai_audiobooks.git import GitWorkingDirectory
import pypandoc


def pandoc_convert_to_text(wd: GitWorkingDirectory) -> None:
    """Convert the input file to plain text using pandoc."""
    # Convert the file
    output = pypandoc.convert_file(
        source_file=wd.input_file_copy,
        to="plain",
        format=wd.input_file_copy.suffixes[-1],
    )
    # Save the converted text to a file
    with open(wd.text_file_path, "w") as f:
        f.write(output)

    # Commit the new text file
    wd.repo.index.add([wd.text_file_path])
    wd.repo.commit("Converted to text")
