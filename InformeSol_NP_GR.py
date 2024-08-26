import gradio as gr
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableSequence
from langchain.prompts import load_prompt
from docx import Document
import io

def read_uploaded_file(file):
    if file.name.endswith('.docx'):
        doc = Document(io.BytesIO(file.read()))
        return ' '.join([paragraph.text for paragraph in doc.paragraphs])
    else:
        return file.read().decode('utf-8')

# Load prompts from files
prompt_template_WRITER = load_prompt("Prompts/Writer.yaml")
prompt_template_REVISOR = load_prompt("Prompts/Revisor.yaml")
prompt_template_CORRECTOR = load_prompt("Prompts/Corrector.yaml")
prompt_template_FINAL = load_prompt("Prompts/Final.yaml")

def process_document(file, google_api_key):
    if not file or not google_api_key:
        return "Please upload a file and enter your Google API Key."

    file_content = read_uploaded_file(file)

    # Initialize language models
    gemini_pro = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=google_api_key)
    gemini_flash = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)

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

    return report_final.content

# Define the Gradio interface
iface = gr.Interface(
    fn=process_document,
    inputs=[
        gr.File(label="Upload a file (txt or docx)"),
        gr.Textbox(label="Enter your Google API Key", type="password")
    ],
    outputs=gr.Markdown(label="Generated Report"),
    title="INFORME ALTA MÉDICA, IA W-T-R-F",
    description="Upload a medical document and enter your Google API Key to generate a report."
)

# Launch the Gradio app
iface.launch()
