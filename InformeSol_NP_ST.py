import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableSequence
from langchain.prompts import load_prompt
from docx import Document
import io

# Function to read the content of the uploaded file
def read_uploaded_file(uploaded_file):
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(io.BytesIO(uploaded_file.getvalue()))
        return ' '.join([paragraph.text for paragraph in doc.paragraphs])
    else:
        return uploaded_file.getvalue().decode("utf-8")

# Load prompts from files
prompt_template_WRITER = load_prompt("C:/Users/marcv/PYTHON/InformeSol/Prompts/Writer.yaml")
prompt_template_TREATMENT = load_prompt("C:/Users/marcv/PYTHON/InformeSol/Prompts/Treatment.yaml")
prompt_template_REVISOR = load_prompt("C:/Users/marcv/PYTHON/InformeSol/Prompts/Revisor.yaml")
prompt_template_FINAL = load_prompt("C:/Users/marcv/PYTHON/InformeSol/Prompts/Final.yaml")

# Streamlit app
def main():
    st.title("INNEX: INFORME IA")

    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "docx"])

    if uploaded_file is not None:
        # Read the content of the uploaded file
        file_content = read_uploaded_file(uploaded_file)

        # Google API Key input
        google_api_key = st.text_input("Enter your Google API Key", type="password")

        if st.button("Process Document"):
            if google_api_key:
                with st.spinner("Processing document..."):
                    # Initialize language models
                    gemini_pro = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=google_api_key)
                    gemini_flash = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)

                    # Create chains
                    chain_1 = RunnableSequence(prompt_template_WRITER, gemini_pro)
                    chain_2 = RunnableSequence(prompt_template_TREATMENT, gemini_pro)
                    chain_3 = RunnableSequence(prompt_template_REVISOR, gemini_flash)
                    chain_4 = RunnableSequence(prompt_template_FINAL, gemini_flash)
                    

                    # Generate reports
                    report_original = chain_1.invoke({"DOCUMENTOS_CLINICOS": file_content})
                    report_treatment = chain_2.invoke({"DOCUMENTOS_CLINICOS": file_content})
                    corrections = chain_3.invoke({"DOCUMENTOS_CLINICOS": file_content, "INFORME_ORIGINAL": report_original})
                    report_final = chain_4.invoke({"INFORME_ORIGINAL": report_original, "TRATAMIENTOS": report_treatment, "CORRECCIONES": corrections})

                    # Display the final report
                    st.markdown(report_final.content)
            else:
                st.error("Please enter your Google API Key to process the document.")

if __name__ == "__main__":
    main()
