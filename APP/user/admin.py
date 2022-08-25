from django.contrib import admin
from user.models import User, UserProfile, AffiliateBalance, AffiliateProfit


# Register your models here.
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(AffiliateBalance)
admin.site.register(AffiliateProfit)
