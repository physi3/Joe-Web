from functools import wraps

from django.http import JsonResponse

from ..models import Awards

def load_award(admin=False):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, username, listname, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {"error": "Authentication required."},
                    status=401
                )

            award = Awards.objects.filter(
                owner__username=username,
                slug=listname.lower()
            ).first()

            if not award:
                return JsonResponse(
                    {"error": "Award not found."},
                    status=404
                )

            if not award.has_access(request.user):
                return JsonResponse(
                    {"error": "You do not have permission to access this award."},
                    status=403
                )

            if admin and not award.is_admin(request.user):
                return JsonResponse(
                    {"error": "Only admins may perform this action."},
                    status=403
                )

            return view_func(
                request,
                award,
                *args,
                **kwargs
            )

        return wrapper

    return decorator