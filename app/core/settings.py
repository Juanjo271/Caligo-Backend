from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    app_title: str = "CaliGuía API"
    app_description: str = "Backend para CaliGuía Go - Asistente Turístico Inteligente de Cali"
    app_version: str = "1.0.0"

    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    database_path: str = "data/caliguia.db"
    static_dir: str = "app/static"
    ref_images_dir: str = "app/static/ref_images"
    narrations_dir: str = "app/static/narrations"

    seed_pois_file: str = "app/core/config/seed_pois.json"
    profiles_file: str = "app/core/config/profiles.json"
    events_file: str = "app/core/config/events.json"

    orb_nfeatures: int = 500
    orb_min_good_matches: int = 10
    orb_match_normalization_divisor: int = 50
    orb_match_threshold: float = 0.50
    orb_query_resize_width: int = 640
    orb_query_resize_height: int = 480
    orb_ref_resize_width: int = 640
    orb_ref_resize_height: int = 480

    tag_match_weight: float = 0.6
    distance_score_weight: float = 0.4
    max_scoring_distance: float = 5000.0

    default_route_poi_count: int = 4
    min_route_poi_count: int = 1
    max_route_poi_count: int = 10

    default_poi_radius: int = 50

    class Config:
        env_prefix = "CALIGUIA_"
        case_sensitive = False


settings = Settings()
