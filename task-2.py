import os 
import streamlit as st
import pickle
import time
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

st.title("Task-2: Chat with Websites using LLM")
st.sidebar.title("Web Scraping")
urls_input = st.sidebar.text_area("Enter URLs (one per line)", height=150)

# Extract URLs from each line
urls = [url.strip() for url in urls_input.split("\n") if url.strip()]

chat_history = []

process_url_clicked = st.sidebar.button("Process URLs")
file_path = "faiss_store_openai.pkl"

main_placeholder = st.empty()
llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-70b-versatile")

if process_url_clicked:
    try:
        # Load data from URLs
        loader = UnstructuredURLLoader(urls=urls)
        main_placeholder.text("Data Loading...Started...✅✅✅")
        data = loader.load()
        
        # Split data into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.', ','],
            chunk_size=1000
        )
        main_placeholder.text("Text Splitter...Started...✅✅✅")
        docs = text_splitter.split_documents(data)
        
        # Create embeddings and save to FAISS index
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore_openai = FAISS.from_documents(docs, embeddings)
        main_placeholder.text("Embedding Vector Started Building...✅✅✅")
        time.sleep(2)

        # Save the FAISS index to a pickle file
        with open(file_path, "wb") as f:
            pickle.dump(vectorstore_openai, f)
    except Exception as e:
        main_placeholder.error(f"Error processing URLs: {str(e)}")

query = main_placeholder.text_input("Question: ")
if query:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            vectorstore = pickle.load(f)
            chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())

            result = chain({"question": query, "chat_history": chat_history})
    
            # Append current question and answer to chat history
            chat_history.append((query, result["answer"]))
            st.header("Answer")
            st.write(result["answer"])