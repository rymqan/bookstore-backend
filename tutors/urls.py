# urls.py

from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import CustomLoginView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/profile/', views.profile, name='profile'),
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/add_review/', views.add_review, name='add_review'),
    path('book/<int:book_id>/review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('book/<int:book_id>/review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('payment/', views.payment_view, name='payment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
