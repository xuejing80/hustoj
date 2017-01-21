from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,
    PermissionsMixin, Group)


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, id_num, password=None):
        """
            Creates and saves a User with the given email, date of
            birth and password.
            """
        if not email:
            raise ValueError('邮箱为必填项目')
        if not 4 < len(id_num) < 16:
            raise ValueError('请调整用户名长度')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            id_num=id_num
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, username, id_num, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=email,
            password=password,
            username=username,
            id_num=id_num
        )
        user.is_admin = True
        user.is_superuser = True
        user.groups.add(Group.objects.get(name="老师"))
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='邮箱，用以登录',
        max_length=255,
        unique=True,
    )
    id_num = models.CharField(max_length=20, null=True, blank=True, verbose_name='用户名（工号/学号）')
    username = models.CharField(max_length=16, verbose_name='昵称（真实姓名）')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'id_num']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.username

    def __str__(self):  # __unicode__ on Python 2
        return self.username

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

