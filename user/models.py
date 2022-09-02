from django.db import models
from django.contrib.auth.models import User
import datetime



class NewUser(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    phone = models.IntegerField(max_length=200, null=True)
    email = models.EmailField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.name)





class Requisition(models.Model):
    STATUS=(
       
        ('Processing', 'Processing'),
        ('Delivered', 'Delivered'),
    )

    submitted_by = models.ForeignKey(NewUser, null=True, on_delete=models.CASCADE, related_name='to_be_sent_by', blank=True )

    send_to = models.ManyToManyField(NewUser)



    title = models.CharField(max_length=200, null=True, blank=True)

    date = models.DateField(auto_now_add=True, null= True, blank= True)
    date_of_delivery = models.DateField(default=datetime.date.today(), null=True, blank=True)

    file = models.FileField(upload_to='user/files/')


    status = models.CharField(max_length=200, null=True, blank=True, choices=STATUS)

    def __str__(self):
        return self.title