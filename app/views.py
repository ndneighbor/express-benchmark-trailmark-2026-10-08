from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q,Sum
from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Activity,Kudos
from .forms import UploadForm,CommentForm
from .tasks import process_activity
def visible(user):return Activity.objects.filter(Q(user=user)|Q(public=True,status='ready'))
def enqueue(a):
    try:process_activity.delay(a.pk)
    except Exception:Activity.objects.filter(pk=a.pk).update(status='failed',error='The processing queue is unavailable. Please retry.')
@login_required
def home(request):
    own=Activity.objects.filter(user=request.user,status='ready');week=own.filter(date__gte=timezone.localdate()-timedelta(days=6),date__lte=timezone.localdate())
    agg=week.aggregate(distance=Sum('distance'),duration=Sum('duration'),elevation=Sum('elevation'))
    context={'activities':visible(request.user).select_related('user').prefetch_related('kudos')[:30],'km':(agg['distance'] or 0)/1000,'minutes':round((agg['duration'] or 0)/60),'elevation':agg['elevation'] or 0,'count':week.count(),'own_count':own.count()}
    return render(request,'home.html',context)
@login_required
def new(request):
    form=UploadForm(request.POST or None,request.FILES or None)
    if request.method=='POST' and form.is_valid():
        a=form.save(commit=False);a.user=request.user;a.gpx=form.cleaned_data['file'].read();a.save();enqueue(a);return redirect('activity',pk=a.pk)
    return render(request,'upload.html',{'form':form})
@login_required
def detail(request,pk):
    a=get_object_or_404(visible(request.user).select_related('user'),pk=pk)
    return render(request,'detail.html',{'activity':a,'form':CommentForm(),'comments':a.comments.select_related('user'),'has_kudos':a.kudos.filter(user=request.user).exists()})
@login_required
@require_POST
def kudos(request,pk):
    a=get_object_or_404(visible(request.user),pk=pk,status='ready');Kudos.objects.get_or_create(user=request.user,activity=a);return redirect('activity',pk=pk)
@login_required
@require_POST
def comment(request,pk):
    a=get_object_or_404(visible(request.user),pk=pk,status='ready');form=CommentForm(request.POST)
    if form.is_valid():c=form.save(commit=False);c.user=request.user;c.activity=a;c.save()
    else:messages.error(request,'Write a comment between 1 and 500 characters.')
    return redirect('activity',pk=pk)
@login_required
@require_POST
def delete(request,pk):get_object_or_404(Activity,pk=pk,user=request.user).delete();messages.success(request,'Activity deleted.');return redirect('/')
@login_required
@require_POST
def retry(request,pk):
    a=get_object_or_404(Activity,pk=pk,user=request.user)
    if a.status=='failed':a.status='pending';a.save(update_fields=['status']);enqueue(a)
    return redirect('activity',pk=pk)
@login_required
@require_POST
def visibility(request,pk):
    a=get_object_or_404(Activity,pk=pk,user=request.user);a.public=not a.public;a.save(update_fields=['public']);return redirect('activity',pk=pk)
@login_required
def download(request,pk):
    a=get_object_or_404(visible(request.user),pk=pk)
    response=HttpResponse(bytes(a.gpx),content_type='application/gpx+xml');response['Content-Disposition']=f'attachment; filename="trailmark-{pk}.gpx"';return response
