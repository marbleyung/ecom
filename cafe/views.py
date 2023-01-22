import json

from django.shortcuts import render
from . import models as m
from django.http import JsonResponse


def home(request):
    return render(request, 'cafe/base.html')
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
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = m.Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    context = {'items': items, 'order': order}
    return render(request, 'cafe/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = m.Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    context = {'items': items, 'order': order}
    return render(request, 'cafe/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = m.Product.objects.get(id=productId)
    order, created = m.Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = m.OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        print('zalypa')
        orderItem.quantity += 1
    elif action =='remove':
        print('zalypa2')
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item has been added', safe=False)