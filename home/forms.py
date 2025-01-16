from django import forms
from django import forms
from .models import Customer
from django.contrib.auth.hashers import make_password
from .models import Customer, Turf
from django import forms
from .models import Booking
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from django.core.exceptions import ValidationError
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password, make_password

class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Customer
        fields = ['first_name', 'middle_name', 'last_name', 'address', 'phone_number', 'gender', 'email', 'photo', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

    def save(self, commit=True):
        customer = super().save(commit=False)
        customer.password = make_password(self.cleaned_data['password'])
        if commit:
            customer.save()
        return customer

class TurfForm(forms.ModelForm):
    class Meta:
        model = Turf
        fields = [
            'name',
            'turf_type',
            'timing_start',
            'timing_end',
            'price_per_hour',
            'location',
            'image',
            'rating',
            'description'
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'duration_hours']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UpdatePasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'readonly': 'readonly'}))  # Email is read-only
    old_password = forms.CharField(widget=forms.PasswordInput, label="Old Password", required=True)
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password", required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm New Password", required=True)

    def __init__(self, *args, **kwargs):
        # Pop 'customer' from kwargs and pass it to the form
        self.customer = kwargs.pop('customer', None)
        super(UpdatePasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = self.customer.email  # Set initial email value from customer

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')  # Corrected reference to 'old_password'

        # Ensure old password is not empty before checking
        if not old_password:
            raise ValidationError("Old password is required.")

        # Check if the old password matches the customer's current password
        if not self.customer.check_password(old_password):
            raise ValidationError("Old password is incorrect.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password')
        new_password2 = cleaned_data.get('confirm_password')

        if old_password is None or new_password1 is None or new_password2 is None:
            raise forms.ValidationError("Please fill out all required fields.")

        
        if new_password1 != new_password2:
            raise forms.ValidationError("The two new passwords do not match.")

        return cleaned_data

    def save(self):
        
        new_password = self.cleaned_data['new_password']
        self.customer.set_password(new_password)
        self.customer.save() 
        return self.customer

