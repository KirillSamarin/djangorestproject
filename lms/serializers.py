from rest_framework.serializers import ModelSerializer, SerializerMethodField
from lms.models import Course, Lesson, Subscription

class CourseSerializer(ModelSerializer):
    lessons = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    def get_lessons(self, course):
        return [lesson.name for lesson in Lesson.objects.filter(course=course)]

    def get_is_subscribed(self, course):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=course
            ).exists()
        return False

    class Meta:
        model = Course
        fields = "__all__"

class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"



class LessonsCountSerializer(ModelSerializer):
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(
        read_only=True,
        required=False,
        source="lesson_set",
    )


    def get_lessons_count(self, obj):
        if obj:
            return obj.lesson_set.count()


    class Meta:
        model = Course
        fields = (
            "name",
            "description",
            "thumbnail",
            "lessons_count",
            "lessons",
        )