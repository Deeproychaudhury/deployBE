from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.forms import TextInput,EmailInput,ImageField
from django.contrib.auth.forms import *
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
class EmailForm(forms.Form):
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        if not User.objects.filter(username=username,email=email).exists():
            raise forms.ValidationError("There is no user associated with this email address.")
        return cleaned_data

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True)

    def clean(self):
        cleaned_data = super().clean()
        otp = cleaned_data.get('otp')
        email = self.initial['email']
        username = self.initial['username']
        try:
            user = User.objects.get(email=email, username=username)
            otp_instance = OTP.objects.get(user=user, otp=otp)
            if not otp_instance.is_valid():
                raise forms.ValidationError("This OTP has expired.")
        except OTP.DoesNotExist:
            raise forms.ValidationError("Invalid OTP.")
        return cleaned_data

class CustomPasswordResetForm(PasswordResetForm):
    username = forms.CharField(max_length=150, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if not User.objects.filter(username=username, email=email).exists():
            raise forms.ValidationError("There is no user with this username and email combination.")
        
        return cleaned_data

    def get_users(self, email):
        username = self.cleaned_data['username']
        return User.objects.filter(username=username, email=email)

    
class Chatform(forms.ModelForm):
    class Meta:
        model = Groupmessage
        fields = ['body']
        widgets = {
            'body': forms.TextInput(attrs={
                'placeholder': 'Add message...',
                'class': 'form-control form-control-lg',
                'id': 'textInput',
                'maxlength': '500',
                'autofocus': True,
                'style': 'border-radius: 20px; padding: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);'
            }),
        }

class NewGroupChatForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['groupchat_name']
        widgets = {
            'groupchat_name': forms.TextInput(attrs={
                'placeholder': 'Group name',
                'class': 'form-control form-control-lg',
                'id': 'textInput',
                'autofocus': True,
                'max_length': '50',
                
            }),
        }

class ChatRoomEditForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['groupchat_name']
        widgets = {
            'groupchat_name' : forms.TextInput(attrs={
                'class': 'form-control form-control-lg', 
                'maxlength' : '300', 
                }),
        }

class Userupdate(forms.ModelForm):
   email=forms.EmailField()

   class Meta:
      model =User
      fields=['username','email']
      widgets = {
            'username': TextInput(attrs={
                'class': "form-control",
                'placeholder': 'Name'
                }),
            'email': EmailInput(attrs={
                'class': "form-control", 
                'placeholder': 'Email',
                'required': True
                }),
        }
class Profileform(forms.ModelForm):
    phone = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': "form-control",
        'placeholder': 'Phone'
    }), required=True,validators=[ RegexValidator( regex='^\d{9,15}$', message='Plz use a proper phone number', code='nomatch')])
    review = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
        'placeholder': 'Review'
    }))
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
        'placeholder': 'Address'
    }),validators=[ RegexValidator( regex='^[a-zA-Z0-9\s,.\-]*$', message='Plz use a proper address', code='nomatch')])
    state = forms.CharField(required= True,widget=forms.TextInput(attrs={
        'class': "form-control",
        'placeholder': 'State',
    }),validators=[ RegexValidator( regex='^[a-zA-Z\s]*$', message='Plz use a proper state', code='nomatch')])
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': "form-control"
    }))

    class Meta:
        model = Profile  # Specify the model
        fields = ['image', 'phone', 'review', 'address', 'state']  # Specify the fields to include

class AvailabilityForm(forms.Form):
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
    
    category_choices = (
        ("Small", "Small"),
        ("Medium", "Medium"),
        ("Grand", "Grand"),
        ("Deluxe", "Deluxe"), )
    SEAT_CHOICES = (
        ("2","2"),
        ("4", "4"),
        ("10", "10"),
        ("buffet", "buffet"),
    )
    category= forms.ChoiceField( choices=category_choices, widget=forms.Select(attrs={'class': 'form-control'}), required=True)

    ammenity = forms.ChoiceField(
        choices=Ammenity_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    
    hallcapacity = forms.ChoiceField(
        choices=SEAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    checkin = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        ),
        required=True
    )
    
    checkout = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        ),
        required=True
    )

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.TextInput(attrs={
                'placeholder': 'Add message...',
                'class': 'form-control form-control-lg',
                'id': 'textInput',
                'maxlength': '2000',
                'autofocus': True,
                'style': 'border-radius: 20px; padding: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);'
            }),
        }