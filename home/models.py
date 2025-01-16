from django.db import models
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.hashers import check_password





class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


# Define the Customer model
class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    address = models.TextField()
    phone_number = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    password = models.CharField(max_length=255)
    otp = models.CharField(max_length=6, blank=True, null=True)  # Store OTP
    otp_generated_at = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)

    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def check_password(self, password):
        """
        Check if the provided password matches the stored hash.
        """
        return check_password(password, self.password)
    

    def update_last_login(self):
        """Update the last login time to the current time."""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])


    def set_password(self, password):
        """
        Set a new password for the customer (store hashed password).
        """
        from django.contrib.auth.hashers import make_password
        self.password = make_password(password)



class Turf(models.Model):
    name = models.CharField(max_length=255)
    turf_type = models.CharField(max_length=255)
    timing_start = models.TimeField(null=True, blank=True)
    timing_end = models.TimeField(null=True, blank=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='turfs/')
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # Update available_services to ManyToManyField
    available_services = models.ManyToManyField(Service, blank=True)

    def __str__(self):
        return self.name




class Booking(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('canceled', 'Canceled'),
        ('pending', 'Pending'),

    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    duration_hours = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    def calculate_total_price(self):
        return self.turf.price_per_hour * self.duration_hours

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.customer} for {self.turf} on {self.booking_date}"


class Feedback(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name="feedbacks")  # Connects feedback to a specific turf
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Links feedback to the customer who gave it
    rating = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])  # Rating choices (1-5 stars)
    comments = models.TextField()  # Comments about the turf
    date_of_visit = models.DateField()  # The date the customer visited the turf
    feedback_type = models.CharField(max_length=50, choices=[('complaint', 'Complaint'), ('suggestion', 'Suggestion'), ('praise', 'Praise')])  # Type of feedback
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('reviewed', 'Reviewed')], default='pending')  # Feedback status (pending/reviewed)

    def __str__(self):
        return f"Feedback from {self.customer.user.username} on {self.turf.name}"

