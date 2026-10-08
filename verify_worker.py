"""Run inside the web container: python verify_worker.py. Uses real Redis/worker."""
import os,time
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from app.models import Activity
from app.demo import sample_gpx
assert not settings.CELERY_TASK_ALWAYS_EAGER,'This check requires a real worker.'
user,_=get_user_model().objects.get_or_create(username='worker-verification')
client=Client(HTTP_HOST='localhost');client.force_login(user)
response=client.post('/new/',{'title':'Worker verification route','sport':'run','date':str(timezone.localdate()),'file':SimpleUploadedFile('loop.gpx',sample_gpx())})
assert response.status_code==302
activity=Activity.objects.filter(user=user).latest('pk')
for _ in range(100):
    activity.refresh_from_db()
    if activity.status in ['ready','failed']:break
    time.sleep(.25)
assert activity.status=='ready',(activity.status,activity.error)
assert 6<activity.km<7 and activity.duration==2160
response=client.get(f'/activities/{activity.pk}/download/')
assert response.status_code==200 and response.content==sample_gpx()
client.post(f'/activities/{activity.pk}/kudos/')
client.post(f'/activities/{activity.pk}/comment/',{'text':'The worker processed my route.'})
assert activity.kudos.count()==1 and activity.comments.count()==1
print('PASS: GPX upload → Postgres → Redis → separate Celery worker → route, stats, kudos, comment, GPX download')
