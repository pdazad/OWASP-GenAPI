import faiss
from sentence_transformers import SentenceTransformer


def search_with_faiss(query, index, processed_data, embedding_model_name="all-MiniLM-L12-v2", top_k=3):
    """
    Busca en el índice FAISS los documentos más relevantes para una consulta.
    """
    try:
        model = SentenceTransformer(embedding_model_name)
        query_embedding = model.encode([query], convert_to_numpy=True)

        distances, indices = index.search(query_embedding, top_k)

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            result = {
                "content": processed_data[idx].get("content", "") or processed_data[idx].get("context", ""),
                "category": processed_data[idx].get("category", "Unknown"),
                "distance": distances[0][i]
            }
            results.append(result)

        return results
    except Exception as e:
        print(f"Error en la búsqueda con FAISS: {str(e)}")
        raise
