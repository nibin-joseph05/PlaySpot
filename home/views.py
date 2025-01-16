from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import random
from .ml_utils import get_best_match, load_faq_data
from django.shortcuts import render
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import Avg
from django.shortcuts import render
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from .models import Customer, Turf, Booking
from .forms import CustomerRegistrationForm, TurfForm, UpdatePasswordForm, BookingForm
from io import BytesIO
from .models import Feedback, Turf




def home(request):
    return render(request, 'home/home.html')

def about(request):
    return render(request, 'home/about.html')

def contact(request):
    return render(request, 'home/contact.html')

def uabout(request):
    return render(request, 'customer/uabout.html')

def ucontact(request):
    return render(request, 'customer/ucontact.html')

def booking(request):
    return render(request, 'customer/booking.html')



def customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Using get() to avoid KeyError
        password = request.POST.get('password')

        if email == 'admin@gmail.com':
            # Admin login check
            if password == 'admin':  # Update with a secure method if needed
                try:
                    user = User.objects.get(username='admin')
                    if user.is_staff:
                        login(request, user)
                        messages.success(request, "Admin logged in successfully.")
                        return redirect('admin01')  # Redirect to admin page
                    else:
                        messages.error(request, "Admin user is not authorized.")
                except User.DoesNotExist:
                    messages.error(request, "Admin account not found.")
            else:
                messages.error(request, "Invalid admin credentials.")
        
        else:
            # Customer login check
            try:
                customer = Customer.objects.get(email=email)
                if check_password(password, customer.password):
                    # Store customer_id in the session for later use
                    request.session['customer_id'] = customer.id
                    messages.success(request, "You are now logged in.")
                    
                    # Redirect to 'customer' page or the page they tried to access
                    next_url = request.GET.get('next', 'customer')  # Default to 'customer' page
                    return redirect(next_url)
                else:
                    messages.error(request, "Invalid login credentials.")
            except Customer.DoesNotExist:
                messages.error(request, "Invalid login credentials.")
    
    return render(request, 'home/login.html')


# Logout view for customer
def customer_logout(request):
    logout(request)  # Clears the session
    messages.success(request, "You have been logged out.")
    return redirect('login')


def customer_page(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')  # Redirect to login if customer_id is not found in session
    
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return redirect('login')  # Optionally, redirect to login if customer not found

    return render(request, 'customer/customer_page.html', {'customer': customer})

def register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful!")
            return redirect('login')
        else:
            print(form.errors)  # Debugging line to print errors
            messages.error(request, "Registration failed. Please check the details and try again.")
    else:
        form = CustomerRegistrationForm()
    return render(request, 'home/register.html', {'form': form})


# Admin View (for admins only)
def admin_view(request):
    return render(request, 'admin/admin.html')

# Turf Views for Admin
def turf_list(request):
    turfs = Turf.objects.all()
    return render(request, 'admin/turf_list.html', {'turfs': turfs})

def add_turf(request):
    if request.method == 'POST':
        form = TurfForm(request.POST, request.FILES)
        if form.is_valid():
            turf = form.save(commit=False)
            turf.save()
            messages.success(request, "Turf Added successfully.")
            return redirect('admin01')  # Replace with your admin dashboard or turf list view
    else:
        form = TurfForm()
    return render(request, 'admin/add_turf.html', {'form': form})

def delete_turf(request, turf_id):
    try:
        turf = Turf.objects.get(id=turf_id)
    except Turf.DoesNotExist:
        raise Http404("Turf not found")
    if request.method == 'POST':
        turf.delete()
        messages.success(request, "Turf deleted successfully.")
        return redirect('turf_list')  # Replace with actual turf list URL
    return render(request, 'admin/delete_turf.html', {'turf': turf})

def edit_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    if request.method == 'POST':
        form = TurfForm(request.POST, request.FILES, instance=turf)
        if form.is_valid():
            turf = form.save(commit=False)
            turf.timing_start = request.POST.get('timing_start')
            turf.timing_end = request.POST.get('timing_end')
            turf.save()
            messages.success(request, "Turf updated successfully.")
            return redirect('turf_list')
        else:
            messages.error(request, "Error updating turf.")
    else:
        form = TurfForm(instance=turf)
    return render(request, 'admin/edit_turf.html', {'form': form, 'turf': turf})

def customer_list(request):
    # Get all customers from the database
    customers = Customer.objects.all()
    return render(request, 'admin/customer_list.html', {'customers': customers})


def customer_delete(request, customer_id):
    # Get the customer object or return a 404 if not found
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        # If the method is POST, delete the customer and show a success message
        customer.delete()
        messages.success(request, "Customer deleted successfully.")
        return redirect('customer_list')  # Redirect to the customer list page after deletion

    # If the method is GET, show the confirmation page
    return render(request, 'admin/customer_delete.html', {'customer': customer})

def customer_details(request):
    # Fetch the customer_id from the session
    customer_id = request.session.get('customer_id')

    if customer_id is None:
        # Handle case where customer_id is not found in the session
        messages.error(request, "Customer ID not found. Please log in again.")
        return redirect('login')  # Redirect to login page if not logged in

    # Fetch the customer object based on the customer_id from session
    customer = get_object_or_404(Customer, id=customer_id)

    return render(request, 'customer/customer_details.html', {'customer': customer})




def turf_details(request):
    # Get all turfs
    turfs = Turf.objects.all()

    # Define the star range outside the loop
    star_range = range(1, 6)

    # Loop through turfs and calculate the average rating
    for turf in turfs:
        # Calculate average rating for each turf
        avg_rating = Feedback.objects.filter(turf=turf).aggregate(Avg('rating'))['rating__avg']
        turf.avg_rating = avg_rating if avg_rating is not None else 0  # Default to 0 if no ratings

    return render(request, 'customer/customer_turf_list.html', {'turfs': turfs, 'star_range': star_range})



def search_turf(request):
    location = request.GET.get('location')
    if location:
        turfs = Turf.objects.filter(location__icontains=location)
    else:
        turfs = Turf.objects.all()

    return render(request, 'customer/customer_turf_list.html', {'turfs': turfs})



def turf_details_home(request):
    turfs = Turf.objects.all()
    stars = range(1, 6)  # Pass the range of numbers (1 to 5)
    return render(request, 'home/home_turf_list.html', {'turfs': turfs, 'stars': stars})



def edit_customer_details(request):
    # Retrieve customer_id from session
    customer_id = request.session.get('customer_id')

    if not customer_id:
        # If customer_id is not found in the session, redirect to login page
        return redirect('login')

    try:
        # Fetch the customer using the retrieved customer_id
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        # In case the customer doesn't exist, redirect to login page or show an error
        messages.error(request, "Customer not found.")
        return redirect('login')

    if request.method == 'POST':
        # Get the new values from the form
        first_name = request.POST['first_name']
        middle_name = request.POST['middle_name']
        last_name = request.POST['last_name']
        address = request.POST['address']
        phone_number = request.POST['phone_number']
        email = request.POST['email']
        gender = request.POST['gender']

        # Check if the phone number or email already exists (excluding the current customer)
        if Customer.objects.filter(phone_number=phone_number).exclude(id=customer.id).exists():
            messages.error(request, "The phone number is already in use by another customer.")
            return redirect('edit_customer_details')  # Optionally, redirect to the edit page with the error

        if Customer.objects.filter(email=email).exclude(id=customer.id).exists():
            messages.error(request, "The email address is already in use by another customer.")
            return redirect('edit_customer_details')  # Optionally, redirect to the edit page with the error

        # Update basic details
        customer.first_name = first_name
        customer.middle_name = middle_name
        customer.last_name = last_name
        customer.address = address
        customer.phone_number = phone_number
        customer.email = email
        customer.gender = gender
        
        # Handle photo upload (optional)
        if request.FILES.get('photo'):
            customer.photo = request.FILES['photo']
        
        customer.save()

        # Display success message
        messages.success(request, "Your details have been updated successfully.")

        # Redirect to the customer details page after saving
        return redirect('customer')  # Adjust to your customer details URL

    return render(request, 'customer/edit_customer_details.html', {'customer': customer})


def update_password(request):
    # Fetch customer_id from session
    customer_id = request.session.get('customer_id')
    print("Customer ID from session:", customer_id)

    if customer_id is None:
        # Handle case where customer_id is not found in session
        messages.error(request, "Customer not logged in. Please log in again.")
        return redirect('login')  # Redirect to login page if not logged in

    try:
        # Retrieve the customer from the database using the customer_id from session
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        # Handle case where customer does not exist
        messages.error(request, "Customer not found. Please log in again.")
        return redirect('login')  # Redirect to login page if customer does not exist

    if request.method == 'POST':
        # Pass the customer object to the form
        form = UpdatePasswordForm(request.POST, customer=customer)
        
        if form.is_valid():
            form.save()  # Save the new password
            print("Updated password:", customer.password)  # Print to check password hash
            messages.success(request, "Your password has been updated successfully.")
            return redirect('customer_details')  # Redirect to customer details page after successful update
        else:
            print("Form errors:", form.errors)  # Print form errors for debugging
            messages.error(request, "There was an error updating your password. Please try again.")
    else:
        form = UpdatePasswordForm(customer=customer)  # Initialize form for GET request

    return render(request, 'customer/update_password.html', {'form': form})
    



def admin_booking_list(request):
    # Get all bookings
    bookings = Booking.objects.all()

    # Filter bookings based on user input
    status_filter = request.GET.get('status', '')
    payment_status_filter = request.GET.get('payment_status', '')
    turf_filter = request.GET.get('turf', '')
    customer_filter = request.GET.get('customer', '')

    # Apply filters
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if payment_status_filter:
        bookings = bookings.filter(payment_status=payment_status_filter)
    if turf_filter:
        bookings = bookings.filter(turf__name__icontains=turf_filter)
    if customer_filter:
        bookings = bookings.filter(customer__first_name__icontains=customer_filter)

    # Paginate bookings
    paginator = Paginator(bookings, 10)  # Show 10 bookings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/admin_booking_list.html', {'page_obj': page_obj})





def book_turf(request, turf_id):
    # Retrieve the turf object
    turf = get_object_or_404(Turf, id=turf_id)

    # Check if the customer is logged in
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, "You need to be logged in to book a turf.")
        return redirect('login')

    # Retrieve the customer object
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect('login')

    # Handle POST request for booking
    if request.method == 'POST':
        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')
        duration_hours = request.POST.get('duration_hours')

        # Check if all fields are filled
        if not booking_date or not booking_time or not duration_hours:
            messages.error(request, "All fields are required.")
            return render(request, 'booking/book_turf.html', {'turf': turf})

        # Convert fields to appropriate data types
        try:
            duration_hours = int(duration_hours)
            booking_datetime = datetime.strptime(f'{booking_date} {booking_time}', '%Y-%m-%d %H:%M')
        except ValueError:
            messages.error(request, "Invalid date, time, or duration.")
            return render(request, 'booking/book_turf.html', {'turf': turf})

        # Ensure booking time is within the turf's available times
        if booking_datetime.time() < turf.timing_start or booking_datetime.time() > turf.timing_end:
            messages.error(request, f"Booking time must be between {turf.timing_start} and {turf.timing_end}.")
            return render(request, 'booking/book_turf.html', {'turf': turf})

        # Calculate end time of the requested booking
        booking_end_time = booking_datetime + timedelta(hours=duration_hours)

        # Ensure the end time is within the turf's available times
        if booking_end_time.time() > turf.timing_end:
            messages.error(request, f"The booking duration exceeds the turf's available time. The turf is only available until {turf.timing_end}.")
            return render(request, 'booking/book_turf.html', {'turf': turf})

        # Check for conflicting bookings within the requested time slot
        conflicting_bookings = Booking.objects.filter(
            turf=turf,
            booking_date=booking_datetime.date(),
            status='approved'
        ).filter(
            booking_time__lt=booking_end_time.time(),
            booking_time__gte=booking_datetime.time()  # Checks for any overlapping booking times
        )

        if conflicting_bookings.exists():
            messages.error(request, "This date and time are already booked. Please choose a different slot.")
            return render(request, 'booking/book_turf.html', {'turf': turf})

        # Create booking with pending status
        booking = Booking.objects.create(
            customer=customer,
            turf=turf,
            booking_date=booking_datetime.date(),
            booking_time=booking_datetime.time(),
            duration_hours=duration_hours,
            total_price=turf.price_per_hour * duration_hours,
            status="pending",
            payment_status="pending"
        )

        # Redirect to payment page
        return redirect('payment', booking_id=booking.id)

    # Render booking form
    return render(request, 'booking/book_turf.html', {'turf': turf})











def payment_page(request, booking_id):
    # Fetch the booking, or return a 404 error if not found
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        try:
            # Update payment and booking status
            booking.payment_status = "paid"
            booking.status = "pending"
            booking.save(update_fields=['payment_status', 'status'])

            # Success message
            messages.success(request, "Payment successful! Your booking is now pending approval.")
            
            # Redirect to the booking list or another page
            return redirect('customer_turf_list')  # Make sure this URL name is correct

        except Exception as e:
            # If there was an error, log it or display an error message
            messages.error(request, f"An error occurred while processing your payment: {e}")
            return redirect('payment_failure')  # Optionally, redirect to a failure page

    return render(request, 'booking/payment.html', {'booking': booking})

        
            
    





def cancel_booking(request, booking_id):
    # Retrieve the customer ID from the session
    customer_id = request.session.get('customer_id')

    if not customer_id:
        messages.error(request, 'Customer not found in session. Please log in again.')
        return redirect('login')  # Redirect to login page if no customer_id is found

    # Get the booking object or return 404 if not found
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Ensure that the customer in the session is the one who made the booking
    if booking.customer.id == customer_id:
        # Delete the booking
        booking.delete()
        messages.success(request, 'Your booking has been cancelled successfully.')
    else:
        messages.error(request, 'You do not have permission to cancel this booking.')
    
    # Redirect to a relevant page after cancellation (e.g., booking history or homepage)
    return redirect('customer_turf_list') 


def update_booking_status(request, booking_id, new_status):
    # Fetch the booking using the ID
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Update the status of the booking
    if new_status in ['approved', 'canceled']:
        booking.status = new_status
        booking.save()

        # Add a success message
        messages.success(request, f"Booking status updated to {new_status.capitalize()}.")
    else:
        messages.error(request, "Invalid status.")

    # Redirect back to the booking list
    return redirect('admin_booking_list')



def customer_bookings(request):
    # Get the customer_id from the session
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, "You need to be logged in to view your bookings.")
        return redirect('login')

    # Retrieve the customer object
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect('login')

    # Fetch bookings for the logged-in customer
    bookings = Booking.objects.filter(customer=customer)

    # Pass the bookings to the template
    return render(request, 'customer/customer_bookings.html', {'customer': customer, 'bookings': bookings})





def generate_rtf_receipt(booking):
    # Start RTF content with some basic settings for font and style
    rtf_content = "{\\rtf1\\ansi\\deff0\\nouicompat\\deflang1033\\pard\\sa200\\sl276\\slmult1\\f0\\fs22\\lang9"
    
    # Title: Receipt Header
    rtf_content += "\\b\\fs28 Receipt for Booking #" + str(booking.id) + "\\b0\\par\\par"
    
    # Customer Details
    rtf_content += "\\b Customer Name: \\b0" + str(booking.customer.first_name) + " " + str(booking.customer.last_name) + "\\par"
    rtf_content += "\\b Booking Date: \\b0" + str(booking.booking_date) + "\\par"
    rtf_content += "\\b Booking Time: \\b0" + str(booking.booking_time) + "\\par"
    
    # Amount and Status
    rtf_content += "\\b Amount: \\b0 $" + str(booking.total_price) + "\\par"
    rtf_content += "\\b Status: \\b0 " + booking.status.capitalize() + "\\par"
    
    # Booking Turf Information
    rtf_content += "\\par\\b Turf Details: \\b0\\par"
    rtf_content += "\\b Turf Name: \\b0 " + str(booking.turf.name) + "\\par"
    rtf_content += "\\b Turf Location: \\b0 " + str(booking.turf.location) + "\\par"
    
    # Footer Information
    rtf_content += "\\par\\i Thank you for your booking!\\i0\\par"
    
    # End the RTF
    rtf_content += "\\par}"

    return rtf_content



def download_receipt(request, booking_id):
    # Get the booking object
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if the booking is approved
    if booking.status != 'approved':
        return HttpResponse("Receipt not available for this booking.", status=400)

    # Generate RTF content
    rtf_content = generate_rtf_receipt(booking)

    # Return the RTF file as a response
    response = HttpResponse(rtf_content, content_type="application/rtf")
    response['Content-Disposition'] = f'attachment; filename="payment_receipt_{booking.id}.rtf"'
    return response



def customer_cancel_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Change the status to 'Cancelled'
        booking.status = 'Canceled'
        booking.save()

        # Redirect to the bookings page or any other relevant page
        return redirect('customer_bookings')
    

def admin_view_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'admin/view_booking.html', {'booking': booking})



#PASSWORD RESET VIEWS



def generate_otp():
    # Generate a random 6-digit OTP
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    subject = 'Your OTP for Password Reset'
    message = f'Your OTP to reset your password is {otp}'
    from_email = 'nibinjoseph2003@gmail.com'  # The email used to send OTPs (configured in settings.py)
    recipient_list = [email]
    
    # Send the OTP email
    send_mail(subject, message, from_email, recipient_list)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if the email exists in the database
        try:
            customer = Customer.objects.get(email=email)

            # Generate OTP
            otp = generate_otp()

            # Send OTP email to the customer's email address
            send_otp_email(customer.email, otp)

            # Optionally, save OTP in session for verification
            request.session['otp'] = otp
            request.session['email'] = email

            # Redirect to OTP verification page
            return redirect('verify_otp')  # Ensure you have this URL mapped in your urls.py
        
        except Customer.DoesNotExist:
            # Handle case when email is not found
            messages.error(request, 'This email is not registered. Please try again with a valid email address.')
            return render(request, 'forget_password/forgot_password.html')  # Ensure correct path

    return render(request, 'forget_password/forgot_password.html')  # Ensure correct path


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        correct_otp = request.session.get('otp')
        
        # Check if OTP exists and is valid
        if not otp or len(otp) != 6:  # OTP length validation
            messages.error(request, "Invalid OTP length. Please enter a 6-digit OTP.")
            return render(request, 'forget_password/verify_otp.html')

        if otp != correct_otp:  # OTP mismatch validation
            messages.error(request, "Incorrect OTP. Please try again.")
            return render(request, 'forget_password/verify_otp.html')

        # OTP is correct, proceed to next step (e.g., reset password)
        # For example:
        return redirect('reset_password')
    
    return render(request, 'forget_password/verify_otp.html')

def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        email = request.session.get('email')

        if email is None:
            messages.error(request, 'Session expired. Please try the password reset process again.')
            return redirect('forgot_password')  # Redirect to forgot password page if session is missing

        try:
            customer = Customer.objects.get(email=email)
            customer.set_password(new_password)  # Update password securely
            customer.save()

            # Log the customer in (optional, if you prefer automatic login)
            login(request, customer)

            messages.success(request, 'Password reset successfully!')
            return redirect('login')  # Redirect to login or any other page

        except Customer.DoesNotExist:
            messages.error(request, 'Error updating the password. Please try again.')
            return render(request, 'forget_password/reset_password.html')

    return render(request, 'forget_password/reset_password.html')




def feedback(request, turf_id):
    # Get the turf object, if it doesn't exist, it will raise a 404 error
    turf = get_object_or_404(Turf, id=turf_id)

    # Retrieve customer from session
    customer_id = request.session.get('customer_id')

    if not customer_id:
        messages.error(request, 'Customer ID not found. Please log in or provide your details.')
        return redirect('login')  # Redirect to a login page or another action if needed

    # Get the customer object using the customer_id
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        messages.error(request, 'Customer does not exist. Please try again.')
        return redirect('login')  # Or another appropriate action

    # Get the customer's booking for the given turf
    booking = Booking.objects.filter(turf=turf, customer=customer).first()

    # If booking not found, handle the case accordingly (optional)
    if not booking:
        messages.error(request, 'No booking found for this turf.')
        return redirect('customer_turf_list')  # Or any page you prefer

    if request.method == 'POST':
        # Capture feedback data from the form
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')
        date_of_visit = request.POST.get('date_of_visit')
        feedback_type = request.POST.get('feedback_type')

        # Validate form data (optional)
        if not rating or not comments or not date_of_visit:
            messages.error(request, 'Please fill out all fields.')
            return redirect('feedback', turf_id=turf.id)

        # Save feedback
        feedback = Feedback(
            turf=turf,
            customer=customer,  # Use the customer retrieved from session
            rating=rating,
            comments=comments,
            date_of_visit=date_of_visit,
            feedback_type=feedback_type,
        )
        feedback.save()

        # Update the average rating of the Turf based on new feedback
        feedbacks = Feedback.objects.filter(turf=turf)
        total_ratings = sum([f.rating for f in feedbacks])
        average_rating = total_ratings / len(feedbacks) if feedbacks else 0  # Avoid division by zero
        turf.rating = round(average_rating, 2)
        turf.save()

        messages.success(request, 'Your feedback has been submitted successfully!')
        return redirect('customer_bookings')  # Redirect to an appropriate page (e.g., customer dashboard)

    return render(request, 'customer/feedback.html', {'turf': turf, 'booking': booking})


def view_feedback(request):
    # Get the customer_id from the session
    customer_id = request.session.get('customer_id')

    # If the customer_id is not found in the session, redirect or show an error
    if not customer_id:
        return redirect('login')  # Customize this as needed (e.g., redirect to login page)

    # Filter feedbacks by customer_id (ForeignKey relationship)
    feedbacks = Feedback.objects.filter(customer__id=customer_id)

    # Render the feedback page with the feedbacks
    return render(request, 'customer/view_feedback_customer.html', {'feedbacks': feedbacks})




def admin_feedback_list(request):
    # Fetch all feedbacks
    feedbacks = Feedback.objects.all()

    # Handle form submission to update status
    if request.method == 'POST':
        feedback_ids = request.POST.getlist('feedback_ids')
        Feedback.objects.filter(id__in=feedback_ids).update(status='reviewed')
        # Optionally, add a message or redirect after updating
        return redirect('admin_feedback_list')

    return render(request, 'admin/admin_feedback_list.html', {'feedbacks': feedbacks})


def home_feedback_list(request):
    # Fetch all feedbacks
    feedbacks = Feedback.objects.all()

    # Handle form submission to update status
    if request.method == 'POST':
        feedback_ids = request.POST.getlist('feedback_ids')
        
        return redirect('home_feedback_list')

    return render(request, 'home/home_feedback_list.html', {'feedbacks': feedbacks})


def admin_payment_summary(request):
    # Filter parameters from GET request
    payment_status = request.GET.get('payment_status', '')
    booking_status = request.GET.get('status', '')

    # Calculate total paid and pending payments
    total_paid = Booking.objects.filter(payment_status='paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    pending_payments = Booking.objects.filter(payment_status='pending').aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Fetch all booking records with optional filtering
    bookings = Booking.objects.select_related('customer', 'turf').order_by('-created_at')
    if payment_status:
        bookings = bookings.filter(payment_status=payment_status)
    if booking_status:
        bookings = bookings.filter(status=booking_status)

    # Paginate results (10 bookings per page)
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'total_paid': total_paid,
        'pending_payments': pending_payments,
        'bookings': page_obj,  # Pass paginated bookings
    }
    return render(request, 'admin/payments_summary.html', context)





sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

def load_faq_data(file_path='home/data/faq.xlsx'):
    """
    Load FAQ data from the Excel file and return it as a list of dictionaries.
    """
    try:
        data = pd.read_excel(file_path)
        data = data[['Question', 'Answer']].dropna()
        return data.to_dict(orient='records')
    except Exception as e:
        print(f"Error loading FAQ data: {e}")
        return []

def get_best_match(user_query, faq_data):
    """
    Match the user query with the most relevant FAQ question.
    Use sentence embeddings for better accuracy.
    """
    try:
        questions = [faq['Question'] for faq in faq_data]
        embeddings = sentence_model.encode(questions)
        query_embedding = sentence_model.encode([user_query])
        similarities = cosine_similarity(query_embedding, embeddings)
        best_match_idx = np.argmax(similarities)

        # Confidence threshold
        if similarities[0][best_match_idx] < 0.5:
            return "I'm sorry, I couldn't find an answer. Please contact support."
        
        return faq_data[best_match_idx]['Answer']
    except Exception as e:
        print(f"Error in query matching: {e}")
        return "An error occurred while processing your query."

def faq(request):
    """
    FAQ view to process user queries and return matched responses.
    """
    if request.method == 'POST':
        user_query = request.POST.get('query')
        if user_query:
            faq_data = load_faq_data('home/data/faq.xlsx')
            if not faq_data:
                return render(request, 'customer/faq.html', {'answer': 'No FAQ data available.'})
            answer = get_best_match(user_query, faq_data)
            return render(request, 'customer/faq.html', {'answer': answer, 'user_query': user_query})

    return render(request, 'customer/faq.html')
