import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableSequence
from langchain.prompts import load_prompt
from docx import Document
import io

# Function to read the content of the uploaded file
def read_uploaded_file(file):
    if file.name.endswith('.docx'):
        doc = Document(file)  # Pass the file object directly
        return ' '.join([paragraph.text for paragraph in doc.paragraphs])
    else:
        return file.read().decode("utf-8")  # For text files, read the content directly

# Load prompts from files
prompt_template_WRITER = load_prompt("Prompts/Writer.yaml")
prompt_template_REVISOR = load_prompt("Prompts/Revisor.yaml")
prompt_template_CORRECTOR = load_prompt("Prompts/Corrector.yaml")
prompt_template_FINAL = load_prompt("Prompts/Final.yaml")

# Streamlit app
def main():
    st.title("INFORME ALTA MÉDICA, IA W-T-R-F")

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
                    gemini_pro = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=google_api_key, temperature="0.1")
                    gemini_flash = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key, temperature="0.1")

                    # Create chains
                    chain_1 = RunnableSequence(prompt_template_WRITER, gemini_pro)
                    chain_2 = RunnableSequence(prompt_template_REVISOR, gemini_flash)
                    chain_3 = RunnableSequence(prompt_template_CORRECTOR, gemini_flash)
                    chain_4 = RunnableSequence(prompt_template_FINAL, gemini_pro)
                    

                    # Generate reports
                    report_original = chain_1.invoke({"DOCUMENTOS_CLINICOS": file_content})
                    report_revised = chain_2.invoke({"DOCUMENTOS_CLINICOS": file_content, "INFORME_ORIGINAL": report_original})
                    report_corrected = chain_3.invoke({"INFORME_ORIGINAL": report_original, "CORRECCIONES": report_revised})
                    report_final = chain_4.invoke({"REPORT_FINAL": report_corrected})

                    # Create a download button for the final report
                    doc = Document()
                    doc.add_paragraph(report_final.content)
                    
                    bio = io.BytesIO()
                    doc.save(bio)
                    
                    st.download_button(
                        label="Download Report as DOCX",
                        data=bio.getvalue(),
                        file_name="final_report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                    # Display the final report
                    st.markdown(report_final.content)

            else:
                st.error("Please enter your Google API Key to process the document.")

if __name__ == "__main__":
    main()
