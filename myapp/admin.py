from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(MyUser, UserAdmin)
admin.site.register(Patient)
admin.site.register(Symptom)
admin.site.register(PatientSymptom)
admin.site.register(RelatedPeople)
admin.site.register(PatientStatus)
admin.site.register(IllnessStatus)
admin.site.register(Status)
