from django.shortcuts import render

def default_web_view(request):
    return render(request, 'default_web_view.html')