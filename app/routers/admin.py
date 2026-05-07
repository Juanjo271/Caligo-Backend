from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from typing import Optional
import json

from app.core.security import decode_access_token
from app.core.limiter import limiter
from app.core.settings import settings
from app.models import POICreate, POIUpdate
from app.services.poi_service import (
    create_poi, update_poi, delete_poi, get_poi, list_pois, count_pois,
    get_stats, get_categories, get_all_tags, update_poi_image
)
from app.services.image_service import save_image, delete_image
from app.services.auth_service import authenticate_user

router = APIRouter(prefix="/api/admin", tags=["Admin API"])


def get_current_admin(request: Request) -> dict:
    token = request.cookies.get("admin_access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return payload


@router.post("/login")
@limiter.limit(settings.rate_limit_login)
async def admin_login(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    user = authenticate_user(username, password)
    if not user:
        return JSONResponse({"success": False, "error": "Usuario o contraseña incorrectos"}, status_code=401)

    from app.core.security import create_access_token
    token = create_access_token({"sub": user["username"], "user_id": user["id"]})

    response = JSONResponse({"success": True, "message": "Login exitoso"})
    response.set_cookie(
        key="admin_access_token",
        value=token,
        httponly=True,
        max_age=7 * 24 * 3600,
        samesite="lax",
    )
    return response


@router.post("/logout")
async def admin_logout():
    response = JSONResponse({"success": True, "message": "Logout exitoso"})
    response.delete_cookie("admin_access_token")
    return response


@router.get("/stats")
async def admin_stats(admin: dict = Depends(get_current_admin)):
    return get_stats()


@router.get("/pois")
async def admin_pois(
    search: str = "",
    category: str = "",
    tag: str = "",
    page: int = 1,
    limit: int = 20,
    admin: dict = Depends(get_current_admin),
):
    offset = (page - 1) * limit
    pois = list_pois(search=search, category=category, tag=tag, limit=limit, offset=offset)
    total = count_pois(search=search, category=category, tag=tag)
    return {
        "pois": pois,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/pois/{poi_id}")
async def admin_poi_detail(poi_id: int, admin: dict = Depends(get_current_admin)):
    poi = get_poi(poi_id)
    if not poi:
        raise HTTPException(status_code=404, detail="POI no encontrado")
    return poi


@router.post("/pois")
async def admin_create_poi(
    request: Request,
    admin: dict = Depends(get_current_admin),
):
    form = await request.form()

    tags_list = []
    tags_raw = form.get("tags", "")
    if tags_raw:
        tags_list = [t.strip() for t in tags_raw.split(",") if t.strip()]

    poi_data = POICreate(
        nombre=form.get("nombre", ""),
        categoria=form.get("categoria", ""),
        tags=json.dumps(tags_list),
        lat=float(form.get("lat", 0)),
        lon=float(form.get("lon", 0)),
        radio_metros=int(form.get("radio_metros", 50)),
        descripcion=form.get("descripcion", ""),
        historia=form.get("historia", ""),
        es_legendario=form.get("es_legendario") == "on",
        generate_audio=form.get("generate_audio") == "on",
    )

    poi_id = create_poi(poi_data)

    image_file = form.get("image")
    if image_file and hasattr(image_file, "filename") and image_file.filename:
        content = await image_file.read()
        filename = save_image(content, image_file.filename, poi_id)
        if filename:
            update_poi_image(poi_id, filename)

    return {"success": True, "poi_id": poi_id}


@router.post("/pois/{poi_id}")
async def admin_update_poi(
    poi_id: int,
    request: Request,
    admin: dict = Depends(get_current_admin),
):
    form = await request.form()

    tags_list = []
    tags_raw = form.get("tags", "")
    if tags_raw:
        tags_list = [t.strip() for t in tags_raw.split(",") if t.strip()]

    poi_data = POIUpdate()

    if form.get("nombre"):
        poi_data.nombre = form.get("nombre")
    if form.get("categoria"):
        poi_data.categoria = form.get("categoria")
    if tags_list:
        poi_data.tags = json.dumps(tags_list)
    if form.get("lat"):
        poi_data.lat = float(form.get("lat"))
    if form.get("lon"):
        poi_data.lon = float(form.get("lon"))
    if form.get("radio_metros"):
        poi_data.radio_metros = int(form.get("radio_metros"))
    if form.get("descripcion") is not None:
        poi_data.descripcion = form.get("descripcion")
    if form.get("historia") is not None:
        poi_data.historia = form.get("historia")
    if form.get("es_legendario") is not None:
        poi_data.es_legendario = form.get("es_legendario") == "on"

    success = update_poi(poi_id, poi_data)
    if not success:
        raise HTTPException(status_code=404, detail="POI no encontrado")

    image_file = form.get("image")
    if image_file and hasattr(image_file, "filename") and image_file.filename:
        content = await image_file.read()
        filename = save_image(content, image_file.filename, poi_id)
        if filename:
            update_poi_image(poi_id, filename)

    if form.get("generate_audio") == "on" and form.get("historia"):
        from app.services.tts_service import generate_audio_sync
        audio_filename = generate_audio_sync(form.get("historia"), poi_id)
        if audio_filename:
            from app.services.poi_service import update_poi_audio
            update_poi_audio(poi_id, audio_filename)

    return {"success": True}


@router.delete("/pois/{poi_id}")
async def admin_delete_poi(poi_id: int, admin: dict = Depends(get_current_admin)):
    delete_image(poi_id)
    success = delete_poi(poi_id)
    if not success:
        raise HTTPException(status_code=404, detail="POI no encontrado")
    return {"success": True}


@router.post("/pois/{poi_id}/generate-audio")
async def admin_generate_audio(poi_id: int, admin: dict = Depends(get_current_admin)):
    poi = get_poi(poi_id)
    if not poi:
        raise HTTPException(status_code=404, detail="POI no encontrado")

    if not poi.get("historia"):
        raise HTTPException(status_code=400, detail="El POI no tiene historia")

    from app.services.tts_service import generate_audio_sync
    from app.services.poi_service import update_poi_audio

    audio_filename = generate_audio_sync(poi["historia"], poi_id)
    if audio_filename:
        update_poi_audio(poi_id, audio_filename)
        return {"success": True, "audio_filename": audio_filename}
    else:
        raise HTTPException(status_code=500, detail="Error generando audio")


@router.get("/categories")
async def admin_categories(admin: dict = Depends(get_current_admin)):
    return get_categories()


@router.get("/tags")
async def admin_tags(admin: dict = Depends(get_current_admin)):
    return get_all_tags()
