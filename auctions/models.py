import datetime
from pyexpat import model
from tkinter import CASCADE
from django.contrib.auth.models import AbstractUser
from django.db import models
from pkg_resources import require


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.FloatField()
    img_url = models.URLField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    is_active = models.BooleanField(default=True)

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    date = models.DateTimeField()
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")

class Bid(models.Model):
    amount = models.FloatField()
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
