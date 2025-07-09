from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    slug = models.CharField(max_length=150)
    title = models.CharField(max_length=150)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.title = self.slug
        return super().save(*args, **kwargs)
    
    
class Menu(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.IntegerField()
    features = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Reservation(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    number_of_guests = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Reservation by {self.first_name} {self.last_name}'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'menuitem')

    def __str__(self):
        return f"{self.user.username} Cart"
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, related_name='delivery_crew', limit_choices_to='DeliveryCrew', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    total = models.DecimalField(decimal_places=2, max_digits=6)
    date = models.DateField(db_index=True)

    def __str__(self):
        return (self.id)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.IntegerField()

    class Meta:
        unique_together = ('order' , 'menuitem')