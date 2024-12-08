from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.views.decorators import csrf, http
from statusdisplay.models import User, Status, Display
from django.forms.models import model_to_dict
from django.utils import timezone

from os.path import join, dirname
from os import environ
from dotenv import load_dotenv
import json

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
def getLatestStatus(request, queryUser) -> JsonResponse:
    queryUserID = User.objects.get(name=queryUser)
    latestStatus = Status.objects.filter(user=queryUserID).order_by("-createTime")
    return JsonResponse({'successs':True, 'queryUser':str(queryUserID), 'status':model_to_dict(latestStatus[0])})

@csrf.csrf_exempt
def getDisplayID(request, displayName) :
    try:
        display = Display.objects.get(name=displayName)
        return JsonResponse({'success':True, 'displayID':display.id})
    except BaseException as error:
        return JsonResponse({'success':False, 'reason':f"{type(error).__name__}: {error}"})

@http.require_http_methods(["GET"])
@csrf.csrf_exempt
def displayCheck(request):
    response = {'success' : False}
    try:
        getDict = json.loads(request.body)

        displayID = getDict["displayID"]
        displayStatus = getDict["displayStatus"]

        display = Display.objects.get(id=displayID)
        
        latestStatus = Status.objects.filter(user=display.targetUser).order_by("-createTime")[0]

        if displayStatus["statusID"] != latestStatus.id:
            response['status'] = model_to_dict(latestStatus)
        
        if displayStatus["backlight"] != display.backlight:
            response['backlight'] = display.backlight

        response['success'] = True
        return JsonResponse(response)
    except BaseException as error:
        response['reason'] = f"{type(error).__name__}: {error}"
        return JsonResponse(response)
