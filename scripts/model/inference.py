import json
import time
import faiss
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import evaluate

# Configuración global
MODEL_PATH = "pdazad/fine_tuned_bloom_owasp"
INDEX_FILE = "./indice_faiss.index"
DATA_FILE = "./owasp_cleaned_dataset.json"
EMBEDDING_MODEL_NAME = "all-MiniLM-L12-v2"

# Cargar métricas
rouge_metric = evaluate.load("rouge")

# Funciones auxiliares

def load_json(file_path):
    """Carga un archivo JSON."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_faiss_index(index_path):
    """Carga un índice FAISS."""
    return faiss.read_index(index_path)


def generate_embeddings(query, embedding_model_name):
    """Genera embeddings para una consulta."""
    model = SentenceTransformer(embedding_model_name)
    return model.encode([query], convert_to_numpy=True)


def search_with_faiss(query, index, data, top_k=3):
    """
    Recupera documentos relevantes usando FAISS.

    Args:
        query (str): Consulta en lenguaje natural.
        index (faiss.Index): Índice FAISS.
        data (list): Datos procesados.
        top_k (int): Número de documentos a recuperar.

    Returns:
        list: Resultados de búsqueda relevantes.
    """
    query_embedding = generate_embeddings(query, EMBEDDING_MODEL_NAME)
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i in range(len(indices[0])):
        idx = indices[0][i]
        results.append({
            "content": data[idx]["content"],
            "category": data[idx]["category"],
            "distance": distances[0][i],
        })
    return results


def ensure_context(context, query, data, max_tokens=512):
    """Garantiza que el contexto no esté vacío y lo optimiza usando TF-IDF."""
    if not context.strip():
        print("Contexto vacío. Usando contexto predeterminado.")
        fallback_context = "\n".join([entry["content"] for entry in data[:3]])
        return truncate_context_with_tfidf(fallback_context, query, max_tokens)
    return context


def truncate_context_with_tfidf(context, query, max_tokens=512):
    """Optimiza el contexto usando TF-IDF."""
    sections = context.split("\n")
    corpus = [query] + sections
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    query_vector = tfidf_matrix[0]
    section_vectors = tfidf_matrix[1:]
    similarities = section_vectors.dot(query_vector.T).toarray().flatten()

    sorted_indices = np.argsort(similarities)[::-1]
    sorted_sections = [sections[i] for i in sorted_indices]

    truncated_context = []
    token_count = 0
    for section in sorted_sections:
        tokens = section.split()
        if token_count + len(tokens) <= max_tokens:
            truncated_context.append(section)
            token_count += len(tokens)
        else:
            break
    return "\n".join(truncated_context)


def generate_response(query, context, tokenizer, model):
    """Genera una respuesta usando el modelo fine-tuned."""
    pipeline_gen = pipeline("text-generation", model=model, tokenizer=tokenizer)
    prompt = (
        f"Pregunta: {query}\n"
        f"Contexto: {context}\n\n"
        f"Respuesta:"
    )
    start_time = time.time()
    result = pipeline_gen(prompt, max_new_tokens=150, temperature=0.4)
    end_time = time.time()

    response = result[0]["generated_text"]
    response = response.split("Respuesta:")[-1].strip()
    response_time = end_time - start_time
    return response, response_time


def evaluate_responses(predictions, references):
    """Evalúa las respuestas generadas usando Rouge-L."""
    result = rouge_metric.compute(predictions=predictions, references=references)
    rouge_l_f1 = result["rougeL"].mid.fmeasure
    return rouge_l_f1


# Pruebas de inferencia


def run_inference_tests(index, data, model_path):
    """Ejecuta pruebas de inferencia con diferentes tipos de preguntas."""
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)

    # Preguntas de prueba
    test_cases = [
        {"query": "¿Qué es el control de acceso roto?", "expected": "Control de acceso..."},
        {"query": "¿Cómo prevenir fallos criptográficos?", "expected": "Para prevenir fallos..."},
        {"query": "¿Qué impacto tiene la inyección SQL?", "expected": "La inyección SQL puede..."},
    ]

    predictions = []
    references = []

    for case in test_cases:
        query = case["query"]
        expected = case["expected"]

        # Recuperar contexto
        search_results = search_with_faiss(query, index, data, top_k=3)
        context = "\n".join([result["content"] for result in search_results])
        context = ensure_context(context, query, data)

        # Generar respuesta
        response, response_time = generate_response(query, context, tokenizer, model)

        # Guardar resultados
        predictions.append(response)
        references.append(expected)

        # Mostrar resultados
        print("\n--- Prueba de Inferencia ---")
        print(f"Pregunta: {query}")
        print(f"Contexto:\n{context}")
        print(f"Respuesta Generada:\n{response}")
        print(f"Respuesta Esperada:\n{expected}")
        print(f"Tiempo de Inferencia: {response_time:.2f}s")

    # Evaluar métricas
    rouge_l_score = evaluate_responses(predictions, references)
    print(f"\nMétrica Rouge-L: {rouge_l_score:.4f}")


# Ejecución principal


if __name__ == "__main__":
    # Cargar datos y modelo
    data = load_json(DATA_FILE)
    index = load_faiss_index(INDEX_FILE)

    # Ejecutar pruebas
    run_inference_tests(index, data, MODEL_PATH)
