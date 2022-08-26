from django.db import models
from user.models import User
# Create your models here.


# Affiliate balance
class AffiliateBalance(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, db_index=True
        )
    balance = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.user


# Afiliate profit
class AffiliateProfit(models.Model):
    user = models.ForeignKey(
            User, on_delete=models.DO_NOTHING,
            db_index=True, related_name='affiliate'
        )
    customer = models.ForeignKey(
            User, on_delete=models.DO_NOTHING, related_name='customer'
        )
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.user
