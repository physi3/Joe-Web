from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.views.decorators import csrf, http
from statusdisplay.models import User, Status
from django.forms.models import model_to_dict
from django.utils import timezone

from os.path import join, dirname
from os import environ
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Create your views here.
@csrf.csrf_exempt
@http.require_http_methods(["GET", "POST"])
def statusView(request):
    try:
        if request.method == "GET":
            return getLatestStatus(request, request.GET["user"])
            
        elif request.method == "POST":
            if (request.POST['key'] != environ.get('KEY')):
                raise Exception("Incorrect key passed.")
            user = User.objects.get(name=request.POST["user"])
            message = request.POST.getlist('message')
            time = timezone.now()

            status = Status(user=user, createTime=time,
                            lineOne = message[0], lineTwo = message[1], lineThree = message[2], lineFour = message[3]
                            )
            status.save()

            return JsonResponse({'success':True})
    except BaseException as error:
        return JsonResponse({'success':False, 'reason':f"{type(error).__name__}: {error}"})

@csrf.csrf_exempt
def getLatestStatus(request, queryUser):
    queryUserID = User.objects.get(name=queryUser)
    latestStatus = Status.objects.filter(user=queryUserID).order_by("-createTime")
    return JsonResponse({'successs':True, 'queryUser':str(queryUserID), 'status':model_to_dict(latestStatus[0])})
