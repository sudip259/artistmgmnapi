from django.db import models

# Create your models here.
from django.db import models

class CustomUser(models.Model):
    ROLES = (
        ('super_admin', 'Super Admin'),
        ('artist_manager', 'Artist Manager'),
        ('artist', 'Artist'),
    )

    GENDERS = (
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other'),
    )
    first_name = models.CharField(max_length=255,blank=True,null=True)
    last_name = models.CharField(max_length=255,blank=True,null=True)
    email = models.EmailField(unique=True,max_length=255)
    password = models.CharField(max_length=500)  
    role_type = models.CharField(choices=ROLES,blank=False,null=False,max_length=14) 
    phone = models.CharField(max_length=20,blank=True,null=True)
    gender = models.CharField(choices=GENDERS,blank=True,null=True,max_length=1)
    address = models.CharField(max_length=255, blank=True,null=True)
    dob = models.DateTimeField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

     
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    @property
    def is_authenticated(self):
        return True  # Return True for authenticated users

    @property
    def is_anonymous(self):
        return False  # Return False for non-anonymous users

    class Meta:
        db_table = 'custom_user'
    