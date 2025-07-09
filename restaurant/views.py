from django.shortcuts import render, get_object_or_404
from .models import Menu, Category, Cart, Order, OrderItem
from .serializers import MenuSerializer, CategorySerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.viewsets import ModelViewSet
from .permissions import IsDeliveryCrew, ReadOnly, IsManager
from rest_framework.views import APIView
from rest_framework import permissions
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


class MenusViewSet(ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [ReadOnly]


class ManagerGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get(self, request):
        managers = User.objects.filter(group__name='Manager')
        return Response({'id' : user.id, 'username' : user.username} for user in managers)
    
    def post(self, request):
        user_id = request.data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.add(user)
            return Response({'message' : 'User added to Manager Group'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error' : 'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
        
class ManagerGroupDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.remove(user)
            return Response({'message' : 'User removed from Manager group'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error' : 'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
        
class DeliveryCrewGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get(self, request):
        managers = User.objects.filter(group__name='Manager')
        return Response({'id' : user.id, 'username' : user.username} for user in managers)
    
    def post(self, request):
        user_id = request.data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.add(user)
            return Response({'message': 'User added to group of Managers'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'message' : 'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
        
class DeliveryCrewDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            groups = Group.objects.get(name='Manager')
            groups.user_set.remove(user)
            return Response({'message' : 'User removed from Manager group'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message' : 'User Not Found'}, status=status.HTTP_404_NOT_FOUND)
        

class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(items, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CartSerializer(data=request.data, context={'request' : request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({'message' : 'Cart Deleted'}, status=204)
    
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        if user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
        elif user.groups.filter(name='DeliveryCrew').exitst():
            orders = Order.objects.filter(delivery_crew=user)
        else:
            orders = Order.objects.filter(user=request.user)
        
        serializer = OrderSerializer()
        return Response(serializer.data)
    
    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            return Response({'error' : 'Cart is empty'}, status=401)
        
        total = sum(item.price for item in cart_items)
        order = Order.objects.create(user=request.user, total=total)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )
        cart_items.delete()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)
    
    def partial_update(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        user = request.user

        # Manager logic 
        if user.groups.filter(name='Manager').exists():
            crew_id = request.data.get('delivery_crew')
            status_value = request.data.get('status')

            if crew_id:
                try:
                    crew_user = User.objects.get(id=crew_id)
                    if not crew_user.groups.filter(name='DeliveryCrew').exists():
                        return Response({'error' : 'User is not Delivery Crew'}, status=400)
                    order.delivery_crew = crew_user
                except User.DoesNotExist:
                    return Response({"error": "User not found"}, status=404)
                
                if status_value is not None:
                    order.status = bool(status_value)
                
                order.save()
        # Delivery Crew Logic
        
        elif user.groups.filter(name='DeliveryCrew').exists():
            status_value = request.data.get('status')
            if status_value is None:
                return Response({'error' : 'Status is required'}, status=400)

            order.status = bool(status_value)
            order.save()
        else:
            return Response({"error": "Unauthorized"}, status=403)
        
        return Response(OrderSerializer(order).data)
    
    def destroy(self, request, pk=None):
        order = get_object_or_404(Order, pk=pk)
        if not request.user.groups.filter(name='Manager').exists():
            return Response({"error": "Only managers can delete orders"}, status=403)
        order.delete()
        return Response(status=204)