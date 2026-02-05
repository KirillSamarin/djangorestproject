from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="email")
    avatar = models.ImageField(upload_to="photos/", null=True, blank=True, verbose_name="аватар")
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="номер телефона")
    country = models.CharField(max_length=60, null=True, blank=True, verbose_name="страна")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email}, {self.first_name}, {self.last_name}"

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="пользователь")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="дата платежа")
    paid_course = models.ForeignKey('lms.Course', on_delete=models.CASCADE, verbose_name="оплаченный курс", null=True, blank=True)
    paid_lesson = models.ForeignKey('lms.Lesson', on_delete=models.CASCADE, verbose_name="оплаченный урок", null=True, blank=True)
    payment_sum = models.IntegerField(verbose_name="сумма оплаты")
    payment_method = models.TextField(verbose_name="способ оплаты")