from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate


def answer_question(vector_store, question):
    retriever = vector_store.as_retriever(search_kwargs={"k": 4}) #top 4 chunks 
    docs = retriever.invoke(question)

    if not docs:
        return "Context not found in document"

    context = "\n".join(doc.page_content for doc in docs)

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are a strict PDF-based assistant.

Answer the question ONLY using the provided context.
If the answer is not present in the context,
respond exactly with:

Context not found in document

Context:
{context}

Question:
{question}

Answer:
"""
    )

    llm = OllamaLLM(model="mistral")

    formatted_prompt = prompt.format(context=context, question=question)

    response = llm.invoke(formatted_prompt)

    # Safety check
    if "Context not found in document" in response:
        return "Context not found in document"

    return response
