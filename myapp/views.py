from . import models
from django.core.mail import send_mail
import http.client
import datetime as DT
import ast

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
import logging,traceback
logger = logging.getLogger('django')

@api_view(['POST'])
@permission_classes(())
def signup(request):
    try:
        data = request.data
        data_username = data['username']
        data_password = data['password']
        data_email = data['email']
        data_confirm_password = data['cpassword']
        if data_confirm_password == data_password:
            newUser = models.MyUser.objects.create(username=data_username, email=data_email)
            newUser.set_password(data_password)
            newUser.save()
            if newUser:
                return Response({"message": "Created Successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Something might be Wrong!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes(())
def login(request):
    try:
        params = request.data
        user = authenticate(username=params['username'], password=params['password'], )
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            is_expired, token = token_expire_handler(token)
            tmp_response = {
                'access': token.key,
                'userid': token.user_id
            }
            return Response(tmp_response, status=status.HTTP_200_OK)
        else:
            logger.info(request.data)
            return Response({"message": "Wrong username or password"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        django_logout(request)
        Token.objects.filter(key=request.headers.get('Authorization')[7:]).delete()
        return Response({"message": "Logout Successfully!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": "An error occurs in logout!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    data = request.headers.get('Authorization')
    user_token = data[7:]
    rsp = {
        'username': Token.objects.get(key=user_token).user.username,
        'email': Token.objects.get(key=user_token).user.email
    }
    return Response(rsp, status=status.HTTP_200_OK)


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def new_report(request):
    if request.method == 'POST':
        data = request.data
        current_user = request.user
        first_name = data["firstName"]
        last_name = data["lastName"]
        phone_number = data["phoneNumber"]
        national_code = data["nationalCode"]
        birth_date = data['birthDate']
        symptoms = data['symptoms']
        try:
            is_Available = models.Patient.objects.filter(national_code=national_code)
            if not is_Available:
                current_patient = models.Patient.objects.create(user_site=current_user, first_name=first_name,
                                                                last_name=last_name, phone_number=phone_number,
                                                                national_code=national_code, birth_date=birth_date)
                sum = 0
                for i in symptoms:
                    if models.Symptom.objects.filter(symptom_title=i):
                        current_symptom = models.Symptom.objects.get(symptom_title=i)
                        models.PatientSymptom.objects.create(patient=current_patient, symptom=current_symptom)
                        sum = sum + current_symptom.weight
                ghatei = models.DiseaseStatus.objects.get(disease_status_title="قطعی کرونا", is_System=True)
                mashkook = models.DiseaseStatus.objects.get(disease_status_title="مشکوک به کرونا", is_System=True)
                anfoolanza = models.DiseaseStatus.objects.get(disease_status_title="آنفولانزا", is_System=True)
                if sum > ghatei.probable:
                    models.Status.objects.create(patient=current_patient, disease_status=ghatei)
                    rsp = {'illness': ghatei.disease_status_title,
                           'patientid': current_patient.id,
                           'flag': True
                           }
                elif sum > mashkook.probable:
                    models.Status.objects.create(patient=current_patient, disease_status=mashkook)
                    rsp = {'illness': mashkook.disease_status_title,
                           'patientid': current_patient.id,
                           'flag': True
                           }
                else:
                    models.Status.objects.create(patient=current_patient, disease_status=anfoolanza)
                    rsp = {'illness': anfoolanza.disease_status_title,
                           'patientid': current_patient.id,
                           'flag': True
                           }

                return Response(rsp, status=status.HTTP_200_OK)

            else:
                # Current_patient = models.Patient.objects.get(nationalCode=national_code)
                # Current_patient.firstName = first_name
                # Current_patient.lastName = last_name
                # Current_patient.phoneNumber = phone_number
                # last_disease = Current_patient.diseases.last()
                # Current_patient.save()
                rsp = {'flag': False}
                return Response(rsp, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            return Response({'Error': "Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'PUT':
        data = request.data
        patient_id = data["patientid"]
        disease_status = data["diseaseStatus"]
        patient_status = data["patientStatus"]
        try:
            if models.Patient.objects.filter(id=patient_id, user_site=request.user):
                current_patient = models.Patient.objects.get(id=patient_id, user_site=request.user)
                current_disease = models.DiseaseStatus.objects.get(disease_status_title=disease_status, is_System=False)
                current_status = models.PatientStatus.objects.get(patient_status_title=patient_status)
                models.Status.objects.create(patient=current_patient, disease_status=current_disease,
                                             patient_status=current_status)
                return Response({'flag': True})
            else:
                return Response({'flag': False})
        except Exception as e:
            return Response({'Error': "Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_user_reports(request):
    try:
        a = models.Patient.objects.filter(user_site=request.user)
        rsp = {}
        if a:
            s = 0
            for i in a:
                b = models.Status.objects.filter(patient=i)
                patient_status = 'ثبت نشده'
                disease_title = 'ثبت نشده'
                for j in b:
                    if j.patient_status:
                        patient_status = j.patient_status.patient_status_title
                    if not j.disease_status.is_System:
                        disease_title = j.disease_status.disease_status_title
                rsp.update({'val' + str(s): {'id': i.id, 'firstname': i.first_name, 'lastname': i.last_name,
                                             'phonenumber': i.phone_number, 'nationalcode': i.national_code,
                                             'disease': disease_title, 'patientstatus': patient_status}})
                s = s + 1
            rsp.update({'flag': True})
            return Response(rsp, status=status.HTTP_200_OK)
        else:
            rsp.update({'flag': False})
            return Response(rsp, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        print(e)
        return Response({'Error': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_email(email, data):
    send_mail('django test title',
              'this email is sent by Corona_Project.\n You should take care of yourself in this situation.\nlast '
              'disease: ' + data,
              'sofwareengineering96@gmail.com',
              [email],
              fail_silently=False)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_report(request, pk):
    data = request.data
    patientid = pk
    firstName = data['firstName']
    lastName = data['lastName']
    nationalCode = data['nationalCode']
    phoneNumber = data['phoneNumber']
    birthDate = data['birthDate']
    diseasestatus = data['diseaseStatus']
    patientstatus = data['patientStatus']
    symptoms = data['symptoms']
    try:
        if models.Patient.objects.filter(id=patientid, user_site=request.user):
            current_patient = models.Patient.objects.get(id=patientid, user_site=request.user)
            a = models.Status.objects.filter(patient=current_patient)
            for i in a:
                if i.disease_status.is_System:
                    current_disease_system = i.disease_status
            if symptoms:
                models.PatientSymptom.objects.filter(patient=current_patient).delete()
                sum = 0
                for i in symptoms:
                    current_symptom = models.Symptom.objects.get(symptom_title=i)
                    sum = sum + current_symptom.weight
                    models.PatientSymptom.objects.create(patient=current_patient, symptom=current_symptom)
                ghatei = models.DiseaseStatus.objects.get(disease_status_title="قطعی کرونا", is_System=True)
                mashkook = models.DiseaseStatus.objects.get(disease_status_title="مشکوک به کرونا", is_System=True)
                anfoolanza = models.DiseaseStatus.objects.get(disease_status_title="آنفولانزا", is_System=True)
                if models.PatientStatus.objects.filter(patient_status_title=patientstatus):
                    current_status = models.PatientStatus.objects.get(patient_status_title=patientstatus)

                    if sum > ghatei.probable:
                        models.Status.objects.create(patient=current_patient, disease_status=ghatei,
                                                     patient_status=current_status)
                        current_disease_system = ghatei
                        for i in models.Connections.objects.filter(patient=current_patient):
                            send_email(i.email, current_disease_system.disease_status_title)
                    elif sum > mashkook.probable:
                        models.Status.objects.create(patient=current_patient, disease_status=mashkook,
                                                     patient_status=current_status)
                        current_disease_system = mashkook
                    else:
                        models.Status.objects.create(patient=current_patient, disease_status=anfoolanza,
                                                     patient_status=current_status)
                        current_disease_system = anfoolanza
                else:
                    if sum > ghatei.probable:
                        models.Status.objects.create(patient=current_patient, disease_status=ghatei)
                        current_disease_system = ghatei
                    elif sum > mashkook.probable:
                        models.Status.objects.create(patient=current_patient, disease_status=mashkook)
                        current_disease_system = mashkook
                    else:
                        models.Status.objects.create(patient=current_patient, disease_status=anfoolanza)
                        current_disease_system = anfoolanza
            current_patient.first_name = firstName
            current_patient.last_name = lastName
            current_patient.national_code = nationalCode
            current_patient.phone_number = phoneNumber
            current_patient.birth_date = birthDate
            if models.DiseaseStatus.objects.filter(disease_status_title=diseasestatus, is_System=False) \
                    and models.PatientStatus.objects.filter(patient_status_title=patientstatus):
                current_disease_user = models.DiseaseStatus.objects.get(disease_status_title=diseasestatus,
                                                                        is_System=False)
                current_status = models.PatientStatus.objects.get(patient_status_title=patientstatus)
                models.Status.objects.create(patient=current_patient, disease_status=current_disease_user,
                                             patient_status=current_status)
            current_patient.save()
            rsp = {
                'first_name': current_patient.first_name,
                'last_name': current_patient.last_name,
                'phone_number': current_patient.phone_number,
                'national_code': current_patient.national_code,
                'birth_date': current_patient.birth_date,
                'user_disease': current_disease_user.disease_status_title,
                'patient_status': current_status.patient_status_title,
                'system_disease': current_disease_system.disease_status_title,
                'flag': True
            }
            return Response(rsp, status=status.HTTP_200_OK)
        rsp = {
            'user_disease': 'null',
            'patient_status': 'null',
            'system_disease': 'null',
            'flag': False
        }
        return Response(rsp, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'Error': 'Error'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_connection(request, pk):
    data = request.data
    patientid = pk
    phonenumber = data['phoneNumber']
    email = data['email']
    try:
        if models.Patient.objects.filter(id=patientid, user_site=request.user):
            current_patient = models.Patient.objects.get(id=patientid, user_site=request.user)
            models.Connections.objects.create(patient=current_patient, phone_number=phonenumber, email=email)
            last_disease = ''
            for i in models.Status.objects.filter(patient=current_patient):
                last_disease = i.disease_status.disease_status_title
            if last_disease == "مشکوک به کرونا":
                send_email(email, last_disease)
            elif last_disease == "قطعی کرونا":
                send_email(email, last_disease)
            return Response({'flag': True}, status=status.HTTP_200_OK)
        else:
            return Response({'flag': False}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        print(e)
        return Response({'Error': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patient_info(request, pk):
    try:
        if models.Patient.objects.filter(id=pk, user_site=request.user):
            current_patient = models.Patient.objects.get(id=pk, user_site=request.user)
            rsp = {
                'firstname': current_patient.first_name,
                'lastname': current_patient.last_name,
                'phonenumber': current_patient.phone_number,
                'nationalcode': current_patient.national_code,
                'birthdate': current_patient.birth_date,
                'flag': True
            }
            return Response(rsp, status=status.HTTP_200_OK)
        else:
            return Response({'flag': False}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'Error': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_patient_connections(request, pk):
    try:
        if models.Patient.objects.filter(id=pk, user_site=request.user):
            current_patient = models.Patient.objects.get(id=pk, user_site=request.user)
            connections = models.Connections.objects.filter(patient=current_patient)
            s = 0
            rsp = {}
            for i in connections:
                rsp.update({'connection' + str(s): {'phoneNumber': i.phone_number,
                                                    'email': i.email
                                                    }
                            })
                s = s + 1
            rsp.update({'flag': True})
            return Response(rsp, status=status.HTTP_200_OK)
        else:
            return Response({'flag': False}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'Error': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes(())
def get_number_corona(request):
    try:
        allStatus = models.Status.objects.filter()
        allPatients = models.Patient.objects.filter()
        last = ''
        statusperpatient = []
        for i in allPatients:
            for j in allStatus:
                if j.patient == i:
                    last = j.disease_status
            statusperpatient.append(last)
        ghateiCorona = models.DiseaseStatus.objects.get(disease_status_title="قطعی کرونا", is_System=False)
        s = 0
        for i in statusperpatient:
            if i == ghateiCorona:
                s = s + 1
        return Response({'result': s}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response({'Error': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes(())
def get_corona_statistics(request):
    try:
        conn = http.client.HTTPSConnection("covid-193.p.rapidapi.com")

        headers = {
            'x-rapidapi-key': "4af2372f70msh1d66abbf15ab96bp13443cjsn3b0f85f58f9a",
            'x-rapidapi-host': "covid-193.p.rapidapi.com"
        }

        today = DT.date.today()
        a = []
        rsp = {}

        for i in range(1, 8):
            date = today - DT.timedelta(days=i)
            dayOfDate = date.day
            day = dayOfDate
            if dayOfDate < 10:
                day = '0' + str(dayOfDate)
            monthOfDate = date.month
            month = monthOfDate
            if monthOfDate < 10:
                month = '0' + str(monthOfDate)
            year = date.year
            conn.request("GET", "/history?country=Iran&day=" + str(year) + "-" + str(month) + "-" + str(day),
                         headers=headers)
            res = conn.getresponse()
            data = res.read()
            my_string = data.decode("utf-8")
            my_dict = ast.literal_eval(my_string)
            date = my_dict.get('parameters').get('day')
            new_case = my_dict.get('response')[0].get('cases').get('new')
            recovered = my_dict.get('response')[0].get('cases').get('recovered')
            deaths = my_dict.get('response')[0].get('deaths').get('new')
            rsp.update({date: {'new_case': int(new_case), 'recovered': recovered, 'deaths': int(deaths)}})
        return Response(rsp, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'flag': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
