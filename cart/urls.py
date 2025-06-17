from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Web URLs
    path('', views.cart_detail, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart_view, name='add-to-cart'),
    path('update/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('remove/<int:item_id>/', views.remove_from_cart_view, name='remove-from-cart'),
    
    # API URLs
    path('api/cart/', views.CartView.as_view(), name='cart-api'),
    path('api/add/', views.add_to_cart_api, name='add-to-cart-api'),
    path('api/update/<int:item_id>/', views.update_cart_item_api, name='update-cart-item-api'),
    path('api/remove/<int:item_id>/', views.remove_from_cart_api, name='remove-from-cart-api'),
    path('api/clear/', views.clear_cart, name='clear-cart-api'),
]