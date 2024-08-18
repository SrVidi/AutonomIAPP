from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatGoogleGenerativeAI
from langchain.chains import LLMChain

# Load the file and parse the data
loader = UnstructuredFileLoader("path_to_your_file.docx")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

# Define the prompts and the language model
prompt_template_1 = PromptTemplate(
    input_variables=["DOCUMENTOS_CLINICOS"],
    template="Eres un experto revisor de documentos clínicos. Tu tarea consiste en revisar y verificar que la información proporcionada en <documentos_clinicos> se ha transcrito de forma fiel y sin errores al <informe_alta>.\n\n<documentos_clinicos>\n{DOCUMENTOS_CLINICOS}\n</documentos_clinicos>\n\n<informe_alta>\n{INFORME}\n</informe_alta>\n\n... rest of the prompt template ...",
)
prompt_template_2 = PromptTemplate(
    input_variables=["INFORME_ORIGINAL", "CORRECCIONES"],
    template="Eres un asistente experto en informes clínicos. Se te proporcionará un informe de alta clínica generado por otro asistente, junto con un documento de correcciones sugeridas por un tercer asistente. Tu tarea es generar un informe de alta final incorporando las correcciones indicadas.\n\nInforme de alta original: \n\n<informe>\n{INFORME_ORIGINAL}\n</informe>\n\nDocumento de correcciones: \n\n<correcciones>\n{CORRECCIONES}\n</correcciones>\n\n... rest of the prompt template ...",
)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key="your_google_api_key")

# Use the prompts and the language model to generate the reports
chain_1 = LLMChain(llm=llm, prompt=prompt_template_1)
report_original = chain_1.run(texts)

chain_2 = LLMChain(llm=llm, prompt=prompt_template_2)
report_final = chain_2.run({"INFORME_ORIGINAL": report_original, "CORRECCIONES": "your_corrections"})

# Output the final report
print(report_final)
