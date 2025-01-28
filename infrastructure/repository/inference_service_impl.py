import os
import faiss
import json
from transformers import AutoTokenizer, AutoModelForCausalLM

from domain.entities.response_entity import InferenceResponse
from domain.interfaces.inference_service_interface import InferenceServiceInterface
from config.settings import (
    MODEL_PATH, INDEX_PATH, PROCESSED_DATA_PATH,
    EMBEDDING_MODEL_NAME, TOP_K
)
from infrastructure.helpers.faiss_helper import search_with_faiss
from infrastructure.helpers.context_utils import ensure_context
from infrastructure.helpers.response_formatter import generate_response


class InferenceServiceImpl(InferenceServiceInterface):
    """
    Implementación concreta del servicio de inferencia
    que combina FAISS + modelo Fine-Tuned Bloom + helpers de truncado.
    """

    # Variables estáticas o de clase para que se carguen 1 sola vez
    _faiss_index = None
    _processed_data = None

    def __init__(self):
        # Aseguramos que se inicialicen (lazy loading)
        if self._faiss_index is None:
            self._faiss_index = self._load_faiss_index(INDEX_PATH)
        if self._processed_data is None:
            self._processed_data = self._load_processed_data(PROCESSED_DATA_PATH)

    def inference(self, query: str) -> InferenceResponse:
        """
        Implementa todo el flujo:
        1) FAISS search,
        2) ensure_context,
        3) generar respuesta.
        """
        try:
            search_results = search_with_faiss(
                query,
                self._faiss_index,
                self._processed_data,
                EMBEDDING_MODEL_NAME,
                TOP_K
            )
            full_context = "\n".join([result["content"] for result in search_results])
            full_context = ensure_context(full_context, query, self._processed_data)

            response, inference_time = generate_response(query, full_context, MODEL_PATH)

            return {
                "response": response,
                "time": inference_time
            }
        except Exception as e:
            print(f"Error durante la inferencia: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def _load_faiss_index(index_path: str):
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Índice FAISS no encontrado en {index_path}")
        print(f"Cargando índice FAISS desde {index_path}...")
        return faiss.read_index(index_path)

    @staticmethod
    def _load_processed_data(processed_data_path: str):
        if not os.path.exists(processed_data_path):
            raise FileNotFoundError(f"Datos procesados no encontrados en {processed_data_path}")
        print(f"Cargando datos procesados desde {processed_data_path}...")
        with open(processed_data_path, "r", encoding="utf-8") as f:
            return json.load(f)
