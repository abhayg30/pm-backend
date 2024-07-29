from django.db import models
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from powerpuff import settings
from django.db.models.signals import post_save, pre_save
from django.core.mail import send_mail
from django.dispatch import receiver
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, user_type, status, password=None, password2=None):
        """
        Creates and saves a User with the given email, name and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email), user_type=user_type, status=status
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, user_type, status, password=None):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(
            email, password=password, user_type=user_type, status=status
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    user_type = models.IntegerField()
    status = models.IntegerField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["user_type", "status"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


# Create your models here.

DATETIME_FORMAT = "%d-%m-%Y"


class UserDetails(models.Model):
    FULL_WORKING_RIGHTS = "FULL"
    PARTIAL_WORKING_RIGHTS = "PARTIAL"
    NO_WORKING_RIGHTS = "NO"
    WORKING_RIGHTS_CHOICES = [
        (FULL_WORKING_RIGHTS, "FULL"),
        (PARTIAL_WORKING_RIGHTS, "PARTIAL"),
        (NO_WORKING_RIGHTS, "NO"),
    ]

    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    GENDER_CHOICE = [(MALE, "Male"), (FEMALE, "Female"), (OTHER, "Other")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    city = models.CharField(max_length=255)  # can be dropdown -- will look into this
    zip_code = models.IntegerField()
    gender = models.CharField(max_length=50, null=True, choices=GENDER_CHOICE)
    working_rights = models.CharField(max_length=50, choices=WORKING_RIGHTS_CHOICES)

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "date_of_birth",
        "city",
        "zip_code",
        "working_rights",
    ]


@receiver(pre_save, sender=User)
def pre_update_model(sender, **kwargs):
    # check if the updated fields exist and if you're not creating a new object
    if not kwargs["update_fields"] and kwargs["instance"].id:
        # Save it so it can be used in post_save
        kwargs["instance"].old = User.objects.get(id=kwargs["instance"].id)


@receiver(post_save, sender=User)
def update_model(sender, created, **kwargs):
    if not created:
        instance = kwargs["instance"]
        # Add updated_fields, from old instance, so the method logic remains unchanged
        if not kwargs["update_fields"] and hasattr(instance, "old"):
            kwargs["update_fields"] = []
            if kwargs["instance"].status != kwargs["instance"].old.status:
                if (
                    kwargs["instance"].old.status == 0
                    and kwargs["instance"].status == 1
                ):
                    kwargs["update_fields"].append("status")

        if "status" in kwargs["update_fields"]:
            send_mail(
                "Your ProjectMe application has been approved",
                "You can now Login into your account",
                settings.EMAIL_HOST_USER,
                [kwargs["instance"].email],
                fail_silently=False,
            )
