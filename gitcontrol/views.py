from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import git
import json

@csrf_exempt
def pullmain(request):
    response = {}
    body_unicode = request.body.decode('utf-8')
    if body_unicode and 'push' in json.loads(body_unicode)['hook']['events']:
        g = git.cmd.Git("./")
        response['results'] = g.pull()
        response['success'] = True
    else:
        response['success'] = False
    return JsonResponse(response)
