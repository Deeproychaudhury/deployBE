from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from PIL import Image
from shortuuid.django_fields import ShortUUIDField
from datetime import timedelta
from django.utils import timezone
from PIL import Image
import mimetypes

from cloudinary_storage.storage import MediaCloudinaryStorage, RawMediaCloudinaryStorage, VideoMediaCloudinaryStorage

# For images
class YourImageModel(models.Model):
    image = models.ImageField(storage=MediaCloudinaryStorage())

# For raw files (e.g., txt, pdf)
class YourRawFileModel(models.Model):
    file = models.FileField(storage=RawMediaCloudinaryStorage())

# For videos
class YourVideoModel(models.Model):
    video = models.FileField(storage=VideoMediaCloudinaryStorage())

REVIEW_CHOICES = (
    ("1 star", "1 star"),
    ("2 star", "2 star"),
    ("3 star", "3 star"),
    ("4 star", "4 star"),
    )
SEAT_CHOICES = (
    ("2","2"),
    ("4", "4"),
    ("10", "10"),
    ("buffet", "buffet"),
    )

from io import BytesIO
from django.core.files.base import ContentFile
# Create your models here. DJANGO already comes with a built in user model 
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', default='media/profile_pics/ojfe8l5ulh2cyuy1wuiv') 
    phone = models.BigIntegerField(default=0000)
    review = models.TextField(default='No review', max_length=525)
    address = models.CharField(max_length=300, default='No address')
    state = models.CharField(max_length=111, default='No state')

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

class Product(models.Model):
    product_id=models.AutoField
    product_name=models.CharField(max_length=100)
    category=models.CharField(max_length=50,default="")
    subcategory=models.CharField(max_length=70,default="spe")
    price=models.IntegerField(default=0)
    oldprice=models.IntegerField(default=330)
    image=models.ImageField(upload_to="shop",default="demo.jpg") # store image
    description=models.CharField(max_length=500)
    pub_date=models.DateField()
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_product_id=models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
       return self.product_name

class OrderModel(models.Model):
    status_choices = (
        (1, 'Not Packed'),
        (2, 'Ready'),
        (3, 'Delivered')
    )
    created_on=models.DateTimeField(auto_now_add=True)
    price=models.IntegerField(default=0)
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,default=0)
    customer = models.ForeignKey(User,
                                 on_delete=models.CASCADE,default=0)
    quantity = models.IntegerField(default=1)
    phone = models.CharField(max_length=50, default='', blank=True)
    status = models.IntegerField(choices = status_choices, default=1)
    payment_status = models.BooleanField(default=False)
    stripe_checkout_sessionid=models.CharField(max_length=255, blank=True, null=True)
    date=models.DateField(default=datetime.today,blank=True)   


    def __str__(self):
        return f'Order: {self.created_on.strftime("%b %d %I: %M %p")}'
    def delete_if_outdated(self):
        #"""Delete if the current date is more than a week after the checkout date."""
        one_week_after_checkout = self.date + timedelta(weeks=3)
        if timezone.now() > one_week_after_checkout:
            self.delete()
            return True
        return False

import shortuuid      
class ChatGroup(models.Model):
    groupname=models.CharField(max_length=100,unique=True,blank=True)
    groupchat_name = models.CharField(max_length=128, null=True, blank=True)
    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank=True)
    admin = models.ForeignKey(User,related_name='groupchats',blank=True,null=True,on_delete=models.SET_NULL)
    members = models.ManyToManyField(User, related_name='chat_groups', blank=True)
    is_private = models.BooleanField(default=False)
    banlist = models.ManyToManyField(User, related_name='banned_from_groups', blank=True)
    def __str__(self):
        return self.groupname

    def save(self, *args, **kwargs):
        if not self.groupname:
            self.groupname = shortuuid.uuid()
        super().save(*args, **kwargs)


class Groupmessage(models.Model):
    group=models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    author=models.ForeignKey(User,on_delete=models.CASCADE)  
    body=models.CharField(max_length=500,null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        if self.body:
         return f'{self.author.username} : {self.body}'
        elif self.file:
         return f'{self.author.username} : {self.file}'
    
    @property    
    def is_image(self):
        try:
            image = Image.open(self.file) 
            image.verify()
            return True 
        except:
            return False
        
    def save(self, *args, **kwargs):
        if self.file:
            mime_type, encoding = mimetypes.guess_type(self.file.name)
            if mime_type and mime_type.startswith('image'):
                self.file.storage = MediaCloudinaryStorage()
            elif mime_type and mime_type.startswith('video'):
                self.file.storage = VideoMediaCloudinaryStorage()
            elif mime_type:
                self.file.storage = RawMediaCloudinaryStorage()
            else:
                raise ValueError("Unsupported file type")

        super(Groupmessage, self).save(*args, **kwargs)
    
    class Meta:
        ordering=['-created']

class Hall(models.Model):

    category_choices = (
        ("Small", "Small"),
        ("Medium", "Medium"),
        ("Grand", "Grand"),
        ("Deluxe", "Deluxe"),
    )
    number=models.IntegerField()
    category=models.CharField(max_length=100, choices=category_choices, default="")
    hallcapacity=models.CharField(max_length=100, choices=SEAT_CHOICES, default="2")
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_product_id=models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
     return f"Hall {self.number}"
    
class HallBookings(models.Model):
    Ammenity_CHOICES = (
    ("Buffet","Buffet"),
    ("Cafeteria-Style", "Cafeteria-Style"),
    ("Pre-Set Service", "Pre-Set Service"),
    ("Cocktail-Style", "Cocktail-Style"),
    ("Cabaret", "Cabaret"),
    ("Banquet-Style", "Banquet-Style"),
    ("Dinner-Dance", "Dinner-Dance"),
    ("Exhibition", "Exhibition"),
    ("Plated", "Plated"),
    ("Meeting-Style", "Meeting-Style"),   
    )
    booking_id=models.CharField(max_length=100,unique=True,blank=True,default=shortuuid.uuid)
    Hall= models.ForeignKey(Hall, on_delete=models.CASCADE)
    ammenity=models.CharField(max_length=100, choices=Ammenity_CHOICES, default="")
    customer = models.ForeignKey(User,on_delete=models.CASCADE,default=0)
    checkin=models.DateTimeField()
    checkout=models.DateTimeField()
    payment_status = models.BooleanField(default=False)
    stripe_checkout_sessionid=models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f'{self.Hall} Booked by {self.customer.username}'
    def delete_if_outdated(self):
        """Delete the booking if the current date is more than a week after the checkout date."""
        one_week_after_checkout = self.checkout + timedelta(weeks=3)
        if timezone.now() > one_week_after_checkout:
            self.delete()
            return True
        return False
    

class MessageBoard(models.Model):
    subscribers = models.ManyToManyField(User, related_name='messageboard', blank=True)
    def __str__(self):
        return str(self.id)
    
class Message(models.Model):
    messageboard = models.ForeignKey(MessageBoard, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    body = models.CharField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']
        
    def __str__(self):
        return self.author.username
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'otp')

    def is_valid(self):
        # OTP is valid for 10 minutes
        now = timezone.now()
        expiry_time = self.created_at + timedelta(minutes=10)
        return now <= expiry_time
    def __str__(self):
        return f"{self.user.username} - {self.otp}"
    

