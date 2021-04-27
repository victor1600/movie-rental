from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator


class Movie(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=1000)
    stock = models.PositiveIntegerField(default=1,
                                        validators=[MinValueValidator(1)])
    rental_price = models.FloatField()
    sale_price = models.FloatField()
    availability = models.BooleanField(auto_created=True)
    likes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['title']

    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.availability = False
        print(self.availability)
        super(Movie, self).save(*args, **kwargs)

    def alter_stock(self, quantity):
        self.stock += quantity

    def check_movie_stock(self, rent_quantity):
        return self.stock >= int(rent_quantity)

    def __str__(self):
        return self.title


class LikeHistory(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.movie.title}, {self.user.username}'


class MovieImage(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='images')
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField()

    def __str__(self):
        return self.photo.path


# use inheritance
class Sell(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    total = models.FloatField()

    class Meta:
        ordering = ['total']

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.movie.sale_price
        super(Sell, self).save(*args, **kwargs)


class Rent(Sell):
    return_date = models.DateTimeField(default=timezone.now() + timedelta(days=5))
    returned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-return_date']

    def set_returned(self, value):
        self.returned = value

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.movie.rental_price
        if self.apply_penalty():
            self.total += 10
        # TODO: test changes

        super(Sell, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.movie.title}, {self.user.username}'

    def apply_penalty(self):
        return timezone.now() > self.return_date


class MovieChangesLog(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    old_title = models.CharField(max_length=100)
    old_rental_price = models.FloatField()
    old_sale_price = models.FloatField()
    new_title = models.CharField(max_length=100)
    new_rental_price = models.FloatField()
    new_sale_price = models.FloatField()
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['updated_at']
