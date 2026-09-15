from datetime import date as _date, timedelta
from PIL.ExifTags import GPSTAGS
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import GroupMember, PhotoSubmission
from django.core.files.storage import default_storage
from django.core.files.base import File
from django.conf import settings
from uuid import uuid4
import os
from decimal import Decimal
from datetime import datetime
from PIL import Image, ExifTags

from .utils.geocoding import dms_to_decimal

def index(request):
    """Redirect to today's photo-of-the-day page."""
    today = timezone.now().date()
    return day(request, today.year, today.month, today.day)

@login_required(login_url="login")
def day(request, year: int, month: int, day: int):
    """Render the photo-of-the-day page for a specific date.

    URL captures `year`, `month`, `day` as integers.
    The current user's group is looked up via `GroupMember`.
    """
    try:
        group = GroupMember.objects.get(user=request.user).group
    except GroupMember.DoesNotExist:
        # If the user has no group, redirect to a sensible page (home)
        return redirect("/")

    try:
        requested_day = _date(int(year), int(month), int(day))
    except ValueError:
        # invalid date
        return redirect("/")

    # Fetch submissions for this group on the requested day
    submissions = (
        PhotoSubmission.objects.select_related("user")
        .filter(group=group, date=requested_day)
    )

    # Build a simple list of location strings (prefer formatted_address)
    locations = []
    for s in submissions:
        loc = None
        fa = getattr(s, "formatted_address", None)
        if fa:
            loc = fa
        elif s.latitude and s.longitude:
            loc = f"{s.latitude}, {s.longitude}"
        if loc and loc not in locations:
            locations.append(loc)

    # Prepare members list pairing each group member with their submission (or None)
    # This ensures we render all three users even if they didn't submit.
    members = []
    sub_by_user = {}
    for s in submissions:
        uid = getattr(s, 'user_id', None) or (getattr(getattr(s, 'user', None), 'pk', None))
        if uid:
            sub_by_user[uid] = s

    members_qs = []
    if hasattr(group, 'members'):
        try:
            members_qs = group.members.all().select_related('user')
        except Exception:
            # Fallback: iterate without select_related
            members_qs = group.members.all()

    for gm in members_qs:
        uid = getattr(getattr(gm, 'user', None), 'pk', None)
        members.append({
            'member': gm,
            'submission': sub_by_user.get(uid),
        })

    # Archive listing: recent 7 days, starting no earlier than group creation.
    archive = []
    group_created_date = group.created_at.date()
    for i in range(0, 7):
        d = timezone.now().date() - timedelta(days=i)
        if d < group_created_date:
            continue
        archive.append({
            "label": d.strftime("%d %b %Y"),
            "url": f"/photooftheday/{d.year}/{d.month}/{d.day}/",
            "active": d == requested_day,
        })

    # Prev / Next URLs
    prev_date = requested_day - timedelta(days=1)
    next_date = requested_day + timedelta(days=1)
    prev_url = None
    next_url = None
    if requested_day > group_created_date:
        prev_url = f"/photooftheday/{prev_date.year}/{prev_date.month}/{prev_date.day}/"
    if requested_day < timezone.now().date():
        next_url = f"/photooftheday/{next_date.year}/{next_date.month}/{next_date.day}/"

    # Day number relative to group's creation date if available
    day_number = None
    try:
        created = group.created_at.date()
        day_number = (requested_day - created).days + 1
        if day_number < 1:
            day_number = None
    except Exception:
        day_number = None

    upload_url = f"/photooftheday/{requested_day.year}/{requested_day.month}/{requested_day.day}/upload/"

    context = {
        "group": group,
        "day": requested_day,
        "today": timezone.now().date(),
        "submissions": submissions,
        "members": members,
        "locations": locations,
        "archive": archive,
        "prev_url": prev_url,
        "next_url": next_url,
        "day_number": day_number,
        "upload_url": upload_url,
    }

    return render(request, "photooftheday/day.html", context)


@login_required(login_url="login") # type: ignore
def upload(request, year: int, month: int, day: int):
    try:
        requested_day = _date(int(year), int(month), int(day))
    except ValueError:
        return redirect("/")

    try:
        group = GroupMember.objects.get(user=request.user).group
    except GroupMember.DoesNotExist:
        return redirect("/")

    existing = PhotoSubmission.objects.filter(user=request.user, date=requested_day).first()

    if request.method == "GET":
        return render(request, "photooftheday/upload.html", {
            "day": requested_day,
            "existing": existing,
            "carto_api_key": settings.CARTO_API_KEY,
        })

    step = request.POST.get("step")

    context = {
        "day": requested_day,
        "existing": existing,
        "carto_api_key": settings.CARTO_API_KEY,
    }

    if step != "confirm":
        imgfile = request.FILES.get("image")
        if not imgfile:
            return render(request, "photooftheday/upload.html", {
                "error": "No image uploaded.",
                "day": requested_day,
                "existing": existing,
                "carto_api_key": settings.CARTO_API_KEY,
            })

        temp_name = f"photooftheday/temp/{uuid4().hex}_{os.path.basename(imgfile.name)}"
        saved_path = default_storage.save(temp_name, imgfile)

        context["temp_path"] = saved_path

        try:
            preview_url = default_storage.url(saved_path)
        except Exception:
            preview_url = settings.MEDIA_URL + saved_path

        context["preview_url"] = preview_url

        if Image:
            try:
                with default_storage.open(saved_path, "rb") as f:
                    img = Image.open(f)

                    exif_data = img.getexif()

                    pretty_exif = {ExifTags.TAGS.get(key, key) : value for key, value in exif_data.items()}

                    if pretty_exif.get('DateTime'):
                        context["exif_timestamp"] = datetime.strptime(pretty_exif.get('DateTime'), "%Y:%m:%d %H:%M:%S") # type: ignore
                         

                    gps_info = exif_data.get_ifd(0x8825)

                    if gps_info:
                        gps = {
                            GPSTAGS.get(key, key): value
                            for key, value in gps_info.items()
                        }


                        context["exif_lat"] = dms_to_decimal(gps.get("GPSLatitude", (0, 0, 0)), gps.get("GPSLatitudeRef", "N"))
                        context["exif_lon"] = dms_to_decimal(gps.get("GPSLongitude", (0, 0, 0)), gps.get("GPSLongitudeRef", "E"))

            except Exception:
                pass


        return render(request, "photooftheday/upload.html", context)

    # Confirm and save
    if step == "confirm":
        temp_path = request.POST.get("temp_path")
        caption = request.POST.get("caption", "")
        t_val = request.POST.get("time")
        lat_val = request.POST.get("latitude")
        lon_val = request.POST.get("longitude")

        print(f"Confirming upload: temp_path={temp_path}, caption={caption}, time={t_val}, lat={lat_val}, lon={lon_val}")

        latitude = None
        longitude = None
        try:
            if lat_val:
                latitude = Decimal(lat_val)
            if lon_val:
                longitude = Decimal(lon_val)
        except Exception:
            latitude = longitude = None

        try:
            with default_storage.open(temp_path, 'rb') as f:
                django_file = File(f)
                if existing:
                    obj = existing
                    obj.image.save(os.path.basename(temp_path), django_file, save=False)
                else:
                    obj = PhotoSubmission(group=group, user=request.user)
                    obj.image.save(os.path.basename(temp_path), django_file, save=False)

                obj.caption = caption
                obj.time = t_val

                if latitude is not None:
                    obj.latitude = latitude
                if longitude is not None:
                    obj.longitude = longitude

                obj.date = requested_day
                obj.save()

            try:
                default_storage.delete(temp_path)
            except Exception:
                pass

            return redirect(f"/photooftheday/{requested_day.year}/{requested_day.month}/{requested_day.day}/")
        except Exception as e:
            print(f"Error saving submission: {e}")
            return render(request, "photooftheday/upload.html", {"error": "Failed to save submission.", "day": requested_day, "existing": existing})