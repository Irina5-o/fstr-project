from rest_framework import serializers
from .models import PerevalUser, PerevalCoords, PerevalAdded, PerevalImage

class PerevalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerevalUser
        fields = ['email', 'fam', 'name', 'otc', 'phone']

    def create(self, validated_data):
        user, created = PerevalUser.objects.get_or_create(
            email=validated_data['email'],
            defaults=validated_data
        )
        return user

class PerevalCoordsSerializer(serializers.ModelSerializer):
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
            'id', 'beauty_title', 'title', 'other_titles', 'connect', 'add_time',
            'user', 'coords', 'level_winter', 'level_summer', 'level_autumn', 'level_spring',
            'status', 'images'
        ]
        read_only_fields = ['id', 'status', 'add_time']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        coords_data = validated_data.pop('coords')
        images_data = validated_data.pop('images')

        user_serializer = PerevalUserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        coords = PerevalCoords.objects.create(**coords_data)

        pereval = PerevalAdded.objects.create(
            user=user,
            coords=coords,
            **validated_data
        )

        for image_data in images_data:
            PerevalImage.objects.create(pereval=pereval, **image_data)

        return pereval
