import gradio as gr
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableSequence
from langchain.prompts import load_prompt
from docx import Document

# Function to read the content of the uploaded file
def read_uploaded_file(file):
    if file.name.endswith('.docx'):
        doc = Document(file)  # Pass the file object directly
        return ' '.join([paragraph.text for paragraph in doc.paragraphs])
    else:
        return file.read().decode("utf-8")  # For text files, read the content directly

# Load prompts from files
prompt_template_WRITER = load_prompt("Prompts/Writer.yaml")
prompt_template_TREATMENT = load_prompt("Prompts/Treatment.yaml")
prompt_template_REVISOR = load_prompt("Prompts/Revisor.yaml")
prompt_template_FINAL = load_prompt("Prompts/Final.yaml")

# Main processing function
def process_document(file, google_api_key):
    if not file or not google_api_key:
        return "Please upload a file and enter your Google API Key."

    file_content = read_uploaded_file(file)

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

    return report_final.content

# Gradio interface
def gradio_interface():
    with gr.Blocks() as app:
        gr.Markdown("# Document Processing App")
        
        with gr.Row():
            file_input = gr.File(label="Upload Document (txt, docx)")
            api_key_input = gr.Textbox(label="Enter your Google API Key", type="password")
        
        process_button = gr.Button("Process Document")
        output = gr.Markdown(label="Final Report")

        process_button.click(
            fn=process_document,
            inputs=[file_input, api_key_input],
            outputs=output
        )

    return app

# Launch the Gradio app
if __name__ == "__main__":
    app = gradio_interface()
    app.launch()
