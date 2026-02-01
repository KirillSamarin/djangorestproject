from rest_framework.serializers import ModelSerializer, SerializerMethodField

from lms.models import Course, Lesson

class CourseSerializer(ModelSerializer):
    lessons = SerializerMethodField()

    def get_lessons(self, course):
        return [lesson.name for lesson in Lesson.objects.filter(course=course)]

    class Meta:
        model = Course
        fields = "__all__"

class LessonsCountSerializer(ModelSerializer):
    lessons_count = SerializerMethodField()
    course = CourseSerializer()

    def get_lessons_count(self, course):
        return Lesson.objects.filter(course=course).count()

    class Meta:
        model = Course
        fields = "__all__"

class LessonSerializer(ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = Lesson
        fields = "__all__"