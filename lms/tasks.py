from datetime import timedelta
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from lms.models import Course, Subscription


@shared_task
def send_course_update_email(course_id: int) -> None:
    """
    Асинхронно отправляет письма всем подписчикам курса
    о том, что курс был обновлен.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return

    subscriptions = Subscription.objects.filter(course=course).select_related("user")
    recipient_list = [
        sub.user.email
        for sub in subscriptions
        if getattr(sub.user, "email", None)
    ]

    if not recipient_list:
        return

    subject = f"Обновление курса: {course.name}"
    message = (
        f'Курс "{course.name}" был обновлен.\n'
        f"Зайдите на платформу, чтобы посмотреть изменения."
    )

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )


@shared_task
def deactivate_inactive_users() -> None:
    """
    Блокирует (is_active = False) пользователей,
    у которых last_login был более месяца назад
    или отсутствует вовсе.
    """
    user = get_user_model()
    threshold = timezone.now() - timedelta(days=30)

    users_qs = user.objects.filter(
        is_active=True
    ).filter(
        Q(last_login__lt=threshold) | Q(last_login__isnull=True)
    )

    users_qs.update(is_active=False)

