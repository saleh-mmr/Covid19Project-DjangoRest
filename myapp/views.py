from . import models
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework import status

# use django authentication for User authentication, We can also use django rest SessionAuthentication.
from django.contrib.auth import authenticate
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# use django user model
from django.contrib.auth.models import User

from django.contrib.auth import logout as django_logout

from rest_framework.authtoken.models import Token

from .Authentication import token_expire_handler


def new_report(request):
    method_data = request.data
    first_name = method_data["firstname"]
    last_name = method_data["lastname"]
    phone_number = method_data["phonenumber"]
    national_code = method_data["nationalcode"]
    patient_status = method_data["patientstatus"]
    symptoms = method_data['symptoms']
    my_user = request.user
    try:
        is_Available = models.Patient.objects.filter(national_code=national_code)
        if not is_Available:
            p = models.Patient.objects.create(user_site=my_user, first_name=first_name, last_name=last_name,
                                              phone_number=phone_number, national_code=national_code)
            sum = 0
            number = 0
            for i in symptoms:
                if models.Symptom.objects.filter(symptom_name=i):
                    s = models.Symptom.objects.get(symptom_name=i)
                    sum = sum + s.weight
                    number = number + 1
                    models.PatientSymptom.objects.create(patient=p, symptom=s)
            avg = sum / number
            patientstatus = models.PatientStatus.objects.get(patient_status_name=patient_status)
            if avg > 5:
                rsp = {
                    'illness': "Ghatei"
                }
                current_illness_status = models.IllnessStatus.objects.get(illness_status_name="Ghatei")
                models.Status.objects.create(patient=p, patient_status=patientstatus,
                                             illness_status=current_illness_status, status_date='2020-11-21')
                return Response(rsp, status=status.HTTP_200_OK)
            elif avg > 3:
                rsp = {
                    'illness': "Mashkook"
                }
                current_illness_status = models.IllnessStatus.objects.get(illness_status_name="Mashkook")
                models.Status.objects.create(patient=p, patient_status=patientstatus,
                                             illness_status=current_illness_status, status_date='2020-11-21')
                return Response(rsp, status=status.HTTP_200_OK)
            rsp = {
                'illness': "Anfoolanza"
            }
            current_illness_status = models.IllnessStatus.objects.get(illness_status_name="Anfoolanza")
            models.Status.objects.create(patient=p, patient_status=patientstatus, illness_status=current_illness_status,
                                         status_date='2020-11-21')
            return Response(rsp, status=status.HTTP_200_OK)
        return Response({"message": "This Patient is already added!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response({"message": "Exception!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)