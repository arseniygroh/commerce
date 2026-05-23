from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add-listing", views.add_listing, name="add"),
    path("listing/<int:item_id>", views.listing_page, name="listing-item"),
    path("watchlist/<int:item_id>", views.watchlist, name="watchlist"),
    path("bid/<int:item_id>", views.bid_handler, name="bid"),
    path("comment/<int:item_id>", views.comment_handler, name="comment"),
    path("close/<int:item_id>", views.close_auction, name="close"),
    path("watchlist", views.watchlist_page, name="watchlist_page"),
    path("categories", views.categories_page, name="categories"),
    path("category/<int:category_id>", views.category_page, name="category"),
]
