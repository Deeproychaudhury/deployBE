from django.contrib import admin
# Register your models here.
from .models import Profile,Product,OrderModel,ChatGroup,Groupmessage,Hall,HallBookings,MessageBoard,Message,Wishlist,OTP
class ProductAdmin(admin.ModelAdmin):
    list_display=['product_name','category','price']
class OrderModelAdmin(admin.ModelAdmin):
    list_display=['product','customer','phone']
admin.site.register(Profile)
admin.site.register(Product,ProductAdmin)
admin.site.register(OrderModel,OrderModelAdmin)
admin.site.register(ChatGroup)
admin.site.register(Groupmessage)
admin.site.register(Hall)
admin.site.register(Wishlist)
admin.site.register(Message)
admin.site.register(MessageBoard)
admin.site.register(HallBookings)
admin.site.register(OTP)