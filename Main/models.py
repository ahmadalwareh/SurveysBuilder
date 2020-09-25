# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from Main.managers import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from OnionOpinion import settings


class Roles(models.Model):
    r_name = models.CharField(max_length=100)

    def __str__(self):
        return self.r_name

    class Meta:
        managed = True
        db_table = 'Roles'


class Permissions(models.Model):
    p_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    # relation = models.ManyToManyField(Roles, through='RolesPermissions')

    def __str__(self):
        return self.p_name

    class Meta:
        managed = True
        db_table = 'Permissions'


class RolesPermissions(models.Model):
    role = models.ForeignKey(Roles, models.DO_NOTHING)
    permission = models.ForeignKey(Permissions, models.DO_NOTHING)

    def __str__(self):
        return str(self.role) + ": " + str(self.permission)

    class Meta:
        managed = True
        db_table = 'Roles_Permissions'


class Countries(models.Model):
    c_name = models.CharField(max_length=50)

    def __str__(self):
        return self.c_name

    class Meta:
        managed = True
        db_table = 'Countries'


class Users(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    mobile = models.CharField(max_length=14, blank=True, null=True)
    GENDER_MALE = 'Male'
    GENDER_FEMALE = 'Female'
    GENDER_CHOICES = [(GENDER_MALE, 'Male'), (GENDER_FEMALE, 'Female')]
    gender = models.CharField(max_length=10, blank=True, null=True, choices=GENDER_CHOICES)
    birth_date = models.DateField(default='1970-01-01')
    image_path = models.ImageField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(Countries, models.DO_NOTHING, default='1')
    role = models.ForeignKey(Roles, models.DO_NOTHING, default='4')

    def __str__(self):
        return self.email

    class Meta:
        managed = True
        db_table = 'Users'


class Messages(models.Model):
    sender_email = models.EmailField(max_length=100)
    sender_name = models.CharField(max_length=100)
    send_date = models.DateTimeField(default=timezone.now)
    msg_subject = models.CharField(max_length=100)
    msg_text = models.CharField(max_length=512)
    msg_status = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING)

    def __str__(self):
        return self.msg_subject

    class Meta:
        managed = True
        db_table = 'Messages'


class Surveys(models.Model):
    title = models.CharField(max_length=100)
    s_name = models.CharField(max_length=100)
    creation_date = models.DateTimeField(default=timezone.now)
    s_status = models.CharField(max_length=20)
    is_private = models.BooleanField()
    is_encrypted = models.BooleanField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING)

    def __str__(self):
        return self.s_name

    class Meta:
        managed = True
        db_table = 'Surveys'


class Questions(models.Model):
    question_body = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20)
    survey = models.ForeignKey('Surveys', models.DO_NOTHING)

    def __str__(self):
        return self.question_type

    class Meta:
        managed = True
        db_table = 'Questions'


class Answers(models.Model):
    answer = models.CharField(max_length=512)
    answer_text = models.CharField(max_length=512, blank=True, null=True)
    question = models.ForeignKey('Questions', models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'Answers'


class UsersAnswers(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING)
    answer = models.ForeignKey(Answers, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'Users_Answers'
