from rest_framework import serializers
from .models import Menu, Reservation, Category, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only = ['user', 'menuitems']

        def create(self, validate_data):
            user = self.context['request'].user
            menuitem = validate_data['menuitem']
            quantity = validate_data['quantity']
            unit_price = menuitem.price
            total_price = quantity * unit_price

            return Cart.objects.create(
                user=user,
                menuitem=menuitem,
                quantity=quantity,
                unit_price=unit_price,
                price=total_price
            )
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('user', 'delivery_crew', 'status', 'total', 'date', )

class OrderItemSerializer(serializers.ModelSerializer):
    order_items = OrderSerializer(many=True, read_only=True)
    class Meta:
        model = OrderItem
        fields = ('order_items', 'menuitem', 'quantity', 'unit_price', 'price')
