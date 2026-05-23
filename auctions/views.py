import datetime
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import User, Category, AuctionListing, Comment, Bid


def index(request):
    return render(request, "auctions/index.html", {
        "listings": AuctionListing.objects.all()
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def add_listing(request):
    if request.method == "POST":
        title = request.POST.get("listing-title")
        desc = request.POST.get("listing-desc")
        bid = request.POST.get("listing-bid")
        img_url = request.POST.get("listing-image")
        category = request.POST.get("listing-category")

        category_obj = None
        if category:
            category_obj = Category.objects.get_or_create(name=category)[0]

        AuctionListing.objects.create(
            title=title, 
            description=desc,  
            starting_bid=bid, 
            img_url=img_url, 
            category=category_obj,
            author=request.user
        )
        return redirect("index") 
        
    else:
        return render(request, "auctions/add-listing.html")
    
def listing_page(request, item_id):
    listing = AuctionListing.objects.get(id=item_id)
    highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
    bids_count = Bid.objects.filter(listing=listing).count()
    comments = Comment.objects.filter(listing=listing)
    if highest_bid:
        current_price = highest_bid.amount
    else:
        current_price = listing.starting_bid

    is_winner = False
    if not listing.is_active and highest_bid and request.user == highest_bid.author:
        is_winner = True

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "highest": current_price,
        "bids_count": bids_count,
        "comments": comments,
        "is_winner": is_winner,
    })

def watchlist(request, item_id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(id=item_id)
        if request.user in listing.watchlist.all():
            listing.watchlist.remove(request.user)
        else:
            listing.watchlist.add(request.user)
    
    return redirect("listing-item", item_id=item_id)

def bid_handler(request, item_id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(id=item_id)
        if request.user == listing.author:
            return render(request, "auctions/error.html", {
                    "message": "You can't place bid on your slots"
                })
        highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
        if highest_bid:
            current_price = highest_bid.amount
        else:
            current_price = listing.starting_bid
        new_bid = request.POST.get("user-bid")
        if new_bid:
            new_bid_num = float(new_bid)
            if new_bid_num <= current_price:
                return render(request, "auctions/error.html", {
                    "message": f"Your bid must be higher than {current_price}"
                })
            elif new_bid_num <= 0:
                return render(request, "auctions/error.html", {
                    "message": "Your bid must be a positive value"
                })
            else:
                Bid.objects.create(amount=new_bid_num, listing=listing, author=request.user)
        else:
            return render(request, "auctions/error.html", {
                    "message": "Enter valid input"
                })
        return redirect("listing-item", item_id=item_id)

def comment_handler(request, item_id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(id=item_id)
        user_comment = request.POST.get("user-comment")
        Comment.objects.create(author=request.user, content=user_comment, date=datetime.datetime.now(), listing=listing)
    
    return redirect("listing-item", item_id=item_id)

def close_auction(request, item_id):
    if request.method == "POST":
        listing = AuctionListing.objects.get(id=item_id)
        listing.is_active = False
        listing.save()
    return redirect("listing-item", item_id=item_id)

def watchlist_page(request):
    return render(request, "auctions/watchlist.html", {
        "listings": request.user.watchlist.all()
    })

def categories_page(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

def category_page(request, category_id):
    category = Category.objects.get(id=category_id)
    listings = AuctionListing.objects.filter(category=category, is_active=True)
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": category,
    })