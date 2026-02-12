from fastapi import FastAPI , UploadFile, File
# from fastapi import UploadFile, File
from backend.pdf_utils import extract_text_from_pdf
from backend.vector_store import chunk_text, create_vector_store
from backend.rag import answer_question
import os
from dotenv import load_dotenv

load_dotenv()



app = FastAPI()

vector_store = None


@app.get("/") # url milta h 
def root(): # function to call the message 
    return {"message": "RAG Assistant Backend Running"} # message in json 


@app.post("/upload") #posting the upload request to the url
async def upload_pdf(file: UploadFile = File(...)): # uploading the file and making it asynchronous(baki sar kaaam continue hote rahenge)
    global vector_store
    text = extract_text_from_pdf(file.file) # function use kiya h pdf se text extract karne ke liye
    if not text:
        return {"message": "No text found in the PDF"} # agar text nahi mila to ye message dega
    #return {"message": "PDF text extracted", "length": len(text)} # response json format me

    chunks = chunk_text(text)
    vector_store = create_vector_store(chunks)
    return {"message": "Document processed successfully"} 

@app.post("/ask")
async def ask(question: str):
    if vector_store is None:
        return {"answer": "No document uploaded"}
    answer = answer_question(vector_store, question)
    return {"answer": answer}
