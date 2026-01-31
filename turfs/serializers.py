from rest_framework import serializers
from .models import Turf, SportType, TurfImage

class SportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportType
        fields = ['id', 'name', 'icon']

class TurfImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurfImage
        fields = ['id', 'image', 'is_cover']

class TurfListSerializer(serializers.ModelSerializer):
    sports = SportTypeSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Turf
        fields = ['id', 'name', 'city', 'price_per_hour', 'sports', 'cover_image']

    def get_cover_image(self, obj):
        cover = obj.images.filter(is_cover=True).first() or obj.images.first()
        if cover:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(cover.image.url)
            return cover.image.url
        return None

class TurfDetailSerializer(serializers.ModelSerializer):
    sports = SportTypeSerializer(many=True, read_only=True)
    images = TurfImageSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    class Meta:
        model = Turf
        fields = [
            'id', 'name', 'description', 'address', 'city', 
            'latitude', 'longitude', 'price_per_hour', 
            'sports', 'amenities', 'images', 'owner_name'
        ]
