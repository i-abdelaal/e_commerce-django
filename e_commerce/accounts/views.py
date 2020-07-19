from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.signals import post_save
from django.contrib.auth.models import User, auth, Group

from store.models import *
from django.contrib.auth import login, authenticate


def register(request):
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
				order,created = Order.objects.get_or_create(customer=customer, complete=False)
				items = order.orderitem_set.all()
				cartItems = order.get_cart_items

			
				user = auth.authenticate(username=username, password=password1)
	
				auth.login(request, user)
				
				return redirect('/')

		else:
			messages.info(request,'Password not matching!')
			return redirect('register')

	else:
		return render(request, 'accounts/register.html')


def login(request):
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

def logout(request):
	auth.logout(request)
	return redirect('/')