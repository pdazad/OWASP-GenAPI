from fastapi import FastAPI, Depends

# Interfaces y servicios
from domain.interfaces.inference_service_interface import InferenceServiceInterface
from domain.entities.query_entity import QueryEntity
from domain.entities.response_entity import InferenceResponse
from infrastructure.repository.inference_service_impl import InferenceServiceImpl

# Caso de uso
from application.use_cases.handle_inference_use_case import HandleInferenceUseCase

# Instanciamos 1 sola vez
inference_service = InferenceServiceImpl()


def get_inference_service() -> InferenceServiceInterface:
    return inference_service


def get_inference_use_case(service: InferenceServiceInterface = Depends(get_inference_service)):
    return HandleInferenceUseCase(service)


app = FastAPI(title="OWASP Inference API")


# ===========
# ENDPOINTS
# ===========
@app.post("/predict", response_model=InferenceResponse)
def predict(
        request: QueryEntity,
        use_case: HandleInferenceUseCase = Depends(get_inference_use_case)
):
    """
    Llama al caso de uso para realizar una inferencia sobre el texto recibido.
    """
    # Asumiendo que tu caso de uso tiene un método .predict(), ajusta según tu lógica
    return use_case.execute(request.query)


@app.get("/health")
def health_check():
    """
    Endpoint de salud para verificar que el servicio esté corriendo.
    """
    return {"status": "OK", "message": "Inference service is up and running."}
