# views.py
from datetime import datetime
from django.http import HttpResponse 
from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from .models import Products, Cart, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def product_list(request):
    query = request.GET.get('q','')
    if query:
        cr = Products.objects.filter(name__icontains=query)
    else:
        cr = Products.objects.all()

    return render(request, 'Product_list.html', {'cr':cr, 'query':query})

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
def checkout_single(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    if request.method == "POST":
        # Create a single-product order
        order = Order.objects.create(user=request.user)
        OrderItem.objects.create(order=order, product=product, quantity=1)

        messages.success(request, "The order is placed successfully!")
        return redirect('collections')  # Redirect after order placement

    return render(request, 'checkout.html', {'total_price': product.price})

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


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    # Compute total price for each item
    for item in cart_items:
        item.total_price = item.product.price * item.quantity

    total_price = sum(item.total_price for item in cart_items)

    if request.method == "POST":
        # Create an order
        order = Order.objects.create(user=request.user)

        # Create OrderItem objects for each cart item
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

        # Clear the cart after placing the order
        cart_items.delete()

        messages.success(request, "The order is placed successfully!")
        return redirect('collections')  # Redirect to collections or confirmation page after checkout

    return render(request, 'checkout.html', {'total_price': total_price})


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_view')

@login_required
def purchase_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-date').prefetch_related('order_items__product__category', 'order_items__product__brand')  # Fetch orders in descending order of date
    # Pre-calculate total price for each order item
    for order in orders:
        for item in order.order_items.all():
            item.total_price = item.product.price * item.quantity
    return render(request, 'purchase_history.html', {'orders': orders})

@login_required
def generate_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Create a response object for PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Create a PDF document
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Set title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Invoice")

    # Order details
    p.setFont("Helvetica", 12)

    purchase_time = order.date.strftime('%Y-%m-%d %H:%M:%S')  # Format order date & time
    invoice_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current date & time

    p.drawString(50, height - 100, f"Order ID: {order.id}")
    p.drawString(50, height - 120, f"Purchase Date: {purchase_time}")  # Show purchase time
    p.drawString(50, height - 140, f"Invoice Generated: {invoice_time}")  # Show invoice time
    p.drawString(50, height - 160, f"Customer: {order.user.first_name} {order.user.last_name}")

    # Table headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 200, "Product")
    p.drawString(250, height - 200, "Quantity")
    p.drawString(350, height - 200, "Price")
    p.drawString(450, height - 200, "Total")

    y = height - 220  # Start position for items
    total_price = 0

    # Order items
    for item in order.order_items.all():
        p.setFont("Helvetica", 12)
        p.drawString(50, y, item.product.name)
        p.drawString(250, y, str(item.quantity))
        p.drawString(350, y, f"${item.product.price}")
        item_total = item.quantity * item.product.price
        p.drawString(450, y, f"${item_total}")
        y -= 20  # Move down for next item
        total_price += item_total

    # Total price
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y - 20, f"Total Amount: ${total_price}")

    p.showPage()
    p.save()
    return response