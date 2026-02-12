from pypdf import PdfReader


def extract_text_from_pdf(pdf_file): #text extract usin the functions 
    reader = PdfReader(pdf_file) # load pdf into memory 
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n" # extract text from each page and add to the final text
    return text 