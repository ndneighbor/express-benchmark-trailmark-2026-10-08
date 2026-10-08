import logging
from celery import shared_task
from .models import Activity
from .gpx import parse,InvalidGPX
@shared_task
def process_activity(pk):
    a=Activity.objects.get(pk=pk)
    if a.status=='ready':return
    Activity.objects.filter(pk=pk).update(status='processing',error='')
    try:result=parse(bytes(a.gpx));Activity.objects.filter(pk=pk).update(**result,status='ready')
    except InvalidGPX as e:Activity.objects.filter(pk=pk).update(status='failed',error=str(e))
    except Exception:
        logging.getLogger(__name__).exception('Processing failed: %s',pk)
        Activity.objects.filter(pk=pk).update(status='failed',error='Processing failed. Please retry.');raise
