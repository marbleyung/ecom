import json
from . import models as m


def form_context(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = m.Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except Exception as e:
            cart = {}
        finally:
            items = []
            order = {"get_cart_total": 0, "get_cart_items": 0, 'shipping': False}
            cart_items = order['get_cart_items']
        for i in cart:
            try:
                product = m.Product.objects.get(id=i)
                category = m.Category.objects.get(title=product.category)
                total = (product.price * cart[i]['quantity'])
                cart_items += cart[i]['quantity']
                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']
                item = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'image_URL': product.image_URL
                },
                    'quantity': cart[i]['quantity'],
                    'get_total': total
                }
                items.append(item)
                if category.digital is False:
                    order['shipping'] = True
                    print('utils line 39')
            except Exception as e:
                pass

    context = {'items': items, 'order': order, 'cartItems': cart_items}
    return context


def guest_order(request, data):
    name = data['shipping']['name']
    email = data['shipping']['email']

    context = form_context(request)
    items = context['items']
    customer, create = m.Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    order = m.Order.objects.create(customer=customer,
                                   complete=False)
    for i in items:
        product = m.Product.objects.get(id=i['product']['id'])
        orderItem = m.OrderItem.objects.create(
            product=product,
            order=order,
            quantity=i['quantity'],
        )

    return customer, order
