from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User, Listing, Category, Comment, Bid, Watchlist
from .forms import AddListingForm

# main page
def index(request):
    listings = Listing.objects.filter(is_active=True).order_by("-date").all()
    context = {
        "title": "Active Listings",
        "listings": listings
    }
    return render(request, "auctions/index.html", context)


@login_required
def add_listing(request):
    if request.method == "POST":
        form = AddListingForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            category = form.cleaned_data.get("category")
            form.instance.category = category
            category_list = [i.category_name for i in Category.objects.all()]
            if category not in category_list:
                new_category = Category(category_name=category)
                new_category.save()
                
            form.instance.current_bid = form.cleaned_data.get("start_bid")
            form.save()
            return redirect("index")

    category_list = [i.category_name for i in Category.objects.all()]
    context = {
        "form": AddListingForm(data_list=category_list)
    }
    return render(request, "auctions/add-listing.html", context)

# single listing page
@login_required
def listing_page(request, id):
    listing = Listing.objects.filter(id=id).first()
    listing_bids = Bid.objects.filter(listing=listing)
    is_highest_bid = False
    if listing_bids.count() > 0:
        highest_bid = listing_bids.order_by("-date")[0]
        is_highest_bid = highest_bid.user.username == request.user.username

    user_watchlist = [item.listing for item in request.user.watchlist.all()]
    is_watched = listing in user_watchlist
    context = {
        "listing": listing,
        "is_watched": is_watched,
        "bids_number": listing_bids.count(),
        "is_highest_bid": is_highest_bid
    }
    return render(request, "auctions/listing-page.html", context)

# watchlist page
@login_required
def watchlist_page(request):
    watchlist_listings = Watchlist.objects.filter(user=request.user).all()
    context = {
        # "watchlist_listings": watchlist_listings
        "title": "Watchlist",
        "listings": [i.listing for i in watchlist_listings]
    }
    return render(request, "auctions/index.html", context)

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
    listing_bids = Bid.objects.filter(listing__id=id).order_by("-date")
    if listing_bids.count() != 0:
        listing.winner = listing_bids[0].user
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


def category_page(request):
    category_list = Category.objects.all()
    context = {
        "categories": category_list
    }
    return render(request, "auctions/category-list.html", context)


def category_search(request):
    category = request.GET.get("category")
    if category == "nocategory":
        results = Listing.objects.filter(is_active=True, category="").all()
    else:
        results = Listing.objects.filter(is_active=True, category=category).all()
            
    context = {
        # "watchlist_listings": watchlist_listings
        "title": f"{category}",
        "listings": results
    }
    return render(request, "auctions/index.html", context)


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
