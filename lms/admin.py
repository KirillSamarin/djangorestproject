from django.contrib import admin
from .models import Course, Lesson

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name", "description"]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "course"]
    search_fields = ["name", "description", "course"]
