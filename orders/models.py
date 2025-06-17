from django.db import models
from django.conf import settings
from products.models import Product
from decimal import Decimal

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('card', 'Credit Card'),
        ('paypal', 'PayPal'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def order_id(self):
        return f"ORD-{self.id:06d}"

    @property
    def total_amount(self):
        return self.total

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Added default
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=Decimal('0.00')  # Added default
    )

    @property
    def total(self):
        if self.quantity is None or self.price is None:
            return Decimal('0.00')
        return Decimal(str(self.quantity)) * self.price

    @property
    def subtotal(self):
        return self.total  # Use the same calculation as total

    def save(self, *args, **kwargs):
        if not self.price and self.product:
            self.price = self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order #{self.order.id}"

    class Meta:
        ordering = ['-id']