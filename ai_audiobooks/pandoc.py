from pathlib import Path
from ai_audiobooks.git import GitWorkingDirectory
import pypandoc
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from rich.progress import track


def convert_to_text(wd: GitWorkingDirectory, *, force_ocr: bool = False) -> None:
    """Convert the input file to plain text using pandoc."""
    # Convert the file
    fmt = wd.input_file_copy.suffixes[-1].replace(".", "")
    if fmt == "pdf":
        output = _pdf_to_text(wd.input_file_copy, force_ocr=force_ocr)
    else:
        if force_ocr:
            raise ValueError("Only PDF files can be OCR'd.")
        output = pypandoc.convert_file(
            source_file=wd.input_file_copy,
            to="plain",
            format=fmt,
        )

    # Save the converted text to a file
    with open(wd.text_file_path, "w") as f:
        f.write(output)

    # Commit the new text file
    wd.repo.index.add([wd.text_file_path.relative_to(wd.working_dir)])
    wd.repo.index.commit("Converted to text")


def _pdf_to_text(pdf_path: Path, *, force_ocr: bool = False) -> str:
    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Initialize an empty string to collect all text
    full_text = ""

    # Iterate over each page in the PDF
    for page_num in track(range(len(doc)), description="Extracting text from PDF"):
        page = doc.load_page(page_num)

        # First, try to extract text directly
        text = page.get_text()

        if not force_ocr and text.strip():  # If text is found, add it to the full_text
            full_text += text
        else:  # If no text is found, attempt OCR
            for img in page.get_images(full=True):
                # get the XREF of the image
                xref = img[0]
                # extract the image bytes
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                # load it to PIL
                image = Image.open(io.BytesIO(image_bytes))
                # use pytesseract to do OCR on the image
                text = pytesseract.image_to_string(image, lang="eng")
                full_text += text

    doc.close()
    return full_text
