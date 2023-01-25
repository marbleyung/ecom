import datetime
import json

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, get_object_or_404, redirect

from . import models as m
from django.http import JsonResponse

from .forms import NewUserForm
from .utils import form_context, guest_order


def home(request):
    return render(request, 'cafe/base.html')


def products(request):
    context = form_context(request)
    products = m.Product.objects.all()
    categories = m.Category.objects.all()
    context['products'] = products
    context['categories'] = categories
    return render(request, 'cafe/products.html', context)


def about(request):
    context = {}
    return render(request, 'cafe/about.html', context)


def show_product(request, product_slug):
    product = get_object_or_404(m.Product, slug=product_slug)
    products = m.Product.objects.all()
    context = form_context(request)
    context['product'] = product
    context['products'] = products
    return render(request, 'cafe/show_product.html', context)


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
    product_id = data['productId']
    action = data['action']

    customer = request.user.customer
    product = m.Product.objects.get(id=product_id)
    order, created = m.Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = m.OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action =='remove':
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

    else:
        customer, order = guest_order(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
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
    return JsonResponse('Order has been submitted', safe=False)


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer = m.Customer.objects.create(
                email=user.email,
                name=user.username,
            )
            customer.user = user
            customer.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("products")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="cafe/register.html", context={"register_form": form})


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("products")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="cafe/login.html", context={"login_form": form})


def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("products")