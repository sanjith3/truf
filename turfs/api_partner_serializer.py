from rest_framework import serializers
from .models import Turf, TurfImage, TurfVideo, SportType
from django.db import transaction

from core.utils.geo import GoogleMapsParser

class PartnerRegistrationSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    video = serializers.FileField(write_only=True, required=False)
    sports_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    class Meta:
        model = Turf
        fields = [
            'name', 'description', 'address', 'city', 
            'latitude', 'longitude', 'map_share_url',
            'price_per_hour', 'amenities', 'sports_ids', 
            'images', 'video'
        ]
        read_only_fields = ['latitude', 'longitude']

    def validate(self, attrs):
        map_url = attrs.get('map_share_url')
        if not map_url:
            raise serializers.ValidationError({"map_share_url": "Google Maps link is required."})
        
        if not GoogleMapsParser.is_valid_link(map_url):
            raise serializers.ValidationError({"map_share_url": "Invalid Google Maps link format."})
        
        lat, lon = GoogleMapsParser.extract_lat_lon(map_url)
        if lat is None or lon is None:
            raise serializers.ValidationError({"map_share_url": "Could not extract location from this link. Drop a pin before sharing."})
        
        # Inject extracted coordinates into the data
        attrs['latitude'] = lat
        attrs['longitude'] = lon
        return attrs

    def validate_video(self, value):
        if value:
            if value.size > 20 * 1024 * 1024:
                raise serializers.ValidationError("Video file too large (max 20MB).")
        return value

    @transaction.atomic
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        video_data = validated_data.pop('video', None)
        sports_ids = validated_data.pop('sports_ids', [])
        
        owner = self.context['request'].user
        turf = Turf.objects.create(owner=owner, **validated_data)
        turf.sports.set(sports_ids)
        
        for image_data in images_data:
            TurfImage.objects.create(turf=turf, image=image_data)
            
        if video_data:
            TurfVideo.objects.create(turf=turf, video=video_data)
            
        return turf
