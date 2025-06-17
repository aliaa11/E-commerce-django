from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Template Views
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # API Endpoints
    path('api/products/', views.ProductAPIView.as_view(), name='product-list-api'),
    path('api/products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product-detail-api'),
    path('api/categories/', views.CategoryListView.as_view(), name='category-list'),
]