import math
from datetime import datetime,timedelta,timezone
def sample_gpx(day=None):
    start=datetime.combine(day or datetime.now(timezone.utc).date(),datetime.min.time(),tzinfo=timezone.utc).replace(hour=7)
    points=[]
    for i in range(181):
        theta=i/180*2*math.pi;lat=37.77+.009*math.sin(theta);lon=-122.45+.012*math.cos(theta)
        stamp=(start+timedelta(seconds=i*12)).isoformat();ele=30+10*math.sin(theta*2)
        points.append(f'<trkpt lat="{lat:.6f}" lon="{lon:.6f}"><ele>{ele:.1f}</ele><time>{stamp}</time></trkpt>')
    return ('<?xml version="1.0"?><gpx version="1.1" xmlns="http://www.topografix.com/GPX/1/1"><trk><name>Synthetic park loop</name><trkseg>'+''.join(points)+'</trkseg></trk></gpx>').encode()
