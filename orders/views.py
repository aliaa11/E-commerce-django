from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from cart.models import Cart

# Template Views
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = 'orders/order_create.html'
    fields = ['shipping_address', 'payment_method']
    success_url = reverse_lazy('orders:order_list')

    def form_valid(self, form):
        try:
            cart = Cart.objects.get(user=self.request.user)
            if not cart.items.exists():
                return redirect('cart:cart')

            with transaction.atomic():
                order = form.save(commit=False)
                order.user = self.request.user
                order.total = cart.total
                order.save()

                # Create order items from cart
                for item in cart.items.all():
                    order.items.create(
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                    # Update product stock
                    item.product.stock -= item.quantity
                    item.product.save()

                # Clear the cart
                cart.items.all().delete()

            return super().form_valid(form)
        except Cart.DoesNotExist:
            return redirect('cart:cart')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderCancelView(LoginRequiredMixin, UpdateView):
    model = Order
    template_name = 'orders/order_cancel.html'
    fields = []  # No fields to update
    success_url = reverse_lazy('orders:order_list')

    def get_queryset(self):
        # Only allow canceling pending orders
        return Order.objects.filter(
            user=self.request.user,
            status='pending'
        )

    def form_valid(self, form):
        order = form.save(commit=False)
        order.status = 'cancelled'
        messages.success(self.request, f'Order #{order.id} has been cancelled.')
        return super().form_valid(form)

# API Views
class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_api(request):
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    total=cart.total,
                    shipping_address=serializer.validated_data['shipping_address'],
                    payment_method=serializer.validated_data['payment_method']
                )
                
                # Create order items
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                    
                    # Update product stock
                    cart_item.product.stock -= cart_item.quantity
                    cart_item.product.save()
                
                # Clear cart
                cart.items.all().delete()
                
                order_serializer = OrderSerializer(order)
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Cart.DoesNotExist:
        return Response(
            {'error': 'Cart not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    new_status = request.data.get('status')
    
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    return Response(
        {'error': 'Invalid status'}, 
        status=status.HTTP_400_BAD_REQUEST
    )