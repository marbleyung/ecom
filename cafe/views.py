from django.shortcuts import render
from . import models as m

def home(request):
    context = {}
    return render(request, 'cafe/base.html', context)


def products(request):
    products = m.Product.objects.all()
    context = {'products': products}
    return render(request, 'cafe/products.html', context)


def about(request):
    context = {}
    return render(request, 'cafe/about.html', context)


def contacts(request):
    context = {}
    return render(request, 'cafe/contacts.html', context)


def blog(request):
    context = {}
    return render(request, 'cafe/blog.html', context)


def cart(request):
    context = {}
    return render(request, 'cafe/cart.html', context)


def checkout(request):
    context = {}
    return render(request, 'cafe/checkout.html', context)