from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PaypalTransaction(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True, db_index=True)
    payment_transfer_arrow = models.CharField(max_length=10, default='',null=True)  
    payment_transfer_arrow= models.BooleanField(default=False,null=True)
    payment_id= models.CharField(max_length=255, default='', null=True)
    payment_hash= models.CharField(max_length=255, default='',null=True)
    payment_status= models.BooleanField(default=False,null=True)
    payment_completion_time= models.DateTimeField('date created',blank=True)
    def __str__(self):
        return self.user + '-' + self.payment_transfer_arrow
