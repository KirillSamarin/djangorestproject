from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from lms.models import Course, Lesson, Subscription
from users.models import User


class LessonCRUDTests(APITestCase):
    """Тестирование CRUD операций для уроков"""

    def setUp(self):
        """Создание тестовых данных"""
        self.user = User.objects.create_user(
            email='owner@example.com',
            username='name',
            password='testpass'
        )

        self.moderator = User.objects.create_user(
            email='moderator@example.com',
            username='name1',
            password='testpass',
            is_staff=True
        )

        self.other = User.objects.create_user(
            email='other@example.com',
            username='name2',
            password='testpass'
        )

        self.course = Course.objects.create(
            name='Тестовый курс',
            owner=self.user
        )

        self.lesson = Lesson.objects.create(
            name='Тестовый урок',
            description='Описание',
            link_video='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.user
        )

        self.lesson_list_url = 'lms:lesson-list'
        self.lesson_detail_url = 'lms:lesson-detail'
        self.lesson_create_url = 'lms:lesson-create'
        self.lesson_update_url = 'lms:lesson-update'
        self.lesson_delete_url = 'lms:lesson-delete'

    # Тесты списка уроков
    def test_list_lessons_auth(self):
        """Список уроков для аутентифицированного"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse(self.lesson_list_url))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


    def test_retrieve_lesson(self):
        """Получение урока владельцем и модератором"""
        test_cases = [
            (self.user, status.HTTP_200_OK),
            (self.moderator, status.HTTP_200_OK),
            (self.other, status.HTTP_403_FORBIDDEN),
        ]

        for user, expected_status in test_cases:
            self.client.force_authenticate(user=user)
            response = self.client.get(
                reverse(self.lesson_detail_url, args=[self.lesson.pk])
            )
            self.assertEqual(response.status_code, expected_status)

    # Тест создания урока
    def test_create_lesson(self):
        """Создание урока пользователем и модератором"""
        data = {
            'name': 'Новый урок',
            'description': 'Описание',
            'link_video': 'https://www.youtube.com/watch?v=new',
            'course': self.course.pk
        }

        test_cases = [
            (self.user, status.HTTP_201_CREATED),  # Обычный пользователь
            (self.moderator, status.HTTP_403_FORBIDDEN),  # Модератор не может создавать
        ]

        for user, expected_status in test_cases:
            self.client.force_authenticate(user=user)
            response = self.client.post(reverse(self.lesson_create_url), data)
            self.assertEqual(response.status_code, expected_status)

    # Тест обновления урока
    def test_update_lesson(self):
        """Обновление урока разными пользователями"""
        data = {'name': 'Обновлено',
                'description': 'Обновлено',
                'link_video': 'https://www.youtube.com/watch?v=updated',
                'course': self.course.pk}

        test_cases = [
            (self.user, status.HTTP_200_OK),
            (self.moderator, status.HTTP_403_FORBIDDEN),
            (self.other, status.HTTP_403_FORBIDDEN),
        ]

        for user, expected_status in test_cases:
            self.client.force_authenticate(user=user)
            response = self.client.put(
                reverse(self.lesson_update_url, args=[self.lesson.pk]),
                data
            )
            self.assertEqual(response.status_code, expected_status)

    # Тест удаления урока
    def test_delete_lesson(self):
        """Удаление урока разными пользователями"""
        test_cases = [
            (self.user, status.HTTP_204_NO_CONTENT),
            (self.moderator, status.HTTP_403_FORBIDDEN),
            (self.other, status.HTTP_403_FORBIDDEN),
        ]

        for user, expected_status in test_cases:
            # Создаем новый урок для каждого теста
            lesson = Lesson.objects.create(
                name=f'Урок для удаления {user.email}',
                description='...',
                link_video='https://www.youtube.com/watch?v=test',
                course=self.course,
                owner=self.user
            )

            self.client.force_authenticate(user=user)
            response = self.client.delete(
                reverse(self.lesson_delete_url, args=[lesson.pk])
            )
            self.assertEqual(response.status_code, expected_status)


class SubscriptionTests(APITestCase):
    """Тестирование подписок на курс"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='kirill',
            password='testpass'
        )

        self.course = Course.objects.create(
            name='Курс для подписки',
            owner=self.user
        )

        self.subscription_url = 'lms:subscription'  # Замените на ваш URL name

    def test_subscribe_unsubscribe(self):
        """Тест добавления и удаления подписки"""
        self.client.force_authenticate(user=self.user)
        data = {'course_id': self.course.pk}

        # Подписываемся
        response = self.client.post(reverse(self.subscription_url), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

        # Отписываемся
        response = self.client.post(reverse(self.subscription_url), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )



