from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, get_object_or_404
from lms.serializers import CourseSerializer, LessonSerializer, LessonsCountSerializer
from lms.models import Lesson
from lms.models import Course, Subscription
from users.permissions import IsOwner, IsNotModer, IsOwnerOrModer
from lms.paginators import PagePagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class SubscriptionAPIView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['course_id'],
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID курса'),
            },
        ),
        responses={
            200: openapi.Response(
                description='Результат подписки',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def post(self, request):
        user = request.user
        course_id = request.data.get('course_id')
        course_item = get_object_or_404(Course, pk=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = 'подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'подписка добавлена'

        return Response({"message": message})

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Получение списка курсов",
    tags=['Courses'],
    manual_parameters=[
        openapi.Parameter(
            'page',
            openapi.IN_QUERY,
            description="Номер страницы",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'page_size',
            openapi.IN_QUERY,
            description="Количество элементов на странице",
            type=openapi.TYPE_INTEGER
        ),
    ]
))
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Получение списка курсов",
    tags=['Courses']
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="Создание нового курса",
    tags=['Courses']
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_description="Получение детальной информации о курсе",
    tags=['Courses']
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_description="Полное обновление курса",
    tags=['Courses']
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_description="Частичное обновление курса",
    tags=['Courses']
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_description="Удаление курса",
    tags=['Courses']
))
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = PagePagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LessonsCountSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        if self.action in ["create", "destroy"]:
            self.permission_classes(IsNotModer, IsAuthenticated)
        elif self.action in ["update", "retrieve"]:
            self.permission_classes(IsOwnerOrModer)
        return super().get_permissions()

@method_decorator(name='post', decorator=swagger_auto_schema(
    operation_description="Создание нового урока",
    tags=['Lessons']
))
class LessonCreateApiView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsNotModer, IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListApiView(ListAPIView):
    pagination_class = PagePagination
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModer]


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModer]


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwner]


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwner]

