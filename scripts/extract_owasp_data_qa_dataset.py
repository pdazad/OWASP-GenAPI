import os
import re
import json
from markdown import markdown

def extract_data_from_md(md_file):
    """
    Convierte el contenido Markdown a HTML para facilitar el procesamiento.
    """
    with open(md_file, "r", encoding="utf-8") as file:
        content = file.read()
    return markdown(content)

def preprocess_text(text):
    """
    Limpia texto eliminando enlaces, etiquetas HTML y caracteres innecesarios.
    """
    text = re.sub(r"\[.*?\]\(.*?\)", "", text)  # Eliminar enlaces
    text = re.sub(r"<.*?>", "", text)          # Eliminar etiquetas HTML
    text = re.sub(r"\s+", " ", text)           # Reducir espacios múltiples
    return text.strip()

def extend_to_complete_sentence(text, limit=512):
    """
    Extiende el texto al próximo punto para completar la oración si el límite corta una palabra.
    """
    if len(text) <= limit:
        return text
    extended_text = text[:limit]
    last_period = extended_text.rfind(".")
    if last_period != -1:
        return text[:last_period + 1].strip()
    return text[:limit].strip()

def extract_sections(html_content):
    """
    Extrae secciones clave como Descripción, Cómo se previene, y Ejemplos.
    """
    sections = {"description": "", "prevention": "", "examples": ""}
    section_titles = {
        "Descripción": "description",
        "Cómo se previene": "prevention",
        "Ejemplos de escenarios de ataque": "examples"
    }

    split_content = re.split(r"<h2.*?>", html_content)
    for section in split_content:
        for title, key in section_titles.items():
            if title.lower() in section.lower():
                sections[key] = preprocess_text(section)
    return sections

def find_relevant_answer(context, category):
    """
    Encuentra una respuesta relevante en el contexto basada en la categoría.
    Elimina títulos como 'Descripción' o 'Cómo se previene' de la respuesta.
    """
    context = re.sub(r"^(Descripción|Cómo se previene|Ejemplos de escenarios de ataque):?", "", context, flags=re.IGNORECASE).strip()
    answer_start = context.lower().find(category.lower())
    if answer_start != -1:
        end = context.find(".", answer_start)
        if end == -1:
            end = len(context)
        return {
            "text": context[answer_start:end].strip(),
            "start": answer_start
        }
    first_sentence = context.split(".")[0]
    return {
        "text": first_sentence.strip(),
        "start": context.find(first_sentence)
    }

def generate_questions(category, sections, language):
    """
    Genera preguntas diversificadas para cada categoría y sección.
    """
    # Eliminar prefijos y sufijos no deseados
    category = re.sub(r"A\\d{2} 2021 ", "", category)  # Eliminar prefijo "A## 2021"
    category = re.sub(r"\\.es$", "", category)  # Eliminar sufijo .es


    category = re.sub(r"Broken Access Control", "el Control de Acceso Roto", category, flags=re.IGNORECASE)
    category = re.sub(r"Cryptographic Failures", "Fallos Criptográficos", category, flags=re.IGNORECASE)
    category = re.sub(r"Injection", "Inyección", category, flags=re.IGNORECASE)
    category = re.sub(r"Insecure Design", " el Diseño Inseguro", category, flags=re.IGNORECASE)
    category = re.sub(r"Security Misconfiguration", "la Mala Configuración de Seguridad", category, flags=re.IGNORECASE)

    if language == "es":
        questions = [
            f"¿Qué es {category}?",
            f"¿Cómo prevenir {category}?",
            f"¿Qué impacto tiene {category} en la seguridad?",
            f"Dame un ejemplo de {category}.",
            f"¿Qué causas tiene {category}?"
        ]
    else:
        questions = [
            f"What is {category}?",
            f"How to prevent {category}?",
            f"What is the impact of {category} on security?",
            f"Give me an example of {category}.",
            f"What causes {category}?"
        ]

    # Asociar preguntas con contextos adecuados
    qa_pairs = []
    for question in questions:
        if "prevenir" in question or "prevent" in question:
            context = sections.get("prevention", "")
        elif "ejemplo" in question or "example" in question:
            context = sections.get("examples", "")
        else:
            context = sections.get("description", "")
        if context:
            context = extend_to_complete_sentence(context, 512) 
            answer = find_relevant_answer(context, category)
            qa_pairs.append({
                "question": question,
                "context": context,
                "answers": [answer]
            })
    return qa_pairs


def is_valid_file(file_name, language):
    """
    Verifica si un archivo cumple con los criterios de idioma y formato.
    """
    excluded_extensions = (".ar.md", ".fr.md", ".id.md", ".it.md", ".ja.md", "pt_BR.md", "zh_CN.md", "zh_TW.md")
    if file_name.endswith(excluded_extensions):
        return False
    if language == "es" and file_name.endswith(".es.md"):
        return True
    if language == "en" and file_name.endswith(".md") and not file_name.endswith(".es.md"):
        return True
    return False

def build_dataset(md_folder, language):
    """
    Construye un dataset QA a partir de archivos Markdown relevantes.
    """
    dataset = []
    for md_file in os.listdir(md_folder):
        if is_valid_file(md_file, language):
            print(f"Procesando archivo: {md_file}")
            html_content = extract_data_from_md(os.path.join(md_folder, md_file))
            sections = extract_sections(html_content)

            # Extraer y limpiar la categoría
            category = os.path.splitext(md_file)[0]  # Nombre del archivo sin extensión
            category = re.sub(r"[-_]", " ", category)  # Reemplazar guiones y subrayados por espacios
            category = re.sub(r"\\.es$", "", category)  # Eliminar el sufijo .es

            qa_pairs = generate_questions(category, sections, language)
            dataset.extend(qa_pairs)
    return dataset


def clean_and_refine_dataset(dataset):
    """
    Limpia y mejora el dataset eliminando redundancias y alineando preguntas, respuestas y contextos.
    """
    refined_dataset = []
    for entry in dataset:
        # Limpiar la pregunta
        question = re.sub(r"A\d{2} 2021 ", "", entry["question"])  # Eliminar prefijo A## 2021
        question = re.sub(r"\.es$", "", question).strip()  # Eliminar sufijo .es
        
        # Añadir la entrada refinada al dataset
        refined_dataset.append({
            "question": question,
            "context": entry["context"],
            "answers": entry["answers"]
        })
    return refined_dataset

# Configuración inicial
md_folder = "../data/OWASP/2021/docs"  
language = "es"

# Generar dataset inicial
raw_dataset = build_dataset(md_folder, language)

# Limpiar y refinar dataset
final_dataset = clean_and_refine_dataset(raw_dataset)

import os

output_folder = "../data"
os.makedirs(output_folder, exist_ok=True)

# Guardar el archivo en la carpeta 'data'
output_file = os.path.join(output_folder, "owasp_qa_dataset_es.json")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(final_dataset, f, indent=4, ensure_ascii=False)

print(f"Dataset refinado guardado en {output_file}")

