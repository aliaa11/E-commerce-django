from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total(self):
        return sum(item.total for item in self.items.all())

    def __str__(self):
        return f"Cart for {self.user.username}"

    class Meta:
        app_label = 'cart'

class CartItem(models.Model):
    cart = models.ForeignKey('cart.Cart', related_name='items', on_delete=models.CASCADE)  # Changed this line
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.cart}"

    class Meta:
        app_label = 'cart'