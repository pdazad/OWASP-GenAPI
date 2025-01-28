from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def truncate_context_with_tfidf(context, query, max_tokens=512):
    """
    Trunca el contexto priorizando secciones más relevantes con TF-IDF.
    """
    if not context.strip():
        print("Contexto vacío proporcionado a TF-IDF.")
        return ""

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

def ensure_context(context, query, processed_data, max_tokens=512):
    """
    Garantiza que el contexto no esté vacío después del truncamiento.
    """
    if not context.strip():
        print("Contexto vacío, utilizando contenido predeterminado.")
        fallback_context = "\n".join(
            [entry["content"] for entry in processed_data[:3]]
        )
        return truncate_context_with_tfidf(fallback_context, query, max_tokens=max_tokens)
    return context
