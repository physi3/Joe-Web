from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import File

from .models import GroupMember, PhotoSubmission, WeeklyDispatch, WeeklyDispatchEntry

from datetime import date as _date, timedelta
from PIL.ExifTags import GPSTAGS
from django.conf import settings
from uuid import uuid4
import os
from decimal import Decimal
from datetime import datetime
from PIL import Image, ExifTags
import calendar
from datetime import date, timedelta


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
    max_date = min(timezone.now().date(), max(requested_day + timedelta(days=3), group_created_date + timedelta(days=6)))  # Limit archive to 3 days after requested day
    for i in range(0, 7):
        d = max_date - timedelta(days=i)
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
        "active_page": "day",
    }

    return render(request, "photooftheday/day.html", context)

def this_week(request):
    start_of_week = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
    return redirect(f"/photooftheday/week/{start_of_week.year}/{start_of_week.month}/{start_of_week.day}/")

def week(request, year: int, month: int, day: int):
    requested_week = _date(int(year), int(month), int(day))

    if requested_week.weekday() != 0:
        # If the requested date is not a Monday, redirect to the Monday of that week
        requested_week = requested_week - timedelta(days=requested_week.weekday())
        return redirect(f"/photooftheday/week/{requested_week.year}/{requested_week.month}/{requested_week.day}/")

    try:
        group = GroupMember.objects.get(user=request.user).group
        members = group.members.all().select_related('user')
    except GroupMember.DoesNotExist:
        return redirect("/")

    creation_week = group.created_at.date() - timedelta(days=group.created_at.date().weekday())
    week_number = (requested_week - creation_week).days // 7

    weekly_dispatch = WeeklyDispatch.objects.filter(group=group, week_start=requested_week).first()
    if not weekly_dispatch:
        weekly_dispatch = WeeklyDispatch.objects.create(
            group=group,
            week_start=requested_week,
            week_number=week_number
        )

        for i in range(7):
            day_date = requested_week + timedelta(days=i)
            submissions = PhotoSubmission.objects.filter(group=group, date=day_date)
            entry = WeeklyDispatchEntry.objects.create(
                weekly_dispatch=weekly_dispatch,
                date=day_date,
                member_order=[member.pk for member in members],
            )
            
    else:
        print(f"WeeklyDispatch already exists for week starting {requested_week}: {weekly_dispatch}")

    days = []
    for i in range(7):
        day_date = requested_week + timedelta(days=i)
        submissions = PhotoSubmission.objects.filter(group=group, date=day_date)
        dispatch_entry = WeeklyDispatchEntry.objects.filter(weekly_dispatch=weekly_dispatch, date=day_date).first()
        if not dispatch_entry:
            dispatch_entry = WeeklyDispatchEntry.objects.create(
                weekly_dispatch=weekly_dispatch,
                date=day_date,
                member_order=[member.id for member in members],
            )
        day_members = [GroupMember.objects.get(id=memberpk) for memberpk in dispatch_entry.member_order]
        days.append({
            "url": f"/photooftheday/{day_date.year}/{day_date.month}/{day_date.day}/",
            "date":day_date,
            "members": [{"member": member, "submission": submissions.filter(user=member.user).first()} for member in day_members],
        })

    context = {
        "active_page": "week",
        "week_number": week_number,
        "week_start": requested_week,
        "week_end": requested_week + timedelta(days=6),
        "photo_count": 21,
        "day_count": 7,
        "place_count": 3,
        "prev_url": None,
        "next_url": None,
        "group": group,
        "days": days,
    }

    return render(request, "photooftheday/week.html", context)

def calendar_this_month(request):
    today = timezone.now().date()
    return redirect(f"/photooftheday/calendar/{today.year}/{today.month}/")

def calendar_view(request, year:int, month_int:int):
    month = date(year, month_int, 1)
    today = timezone.now().date()

    try:
        group = GroupMember.objects.get(user=request.user).group
        members = group.members.all().select_related('user')
    except GroupMember.DoesNotExist:
        return redirect("/")

    # get monday of the creation week
    creation_week = group.created_at.date() - timedelta(days=group.created_at.date().weekday())

    weeks = []

    for dates in calendar.Calendar(firstweekday=0).monthdatescalendar(
        month.year, month.month
    ):
        week_start = dates[0]

        days = []
        for day in dates:
            days.append({
                "date": day,
                "url": f"/photooftheday/{day:%Y}/{day:%m}/{day:%d}/",
                "in_month": day.month == month.month,
                "is_today": day == today,
                "is_disabled": day < group.created_at.date() or day > today,
                "uploads": [
                    {
                        "name": member.name,
                        "colour": member.colour,
                        "uploaded": PhotoSubmission.objects.filter(
                            group=group, user=member.user, date=day).exists()
                    }
                    for i, member in enumerate(members)
                ],
            })

        weeks.append({
            "number": (week_start - creation_week).days // 7,
            "url": f"/photooftheday/week/{week_start:%Y}/{week_start:%m}/{week_start:%d}/",
            "days": days,
            "is_disabled": week_start < creation_week or week_start > today,
        })

    previous_month = (month - timedelta(days=1)).replace(day=1)
    next_month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)

    context = {
        "group": group,
        "month": month,
        "members": members,
        "weeks": weeks,
        "previous_month_url": f"/photooftheday/calendar/{previous_month:%Y}/{previous_month:%m}/" if month > creation_week else None,
        "next_month_url": f"/photooftheday/calendar/{next_month:%Y}/{next_month:%m}/" if next_month < today else None,
        "active_page": "calendar",
    }

    return render(request, "photooftheday/calendar.html", context)

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