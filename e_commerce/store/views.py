from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import *
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.models import User, Group, auth
from django.contrib.auth import login, authenticate
from django.contrib import messages




def registerPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password2 == password1:
            if User.objects.filter(username=username).exists():
                messages.info(request,'User Name taken!')
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email taken!')
                return redirect('register')

            else:
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password1, email=email)
                user.save()

                group = Group.objects.get(name='customer')
                user.groups.add(group)

                customer = Customer.objects.create(
                    user = user,
                    name = user.username,
                    email = user.email
                    )

                order = Order.objects.create(customer=customer, complete=False, transaction_id=False)
                items = order.orderitem_set.all()
                cartItems = order.get_cart_items
                ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=False,
                city=False,
                state=False,
                country=False,
                zipcode=False)

            
                user = auth.authenticate(username=username, password=password1)
    
                auth.login(request, user)
                
                return redirect('/')

        else:
            messages.info(request,'Password not matching!')
            return redirect('register')

    else:
        return render(request, 'accounts/register.html')

def loginPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)

            return redirect('/')
        else:
            messages.info(request, 'Invalid Credentials!')
            return redirect('login')


    else:
        return render(request, 'accounts/login.html')

def logoutPage(request):
    auth.logout(request)
    return redirect('/')




def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
        

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)

def picture(request):
    pass


def cart(request):
    data = cartData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items': items, 'order': order, 'cartItems':cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('ProductID:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    
    else:
        customer, order = guestOrder(request, data)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total()):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            country=data['shipping']['country'],
            zipcode=data['shipping']['zipcode'])


    return JsonResponse('Payment complete!', safe=False)


