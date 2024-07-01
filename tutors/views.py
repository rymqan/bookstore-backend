# views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Book, Author, Genre, Subgenre, Language, Cart, CartItem, Review
from django.db.models import Q
from django.contrib.sessions.models import Session
from django.views.decorators.http import require_POST
from django.utils.crypto import get_random_string
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from .forms import ReviewForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'tutors/login.html'



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'tutors/register.html', {'form': form})

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            
            # Transfer items from session cart to user's cart
            if not user.is_anonymous:
                session_id = request.session.get('cart_id')
                if session_id:
                    session_cart = Cart.objects.filter(session_id=session_id).first()
                    if session_cart:
                        user_cart, created = Cart.objects.get_or_create(user=user)
                        session_cart_items = session_cart.items.all()
                        for item in session_cart_items:
                            cart_item, created = CartItem.objects.get_or_create(cart=user_cart, book=item.book)
                            if not created:
                                cart_item.quantity += item.quantity
                            else:
                                cart_item.quantity = item.quantity
                            cart_item.save()
                        # Clear session cart
                        session_cart.delete()
                        del request.session['cart_id']
            
            next_url = request.POST.get('next') or request.GET.get('next') or 'profile'
            return redirect(next_url)
        else:
            return render(request, 'tutors/login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'tutors/login.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def profile(request):
    profile = request.user.profile
    purchased_books = profile.purchased_books.all()
    return render(request, 'tutors/profile.html', {'purchased_books': purchased_books})

def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.get('cart_id', None)
        if not session_id:
            session_id = get_random_string(32)
            request.session['cart_id'] = session_id
        cart, created = Cart.objects.get_or_create(session_id=session_id)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Get the URL of the previous page
    referer = request.META.get('HTTP_REFERER', 'book_list')
    return redirect(referer)

def cart_detail(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_id = request.session.get('cart_id', None)
        if session_id:
            cart = Cart.objects.filter(session_id=session_id).first()
        else:
            cart = None

    if not cart:
        cart_items = []
        total_price = 0
    else:
        cart_items = cart.items.all()
        total_price = sum(item.total_price() for item in cart_items)

    return render(request, 'tutors/cart_detail.html', {'cart_items': cart_items, 'total_price': total_price})

@require_POST
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    item.quantity = quantity
    item.save()
    return redirect('cart_detail')

def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart_detail')

def book_list(request):
    query = request.GET.get('q', '')
    genre_id = request.GET.get('genre', '')
    author_id = request.GET.get('author', '')
    language_id = request.GET.get('language', '')

    books = Book.objects.all()

    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__name__icontains=query))
    if genre_id:
        books = books.filter(genre_id=genre_id)
    if author_id:
        books = books.filter(author_id=author_id)
    if language_id:
        books = books.filter(language_id=language_id)

    genres = Genre.objects.all()
    authors = Author.objects.all()
    languages = Language.objects.all()

    return render(request, 'tutors/book_list.html', {
        'books': books,
        'genres': genres,
        'authors': authors,
        'languages': languages,
        'query': query,
        'selected_genre': genre_id,
        'selected_author': author_id,
        'selected_language': language_id,
    })

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = book.reviews.all()
    return render(request, 'tutors/book_detail.html', {'book': book, 'reviews': reviews})

@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect('book_detail', book_id=book.id)
    else:
        form = ReviewForm()
    return render(request, 'tutors/add_review.html', {'form': form, 'book': book})

@login_required
def edit_review(request, book_id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user, book_id=book_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('book_detail', book_id=book_id)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'tutors/edit_review.html', {'form': form, 'book': review.book})

@login_required
def delete_review(request, book_id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user, book_id=book_id)
    if request.method == 'POST':
        review.delete()
        return redirect('book_detail', book_id=book_id)
    return render(request, 'tutors/delete_review.html', {'review': review})

@login_required
def payment_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('cart_detail')

    total_cost = sum(item.total_price() for item in cart.items.all())
    user_profile = request.user.profile
    user_balance = user_profile.balance

    if request.method == 'POST':
        if user_balance >= total_cost:
            user_profile.balance -= total_cost
            user_profile.save()
            for item in cart.items.all():
                user_profile.purchased_books.add(item.book)
            cart.items.all().delete()  # Clear the cart
            return redirect('profile')
        else:
            return redirect('cart_detail')  # Redirect to cart detail without any query parameters

    return render(request, 'tutors/payment.html', {'total_cost': total_cost, 'user_balance': user_balance})

