from django.contrib import admin
from .models import MovieImage, Movie, LikeHistory, Rent, MovieChangesLog
# Register your models here.
admin.site.register(MovieImage)
admin.site.register(Movie)
admin.site.register(LikeHistory)
admin.site.register(Rent)
admin.site.register(MovieChangesLog)

