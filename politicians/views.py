from django.shortcuts import render
import politicians.models

def rank(request):
    context = {}
    if (request.method == 'POST'):
        # Update elo
        pass

    return render(request, "base.html", context)