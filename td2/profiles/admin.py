"""admin imports from profiles app"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

#from .forms import SignUpForm, UserUpdateForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    #Fieldsets is a tuple, and thus immutable so we create  a new one with our custom values wedged inside
    #a=a[:3]+(4,)+a[3:] <- Format

    new_admin_order =  (
        'ThunderDome',
        {
            'fields': ('bio', 'public_profile', 'highest_access', 'timezone', 'slug' , 'wins', 'hms', 'dms', 'losses')
        }
    )

    fieldsets = UserAdmin.fieldsets[:2] + (new_admin_order,) +  UserAdmin.fieldsets[2:]

# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
