from pydantic import BaseModel
from typing import Optional, List


class POIBase(BaseModel):
    id: int
    nombre: str
    categoria: str
    tags: List[str]
    lat: float
    lon: float
    radio_metros: int
    descripcion: str
    historia: str
    imagen_referencia: str
    audio_narracion: str
    es_legendario: bool


class POIListItem(BaseModel):
    id: int
    nombre: str
    categoria: str
    tags: List[str]
    lat: float
    lon: float
    radio_metros: int
    es_legendario: bool


class VerifyRequest(BaseModel):
    pass


class VerifyResponse(BaseModel):
    match: bool
    score: float
    poi_id: int
    poi_nombre: str
    mensaje: str


class RutaRequest(BaseModel):
    perfil: str
    lat: float
    lon: float


class RutaResponse(BaseModel):
    pois: List[POIListItem]
    ruta_personalizada: List[int]


class CheckinRequest(BaseModel):
    poi_id: int
    bypassed: bool = False


class CheckinResponse(BaseModel):
    success: bool
    mensaje: str
    poi: Optional[POIBase] = None


class ConfigResponse(BaseModel):
    modo_evento: str
    evento_activo: bool
    informacion: str