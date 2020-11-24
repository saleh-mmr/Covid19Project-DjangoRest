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

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Symptom(models.Model):
    symptom_name = models.CharField(max_length=30)
    weight = models.IntegerField(default=0)

    def __str__(self):
        return self.symptom_name


class PatientSymptom(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)


class RelatedPeople(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=30)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class PatientStatus(models.Model):
    patient_status_name = models.CharField(max_length=30)

    def __str__(self):
        return self.patient_status_name


class IllnessStatus(models.Model):
    illness_status_name = models.CharField(max_length=30)

    def __str__(self):
        return self.illness_status_name


class Status(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    patient_status = models.ForeignKey(PatientStatus, on_delete=models.CASCADE)
    illness_status = models.ForeignKey(IllnessStatus, on_delete=models.CASCADE)
    status_date = models.DateField(blank=True, null=True)
