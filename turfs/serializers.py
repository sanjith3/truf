from rest_framework import serializers
from .models import Turf, SportType, TurfImage, TurfVideo

class SportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportType
        fields = ['id', 'name', 'icon']

class TurfImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurfImage
        fields = ['id', 'image', 'is_cover']

class TurfVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TurfVideo
        fields = ['id', 'video']

class TurfListSerializer(serializers.ModelSerializer):
    sports = SportTypeSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()
    distance = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Turf
        fields = ['id', 'name', 'city', 'price_per_hour', 'sports', 'cover_image', 'distance']

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
    videos = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.phone_number', read_only=True)
    distance = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Turf
        fields = [
            'id', 'name', 'description', 'address', 'city', 
            'latitude', 'longitude', 'map_share_url',
            'price_per_hour', 'sports', 'amenities', 
            'images', 'videos', 'owner_name', 'distance'
        ]

    def get_videos(self, obj):
        request = self.context.get('request')
        return [
            request.build_absolute_uri(v.video.url) if request else v.video.url 
            for v in obj.videos.all()
        ]
