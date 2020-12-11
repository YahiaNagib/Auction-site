from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("listing/<int:id>", views.listing_page, name="listing-page"),
    path("accounts/login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist_page, name="watchlist-page"),
    path("addwatchlist/<int:id>", views.add_watchlist, name="add-watchlist"),
    path("remove/watchlist/<int:id>", views.remove_watchlist, name="remove-watchlist"),
    path("close/<int:id>", views.close_bid, name="close-bid"),
    path("addcomment", views.add_comment, name="add-comment"),
    path("addbid", views.add_bid, name="add-bid"),
    path("addlisting", views.add_listing, name="add-listing"),
    path("categories", views.category_page, name="category-page"),
    path("search", views.category_search, name="category-search"),

]
