# En domain/entities/response_entity.py
from pydantic import BaseModel


class InferenceResponse(BaseModel):
    response: str
    time: float
