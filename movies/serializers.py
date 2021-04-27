from rest_framework import serializers
from .models import MovieImage, Movie, LikeHistory, Rent, Sell, MovieChangesLog


class MovieImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieImage
        fields = '__all__'


class LikeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeHistory
        fields = '__all__'


class RentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent
        fields = '__all__'


class SellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sell
        fields = '__all__'


class MovieChangesLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieChangesLog
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    images = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Movie
        depth = 1
        fields = '__all__'

    def create(self, validated_data):
        images = self.context['request'].FILES.getlist('images')
        if not images:
            raise serializers.ValidationError({'images': ['You must sent at least one movie image.']})
        validated_data = {**validated_data, 'availability': True}
        movie = Movie.objects.create(**validated_data,)
        for image in images:
            m = MovieImage(photo=image, movie=movie)
            m.save()
            print('Movie image was saved successfully.')

        return movie

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request:
            images = request.FILES.getlist('images')
            if images:
                for image in images:
                    m = MovieImage(photo=image, movie=instance)
                    m.save()
                    print('Movie image was saved successfully.')

        log_fields = {}
        store_log = False
        for field, value in validated_data.items():
            if field in ['sale_price', 'rental_price', 'title']:
                new_value = value
                old_value = getattr(instance, field)
                log_fields[f'new_{field}'] = new_value
                log_fields[f'old_{field}'] = old_value
                if new_value != old_value:
                    store_log = True
        if store_log:
            movie_log = MovieChangesLog(movie=instance)
            serializer = MovieChangesLogSerializer(movie_log, data={**log_fields}, partial=True)
            if serializer.is_valid():
                serializer.save()
                print('Created log for Movie update')
        return super(MovieSerializer, self).update(instance, validated_data)
