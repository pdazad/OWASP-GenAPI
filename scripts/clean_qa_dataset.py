import json

def clean_qa_dataset(data):
    """
    Limpia y filtra el dataset de QA para asegurar que las preguntas, contextos y respuestas sean válidos.

    Parameters:
        data (list): Lista de ejemplos en formato QA.

    Returns:
        list: Lista de ejemplos limpios y válidos.
    """
    cleaned_data = []

    for entry in data:
        question = entry["question"]
        context = entry["context"]
        answers = entry["answers"]

        # Filtrar categorías irrelevantes como "Next Steps"
        if "Next Steps" in question or "Next Steps" in context:
            continue

        # Limpiar contextos que contienen tablas o datos inútiles
        if "|" in context:
            continue

        # Validar respuestas
        valid_answers = [
            ans for ans in answers if "text" in ans and "start" in ans and ans["text"]
        ]
        if not valid_answers:
            continue

        # Validar que las posiciones de inicio estén alineadas con el contexto
        for ans in valid_answers:
            start = ans["start"]
            if start < 0 or start >= len(context):
                continue
            end = start + len(ans["text"])
            if context[start:end] != ans["text"]:
                continue

        # Agregar entrada limpia
        cleaned_data.append({
            "question": question.strip(),
            "context": context.strip(),
            "answers": valid_answers
        })

    print(f"Ejemplos válidos tras limpieza: {len(cleaned_data)}")
    return cleaned_data

# Ajuste en la preparación del dataset de QA
qa_data_file = "../data/owasp_qa_dataset_es.json"
with open(qa_data_file, "r", encoding="utf-8") as f:
    qa_data = json.load(f)

# Limpiar el dataset
qa_data_cleaned = clean_qa_dataset(qa_data)

# Guardar el dataset limpio
qa_cleaned_file = "owasp_qa_dataset_es_cleaned.json"
with open(qa_cleaned_file, "w", encoding="utf-8") as f:
    json.dump(qa_data_cleaned, f, indent=4, ensure_ascii=False)

print(f"Dataset limpio guardado en {qa_cleaned_file}")
