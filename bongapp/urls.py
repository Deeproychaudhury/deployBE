from bongapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from .views import CustomPasswordResetView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("",views.index,name="home"),
    path("login",views.loginuser,name='loginuser'),
    path("logout",views.logoutuser,name='logoutuser'),
    path("signin",views.handlesignin,name='handlesignin'),
    path("prof/<str:username>/",views.prof,name='prof'),
    path("menu",views.menu,name='menu'),
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
    path("cart",views.cart,name='cart'),
    path("create-checkout-session",views.createcheckoutsession,name='/create-checkout-session'),
    path('success/', views.payment_success, name='payment_success'),
    path('stripe_webhook', views.stripe_webhook, name='stripe_webhook'),
    path('ordertracker',views.ordertracker,name="ordertracker"),
    path('list-orders/', views.list_orders, name='list_orders'),
    path('deleteprofile',views.deleteprofile,name="deleteprofile"),
    path("chatview",views.chatview,name="chat"),
    path("chat/<str:username>",views.get_or_createchatroom,name="start-chat"),
    path("chat/room/<chatroom_name>",views.chatview,name="chatroom"),
    path('chat/new_groupchat/', views.create_groupchat, name="new-groupchat"),
    path('chat/edit/<chatroom_name>', views.chatroom_edit_view, name="edit-chatroom"),
    path('chat/delete/<chatroom_name>', views.chatroom_delete_view, name="chatroom-delete"),
    path('chat/leave/<chatroom_name>', views.chatroom_leave_view, name="chatroom-leave"),
    path('halllist',views.halllist,name='halllist'),
    path('hallbookinglist',views.Hallbookinglist,name='hallbookinglist'),
    path('hallbooking',views.HallBookingView,name='hallbooking'),
    path('unblockuser/<chatroom_name>',views.unblockuser,name='unblockuser'),
    path('blockuser/<chatroom_name>',views.blockuser,name='blockuser'),
    path('deletechat/',views.deletechat,name='deletechat'),
    path('newsletter',views.messageboard_view,name='messageboard'),
    path('subscribe',views.subscribe,name='subscribe'),
    path('password_reset/<str:email>/<str:username>', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('send_otp/', views.send_otp_email, name='send_otp'),
    path('verify_otp/<str:email>/<str:username>/', views.verify_otp, name='verify_otp'),
    path('wishlist',views.makeWishlist,name='wishlist'),
    path('remove_wishlist/<int:id>',views.removeWishlist,name='remove_wishlist'),
    path('display_wishlist',views.displayWishlist,name='display_wishlist'),
    path('chat/fileupload/<chatroom_name>',views.chatfileupload,name='chatfileupload'),
       

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# store image url
