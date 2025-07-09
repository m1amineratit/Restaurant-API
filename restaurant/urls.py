from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Registering OrderViewSet with DRF router
router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='orders')
router.register(r'menu-items', views.MenusViewSet, basename='menuitems')

urlpatterns = [

    # Group management endpoints
    path('api/groups/managers/users', views.ManagerGroupView.as_view()),
    path('api/groups/managers/users/<int:user_id>', views.ManagerGroupDetailView.as_view()),
    path('api/groups/delivery-crew/users', views.DeliveryCrewGroupView.as_view()),
    path('api/groups/delivery-crew/users/<int:user_id>', views.DeliveryCrewDetailView.as_view()),

    # Cart endpoints
    path('cart/menu-items', views.CartView.as_view()),

    # Menu Items and Order endpoints (GET/POST/PATCH/DELETE)
    path('', include(router.urls)),
]
