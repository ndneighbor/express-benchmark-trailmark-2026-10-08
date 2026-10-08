from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET
import logging
def signup(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save()); return redirect('/')
    return render(request,'registration/signup.html',{'form':form})
@require_GET
def health(request):
    try:
        with connection.cursor() as c: c.execute('SELECT 1'); c.fetchone()
        return JsonResponse({'status':'ok','database':'connected'})
    except Exception:
        logging.exception('database_health_failed')
        return JsonResponse({'status':'unavailable'},status=503)
