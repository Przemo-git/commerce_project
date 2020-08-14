from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from auctions.models import Listing, Watchlist, User, Alllisting, Comment, Bid, Closedbid


def index(request):
    items = Listing.objects.all()
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount = len(w)
    except:
        wcount = None
    return render(request, 'auctions/index.html', {
        'items': items,
        'wcount': wcount
    })


def category(request, category):
    catitems = Listing.objects.filter(category=category)
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount = len(w)
    except:
        wcount = None
    return render(request, 'auctions/category.html', {
        'items': catitems,
        'cat': category,
        'wcount': wcount
    })

def create(request):
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount = len(w)
    except:
        wcount = None
    return render(request, 'auctions/create.html', {
        'wcount': wcount
    })


def submit(request):
    if request.method == 'POST':
        listtable = Listing()
        now = datetime.now()
        dt = now.strftime('%d, %Y, %B, %X')
        listtable.owner = request.user.username
        listtable.title = request.POST.get('title')
        listtable.description = request.POST.get('description')
        listtable.price = request.POST.get('price')
        listtable.category = request.POST.get('category')
        if request.POST.get('link'):
            listtable.link = request.POST.get('link')
        else:
            pass
        listtable.time = dt
        listtable.save()
        all = Alllisting()
        items = Listing.objects.all()
        for i in items:
            all.listingid = i.id
            all.title = i.title
            all.description = i.description
            all.link = i.link
            all.save()
        return redirect('index')
    else:
        return redirect('index')


def listingpage(request,id):
    try:
        items = Listing.objects.get(id=id)
    except:
        return redirect('index')
    try:
        comments = Comment.objects.filter(listingid=id)
    except:
        comments = None
    if request.user.username:
        added = True
        try:
            if Watchlist.objects.get(user=request.user.username, listingid=id):
                added = True
        except:
            added = False
        try:
            l = Listing.objects.get(id=id)
            if l.owner == request.user.username:
                owner = True
            else:
                owner = False
        except:
            return redirect('index')
    else:
        owner = False
        added = False
    try:
        w = Watchlist.objects.filter(user=request.user.username)
        wcount = len(w)
    except:
        wcount = None
    return render(request, 'auctions/listingpage.html', {
        'i': items,
        'error': request.COOKIES.get('error'),
        'errorgreen': request.COOKIES.get('errorgreen'),
        'comments': comments,
        'owner': owner,
        'added': added,
        'wcount': wcount
    })



def bidsubmit(request, listingid):
    current_bid = Listing.objects.get(id=listingid)
    current_bid = current_bid.price
    if request.method == 'POST':
        user_bid = int(request.POST.get('bid'))
        if user_bid > current_bid:
            listing_items = Listing.objects.get(id=listingid)
            listing_items.price = user_bid
            listing_items.save()
            try:
                if Bid.objects.filter(id=listingid):
                    bid_row = Bid.objects.filter(id=listingid)
                    bid_row.delete()
                bidtable = Bid()
                bidtable.user = request.user.username
                bidtable.title = listing_items.title
                bidtable.listingid = listingid
                bidtable.bid = user_bid
                bidtable.save()
            except:
                bidtable = Bid()
                bidtable.user = request.user.username
                bidtable.title = listing_items.title
                bidtable.listingid = listingid
                bidtable.bid = user_bid
                bidtable.save()

            response = redirect('listingpage', id=listingid)
            response.set_cookie('errorgreen','success!', max_age=3)
            return response
        else:
            response = redirect('listingpage', id=listingid)
            response.set_cookie('error', 'bid must be greater than current', max_age=3)
            return response
    else:
        return redirect('index')


def cmntsubmit(request,listingid):
    if request.method == 'POST':
        now = datetime.now()
        dt = now.strftime('%d %B %Y %X')
        c = Comment()
        c.comment = request.POST.get('comment')
        c.user = request.user.username
        c.listingid = listingid
        c.time = dt
        c.save()
        return redirect('listingpage', id=listingid)
    else:
        return redirect('index')


def addwatchlist(request, listingid):
    if request.user.username:
        w = Watchlist()
        w.user = request.user.username
        w.listingid = listingid
        w.save()
        return redirect('listingpage', id=listingid)
    else:
        return redirect('index')


def removewatchlist(request,listingid):
    if request.user.username:
        try:
            w = Watchlist.objects.get(user=request.user.username, listingid=listingid)
            w.delete()
            return redirect('listingpage', id=listingid)
        except:
            return redirect('listingpage', id=listingid)
    else:
        return redirect('index')


def watchlistpage(request, username):
    if request.user.username:
        try:
            w = Watchlist.objects.filter(user=username)
            items = []
            for i in w:     #
                items.append(Listing.objects.filter(id=i.listingid))
            try:
                w = Watchlist.objects.filter(user=request.user.username)
                wcount = len(w)
            except:
                wcount = None
            return render(request, 'auctions/watchlistpage.html', {
                'items': items,
                'wcount': wcount
            })
        except:
            try:
                w = Watchlist.objects.filter(user=request.user.username)
                wcount = len(w)
            except:
                wcount = None
            return render(request, 'auctions/watchlistpage.html', {
                'items': None,
                'wcount': wcount
            })
    else:
        return redirect('index')

def closebid(request, listingid):
    if request.user.username:
        try:
            listingrow = Listing.objects.get(id=listingid)
        except:
            return redirect('index')
        cb = Closedbid()
        cb.title = listingrow.title
        cb.owner =listingrow.owner
        cb.listingid = listingid
        try:
            bidrow = Bid.objects.get(listingid=listingid, bid=listingrow.price)
            cb.winner = bidrow.user
            cb.winprice = bidrow.bid
            cb.save()
            bidrow.delete()
        except:
            cb.winner = listingrow.owner
            cb.winprice = listingrow.price
            cb.save()
        try:
            if Watchlist.objects.filter(listingid=listingid):
                watchrow = Watchlist.objects.filter(listingid=listingid)
                watchrow.delete()
            else:
                pass
        except:
            pass
        try:
            cmtrow = Comment.objects.filter(listingid=listingid)
            cmtrow.delete()
        except:
            pass
        try:
            cbrow = Bid.objects.filter(listingid=listingid)
            cbrow.delete()
        except:
            pass
        try:
            cblist = Closedbid.objects.get(listingid=listingid)
        except:
            cb.winner = listingrow.owner
            cb.winprice = listingrow.price
            cb.title = listingrow.title
            cb.owner = listingrow.owner
            cb.listingid = listingid
            cb.save()
            cblist = Closedbid.objects.get(listingid=listingid)
        listingrow.delete()

        try:
            w = Watchlist.objects.filter(user=request.user.username)
            wcount = len(w)
        except:
            wcount = None

        return render(request, 'auctions/winningpage.html', {
            'cb': cblist,
            'title': cb.title,
            'wcount': wcount
    })
    else:
        return redirect('index')



def mywinnings(request):
    if request.user.username:
        items = []
        try:
            wonitems = Closedbid.objects.filter(winner=request.user.username)
            for w in wonitems:
                items.append(Alllisting.objects.filter(listingid=w.listingid))
        except:
            wonitems = None
            items = None
        try:
            w = Watchlist.objects.filter(user=request.user.username)
            wcount = len(w)
        except:
            wcount = None

        return render(request, 'auctions/mywinnings.html', {
            'items': items,
            'wonitems': wonitems,
            'wcount': wcount
        })
    else:
        return redirect('index')



def login_views(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'auctions/login.html', {
                'message': 'Invalid username and/or password.'
            })
    else:
        return render(request, 'auctions/login.html')


def logout_views(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        email = request.POST['email']
        confirmation = request.POST['confirmation']

        if password != confirmation:
            return render(request, 'auctions/register.html', {
                'message': 'Password must matched'
            })
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, 'auctions/register.html', {
                'message': 'User Name already exist'
            })
        login(request, user)
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'auctions/register.html')









