from django import forms
from .models import Review, Book
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from .models import Cart, CartItem

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        # Transfer items from session cart to user's cart
        if not user.is_anonymous:
            session_id = self.request.session.get('cart_id')
            if session_id:
                session_cart = Cart.objects.filter(session_id=session_id).first()
                if session_cart:
                    user_cart, created = Cart.objects.get_or_create(user=user)
                    session_cart_items = session_cart.items.all()
                    for item in session_cart_items:
                        cart_item, created = CartItem.objects.get_or_create(cart=user_cart, book=item.book)
                        if not created:
                            cart_item.quantity += item.quantity
                            cart_item.save()
                    # Clear session cart
                    session_cart.delete()
                    del self.request.session['cart_id']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text', 'rating']

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'description', 'author', 'genre', 'subgenre', 'language', 'price', 'ebook']
