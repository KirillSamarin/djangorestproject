from django.urls import path
from rest_framework.routers import SimpleRouter
from lms.views import CourseViewSet, LessonCreateApiView, LessonListApiView, LessonUpdateApiView, LessonRetrieveApiView, LessonDestroyApiView
from lms.apps import LmsConfig

app_name = LmsConfig.name

router = SimpleRouter()
router.register("", CourseViewSet)

urlpatterns = [
    path("lessons/", LessonListApiView.as_view()),
    path("lessons/<int:pk>", LessonRetrieveApiView.as_view()),
    path("lessons/create/", LessonCreateApiView.as_view()),
    path("lessons/<int:pk>/delete/", LessonDestroyApiView.as_view()),
    path("lessons/<int:pk>/update", LessonUpdateApiView.as_view())
]

urlpatterns += router.urls