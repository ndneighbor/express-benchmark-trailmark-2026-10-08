import math
from datetime import datetime
from defusedxml.ElementTree import fromstring
class InvalidGPX(ValueError):pass
def distance(a,b):
    lat1,lon1,lat2,lon2=map(math.radians,[*a,*b]);dlat=lat2-lat1;dlon=lon2-lon1
    h=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371000*2*math.asin(min(1,math.sqrt(h)))
def parse(raw):
    if len(raw)>2_000_000:raise InvalidGPX('GPX files must be 2 MB or smaller.')
    try:root=fromstring(raw)
    except Exception as exc:raise InvalidGPX('This file is not safe, valid GPX XML.') from exc
    if root.tag.rsplit('}',1)[-1]!='gpx':raise InvalidGPX('Expected a GPX document.')
    total=0;gain=0;duration=0;route=[];count=0;timestamps=0
    segments=[e for e in root.iter() if e.tag.rsplit('}',1)[-1]=='trkseg']
    for seg in segments:
        prev=None;prev_ele=None;prev_time=None
        for e in seg:
            if e.tag.rsplit('}',1)[-1]!='trkpt':continue
            count+=1
            if count>50000:raise InvalidGPX('GPX contains too many track points.')
            try:point=(float(e.attrib['lat']),float(e.attrib['lon']))
            except (KeyError,ValueError):raise InvalidGPX('Track points need valid coordinates.')
            if not all(math.isfinite(n) for n in point) or not(-90<=point[0]<=90 and -180<=point[1]<=180):raise InvalidGPX('Track coordinates are out of range.')
            children={x.tag.rsplit('}',1)[-1]:x.text for x in e}
            ele=None;stamp=None
            try:
                if children.get('ele') is not None:
                    ele=float(children['ele'])
                    if not math.isfinite(ele):raise ValueError()
                if children.get('time') is not None:
                    stamp=datetime.fromisoformat(children['time'].replace('Z','+00:00'))
                    if stamp.tzinfo is None:raise ValueError()
                    timestamps+=1
            except (ValueError,TypeError):raise InvalidGPX('Elevation or timestamp is invalid. Times need a timezone.')
            if prev is not None:total+=distance(prev,point)
            if prev_ele is not None and ele is not None:gain+=max(0,ele-prev_ele)
            if prev_time is not None and stamp is not None:
                delta=(stamp-prev_time).total_seconds()
                if delta<0:raise InvalidGPX('Track timestamps must move forwards within each segment.')
                duration+=delta
            route.append(point);prev=point;prev_ele=ele;prev_time=stamp
    if count<2:raise InvalidGPX('Add a GPX track with at least two points.')
    if timestamps!=count:raise InvalidGPX('Each track point needs a timestamp to calculate pace.')
    if duration<=0:raise InvalidGPX('The activity needs a positive duration.')
    stride=max(1,math.ceil(count/500));simple=route[::stride]
    if simple[-1]!=route[-1]:simple.append(route[-1])
    return {'distance':total,'elevation':gain,'duration':round(duration),'route':simple}
