from django.contrib import admin
from django.conf.urls import url
from myapp.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^signup/', signup, name='signup'),
    url(r'^login/', login, name='login'),
    url(r'^logout/', logout, name='logout'),
    url(r'^get-user-info/', get_user_info, name='userinfo'),
    url(r'^newreport/', new_report, name='newreport'),
    url(r'^recent-reports/', get_all_user_reports, name='allreports'),
    url(r'^edit-report/(?P<pk>\d+)$', edit_report, name='editreport'),
    url(r'^add-connection/(?P<pk>\d+)$', add_connection, name='addconnection'),
    url(r'^patient-info/(?P<pk>\d+)$', get_patient_info, name='patientinfo'),
    url(r'^patient-connections/(?P<pk>\d+)$', get_patient_connections, name='patientconnections'),
    url(r'^number-corona/', get_number_corona, name='numbercorona'),
    url(r'^corona_statistics/', get_corona_statistics, name='coronastatistics'),
]