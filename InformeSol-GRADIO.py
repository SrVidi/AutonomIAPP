import gradio as gr
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableSequence
from docx import Document

# Function to read the content of the uploaded file
def read_uploaded_file(file):
    if file.name.endswith('.docx'):
        doc = Document(file)  # Pass the file object directly
        return ' '.join([paragraph.text for paragraph in doc.paragraphs])
    else:
        return file.read().decode("utf-8")  # For text files, read the content directly

# Define the prompts
prompt_template_1 = PromptTemplate(
    input_variables=["DOCUMENTOS_CLINICOS"],
    template="Eres un experto en extraer con precisión los datos clínicos relevantes de los documentos de curso clínico proporcionados y sintetizarlos en un informe de alta coherente y completo.\n\nTu propósito es optimizar el proceso de alta hospitalaria, garantizando que toda la información crucial se transmita de manera clara y estructurada.\n\nTu tarea es examinar cuidadosamente la información proporcionada, extraer los datos relevantes y sintetizarlos en un informe estructurado. Sigue estas instrucciones detalladas:\n\n1. Lee atentamente los siguientes documentos de curso clínico:\n\n<documentos_clinicos>\n{DOCUMENTOS_CLINICOS}\n</documentos_clinicos>\n\n1. Analiza minuciosamente toda la información proporcionada, identificando los datos cruciales sobre el paciente y su estancia hospitalaria.\n2. Extrae la información relevante, incluyendo pero no limitándose a:\n- Datos demográficos del paciente\n- Diagnósticos (principal, secundarios, adicionales y complicaciones)\n- Tratamientos y procedimientos realizados\n- Evolución clínica\n- Resultados de pruebas y exámenes\n3. Organiza la información extraída de manera lógica y coherente, asegurándote de que todos los datos importantes estén incluidos y estructurados adecuadamente.\n4. Redacta el informe de alta hospitalaria siguiendo estrictamente la siguiente estructura:\n<informe_alta>\n# Informe médico de alta hospitalaria\n\n---\n### Paciente que consulta por: [Motivo de la consulta inicial]\n### Fecha de ingreso\n[Indicar fecha de ingresso formato DD/MM/YYYY]\n### Fecha de alta\n[Indicar fecha de alta formato DD/MM/YYYY]\n\n---\n\n## Historial médico\n[Un resumen de los antecedentes personales, destacando aquellos datos que por su significación positiva o negativa ayuden a hacer más comprensible el proceso nosológico. Solo considerar historial hasta la fecha de ingreso]\n\n**Antecedentes familiares:** [Resumen de los antecedentes familiares relevantes]\n\n**Alergias:** [Listado de alergias si existen]\n\n**Hábitos tóxicos:** [Listado de Hábitos tóxicos manifestados si existen]\n\n**Estado basal:** [Resumen del estado basal del paciente]\n\n---\n\n## Medicación habitual\n[Listado detallado de la medicación habitual tomada por el paciente. Cada elemento de la lista debe seguir el siguiente patrón <Medicamento>, <Posología> : <Pautadelamedicación>]\n\n---\n\n## Antecedentes patológicos\n[Listado de las patologías pre existentes a la fecha de ingreso. Cada elemento de la lista debe seguir el siguiente patrón <Patología>: <Descripción>]\n\n---\n\n## Enfermedad actual\n[Resumen del motivo de la consulta, incluyendo síntomas iniciales, pruebas de laboratorio y estudios de imagen, elementos contextuales que puedar mejorar el entendimiento de la situación del paciente, etc. practicados en su consulta inicial y motivo de hospitalización.]\n\n---\n\n## Exploración física\n[Listado de resultados de exploración física a la llegada al hospital (Urgencias) y/o de la llegada a planta. Detalla todos los elementos, incluyendo peso, talla y otras medidas corporales si aparecen el documento clínico.]\n\n---\n\n## Exploraciones complementarias\n[Lista de pruebas de laboratorio, estudios de imagen, tratamientos, medicamentos, intervenciones quirúrgicas y cualquier otra terapia aplicada durante la estancia hospitalaria. Describe con detalle cada uno de los elementos de la lista. Orden cronológico ascendente. Cada elemento de la lista debe seguir el siguiente patrón <Fecha>: <Prueba>, <Descripción> ]\n\n---\n\n## Evolución y tratamiento realizado\n[Valoración muy detallada de la evolución durante su estancia en el centro. Citando hitos importantes y tratamientos clave. Recuerda ser muy cuidadoso con los detalles.]\n\n---\n\n## Procedimientos invasivos\n[lista de procedimientos invasivos que no hayan sido recogidos en el apartado de exploraciones complementarias. Cada elemento de la lista debe seguir el siguiente patrón <Fecha>: <Prueba>, <Descripción> ]]\n\n---\n\n## Diagnósticos\n### Diagnóstico principal:\n[Listado del proceso patológico o afección que tras el estudio pertinente y según criterio facultativo, se considera la causa principal o motivo del ingreso o contacto de la persona en el hospital.]\n### Diagnóstico/s secundario/s:\n[Listado de patologías que coexisten con la considerada diagnóstico principal en el momento del ingreso o se desarrolla durante la estancia hospitalaria e influye en su duración o en los cuidados administrados.]\n### Diagnóstico/s adicional/s:\n### Diagnóstico/s de complicaciones:\n\n---\n\n## Informaciones extras:\n[Listado informaciones extraida del <documentos_clinicos> que consideres relevante para entender el caso pero que no encaja en ninguna de las secciones anteriores. Solo informaciones muy relevante y no repetida en otros apartados.]\n</informe_alta>\n\n<importante>\n1. Asegúrate de que el informe sea preciso, completo y utilice terminología médica apropiada. Mantén un equilibrio entre el rigor técnico, la claridad y la empatia.\n2. Si encuentras información incompleta o ambigua en los documentos originales, indícalo claramente en el informe para su posterior revisión.\n3. Adapta el nivel de detalle y el enfoque del informe según las necesidades específicas del caso y las prácticas estándar en medicina.\n4. Revisa cuidadosamente el informe final para garantizar que toda la información crucial esté incluida y que siga la estructura especificada.\n5. Si tienes dudas o necesitas aclaraciones sobre algún aspecto de los documentos clínicos, indícalo claramente antes de proceder con el informe.\n6. No incluir nombres del paciente o doctores.\n\nRecuerda, tu objetivo es crear un informe de alta hospitalaria completo, preciso y útil para la continuidad de la atención médica del paciente. Sé meticuloso en tu análisis y síntesis de la información.\n</importante>"
)

prompt_template_2 = PromptTemplate(
    input_variables=["DOCUMENTOS_CLINICOS", "INFORME_ORIGINAL"],
    template="Eres un experto revisor de documentos clínicos.\n\nTu tarea consiste en revisar y verificar que la información proporcionada en <documentos_clinicos> se ha transcrito de forma fiel y sin errores al <informe_alta>.\n\nPara sobresalir en su objetivo, siga estos pasos:\n1. Lee atentamente los siguientes documentos de curso clínico y de informe de alta:\n<documentos_clinicos>{DOCUMENTOS_CLINICOS}</documentos_clinicos>\n\n<informe_alta>{INFORME_ORIGINAL}</informe_alta>\n\n2. Revisa la información del <informe_alta>, comparándola punto por punto con los <documentos_clinicos>.\n3. Verifica que toda la información extraída esté presente en el <documentos_clinicos> y representada con precisión.\n4. Identifique cualquier información en <documentos_clinicos> que se pueda haber pasado por alto o malinterpretado.\n5. Cree una lista completa de las discrepancias, omisiones o inexactitudes encontradas durante su revisión.\n6. Proporcione correcciones y adiciones cuando sea necesario, citando siempre la ubicación específica en el documento original.\n7. Resuma sus hallazgos, destacando tanto las fortalezas de la extracción inicial como las áreas de mejora.\n\nObservaciones para completar la tarea con éxito:\n* Mantenga una postura objetiva e imparcial durante todo el proceso de revisión.\n* Preste mucha atención a la terminología médica, las dosis, las fechas y los valores numéricos, ya que estos son propensos a errores de transcripción.\n* Considere el contexto y la relevancia de la información al determinar si una omisión es significativa.\n* Sea minucioso en su examen, ya que incluso los pequeños detalles pueden tener implicaciones significativas en el ámbito clínico.\n* Si encuentra alguna ambigüedad en el documento original, anótela y sugiera una aclaración si es posible.\n* Recuerde que su papel es crucial para garantizar la integridad y la fiabilidad de la información clínica extraída, que puede utilizarse para la atención al paciente o con fines de investigación."
)

prompt_template_3 = PromptTemplate(
    input_variables=["INFORME_ORIGINAL", "CORRECCIONES"],
    template="Eres un asistente experto en informes clínicos.\n\nSe te proporcionará un informe de alta clínica generado por otro asistente, junto con un documento de correcciones sugeridas por un tercer asistente.\n\nTu tarea es generar un informe de alta final incorporando las correcciones indicadas.\n\nInforme de alta original:\n<informe>{INFORME_ORIGINAL}</informe>\n\nDocumento de correcciones:\n<correcciones>{CORRECCIONES}</correcciones>\n\nInstrucciones:\n\n* Lee detenidamente el informe de alta original <informe> y el documento de correcciones <correcciones>.\n* Identifica cada una de las correcciones sugeridas en el documento de correcciones.\n* Edita el informe de alta original aplicando todas las correcciones de manera precisa. Esto puede implicar añadir, eliminar o modificar texto según se indique, pero siempre manteniendo la estructura original del informe de alta <informe>.\n* Asegúrate de mantener la estructura, formato y estilo del informe original.\n* Verifica que el informe final tenga sentido, sea coherente y no contenga errores o inconsistencias tras aplicar las correcciones.\n* Genera el informe de alta final con todas las correcciones incorporadas."
)

# Main processing function
def process_document(file, google_api_key):
    if not file or not google_api_key:
        return "Please upload a file and enter your Google API Key."
    
    file_content = read_uploaded_file(file)

    # Initialize language models
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=google_api_key)
    llm2 = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_api_key)

    # Create chains
    chain_1 = RunnableSequence(prompt_template_1, llm)
    chain_2 = RunnableSequence(prompt_template_2, llm2)
    chain_3 = RunnableSequence(prompt_template_3, llm2)

    # Generate reports
    report_original = chain_1.invoke({"DOCUMENTOS_CLINICOS": file_content})
    corrections = chain_2.invoke({"DOCUMENTOS_CLINICOS": file_content, "INFORME_ORIGINAL": report_original})
    report_final = chain_3.invoke({"INFORME_ORIGINAL": report_original, "CORRECCIONES": corrections})

    return report_final.content

# Gradio interface
def gradio_interface():
    with gr.Blocks() as app:
        gr.Markdown("# Document Processing App")
        
        with gr.Row():
            file_input = gr.File(label="Upload Document (txt, docx, pdf)")
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
    app.launch(share=True)
