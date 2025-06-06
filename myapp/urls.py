# urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path("collections/", views.product_list, name = 'collections'),
    path("register/", views.reg, name = 'register'),
    path("login/", views.userlog, name = 'login'),
    path('logout/', views.user_logout, name='logout'),
    path("add_to_cart/<int:product_id>/", views.add_to_cart, name='add_to_cart'), 
    path('checkout/<int:product_id>/', views.checkout_single, name='checkout_single'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout, name='checkout'),  
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_quantity/<int:item_id>/<str:action>/', views.update_quantity, name='update_quantity'),
    path('purchase-history/', views.purchase_history, name='purchase_history'),
    path('generate-invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)