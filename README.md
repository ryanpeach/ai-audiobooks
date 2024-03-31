# ai-audiobooks
A library for taking any arbitrary file and converting it into an audiobook using AI. Please do not use commercially.

**Work in progress**

# Installation

First [install poetry](https://python-poetry.org/docs/#installing-with-pipx)

Then:

## MacOSX

```bash
brew install tesseract pandoc just
pipx install poetry
poetry install
poetry run pre-commit install
```

## Ubuntu

```bash
sudo apt install pandoc tesseract-ocr libtesseract-dev just
pipx install poetry
poetry install
poetry run pre-commit install
```

## OpenAI

You will need to create an account on OpenAI and get an API key.
You can do that [here](https://platform.openai.com/signup)

Then you will need to set the API key as an environment variable. Create a `.env`
file in the root of the project and add the following:

```
OPENAI_API_KEY=your-api-key
```
