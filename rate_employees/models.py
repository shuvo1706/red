from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.

class Employee(models.Model):
    empid = models.IntegerField()
    enothi_id = models.CharField(max_length=40)
    ename = models.CharField(max_length=40)
    eemail = models.EmailField(max_length=40)
    edesignation = models.CharField(max_length=40)
    edept = models.CharField(max_length=40)
    esection = models.CharField(max_length=40)
    edivision = models.CharField(max_length=40, default='null_div')
    edirectorate = models.CharField(max_length=40)
    counter = models.IntegerField(default=10)
    

    def setEname(self,ename):
        self.ename = ename

 
class Evaluation(models.Model):
    evaluateeid = models.IntegerField()
    evaluatorid = models.IntegerField()
    secDeptEv = models.IntegerField(default=None)
    commEv = models.IntegerField(default=None)
    behavEv = models.IntegerField(default=None)
    comid = models.IntegerField(default=None)


class Designation(models.Model):
    desigid = models.IntegerField()
    designame = models.CharField(max_length=40)
    desigshortname = models.CharField(max_length=40)

    
class Award(models.Model):
    awardid = models.AutoField(primary_key=True)
    created_date = models.DateField(auto_now_add=True)

    award_evaluatorid = models.IntegerField(default=0)
    award_evaluateeid = models.IntegerField(default=0)
    purposeid=models.CharField(max_length=40)
    description= models.CharField(max_length=400)
        


class Notification(models.Model):
    recipient = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sent_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification from {self.sender} to {self.recipient}'    
