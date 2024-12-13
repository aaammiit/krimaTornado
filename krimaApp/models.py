from django.db import models
from django.contrib.auth.models import User
from django import forms

# Create your models here.
    
class My_Upload_file(models.Model):
    file=models.FileField()
    count=models.IntegerField(null=True)
    o_len=models.IntegerField(null=True)
    from_date=models.CharField(max_length=100,null=True)
    to_date=models.CharField(max_length=100,null=True)
    status=models.BooleanField(default=False)
    date=models.DateField(auto_now=True)
    def __str__(self):
        return self.file.name

    
class Qc_user(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)   
    def __str__(self):
        u=self.user.first_name+'-'+self.user.last_name
        return u
    
class my_Qc_data(models.Model):
    my_file=models.ForeignKey(My_Upload_file,on_delete=models.CASCADE)
    qc_file=models.FileField(upload_to='qc')
    from_date=models.CharField(max_length=100,null=True)
    to_date=models.CharField(max_length=100,null=True)
    user=models.ForeignKey(Qc_user,on_delete=models.CASCADE)
    start=models.IntegerField(default=0)
    date=models.DateField(auto_now=True)
    end=models.IntegerField()
    status=models.BooleanField(default=False)
    
    

class qc_Form(forms.ModelForm):
    class Meta:
        model=my_Qc_data
        fields=['user']



class ED_User(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)  
    def __str__(self):
        u=self.user.first_name+'-'+self.user.last_name
        return u

class Editor_push(models.Model):
    Editior=models.ForeignKey(ED_User,on_delete=models.CASCADE)
    qc_data=models.ForeignKey(my_Qc_data,on_delete=models.CASCADE)
    qc_user=models.ForeignKey(Qc_user,on_delete=models.CASCADE)
    rec_length=models.IntegerField()
    date=models.DateField(auto_now=True)
    sta=models.BooleanField(default=False)
    def __str__(self):
        return self.qc_data.qc_file.name
    

class pushForm(forms.ModelForm):
    class Meta:
        model=Editor_push
        fields=['Editior']


class Final_data_PM(models.Model):

    Editior=models.ForeignKey(ED_User,on_delete=models.CASCADE)
    Edited_file=models.ForeignKey(Editor_push,on_delete=models.CASCADE)
    date=models.DateField(auto_now=True)    
    status=models.BooleanField(default=False)

class Doubt(models.Model):
    file=models.ForeignKey(my_Qc_data,on_delete=models.CASCADE)
    user=models.ForeignKey(Qc_user,on_delete=models.CASCADE)
    Sr_no=models.CharField(max_length=100)
    msg=models.CharField(max_length=2000)