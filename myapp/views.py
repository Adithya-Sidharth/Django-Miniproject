# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from .models import Products, Brand, Cart
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

def product_list(request):
    query = request.GET.get('q','')
    if query:
        cr = Products.objects.filter(name__icontains=query)
    else:
        cr = Products.objects.all()

    return render(request, 'Product_list.html', {'cr':cr, 'query':query})

# def brand_list(request):
#     br = 

def reg(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        User.objects.create_user(username=email, password=password, first_name=first_name, last_name=last_name, email=email)

    return render(request, 'Register.html')


def userlog(request):
    next_url = request.GET.get('next', 'collections')  
    error_message = None

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user) 
            return redirect(next_url) 
        else:
            error_message = "Invalid email or password."

    return render(request, 'Login.html', {'error_message': error_message})

def user_logout(request):
    logout(request)
    return redirect('collections')

@login_required
def add_to_cart(request, product_id):
    product = Products.objects.get(id=product_id)

    # Check if the product already exists in the cart for the user
    existing_cart_item = Cart.objects.filter(user=request.user, product=product).first()
    if existing_cart_item:
        # If the product already exists, increment the quantity
        existing_cart_item.quantity += 1
        existing_cart_item.save()
    else:
        # If the product is not in the cart, create a new cart item
        Cart.objects.create(user=request.user, product=product)

    return redirect('collections')

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)

    # Compute total price for each item
    for item in cart_items:
        item.total_price = item.product.price * item.quantity

    total_price = sum(item.total_price for item in cart_items)

    return render(request, 'cart_view.html', {'cart_items': cart_items, 'total_price': total_price})

def update_quantity(request, item_id, action):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)

    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        cart_item.delete()  # If quantity becomes 0, remove item

    cart_item.save()
    return redirect('cart_view')


def checkout(request):
    if request.method == "POST":
        # Here, you can add order processing logic (saving to DB, payment integration, etc.)
        return render(request, 'order_confirmation.html')  # Redirect to order confirmation page

    return render(request, 'checkout.html')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_view')