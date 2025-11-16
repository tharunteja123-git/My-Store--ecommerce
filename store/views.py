from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Product, CartItem
from .models import CartItem, Order, OrderItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Order
from django.db.models import Q
from .models import Product, Category
from django.shortcuts import get_object_or_404
import random
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP
from .models import User

# Create your views here.

def home(request):
    return HttpResponse("Welcome to the E‑Commerce App!")
def home(request):
    categories = Category.objects.all()
    top_deals = Product.objects.filter(is_deal=True)[:10]
    mobiles = Product.objects.filter(category__name__icontains="Mobiles")[:10]
    fashion = Product.objects.filter(category__name__icontains="Fashion")[:10]
    electronics = Product.objects.filter(category__name__icontains="Electronics")[:10]
    home_kitchen = Product.objects.filter(category__name__icontains="Home")[:10]

    return render(request, 'store/home.html', {
        'categories': categories,
        'top_deals': top_deals,
        'mobiles': mobiles,
        'fashion': fashion,
        'electronics': electronics,
        'home_kitchen': home_kitchen,
    })


def product_list(request):
    products=Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})


def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    if product.stock <= 0:
        return  redirect('product_list') # prevent adding if no stock

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
    return redirect('cart')


def cart(request):
    items = CartItem.objects.filter(user=request.user)
    for item in items:
        item.item_total = item.product.price * item.quantity
    total = sum(item.item_total for item in items)
    return render(request, 'store/cart.html', {'items': items, 'total': total})


def request_otp(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        try:
            # Find user by email or phone
            user = User.objects.filter(email=identifier).first() or User.objects.filter(username=identifier).first()
            if not user:
                return render(request, "store/login.html", {"error": "User not found. Please signup."})

            # Generate OTP
            code = OTP.generate_code()
            OTP.objects.create(user=user, code=code)

            # Send OTP via email (SMS requires integration with Twilio/msg91)
            send_mail(
                "Your MyStore OTP",
                f"Your login OTP is {code}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return render(request, "store/verify_otp.html", {"identifier": identifier})
        except Exception as e:
            return render(request, "store/login.html", {"error": str(e)})
    return render(request, "store/login.html")

def verify_otp(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        code = request.POST.get("otp")

        user = User.objects.filter(email=identifier).first() or User.objects.filter(username=identifier).first()
        otp = OTP.objects.filter(user=user, code=code).last()

        if otp:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "store/verify_otp.html", {"error": "Invalid OTP", "identifier": identifier})
    return redirect("login")


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        return redirect('cart')

    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        # Create order only when user clicks Proceed to Payment
        order = Order.objects.create(user=request.user, total_price=total, status="Pending")
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        request.session['order_id'] = order.id
        return redirect('payment')
    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})



def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after signup
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})

'''def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('product_list')
    return render(request, 'store/login.html')'''



def generate_otp():
    return str(random.randint(100000, 999999))

def request_otp(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # ✅ matches form field
        user = User.objects.filter(email=identifier).first() or User.objects.filter(username=identifier).first()

        if not user:
            return render(request, 'store/login.html', {'error': 'User not found. Please sign up.'})

        code = generate_otp()
        OTP.objects.create(user=user, code=code)

        send_mail(
            'Your MyStore OTP',
            f'Your login OTP is {code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return render(request, 'store/verify_otp.html', {'identifier': identifier})
    return render(request, 'store/login.html')

def verify_otp(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        code = request.POST.get('otp')

        user = User.objects.filter(email=identifier).first() or User.objects.filter(username=identifier).first()
        otp = OTP.objects.filter(user=user, code=code).last()

        if otp:
            login(request, user)
            return redirect('product_list')
        else:
            return render(request, 'store/verify_otp.html', {'error': 'Invalid OTP', 'identifier': identifier})
    return redirect('login')


def user_logout(request):
    logout(request)
    return redirect('product_list')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})

def product_list(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories
    })

def update_cart(request, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if action == "increase":
        if cart_item.quantity < cart_item.product.stock:  # respect stock limit
            cart_item.quantity += 1
            cart_item.save()
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()  

    return redirect('cart')

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {
        'user': request.user,
        'orders': orders
    })

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Filters
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if status:
        orders = orders.filter(status=status)
    if start_date and end_date:
        orders = orders.filter(created_at__range=[start_date, end_date])

    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()  # assuming you have a related_name="items" on OrderItem

    # add subtotal for each item
    for item in items:
        item.subtotal = item.price * item.quantity

    return render(request, 'store/order_detail.html', {
        'order': order,
        'items': items
    })



@login_required
def payment(request):
    if request.method == 'POST':
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Mark order as completed (simulate payment success)
        order.status = "Completed"
        order.save()

        # Clear cart after payment
        CartItem.objects.filter(user=request.user).delete()

        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'store/payment.html')


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})

def home(request):
    products = Product.objects.all()[:8]  # show top 8 products
    return render(request, 'store/home.html', {'products': products})


def buy_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

    # Create a single-item order
    order = Order.objects.create(
        user=request.user,
        total_price=cart_item.product.price * cart_item.quantity,
        status="Pending"
    )
    OrderItem.objects.create(
        order=order,
        product=cart_item.product,
        quantity=cart_item.quantity,
        price=cart_item.product.price
    )

    # Remove item from cart after purchase
    cart_item.delete()

    return redirect('payment')  # or redirect to an order confirmation page

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def orders(request):
    user_orders = []  
    return render(request, 'store/orders.html', {'orders': user_orders})

@login_required
def wishlist(request):
    user_wishlist = []  
    return render(request, 'store/wishlist.html', {'wishlist': user_wishlist})

@login_required
def rewards(request):
    user_rewards = []  
    return render(request, 'store/rewards.html', {'rewards': user_rewards})

@login_required
def gift_cards(request):
    return render(request, 'store/gift_cards.html', {'gift_cards': []})


