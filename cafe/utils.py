import json
from . import models as m
def form_context(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = m.Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
            print('Cart:', cart)
        except Exception as e:
            print(e)
            cart = {}
        finally:
            items = []
            order = {"get_cart_total": 0, "get_cart_items": 0, 'shipping': False}
            cartItems = order['get_cart_items']

        for i in cart:
            product = m.Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])
            if total == 0:
                print('views line 33')
                continue
            else:
                cartItems += cart[i]['quantity']
                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']
                item = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'imageURL': product.imageURL
                    },
                    'quantity': cart[i]['quantity'],
                    'get_total': total
                }
                items.append(item)

                if product.digital is False:
                    order['shipping'] = True


    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return context