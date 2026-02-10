from rest_framework import serializers

def validate_link(link_video):
    if "youtube.com" not in link_video:
        raise serializers.ValidationError("Нельзя оставлять ссылки на сторонние ресурсы")
