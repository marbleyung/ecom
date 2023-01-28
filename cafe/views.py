import datetime
import json

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from . import models as m
from django.http import JsonResponse, HttpResponse

from .forms import NewUserForm, PostForm, CommentForm
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


def blog(request):
    posts = m.Post.objects.all()
    context = form_context(request)
    context['posts'] = posts
    return render(request, 'cafe/blog.html', context)


def post_detail(request, slug):
    post = get_object_or_404(m.Post, slug=slug)
    return render(request, 'cafe/post_detail.html', {'post': post})


def post_edit(request, slug):
    post = get_object_or_404(m.Post, slug=slug)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'cafe/post_edit.html', {'form': form})


def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'cafe/post_edit.html', {'form': form})


def post_remove(request, slug):
    post = get_object_or_404(m.Post, slug=slug)
    post.delete()
    return redirect('blog')


def add_comment(request, slug):
    post = get_object_or_404(m.Post, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = CommentForm()
    return render(request, 'cafe/add_comment.html', {'form': form})


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
    print(action, data, 'line 67')
    customer = request.user.customer
    product = m.Product.objects.get(id=product_id)
    order, created = m.Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = m.OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    print('views line 82')
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


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = m.User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "cafe/password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    messages.success(request,
                                     'A message with reset password instructions has been sent to your inbox.')
                    return redirect("main:homepage")
                messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="cafe/password/password_reset.html",
                  context={"password_reset_form": password_reset_form})
