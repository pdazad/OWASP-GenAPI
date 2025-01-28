from domain.entities.response_entity import InferenceResponse
from domain.interfaces.inference_service_interface import InferenceServiceInterface


class HandleInferenceUseCase:
    def __init__(self, inference_service: InferenceServiceInterface):
        self.inference_service = inference_service

    def execute(self, query: str) -> InferenceResponse:
        """
        Invoca la lógica de inferencia y retorna un dict con la respuesta.
        """
        return self.inference_service.inference(query)
