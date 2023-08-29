import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artistmgmnapi.settings")
django.setup()

from django.contrib.auth.hashers import make_password

password = "p@ssw0rd123A"
hashed_password = make_password(password)

print(hashed_password)
