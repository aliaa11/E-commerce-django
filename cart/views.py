from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from products.models import Product
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from django.views.decorators.http import require_POST

class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {
        'cart': cart,
        'cart_items': cart.items.all()
    }
    return render(request, 'cart/cart.html', context)

@login_required
def add_to_cart_view(request, product_id):
    """Web view for adding items to cart"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > product.stock:
            messages.error(request, 'Not enough stock available.')
            return redirect('products:product_detail', slug=product.slug)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'Added {quantity}x {product.name} to your cart.')
        return redirect('cart:cart')
    
    return redirect('products:product_list')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart_api(request):
    """API endpoint for adding items to cart"""
    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if quantity > product.stock:
        return Response(
            {'error': 'Not enough stock available'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@require_POST
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action')
    
    try:
        if action == 'increase':
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
            else:
                messages.warning(request, f'Sorry, only {cart_item.product.stock} items available.')
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()
                messages.info(request, 'Item removed from cart.')
                return redirect('cart:cart')
        
        cart_item.save()
        messages.success(request, 'Cart updated successfully.')
        
    except Exception as e:
        messages.error(request, 'Error updating cart.')
    
    return redirect('cart:cart')

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item_api(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.data.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)
    else:
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@login_required
def remove_from_cart_view(request, item_id):
    """Web view for removing items from cart"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        messages.success(request, 'Item removed from cart successfully.')
    
    return redirect('cart:cart')

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart_api(request, item_id):
    """API endpoint for removing items from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    return Response(status=status.HTTP_204_NO_CONTENT)