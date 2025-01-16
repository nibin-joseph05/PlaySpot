from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from .views import customer_list, customer_delete
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('admin01/', views.admin_view, name='admin01'),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.customer_login, name='login'),
    path('customer/', views.customer_page, name='customer'),
    path('logout/', views.customer_logout, name='logout'),
    path('booking/', views.booking, name='booking'),
    path('turf_list/', views.turf_list, name='turf_list'),
    path('add_turf/', views.add_turf, name='add_turf'),
    path('delete_turf/<int:turf_id>/', views.delete_turf, name='delete_turf'),
    path('edit_turf/<int:turf_id>/', views.edit_turf, name='edit_turf'),
    path('customer_list/', views.customer_list, name='customer_list'),
    path('customer_delete/<int:customer_id>/', customer_delete, name='customer_delete'),  # Correct the name here
    path('customer_details/', views.customer_details, name='customer_details'),
    path('customer_turf_list/', views.turf_details, name='customer_turf_list'),
    path('search_turf/', views.search_turf, name='search_turf'),  # Add this line
    path('book_turf/<int:turf_id>/', views.book_turf, name='book_turf'),
    path('payment/<int:booking_id>/', views.payment_page, name='payment'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('home_turf_list/', views.turf_details_home, name='home_turf_list'),
    path('edit_customer_details/', views.edit_customer_details, name='edit_customer_details'),
    path('update_password/', views.update_password, name='update_password'),
    path('admin_booking_list/', views.admin_booking_list, name='admin_booking_list'),
    path('update_status/<int:booking_id>/<str:new_status>/', views.update_booking_status, name='update_status'),
    path('customer_bookings', views.customer_bookings, name='customer_bookings'),
    path('download_receipt/<int:booking_id>/', views.download_receipt, name='download_receipt'),
    path('customer_cancel_booking/<int:booking_id>/', views.customer_cancel_booking, name='customer_cancel_booking'),
    path('view_booking<int:booking_id>/', views.admin_view_booking, name='view_booking'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('uabout/', views.uabout, name='uabout'),
    path('ucontact/', views.ucontact, name='ucontact'),
    path('feedback/<int:turf_id>/', views.feedback, name='feedback'),
    path('view_feedback_customer/', views.view_feedback, name='view_feedback_customer'),
    path('admin_feedback/', views.admin_feedback_list, name='admin_feedback_list'),
    path('home_feedback/', views.home_feedback_list, name='home_feedback_list'),
    path('admin_payment_summary/', views.admin_payment_summary, name='admin_payment_summary'),
    path('faq/', views.faq, name='faq'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
