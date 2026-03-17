from pypdf import PdfReader
import re


def clean_text(text):
    # remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # remove weird characters like !! "
    text = re.sub(r'[!"]+', '', text)

    return text.strip()


def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:  # avoid None pages
            text += page_text + "\n"

    # clean the extracted text
    text = clean_text(text)

    return text