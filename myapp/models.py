from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import *


class MyUser(AbstractUser):
    pass


class Symptom(models.Model):
    title = models.CharField(max_length=100, null=True)
    weight = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.title


class PatientStatus(models.Model):
    title = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title


class DiseaseStatus(models.Model):
    title = models.CharField(max_length=100, null=True)
    is_System = models.BooleanField(default=False)

    def __str__(self):
        return self.title + " " + str(self.is_System)


class Patient(models.Model):
    user_site = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=100, null=True)
    lastName = models.CharField(max_length=100, null=True)
    nationalCode = models.CharField(max_length=100, null=True)
    phoneNumber = models.CharField(max_length=100, null=True)
    symptoms = models.ManyToManyField(Symptom)
    statuses = models.ManyToManyField(PatientStatus)
    diseases = models.ManyToManyField(DiseaseStatus)

    def __str__(self):
        return self.firstName + " " + self.lastName


class Connections(models.Model):
    patient = models.ForeignKey(Patient, null=True, on_delete=models.SET_NULL)
    phoneNumber = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
