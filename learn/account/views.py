from django.contrib.messages.api import success
from django.forms.forms import Form
from django.shortcuts import render, redirect

from django.http import HttpResponse

from .models import *

from .forms import OrderForm , CreateUserForm , CustomerForm , ProductForm
from .filters import OrderFilter
from .decorators import unauth_user, allowed_user , admin_only

from django.contrib import messages

from django.contrib.auth import authenticate , login , logout

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import Group
# from django.contrib.auth.forms import UserCreationForm

# Create your views here.

@unauth_user
def registerpage(request):
    form = CreateUserForm()

    if request.method== 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')    
            
            #signals will do the remaning jobs.

            messages.success(request , 'Account Successfully created for ' +username)

            return redirect('login')
    
    context = {'form' : form}
    return render(request , 'accounts/registerpage.html', context)

@unauth_user
def loginpage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request , username = username , password = password)

        if user is not None:
            login( request , user)
            return redirect('home')
        else:
            messages.info(request , 'Invalid Username or Password')

        # return 'jmfnsd'
    context = {}
    return render(request , 'accounts/loginpage.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
    
    products = Product.objects.all()
    customer = Customer.objects.all()
    total_customers = customer.count()
    
    order_count = Order.objects.count()

    deliverd = Order.objects.filter(status = 'Delivered').count()
    pending = Order.objects.filter(status = 'Pending').count()

    context = {'products': products , 'customer': customer , 'total_consumer':total_customers, 'order_count':order_count, 'deliverd': deliverd , 'pending': pending} 

    # orders = Product.objects.all()
    # orders = Product.objects.all()
    # return HttpResponse(Product.objects.all())

    return render(request , 'accounts/dashboard.html' , context)

@login_required(login_url='login')
@allowed_user(allowed_roles = ['customer', 'admin'])
def userpage(request):    
    products = Product.objects.all()
    context = {'products': products}

    return render(request , 'accounts/userpage.html' , context)


@login_required(login_url='login')
@allowed_user(allowed_roles = ['customer'])
def cust_order(request):

    if request.method == 'POST':
        form = OrderForm(request.POST)
        form.save()
        return redirect('/')

    return HttpResponse('ERROR OCCURED')



@login_required(login_url='login')
@allowed_user(allowed_roles = ['customer'])
def myorders(request):

    orders = request.user.customer.order_set.all()

    order_count = orders.count()

    deliverd = orders.filter(status = 'Delivered').count()
    pending = orders.filter(status = 'Pending').count()

    context = {'orders': orders , 'customer': customer , 'order_count':order_count, 'deliverd': deliverd , 'pending': pending} 


    # context = {'orders': orders}
    
    return render(request , 'accounts/myorders.html' , context)


@login_required(login_url='login')
@allowed_user(allowed_roles = ['customer'])
def accountSettings(request):
    user = request.user.customer

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES , instance= user)
        if form.is_valid():
            form.save()
            
    form = CustomerForm(instance= user)
    context = { 'form' : form}
    return render(request , 'accounts/account_settings.html' , context)


@login_required(login_url='login')
@allowed_user(allowed_roles = ['admin'])
def all_orders(request):
    orders = Order.objects.filter(status = 'Pending')
    # return HttpResponse(orders)

    return render(request , 'accounts/ordered_products.html' , {'orders' : orders})

@login_required(login_url='login')
@allowed_user(allowed_roles = ['admin'])
def products(request):
    products = Product.objects.all()
    return render(request , 'accounts/products.html' , {'product' : products})


@login_required(login_url='login')
@allowed_user(allowed_roles = ['admin'])
def customer(request , pk):

    customer = Customer.objects.get(id = pk)
    orders = customer.order_set.all()

    orders_count = orders.count()
    my_filter = OrderFilter(request.GET , queryset= orders) 
    orders = my_filter.qs


    context = {'customer': customer , 'orders': orders , 'orders_count' : orders_count , 'my_filter':my_filter}

    # return HttpResponse(context.cus)

    return render(request , 'accounts/customer.html' , context)


@login_required(login_url='login')
@allowed_user(allowed_roles = ['admin'])
def createOrder(request):
    form = OrderForm()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request , 'accounts/order_form.html' , context)


@login_required(login_url='login')
@allowed_user(allowed_roles = ['admin'])
def updateOrder(request , pk):

    order = Order.objects.get(id = pk)
    form = OrderForm(instance= order)

    if request.method == 'POST':
        form = OrderForm(request.POST , instance=order)

        if(form.is_valid()):
            form.save()
            return redirect('/')
    
    context = {'form': form}
    return render(request , 'accounts/order_form.html' , context)

@login_required(login_url='login')
@allowed_user(allowed_roles = ['customer'])
def deleteOrder(request , pk):
    order = Order.objects.get(id = pk)

    if request.method == 'POST':
        order.delete()
        return redirect('/')
    
    context = {'order': order}
    return render(request , 'accounts/delete.html' , context)


@login_required(login_url='login')
@allowed_user(allowed_roles = ['admin'])
def createProduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect('/')

    form = ProductForm()
    context = {'form': form}
    return render(request , 'accounts/product_form.html' , context)
   

@login_required(login_url='login')
@allowed_user(allowed_roles = ['admin'])
def updateProduct(request , pk):
    product = Product.objects.get(id = pk)
    form = ProductForm(instance= product)

    if request.method == 'POST':
        form = ProductForm(request.POST , instance=product)

        if(form.is_valid()):
            form.save()
            return redirect('/')
    
    context = {'form': form}
    return render(request , 'accounts/product_form.html' , context)


@login_required(login_url='login')
@allowed_user(allowed_roles = ['admin'])
def deleteProduct(request , pk):
    
    product = Product.objects.get(id = pk)

    if request.method == 'POST':
        product.delete()
        return redirect('/')
    
    context = {'product': product}
    return render(request , 'accounts/delete_product.html' , context)