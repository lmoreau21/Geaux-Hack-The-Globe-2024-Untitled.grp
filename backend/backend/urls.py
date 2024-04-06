"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .json_llm import chatbot_post
#from .json_llm import json_chatbot_post
from .views import default_web_view
urlpatterns = [
    path('', default_web_view),
    #path('chatbot/json_post/', json_chatbot_post)
    path('chatbot/', chatbot_post)
]

#paul: These bottom two url patterns are used in port 8000 so people can communicate directly with backend. 
#what do the two above do?

#james: The blank one and admin is not really used directly. 