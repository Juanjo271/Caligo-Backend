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


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = True


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    created_at: int


class POICreate(BaseModel):
    nombre: str
    categoria: str = ""
    tags: str = "[]"
    lat: float
    lon: float
    radio_metros: int = 50
    descripcion: str = ""
    historia: str = ""
    es_legendario: bool = False
    generate_audio: bool = True


class POIUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    tags: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    radio_metros: Optional[int] = None
    descripcion: Optional[str] = None
    historia: Optional[str] = None
    es_legendario: Optional[bool] = None
    imagen_referencia: Optional[str] = None
    audio_narracion: Optional[str] = None
