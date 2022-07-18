from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class UserProfile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, db_index=True)
    registration= models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.user.username







class AffiliateBalance(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True, db_index=True)
    balance= models.DecimalField(max_digits=6, decimal_places=2)
    def __str__(self):
        return self.user

class AffiliateProfit(models.Model):
    user= models.ForeignKey(User,on_delete=models.DO_NOTHING, 
            db_index=True, related_name='affiliate')
    customer= models.ForeignKey(User,on_delete=models.DO_NOTHING, related_name='customer')
    amount= models.DecimalField(max_digits=6, decimal_places=2)
    def __str__(self):
        return self.user
