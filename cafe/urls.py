from django.urls import path
from . import views as v


urlpatterns = [
    path('', v.products, name='products'),
    path('blog/', v.blog, name='blog'),
    path('contact/', v.contact, name='contact'),
    path('about/', v.about, name='about'),
    path('blog/', v.blog, name='blog'),
    path('cart/', v.cart, name='cart'),
    path('login/', v.login_user, name='login'),
    path('logout/', v.logout_user, name='logout'),
    path('register/', v.register, name='register'),
    path('checkout/', v.checkout, name='checkout'),
    path('update_item/', v.updateItem, name='update_item'),
    path('process_order/', v.processOrder, name='process_order'),
    path('product/<slug:product_slug>/', v.show_product, name='show_product'),
    path('blog/new/', v.post_new, name='post_new'),
    path('blog/<slug:slug>/', v.post_detail, name='post_detail'),
    path('blog/<slug:slug>/edit', v.post_edit, name='post_edit'),
    path('blog/<slug>/remove', v.post_remove, name='post_remove'),
    path('blog/<slug:slug>/comment/', v.add_comment, name='add_comment'),
    path("password_reset", v.password_reset_request, name="password_reset")
]