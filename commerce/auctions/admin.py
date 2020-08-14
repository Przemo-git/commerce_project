from django.contrib import admin

# Register your models here.
from .models import Listing, Watchlist, User, Alllisting, Comment, Bid, Closedbid

admin.site.register(Listing)
admin.site.register(Watchlist)
admin.site.register(User)
admin.site.register(Alllisting)
admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(Closedbid)