from abc import ABC, abstractmethod

from domain.entities.response_entity import InferenceResponse


class InferenceServiceInterface(ABC):
    @abstractmethod
    def inference(self, query: str) -> InferenceResponse:
        """
        Ejecuta todo el flujo de búsqueda FAISS + generación de respuesta
        con el modelo y retorna un dict con la información generada.
        """
        pass
