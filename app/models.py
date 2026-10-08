from django.conf import settings
from django.db import models
class Activity(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    title=models.CharField(max_length=120)
    sport=models.CharField(max_length=12,choices=[('run','Run'),('ride','Ride'),('walk','Walk')])
    public=models.BooleanField(default=False)
    created=models.DateTimeField(auto_now_add=True)
    date=models.DateField()
    status=models.CharField(max_length=12,default='pending')
    error=models.CharField(max_length=200,blank=True)
    gpx=models.BinaryField()
    distance=models.FloatField(default=0)
    duration=models.PositiveIntegerField(default=0)
    elevation=models.FloatField(default=0)
    route=models.JSONField(default=list)
    class Meta:ordering=['-date','-id'];indexes=[models.Index(fields=['user','date']),models.Index(fields=['public','status'])]
    @property
    def km(self):return self.distance/1000
    @property
    def minutes(self):return round(self.duration/60)
    @property
    def pace(self):
        if not self.distance:return '—'
        seconds=round(self.duration/(self.distance/1000));return f'{seconds//60}:{seconds%60:02d}'
    @property
    def polyline(self):
        if len(self.route)<2:return ''
        # Local equirectangular projection with latitude correction. No external map service.
        import math
        lat=sum(p[0] for p in self.route)/len(self.route)
        points=[(p[1]*math.cos(math.radians(lat)),-p[0]) for p in self.route]
        lo_x=min(p[0] for p in points);lo_y=min(p[1] for p in points)
        span=max(max(p[0] for p in points)-lo_x,max(p[1] for p in points)-lo_y,1e-6)
        return ' '.join(f'{30+(x-lo_x)/span*420:.1f},{30+(y-lo_y)/span*420:.1f}' for x,y in points)
class Kudos(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    activity=models.ForeignKey(Activity,related_name='kudos',on_delete=models.CASCADE)
    class Meta:constraints=[models.UniqueConstraint(fields=['user','activity'],name='one_kudos_per_user')]
class Comment(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    activity=models.ForeignKey(Activity,related_name='comments',on_delete=models.CASCADE)
    text=models.CharField(max_length=500)
    created=models.DateTimeField(auto_now_add=True)
    class Meta:ordering=['created']
