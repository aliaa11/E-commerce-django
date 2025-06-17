from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Template URLs
    path('', views.OrderListView.as_view(), name='order_list'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/cancel/', views.OrderCancelView.as_view(), name='order_cancel'),

    # API URLs
    path('api/orders/', views.OrderListAPIView.as_view(), name='api-order-list'),
    path('api/orders/<int:pk>/', views.OrderDetailAPIView.as_view(), name='api-order-detail'),
    path('api/orders/create/', views.create_order_api, name='api-order-create'),
    path('api/orders/<int:pk>/status/', views.update_order_status, name='api-order-status'),
]