from django.urls import path
from rest_framework.routers import SimpleRouter
from lms.views import (CourseViewSet, LessonCreateApiView, LessonListApiView, LessonUpdateApiView, LessonRetrieveApiView, LessonDestroyApiView,
                       SubscriptionAPIView)
from lms.apps import LmsConfig

app_name = LmsConfig.name

router = SimpleRouter()
router.register("", CourseViewSet)

urlpatterns = [
    path("lessons/", LessonListApiView.as_view(), name='lesson-list'),
    path("lessons/<int:pk>", LessonRetrieveApiView.as_view(), name='lesson-detail'),
    path("lessons/create/", LessonCreateApiView.as_view(), name='lesson-create'),
    path("lessons/<int:pk>/delete/", LessonDestroyApiView.as_view(), name='lesson-delete'),
    path("lessons/<int:pk>/update", LessonUpdateApiView.as_view(), name='lesson-update'),
    path("subscription/", SubscriptionAPIView.as_view(), name='subscription')
]

urlpatterns += router.urls