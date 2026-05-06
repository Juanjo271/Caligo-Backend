from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

from app.core.security import decode_access_token
from app.services.poi_service import get_poi, list_pois, count_pois, get_stats, get_categories, get_all_tags
from app.services.auth_service import authenticate_user

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))

router = APIRouter(prefix="/admin", tags=["Admin Pages"])


def get_current_admin(request: Request) -> dict:
    token = request.cookies.get("admin_access_token")
    if not token:
        return None
    payload = decode_access_token(token)
    return payload


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    admin = get_current_admin(request)
    if admin:
        return RedirectResponse(url="/admin")
    return templates.TemplateResponse(request, "admin/login.html", {"request": request})


@router.get("/logout")
async def logout_page():
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("admin_access_token")
    return response


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    admin = get_current_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login")

    stats = get_stats()
    return templates.TemplateResponse(request, "admin/dashboard.html", {
        "request": request,
        "admin": admin,
        "stats": stats,
    })


@router.get("/pois", response_class=HTMLResponse)
async def poi_list_page(
    request: Request,
    search: str = "",
    category: str = "",
    tag: str = "",
    page: int = 1,
):
    admin = get_current_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login")

    limit = 20
    offset = (page - 1) * limit
    pois = list_pois(search=search, category=category, tag=tag, limit=limit, offset=offset)
    total = count_pois(search=search, category=category, tag=tag)
    pages = (total + limit - 1) // limit
    categories = get_categories()
    tags = get_all_tags()

    return templates.TemplateResponse(request, "admin/poi_list.html", {
        "request": request,
        "admin": admin,
        "pois": pois,
        "total": total,
        "page": page,
        "pages": pages,
        "search": search,
        "category": category,
        "tag": tag,
        "categories": categories,
        "tags": tags,
    })


@router.get("/pois/new", response_class=HTMLResponse)
async def poi_new_page(request: Request):
    admin = get_current_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login")

    categories = get_categories()
    tags = get_all_tags()
    return templates.TemplateResponse(request, "admin/poi_form.html", {
        "request": request,
        "admin": admin,
        "poi": None,
        "categories": categories,
        "tags": tags,
        "mapbox_token": os.environ.get("MAPBOX_PUBLIC_TOKEN", ""),
    })


@router.get("/pois/{poi_id}/edit", response_class=HTMLResponse)
async def poi_edit_page(request: Request, poi_id: int):
    admin = get_current_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login")

    poi = get_poi(poi_id)
    if not poi:
        return RedirectResponse(url="/admin/pois")

    try:
        import json
        poi["tags_list"] = json.loads(poi.get("tags", "[]"))
    except:
        poi["tags_list"] = []

    categories = get_categories()
    tags = get_all_tags()
    return templates.TemplateResponse(request, "admin/poi_form.html", {
        "request": request,
        "admin": admin,
        "poi": poi,
        "categories": categories,
        "tags": tags,
        "mapbox_token": os.environ.get("MAPBOX_PUBLIC_TOKEN", ""),
    })


@router.get("/pois/{poi_id}", response_class=HTMLResponse)
async def poi_detail_page(request: Request, poi_id: int):
    admin = get_current_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login")

    poi = get_poi(poi_id)
    if not poi:
        return RedirectResponse(url="/admin/pois")

    return templates.TemplateResponse(request, "admin/poi_detail.html", {
        "request": request,
        "admin": admin,
        "poi": poi,
    })
