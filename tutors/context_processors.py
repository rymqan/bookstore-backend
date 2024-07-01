from .models import Cart

def cart_status(request):
    cart_items = []
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_id = request.session.get('cart_id', None)
        if session_id:
            cart = Cart.objects.filter(session_id=session_id).first()
        else:
            cart = None
    
    if cart:
        cart_items = [item.book.id for item in cart.items.all()]

    return {
        'cart_items': cart_items,
    }
