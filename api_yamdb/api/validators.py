import re
from datetime import datetime as dt

from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_username(data):
    if data == 'me':
        raise ValidationError(
            'Имя "me" зарезервировано, используйте другое'
        )
    if not re.search(r'^[\w.@+-]+\Z', data):
        raise ValidationError(
            'В имени пользователя использованы недопустимые символы')
    return data


def validate_year(value):
    if value > dt.now().year or value < 0:
        raise serializers.ValidationError(
            'Год выхода не может превышать текущий'
            'год или быть отрицательным!')
    return value


def validate_genre(value):
    if not value:
        raise serializers.ValidationError(
            'Нельзя передавать пустой список жанров!')
    return value
