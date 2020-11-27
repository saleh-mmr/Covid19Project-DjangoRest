from django.contrib import admin
from django.conf.urls import url
from myapp.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^signup/', signup, name='signup'),
    url(r'^login/', login, name='login'),
    url(r'^logout/', logout, name='logout'),
    url(r'^getinfo/', get_user_info, name='getinfo'),
    url(r'^newreport/', new_report, name='newreport'),
    url(r'^recent-reports/', get_all_user_reports, name='allreports'),
    url(r'^edit-report/', edit_report, name='editreport'),

]