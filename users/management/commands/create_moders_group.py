from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'create group of moderators'

    def handle(self, *args, **options):
        moders_group = Group.objects.create(name="Moders")
        moders_group.permissions.clear()

        change_course_permission = Permission.objects.get(codename='change_course')
        view_course_permission = Permission.objects.get(codename='view_course')
        change_lesson_permission = Permission.objects.get(codename='change_lesson')
        view_lesson_permission = Permission.objects.get(codename='view_lesson')

        moders_group.permissions.add(change_course_permission, view_course_permission,
                                     change_lesson_permission, view_lesson_permission)
        moders_group.save()