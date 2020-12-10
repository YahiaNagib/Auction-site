from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User, Listing, Category, Comment, Bid, Watchlist

# main page
def index(request):
    listings = Listing.objects.filter(is_active=True).order_by("-date").all()
    context = {
        "listings": listings
    }
    return render(request, "auctions/index.html", context)

# single listing page
@login_required
def listing_page(request, id):
    listing = Listing.objects.filter(id=id).first()
    listing_bids = Bid.objects.filter(listing=listing).count()
    user_watchlist = [item.listing for item in request.user.watchlist.all()]
    is_watched = listing in user_watchlist
    context = {
        "listing": listing,
        "is_watched": is_watched,
        "bids_number": listing_bids
    }
    return render(request, "auctions/listing-page.html", context)

# watchlist page
@login_required
def watchlist_page(request):
    watchlist_listings = Watchlist.objects.filter(user=request.user).all()
    context = {
        "watchlist_listings": watchlist_listings
    }
    return render(request, "auctions/watchlist.html", context)

# add a listing to the wathchlist
@login_required
def add_watchlist(request, id):
    listing = Listing.objects.filter(id=id).first()
    watchlist = Watchlist(listing=listing, user=request.user)
    watchlist.save()
    return redirect("watchlist-page")

# remove a listing from the wathchlist
@login_required
def remove_watchlist(request, id):
    watchlist_item = Watchlist.objects.filter(listing__id=id).first()
    watchlist_item.delete()
    return redirect("watchlist-page")

# close a bid
def close_bid(request, id):
    listing = Listing.objects.filter(id=id).first()
    listing.is_active = False
    highest_bid = Bid.objects.filter(listing__id=id).order_by("-date")
    if highest_bid.count() != 0:
        listing.winner = highest_bid[0].user
    listing.save()
    return redirect("index")


def add_bid(request):
    if request.method == "POST":
        id = request.POST["listing-id"]
        listing = Listing.objects.filter(id=id).first()
        listing_current_bid = listing.current_bid
        bid_value = float(request.POST["bid"])
        
        if bid_value > listing_current_bid:
            listing.current_bid = bid_value
            listing.save()
            bid = Bid(bid=bid_value, listing=listing, user=request.user)
            bid.save()
            return redirect(f"/listing/{id}")

# add comment
def add_comment(request):
    if request.method == "POST":
        content = request.POST["comment-content"]
        id = request.POST["listing-id"]
        listing = Listing.objects.filter(id=id).first()
        comment = Comment(content=content, listing=listing, user=request.user)
        comment.save()
        return redirect(f"/listing/{id}")


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
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

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
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
