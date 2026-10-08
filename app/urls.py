from django.urls import path
from . import views
urlpatterns=[path('',views.home),path('new/',views.new),path('activities/<int:pk>/',views.detail,name='activity'),path('activities/<int:pk>/kudos/',views.kudos),path('activities/<int:pk>/comment/',views.comment),path('activities/<int:pk>/delete/',views.delete),path('activities/<int:pk>/retry/',views.retry),path('activities/<int:pk>/visibility/',views.visibility),path('activities/<int:pk>/download/',views.download)]
