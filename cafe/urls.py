from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.home, name='home'),
    path('products/', v.products, name='products'),
    path('about/', v.about, name='about'),
    path('contacts/', v.contacts, name='contacts'),
    path('blog/', v.blog, name='blog'),
    path('cart/', v.cart, name='cart'),
    path('checkout/', v.checkout, name='checkout'),
    path('update_item/', v.updateItem, name='update_item'),
]