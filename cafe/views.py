import datetime
import json

from django.shortcuts import render
from . import models as m
from django.http import JsonResponse
from .utils import form_context

def home(request):
    return render(request, 'cafe/base.html')


def products(request):
    context = form_context(request)
    products = m.Product.objects.all()
    context['products'] = products
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
    context = form_context(request)
    return render(request, 'cafe/cart.html', context)


def checkout(request):
    context = form_context(request)
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
        print('add-zalypa')
        orderItem.quantity += 1
    elif action =='remove':
        print('remove-zalypa')
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item has been added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = m.Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping is True:
            m.ShippingAddress.objects.create(
                    customer=customer,
                    order=order,
                    address=data['shipping']['address'],
                    city=data['shipping']['city'],
                    state=data['shipping']['state'],
                    zipcode=data['shipping']['zipcode'],


            )
    else:
        print('User is not logged...')
    print('Data', request.body)
    return JsonResponse('Order has been submitted', safe=False)
