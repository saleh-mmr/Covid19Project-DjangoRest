from datetime import date
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import *


class MyUser(AbstractUser):
    pass


class Patient(models.Model):
    user_site = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    national_code = models.CharField(max_length=15)
    birth_date = models.DateField(default=date.today)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Symptom(models.Model):
    symptom_title = models.CharField(max_length=100, null=True)
    weight = models.IntegerField(default=1)

    def __str__(self):
        return self.symptom_title


class PatientSymptom(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)


class PatientStatus(models.Model):
    patient_status_title = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.patient_status_title


class DiseaseStatus(models.Model):
    disease_status_title = models.CharField(max_length=100, null=True)
    probable = models.IntegerField(default=1)
    is_System = models.BooleanField(default=False)

    def __str__(self):
        return self.disease_status_title + " " + str(self.is_System)


class Connections(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, null=True)
    email = models.EmailField(max_length=30, null=True)


class Status(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    patient_status = models.ForeignKey(PatientStatus, on_delete=models.CASCADE, null=True)
    disease_status = models.ForeignKey(DiseaseStatus, on_delete=models.CASCADE)
    status_date = models.DateField(default=date.today)
