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
        symptoms = data['symptoms']
        try:
            is_Available = models.Patient.objects.filter(nationalCode=national_code)
            if not is_Available:
                current_patient = models.Patient.objects.create(user_site=current_user, firstName=first_name,
                                                                lastName=last_name, phoneNumber=phone_number,
                                                                nationalCode=national_code)
                sum = 0
                for i in symptoms:
                    current_symptom = models.Symptom.objects.get(title=i)
                    current_patient.symptoms.add(current_symptom)
                    sum = sum + int(current_symptom.weight)
                if sum > 10:
                    current_DiseaseStatus = models.DiseaseStatus.objects.get(title="قطعی کرونا", is_System=True)
                    current_patient.diseases.add(current_DiseaseStatus)
                    rsp = {'illness': "قطعی کرونا",
                           'patientid': current_patient.id,
                           'flag': True
                           }
                elif sum > 5:
                    current_DiseaseStatus = models.DiseaseStatus.objects.get(title="مشکوک به کرونا", is_System=True)
                    current_patient.diseases.add(current_DiseaseStatus)
                    rsp = {'illness': "مشکوک به کرونا",
                           'patientid': current_patient.id,
                           'flag': True
                           }
                else:
                    current_DiseaseStatus = models.DiseaseStatus.objects.get(title="آنفولانزا", is_System= True)
                    current_patient.diseases.add(current_DiseaseStatus)
                    rsp = {'illness': "آنفولانزا",
                           'patientid': current_patient.id,
                           'flag': True
                           }

                return Response(rsp, status=status.HTTP_200_OK)

            else:
                Current_patient = models.Patient.objects.get(nationalCode=national_code)
                Current_patient.firstName = first_name
                Current_patient.lastName = last_name
                Current_patient.phoneNumber = phone_number
                last_disease = Current_patient.diseases.last()
                Current_patient.save()
                rsp = {'illness': last_disease,
                       'patientid': Current_patient.id,
                       'flag': True}
                return Response(rsp, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'Error': "Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'PUT':
        data = request.data
        patient_id = data["patientid"]
        disease_status = data["DiseaseStatus"]
        patient_status = data["PatientStatus"]
        current_patient = models.Patient.objects.get(id=patient_id)
        disease = models.DiseaseStatus.objects.get(title=disease_status , is_System= False)
        current_patient.diseases.add(disease)
        current_status = models.PatientStatus.objects.get(title=patient_status)
        current_patient.statuses.add(current_status)
        return Response({'Message': "Done"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_user_reports(request):
    a = models.Patient.objects.filter(user_site=request.user)
    rsp = {}
    s = 0
    for i in a:
        rsp.update({'val'+str(s): {'id': i.id, 'firstname': i.firstName, 'lastname': i.lastName, 'phonenumber': i.phoneNumber, 'nationalcode': i.nationalCode, 'lastdisease': i.diseases.last()}})
        s = s+1
    print(rsp)
    return Response(a.values(), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_report(request):
    data = request.data
    patientid = data['patientid']
    # firstName = data['firstName']
    # lastName = data['lastName']
    # nationalCode = data['nationalCode']
    # phoneNumber = data['phoneNumber']
    diseasestatus = data['diseasestatus']
    patientstatus = data['patientstatus']
    symptoms = data['symptoms']
    current_patient = models.Patient.objects.get(id=patientid)
    a = current_patient.diseases.values()
    for i in a:
        if i['is_System']== True:
            current_disease_system = i

    if symptoms:
        models.Patient.objects.get(id=patientid).symptoms.clear()
        sum = 0
        for i in symptoms:
            current_symptom = models.Symptom.objects.get(title=i)
            sum = sum + int(current_symptom.weight)
            current_patient.symptoms.add(current_symptom)
        if sum > 10:
            current_disease_system = models.DiseaseStatus.objects.get(title="قطعی کرونا", is_System=True)
            current_patient.diseases.add(current_disease_system)
        elif sum > 5:
            current_disease_system = models.DiseaseStatus.objects.get(title="مشکوک به کرونا", is_System=True)
            current_patient.diseases.add(current_disease_system)
        else:
            current_disease_system = models.DiseaseStatus.objects.get(title="آنفولانزا", is_System=True)
            current_patient.diseases.add(current_disease_system)

    # current_patient.firstName = firstName
    # current_patient.lastName = lastName
    # current_patient.nationalCode = nationalCode
    # current_patient.phoneNumber = phoneNumber
    current_disease_user = models.DiseaseStatus.objects.get(title=diseasestatus, is_System=False)
    current_status = models.PatientStatus.objects.get(title=patientstatus)
    current_patient.diseases.create()
    current_patient.statuses.add(current_status)
    current_patient.save()
    rsp = {
        'message': 'Done',
        'disease': current_patient.diseases.last().title,
        'patientstatus': current_patient.statuses.last().title,
        'system_disease': current_disease_system.title
    }
    print(current_patient.diseases.values())
    print(current_patient.diseases.last())
    return Response(rsp, status=status.HTTP_200_OK)
