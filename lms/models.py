from django.db import models
from lms.validators import validate_link

class Course(models.Model):

    name = models.CharField(max_length=120, verbose_name="название курса")
    thumbnail = models.ImageField(upload_to="photos/", null=True, blank=True, verbose_name="превью")
    description = models.TextField(verbose_name='описание', null=True, blank=True)
    owner = models.ForeignKey("users.User", verbose_name='владелец', on_delete=models.CASCADE, null=True)

class Lesson(models.Model):

    name = models.CharField(max_length=120, verbose_name="название урока")
    description = models.TextField(verbose_name='описание')
    thumbnail = models.ImageField(upload_to="photos/", null=True, blank=True, verbose_name="превью")
    link_video = models.TextField(verbose_name="ссылка на видео", validators=[validate_link])
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="курс")
    owner = models.ForeignKey("users.User", verbose_name='владелец', on_delete=models.CASCADE, null=True)

class Subscription(models.Model):

    user = models.ForeignKey("users.User", verbose_name='владелец', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="курс")
