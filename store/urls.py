from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views_api import ProductViewSet, CartItemViewSet, OrderViewSet

# DRF Router
router = DefaultRouter()
router.register(r'products-api', ProductViewSet, basename='products')
router.register(r'cart-api', CartItemViewSet, basename='cart')
router.register(r'orders-api', OrderViewSet, basename='orders')

urlpatterns = [
    path('', views.home, name='home'),
    path('payment/', views.payment, name='payment'),
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.request_otp, name='login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('logout/', views.logout,name='logout'),
    path('logout/', views.user_logout, name='logout'),  
    path('products/', views.product_list, name='product_list'),
    path('product_list/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('cart/buy/<int:item_id>/', views.buy_item, name='buy_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('checkout/', views.checkout, name='checkout'),
    path('rewards/', views.rewards, name='rewards'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/', views.orders, name='orders'),
    path('rewards/', views.rewards, name='rewards'), 
    path('order_history/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('gift-cards/', views.gift_cards, name='gift_cards'),
    


]

# Add API routes
urlpatterns += router.urls
