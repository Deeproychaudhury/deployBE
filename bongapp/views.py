from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from django.db import transaction
from django.http import HttpResponseBadRequest,Http404,HttpResponseForbidden
from datetime import datetime,timedelta
from django.contrib import messages
from django.conf import settings
from .tasks import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout,login 
from .forms import Profileform,Userupdate,Chatform,NewGroupChatForm,ChatRoomEditForm,AvailabilityForm,MessageForm,CustomPasswordResetForm,EmailForm,OTPForm
from .models import Profile,Product,OrderModel,ChatGroup,Groupmessage,Hall,HallBookings,MessageBoard,Message
from django.core.mail import EmailMessage,send_mail
from django.contrib.auth import get_user_model
from math import ceil
from django.views import View
import json
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Count
from django.contrib import messages
from django.http import JsonResponse
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import threading
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.
def send_otp_email(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            messages.info(request, f"An OTP has been sent to {email}.{username}")
            user = User.objects.get(username=username, email=email)
            otp = get_random_string(6, '0123456789')
            OTP.objects.create(user=user,otp=otp)
            subject = 'OTP for password reset'
            message = f'Your OTP is {otp}'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            return redirect('verify_otp', email=email, username=username)
        else:
            
            messages.error(request, f"Invalid email or username.")
    else:
        form = EmailForm()
    return render(request, 'registration/send_otp_email.html', {'form': form})

def verify_otp(request, email, username):
    if request.method == 'POST':
        form = OTPForm(request.POST, initial={'email': email, 'username': username})
        if form.is_valid():
            user = User.objects.get(username=username,email=email)
            otp=OTP.objects.get(user=user,otp=form.cleaned_data['otp'])
            otp.delete()
            return redirect('password_reset', email=email, username=username)
    else:
        form = OTPForm(initial={'email': email, 'username': username})
    return render(request, 'registration/verify_otp.html', {'form': form})

class CustomPasswordResetView(auth_views.PasswordResetView):
    def get_initial(self):
        initial = super().get_initial()
        initial['email'] = self.kwargs['email']
        initial['username'] = self.kwargs['username']
        return initial
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    template_name = 'registration/password_reset_form.html'

def logoutuser(request):
    logout(request)
    # Redirect to a success page.
    return redirect('/')



def loginuser(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if user is not None:
            # A backend authenticated the credentials
            login(request, user)
            if is_ajax:
                return JsonResponse({"success": True}, status=200)
            else:
                return redirect("/")
        else:
            error_message = "Invalid username or password."
            if is_ajax:
                return JsonResponse({"error": error_message}, status=400)
            else:
                messages.error(request, error_message)
                return render(request, 'login.html')
    return render(request, 'login.html')
  
def index(request):
    messageboard = get_object_or_404(MessageBoard, id=1)
    form=AvailabilityForm()
    if request.user.is_anonymous:
        value="customer"
        sign=False
    else:
       value=request.user.username
       sign=True
    context={
        'value':value,
        'sign':sign,
        'form':form,
        'messageboard': messageboard 
             }
    return render(request,'index.html',context)


def uns(request):
    return render(request,'monthly_newsletter.html')



def handlesignin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        name = request.POST.get('name')
        title = request.POST.get('title')  
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        # Check if all required fields are provided
        if not name or not email or not password or not title:
            messages.error(request, "All fields are required.")
            return redirect("/signin")
        
        if len(phone) < 10:
            messages.error(request, "Phone number must be at least 10 digits long.")
            return redirect("/signin")

        # Create the user
        try:
            myuser = User.objects.create_user(username=name, email=email, password=password)
            myuser.first_name = name
            myuser.last_name = title  # Assign the title or last name
            myuser.profile.phone = phone
            myuser.save()
            
            # Send a welcome email
            subject = 'Welcome to INDOBITES'
            message = f'Hi {myuser.username}, thank you for registering'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = myuser.email
            # send_mail(subject, message, email_from, recipient_list)
            send_email_task.delay(subject, message, str(recipient_list))

            # Authenticate and log the user in
            user = authenticate(username=name, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Profile created successfully.')
                return redirect("/")
            else:
                messages.error(request, "Authentication failed. Please try logging in.")
                return redirect("/login")

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect("/signin")

    return render(request, 'CreateAccount.html')


def prof(request, username):
    if request.user.is_anonymous:
        return redirect("/login")

    user = get_object_or_404(User, username=username)

    # If the logged-in user is viewing another user's profile
    if request.user.username != username:
        return render(request, 'ProfileDifferent.html', {'user': user})

    if request.method == 'POST':
        uform = Userupdate(request.POST, instance=request.user)
        pform = Profileform(request.POST, request.FILES, instance=request.user.profile)

        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, f"Profile update done")
            return redirect(f"/prof/{request.user.username}")
        else:
             for field, errors in uform.errors.items():
                for error in errors:
                    messages.error(request, f"User Form Error in {field}: {error}")
             for field, errors in pform.errors.items():
                for error in errors:
                    messages.error(request, f"Profile Form Error in {field}: {error}")
    else:
        uform = Userupdate(instance=request.user)
        pform = Profileform(instance=request.user.profile)
    context = {
        'uform': uform,
        'pform': pform,
    }
    return render(request, 'ProfileCustomer.html', context)
def deleteprofile(request):
     user = request.user
     if request.method == "POST":
        logout(request)
        user.delete()
        return redirect("/")
     
def is_staff_or_admin(user):
    return user.is_staff or user.is_superuser

def menu(request):
   if request.method == 'POST':
      filter_query=request.POST.get('select')
      search_query=request.POST.get('searchMenu')
   else:
      filter_query='Biriyani'
      search_query='###'
   if search_query=="":
      search_query="###"
   prodobject=Product.objects.all()
   cat1= Product.objects.filter(category=filter_query)
   cati2=prodobject.filter( product_name__icontains=search_query)|prodobject.filter(category__icontains=search_query)|prodobject.filter(price__startswith=search_query)
   cat2=cati2.values()
   if request.user.is_anonymous:
        value="customer"
        sign=False
   else:
       value=request.user.username
       sign=True
    
   context={
         'objects':prodobject,
         'value':value,
         'sign':sign,
         'cat1':cat1,
         'deli':filter_query,
         'cat2':cat2

    }
   return render(request,'menu.html',context)

@login_required(login_url='/login')
def add_to_cart(request):
    if request.method=='POST':
     product=request.POST.get('obj_id')
     quantity=request.POST.get('quantity')
     if not product or not quantity:
         messages.error(request,"Invalid input in add to cart")
    phone= request.user.profile.phone 
    try:
            product = Product.objects.get(id=product)
    except Product.DoesNotExist:
            return HttpResponseBadRequest("Product not found")
    
    order=OrderModel(
        product=product,
        phone=phone,
        customer=request.user,
        quantity=quantity,
        price=product.price * int(quantity)
        
     )
    order.save()
    messages.success(request,"Item added. Proceed to checkout or add browse other items")
    return redirect('menu')

@login_required(login_url='/login')
def cart(request):
      orders=OrderModel.objects.filter(customer=request.user,payment_status=False)
      count=orders.count() #count number of orders
      sum=0
      for ord in orders:
          sum+=ord.price
      if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')

        order = get_object_or_404(OrderModel, id=order_id, customer=request.user)

        if action == 'update':
            quantity = request.POST.get('quantity')
            if quantity is not None:
                try:
                    new_quantity = int(quantity)
                    if new_quantity > 0:
                        order.quantity = new_quantity
                        order.price = order.product.price * new_quantity
                        order.save()
                    else:
                        order.delete()
                        messages.success(request, "Item removed from cart")
                except ValueError:
                    messages.error(request, "Invalid quantity")
        elif action == 'delete':
            order.delete()
            messages.success(request, "Item removed from cart")

        return redirect('cart')

      return render(request, 'Cart.html', {'orders': orders, 'count': count, 'value': request.user.username, 'sum': sum})

#HAndle payment

stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = "http://127.0.0.1:8000"
TAX_RATE=stripe.TaxRate.create(
  display_name="GST",
  inclusive=False,
  percentage=18,
  country="IN",
  description="IN Tax",
)
TAX_RATE_ID=TAX_RATE.id

@login_required(login_url='/login')
@csrf_exempt
def createcheckoutsession(request):
    order_id = "Pending"
    totalprice = 0
    line_items = []
    orders = OrderModel.objects.filter(customer=request.user, payment_status=False)

    for order in orders:
        totalprice += order.price
        product = order.product
        if not product.stripe_price_id:
            # Create a product in Stripe if it doesn't exist
            stripe_product = stripe.Product.create(name=product.product_name)
            product.stripe_product_id = stripe_product.id
            product.save()

            # Create a price for the product in Stripe
            price = stripe.Price.create(
                product=stripe_product.id,
                unit_amount=product.price * 100,  # amount in the smallest currency unit
                currency="inr",
            )
            product.stripe_price_id = price.id
            product.save()

        line_items.append({
            'price': product.stripe_price_id,
            'quantity': order.quantity,
            'tax_rates':[TAX_RATE_ID]

        })

    if request.method == 'POST':
        try:
            checkout_session = stripe.checkout.Session.create(

                line_items=line_items,
                mode='payment',
                success_url=YOUR_DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=YOUR_DOMAIN + '/cart',
            )
            order_id = checkout_session.id
            for ord in orders:
                ord.stripe_checkout_session_id = checkout_session.id
                ord.save()
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return render(request, 'payment.html', {'order_id': order_id})

@login_required(login_url='/login')
def payment_success(request):
    orders = OrderModel.objects.filter(customer=request.user, payment_status=False)
    checkout_session_id = request.GET.get('session_id', None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    for order in orders:
        order.payment_status = True
        order.stripe_checkout_sessionid=checkout_session_id
        order.save()
    return render(request, 'success.html',{'session':checkout_session_id})

import time
@csrf_exempt
def stripe_webhook(request):
    time.sleep(10)
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponseBadRequest()
    except stripe.error.SignatureVerificationError as e:
        return HttpResponseBadRequest()
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_details', {}).get('email', '')
        # Mark orders as paid
        orders=OrderModel.objects.filter(customer=request.user, payment_status=False)
        for order in orders:
            order.payment_status = True
            checkout_session_id = request.GET.get('session_id', None)
            order.stripe_checkout_sessionid=checkout_session_id
            order.date=datetime.today()
            order.save()
        subject = 'Payment Receipt'
        message = f'Thank you for your payment. Your order details are as follows:\n\n'
        for order in orders:
            message += f'Order ID: {order.id} and Session Id : {checkout_session_id}\n'
            message += f'Product: {order.product.product_name}\n'
            message += f'Quantity: {order.quantity}\n'
            message += f'Total Price: {order.price}\n'
            message += f'Status: {"Paid" if order.payment_status else "Pending"}\n\n'
        message += 'Thank you for shopping with us!'

        if request.user.email or customer_email:
            # send_mail(
            #     subject,
            #     message,
            #     settings.EMAIL_HOST_USER,
            #     [request.user.email,customer_email],
            #     fail_silently=False,
            # )
            send_email_task.delay(subject, message, str(request.user.email))
    return HttpResponse(status=200)

@login_required(login_url='/login')
def ordertracker(request):
    if request.user.is_anonymous:
        sign=False
    else:
        sign=True
    orders = OrderModel.objects.filter(customer=request.user, payment_status=True)
    return render(request, 'ordertracker.html', {'orders': orders,'sign':sign})


@user_passes_test(is_staff_or_admin, login_url='/login')
def list_orders(request):
    if request.user.is_anonymous:
        sign=False
    else:
        sign=True
    orders = OrderModel.objects.all().select_related('customer', 'product')
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        order = OrderModel.objects.get(id=order_id)
        order.status = status
        order.save()
        return redirect('list_orders')
    return render(request, 'list_orders.html', {'orders': orders,'sign':sign})


@login_required(login_url='/login')
def chatview(request,chatroom_name='Public-chat'):
    if request.user.is_anonymous:
        sign=False
    else:
        sign=True
    chat_group=get_object_or_404(ChatGroup,groupname=chatroom_name)
    chat_messages=chat_group.chat_messages.all()[:100]
    form=Chatform()
    other_user=None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404("You are not allowed here")
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break
    
    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
          if request.user not in chat_group.banlist.all():  
            chat_group.members.add(request.user)

    if request.method =='POST':
        form=Chatform(request.POST)
        if form.is_valid:
            message=form.save(commit=False)
            message.author = request.user
            message.group=chat_group
            message.save()
            context = {
                'message' : message,
                'user' : request.user
            }
            return render(request,'partials/chat_message_p.html',context)
    context={
'chat_messages':chat_messages,
'form':form,
'otheruser':other_user,
'chatroom_name':chatroom_name,
'chat_group':chat_group,
'sign':sign
    }    
    return render(request,'chat.html',context)

@login_required(login_url="/login")
def get_or_createchatroom(request,username):
    if request.user.username == username:
        return redirect('')
    other_user = User.objects.get(username = username)
    my_chatrooms = request.user.chat_groups.filter(is_private=True)
    if my_chatrooms.exists():
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
             if other_user not in chatroom.banlist.all():
                chatroom=chatroom
                break
            else:
                chatroom=ChatGroup.objects.create(is_private=True)
                chatroom.members.add(other_user,request.user)
    else:
        chatroom=ChatGroup.objects.create(is_private=True)
        chatroom.members.add(other_user,request.user)
    return redirect('chatroom', chatroom.groupname)

@login_required(login_url="/login")
def create_groupchat(request):
    form=NewGroupChatForm()
    if request.method == 'POST':
        form = NewGroupChatForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect('chatroom', new_groupchat.groupname)
    
    context = {
        'form': form
    }
    return render(request,'create_groupchat.html',context)

login_required(login_url="/login")
def chatroom_edit_view(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup, groupname=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    form=ChatRoomEditForm(instance=chat_group)
    if request.method == 'POST':
        form = ChatRoomEditForm(request.POST, instance=chat_group)
        if form.is_valid():
            form.save()
            remove_members = request.POST.getlist('remove_members')
            for member_id in remove_members:
                member = User.objects.get(id=member_id)
                if member not in chat_group.banlist.all():
                    chat_group.banlist.add(member)
                chat_group.members.remove(member)  
            ban_members = request.POST.getlist('ban_members')
            if ban_members:
                for member_id in ban_members:
                    member = User.objects.get(id=member_id)
                    if member  in chat_group.banlist.all():
                        chat_group.banlist.remove(member)
                    chat_group.members.add(member)
                
            return redirect('chatroom', chatroom_name)
    return render(request,'chatroomedit.html',{
        'form' : form,
        'chat_group' : chat_group
    } )

@login_required(login_url="/login")
def chatroom_delete_view(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup, groupname=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    else:
        chat_group.delete()
        return redirect('/')
    
def chatroom_leave_view(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup, groupname=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()
    else:
        chat_group.members.remove(request.user)
        return redirect('/')    

from bongapp.availability import availability

def halllist(request):
    rooms = Hall.objects.all()  # Query all Room objects
    return render(request, 'room_list.html', {'rooms': rooms})
def Hallbookinglist(request):
    if request.user.is_anonymous:
        sign:False
    else:
        sign=True  
    bookings = HallBookings.objects.all()  # Query all Booking objects
    return render(request, 'booking_list.html', {'bookings': bookings,'sign':sign})

@login_required(login_url='/login')
def HallBookingView(request):
    if request.user.is_anonymous:
        sign:False
    else:
        sign=True    
    form=AvailabilityForm()
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            hall_list=Hall.objects.filter(category=data['category'])
            available_halls=[]
            with transaction.atomic():
              for hall in hall_list:
                if availability(hall,data['checkin'],data['checkout']):
                    available_halls.append(hall)
              if len(available_halls)>0:
               hall= available_halls[0]
               # Check if Stripe product and price exist, if not create them
               if not hall.stripe_product_id:
                        product = stripe.Product.create(name=f"Hall {hall.number} ({hall.category})")
                        hall.stripe_product_id = product.id
                        hall.save()

               if not hall.stripe_price_id:
                        price = stripe.Price.create(
                            product=hall.stripe_product_id,
                            unit_amount=int(hall.price_per_hour * 100),  # amount in cents
                            currency="inr",
                        )
                        hall.stripe_price_id = price.id
                        hall.save()
               booking=HallBookings.objects.create(Hall=hall,ammenity=data['ammenity'],customer=request.user,checkin=data['checkin'],checkout=data['checkout'])

               session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price': hall.stripe_price_id,
                            'quantity': 1,
                            'tax_rates':[TAX_RATE_ID]
                        }],
                        mode='payment',
                        success_url=YOUR_DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
                        cancel_url=YOUR_DOMAIN + '/hallbooking',
                    )
               booking.stripe_checkout_sessionid = session.id
               booking.save()
               if booking.payment_status:
                   subject: str = 'Hall Booking Confirmation'
                   message: str = f'Your hall booking has been confirmed. Details are as follows:\n\n'
                   message += f'Booking ID: {HallBookings.id},Hall number:{HallBookings.Hall.number}\n'
                   message += f'Category: {HallBookings.Hall.category}\n'
                   message += f'Check-in: {HallBookings.checkin}\n'
                   message += f'Check-out: {HallBookings.checkout}\n'
                   message += f'Ammenity: {HallBookings.ammenity}\n'
                   checkout_session_id = request.GET.get('session_id', None)
                   message += f'Session ID: {checkout_session_id}\n'
                   send_email_task.delay(subject, message, str(request.user.email))
               messages.success(request, "Hall booked successfully")
               return redirect(session.url)
               
              else:
                messages.error(request, "No hall available for the selected dates")
            
    context = { 'form': form,'sign':sign} 
    return render(request, 'booking_form.html', context)

@login_required(login_url='/login')
def unblockuser(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup, groupname=chatroom_name)
    if request.method == 'POST':
        user_id = request.POST.get('otheruserid')
        user = User.objects.get(id=user_id)
        if user in chat_group.banlist.all():
         chat_group.banlist.remove(user)
    return redirect('chatroom', chatroom_name)

@login_required(login_url='/login')
def blockuser(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup, groupname=chatroom_name)
    if request.method == 'POST':
        otheruser_id = request.POST.get('otheruserid')
        user = User.objects.get(id=otheruser_id)
        if user not in chat_group.banlist.all():
         chat_group.banlist.add(user)
        
        return redirect('chatroom', chatroom_name)
    return redirect('chatroom', chatroom_name)

@csrf_exempt
def deletechat(request):
    if request.method == 'POST':
        message_id=request.POST.get('message_id')
        message=Groupmessage.objects.get(id=message_id)
        message.delete()
        return redirect('chatroom', message.group.groupname)
    return redirect('chatroom', message.group.groupname)


@user_passes_test(is_staff_or_admin, login_url='/login')
def messageboard_view(request):
    messageboard = get_object_or_404(MessageBoard, id=1)
    subscribers = messageboard.subscribers.all()
    form=MessageForm()
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.messageboard = messageboard
            message.author = request.user
            message.save()
            for subscriber in subscribers:
                body= f'{message.author.username}: {message.body}\n\nRegards from\nMy Message Board'
                send_email_task.delay('New message on the messageboard', body,str(subscriber.email))
            
            return redirect('messageboard')
      
    return render(request, 'sendnewsletter.html', {'messageboard': messageboard, 'form': form})

@login_required(login_url='/login')
def subscribe(request):
    messageboard = get_object_or_404(MessageBoard, id=1)
    if request.user in messageboard.subscribers.all():
        messageboard.subscribers.remove(request.user)
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            request.user.email = email
            request.user.save()
            if request.user not in messageboard.subscribers.all:
                messageboard.subscribers.add(request.user)
            return redirect('/')
        else:
            if request.user not in messageboard.subscribers.all():
                messageboard.subscribers.add(request.user)
    return redirect('/')

# views.py

from collections import defaultdict
def dashboard(request):
    transactions = stripe.PaymentIntent.list(limit=100)  # Adjust the limit as needed
    transactions_data = transactions['data']    
    # Calculate total amount earned each day
    daily_earnings = defaultdict(int)
    for transaction in transactions_data:
        if transaction['status'] == 'succeeded':
            created = datetime.fromtimestamp(transaction['created'])
            day = created.strftime("%Y-%m-%d")  # Format as 'YYYY-MM-DD'
            daily_earnings[day] += transaction['amount_received'] / 100  # Convert from cents to dollars
    # Prepare data for Chart.js
    labels = list(daily_earnings.keys())
    data = list(daily_earnings.values())

    context = {
        'transactions': transactions_data,
        'labels': labels,
        'data': data,
    }

    return render(request, 'dashboard.html', context)

@login_required(login_url='/login')
@csrf_exempt
def makeWishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            messages.error(request, "Product already in wishlist")
        else:
            messages.success(request, "Product added to wishlist")
    return redirect('menu')

def displayWishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist': wishlist})

def removeWishlist(request, product_id):
    product_id = request.POST.get('product_id')
    product = Product.objects.get(id=product_id)
    wishlist = Wishlist.objects.get(user=request.user, product=product)
    wishlist.delete()
    messages.success(request, "Product removed from wishlist")
    return redirect('display_wishlist')

def chatfileupload(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup, groupname=chatroom_name)
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        message = Groupmessage.objects.create(author=request.user, group=chat_group, file=file)
        channel_layer = get_channel_layer()
        event={
            'type':'message_handler',
            'message_id': message.id
        }
        async_to_sync(channel_layer.group_send)(chatroom_name,event)
        return HttpResponse()
    return HttpResponse()