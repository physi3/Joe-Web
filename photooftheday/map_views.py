"""Read-only, group-scoped map and small, on-demand image derivatives."""

import hashlib
import re
from datetime import timedelta
from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET
from django.views.decorators.vary import vary_on_cookie
from PIL import Image, ImageOps, UnidentifiedImageError

from .models import GroupMember, PhotoSubmission, WeeklyDispatch


def _membership(request):
    return get_object_or_404(GroupMember.objects.select_related("group"), user=request.user)


def _photos(member):
    # Zero is a valid coordinate. Null, out-of-range and missing-image records
    # must never become a marker (or accidentally appear at 0, 0).
    return PhotoSubmission.objects.filter(
        group_id=member.group_id,
        latitude__gte=-90, latitude__lte=90,
        longitude__gte=-180, longitude__lte=180,
    ).exclude(image="")


def _url(request, name, **kwargs):
    namespace = request.resolver_match.namespace if request.resolver_match else ""
    return reverse(f"{namespace}:{name}" if namespace else name, kwargs=kwargs)


def _location(photo):
    address = photo.cached_address if isinstance(photo.cached_address, dict) else {}
    parts = []
    for key in ("name", "city", "country"):
        value = address.get(key)
        if isinstance(value, str) and value.strip() and value.strip().lower() != "unknown":
            if value.strip() not in parts:
                parts.append(value.strip())
    return ", ".join(parts) or f"{photo.latitude:.4f}, {photo.longitude:.4f}"


def _thumbnail_url(request, photo, size):
    version = hashlib.sha256(photo.image.name.encode()).hexdigest()[:12]
    return f"{_url(request, 'photo_map_thumbnail', photo_id=photo.pk, size=size)}?v={version}"


@login_required(login_url="login")
@require_GET
@never_cache
def photo_map(request):
    member = _membership(request)
    return render(request, "photooftheday/map.html", {
        "group": member.group,
        "active_page": "map",
        "map_config": {
            "data_url": _url(request, "photo_map_data"),
            "carto_api_key": getattr(settings, "CARTO_API_KEY", ""),
        },
    })


@login_required(login_url="login")
@require_GET
@never_cache
def map_data(request):
    member = _membership(request)
    contributors = []
    for person in member.group.members.select_related("user").order_by("pk"):
        contributors.append({
            "id": person.user_id,
            "name": person.name or person.user.get_username(),
            "colour": person.colour if re.fullmatch(r"#[0-9a-fA-F]{6}", person.colour) else "#526b78",
        })

    # No caption, original image URL, file reads, or reverse-geocoding requests
    # are needed for the map index. Images load only when markers are visible.
    photos = []
    for photo in _photos(member).only(
        "id", "user_id", "date", "latitude", "longitude", "cached_address", "image",
    ).order_by("date", "pk").iterator():
        photos.append({
            "id": photo.pk,
            "photographer_id": photo.user_id,
            "date": photo.date.isoformat(),
            "latitude": float(photo.latitude),
            "longitude": float(photo.longitude),
            "location": _location(photo),
            "thumbnail": _thumbnail_url(request, photo, "marker"),
            "detail_url": _url(request, "photo_map_detail", photo_id=photo.pk),
        })

    # Reuse real archive records and its publication/editor visibility rules.
    dispatches = WeeklyDispatch.objects.filter(group_id=member.group_id).order_by("-week_start")
    weeks = [{
        "id": dispatch.pk,
        "number": dispatch.week_number,
        "title": dispatch.title,
        "start": dispatch.week_start.isoformat(),
        "end": (dispatch.week_start + timedelta(days=6)).isoformat(),
        "published": dispatch.published,
        "url": _url(request, "this_week", year=dispatch.week_start.year,
                    month=dispatch.week_start.month, day=dispatch.week_start.day),
    } for dispatch in dispatches if dispatch.published or dispatch.editor_id == member.pk]
    return JsonResponse({"photographers": contributors, "photos": photos, "weeks": weeks})


@login_required(login_url="login")
@require_GET
@never_cache
def map_photo(request, photo_id):
    photo = get_object_or_404(_photos(_membership(request)), pk=photo_id)
    return JsonResponse({
        "id": photo.pk,
        "date": photo.date.isoformat(),
        "location": _location(photo),
        "caption": photo.caption,
        "thumbnail": _thumbnail_url(request, photo, "preview"),
        "day_url": _url(request, "day", year=photo.date.year, month=photo.date.month, day=photo.date.day),
    })


@login_required(login_url="login")
@require_GET
@cache_control(private=True, max_age=3600)
@vary_on_cookie
def map_thumbnail(request, photo_id, size):
    sizes = {"marker": (96, 96), "preview": (640, 480)}
    if size not in sizes:
        raise Http404("Unknown thumbnail size")
    photo = get_object_or_404(_photos(_membership(request)), pk=photo_id)
    storage = photo.image.storage
    # ImageField assigns a new filename on replacement, invalidating derivatives.
    digest = hashlib.sha256(f"map-v1:{photo.image.name}:{size}".encode()).hexdigest()
    name = f"photooftheday/map_thumbnails/{digest[:2]}/{digest}.jpg"
    try:
        if storage.exists(name):
            return FileResponse(storage.open(name, "rb"), content_type="image/jpeg")
        with photo.image.open("rb") as source:
            with Image.open(source) as original:
                original.draft("RGB", sizes[size])
                image = ImageOps.exif_transpose(original).convert("RGB")
                if size == "marker":
                    image = ImageOps.fit(image, sizes[size], method=Image.Resampling.LANCZOS)
                else:
                    image.thumbnail(sizes[size], Image.Resampling.LANCZOS)
                output = BytesIO()
                image.save(output, "JPEG", quality=82, optimize=True)
        content = output.getvalue()
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise Http404("Photograph unavailable") from exc

    # A read-only media backend may still serve the generated small derivative.
    try:
        storage.save(name, ContentFile(content))
    except OSError:
        pass
    return FileResponse(BytesIO(content), content_type="image/jpeg")
