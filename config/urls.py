from django.contrib import admin
from django.urls import path, include
from app import common
urlpatterns = [path('admin/',admin.site.urls),path('accounts/',include('django.contrib.auth.urls')),path('accounts/signup/',common.signup,name='signup'),path('healthz',common.health),path('',include('app.urls'))]
