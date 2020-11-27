from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(MyUser, UserAdmin)
admin.site.register(Patient)
admin.site.register(PatientStatus)
admin.site.register(Symptom)
admin.site.register(DiseaseStatus)
admin.site.register(Connections)