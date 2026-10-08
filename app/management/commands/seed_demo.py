import os
from datetime import timedelta
from django.core.management.base import BaseCommand,CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from app.models import Activity,Comment,Kudos
from app.demo import sample_gpx
from app.gpx import parse
class Command(BaseCommand):
    help='Seed synthetic routes. Requires DEMO_PASSWORD; safe to repeat.'
    def handle(self,*a,**kw):
        password=os.environ.get('DEMO_PASSWORD')
        if not password:raise CommandError('Set DEMO_PASSWORD to seed the demo accounts.')
        users=[]
        for name in ['demo','jules']:
            u,created=get_user_model().objects.get_or_create(username=name)
            if created:u.set_password(password);u.save()
            users.append(u)
        for i,title in enumerate(['The morning loop','Easy miles, clear head','A little farther today']):
            day=timezone.localdate()-timedelta(days=i*2);raw=sample_gpx(day)
            activity,_=Activity.objects.get_or_create(user=users[i%2],title=title,defaults={'date':day,'sport':'run' if i!=1 else 'walk','public':i!=2,'gpx':raw,'status':'ready',**parse(raw)})
            if activity.public:Kudos.objects.get_or_create(user=users[(i+1)%2],activity=activity)
        first=Activity.objects.filter(title='The morning loop',user=users[0]).first()
        Comment.objects.get_or_create(user=users[1],activity=first,text='That loop looks like a great way to start the day.')
        self.stdout.write('Synthetic activity log ready. Usernames: demo, jules')
