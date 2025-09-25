from rest_framework import serializers
from .models import PerevalUser, PerevalCoords, PerevalAdded, PerevalImage


class PerevalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerevalUser
        fields = ['email', 'fam', 'name', 'otc', 'phone']

    def create(self, validated_data):
        # Пытаемся найти пользователя по email
        user, created = PerevalUser.objects.get_or_create(
            email=validated_data['email'],
            defaults={
                'fam': validated_data.get('fam', ''),
                'name': validated_data.get('name', ''),
                'otc': validated_data.get('otc', ''),
                'phone': validated_data.get('phone', ''),
            }
        )
        return user


class PerevalCoordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerevalCoords
        fields = ['latitude', 'longitude', 'height']


class PerevalCoordsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerevalCoords
        fields = ['latitude', 'longitude', 'height']


class PerevalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerevalImage
        fields = ['title', 'image_url']


class PerevalAddedSerializer(serializers.ModelSerializer):
    user = PerevalUserSerializer()
    coords = PerevalCoordsSerializer()
    images = PerevalImageSerializer(many=True)

    class Meta:
        model = PerevalAdded
        fields = [
            'beauty_title', 'title', 'other_titles', 'connect', 'add_time',
            'user', 'coords', 'level_winter', 'level_summer',
            'level_autumn', 'level_spring', 'images'
        ]

    def create(self, validated_data):
        # Извлекаем вложенные данные
        user_data = validated_data.pop('user')
        coords_data = validated_data.pop('coords')
        images_data = validated_data.pop('images')

        # Создаём или находим пользователя
        user_serializer = PerevalUserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        # Создаем координаты
        coords = PerevalCoords.objects.create(**coords_data)

        # Создаем сам перевал
        pereval = PerevalAdded.objects.create(user=user, coords=coords, **validated_data)

        # Создаем изображения и связываем их с перевалом
        for image_data in images_data:
            PerevalImage.objects.create(pereval=pereval, **image_data)

        return pereval


class PerevalInfoSerializer(serializers.ModelSerializer):
    user = PerevalUserSerializer()
    coords = PerevalCoordsSerializer()
    images = PerevalImageSerializer(many=True)

    class Meta:
        model = PerevalAdded
        fields = [
            'id', 'beauty_title', 'title', 'other_titles', 'connect', 'add_time',
            'status', 'user', 'coords', 'level_winter', 'level_summer',
            'level_autumn', 'level_spring', 'images'
        ]
        read_only_fields = ['id', 'add_time', 'status']


class PerevalUpdateSerializer(serializers.ModelSerializer):
    coords = PerevalCoordsUpdateSerializer(required=False)
    images = PerevalImageSerializer(many=True, required=False)

    class Meta:
        model = PerevalAdded
        fields = [
            'beauty_title', 'title', 'other_titles', 'connect',
            'level_winter', 'level_summer', 'level_autumn', 'level_spring',
            'coords', 'images'
        ]

    def update(self, instance, validated_data):
        # Извлекаем вложенные данные
        coords_data = validated_data.pop('coords', None)
        images_data = validated_data.pop('images', None)

        # Обновление простых полей
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновление координат
        if coords_data:
            coords_serializer = PerevalCoordsUpdateSerializer(instance.coords, data=coords_data, partial=True)
            if coords_serializer.is_valid(raise_exception=True):
                coords_serializer.save()

        # Обновление изображений: удалить старые и добавить новые
        if images_data:
            instance.images.all().delete()
            for img in images_data:
                PerevalImage.objects.create(pereval=instance, **img)

        return instance

    def to_representation(self, instance):
        """Добавляем поле level в ответ для совместимости"""
        data = super().to_representation(instance)
        data['level'] = {
            'winter': instance.level_winter or '',
            'summer': instance.level_summer or '',
            'autumn': instance.level_autumn or '',
            'spring': instance.level_spring or ''
        }
        return data