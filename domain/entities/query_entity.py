from pydantic import BaseModel


class QueryEntity(BaseModel):
    """
    Entidad del dominio que representa la consulta a procesar.
    """
    query: str
