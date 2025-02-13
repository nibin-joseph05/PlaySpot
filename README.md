⚽ Football Turf Booking System
📌 Overview
The Football Turf Booking System is a web-based application built with Django that allows users to search, book, and manage football turf reservations. 
The system provides a seamless booking experience for customers and an intuitive admin dashboard for managing turfs, bookings, and payments.

✨ Features
🔹 User Features:
✔ User Registration & Authentication – Secure login and signup functionality.
✔ Turf Search & Filtering – Search for turfs by location and availability.
✔ Booking Management – Book, cancel, and view turf reservations.
✔ Feedback System – Rate and review booked turfs.
✔ Download Invoice – Download invoices for completed bookings.
✔ Chatbot FAQ – AI-powered chatbot to assist users with common queries.

🔹 Admin Features:
✔ Turf Management – Add, update, and delete turf details.
✔ Booking & Payment Summary – View and manage user bookings & payments.
✔ User Management – View customer details and feedback.
✔ Profit Calculation – Track admin profits from bookings.

🏗️ Tech Stack
Frontend:

HTML, CSS, Bootstrap
JavaScript

Backend:

Django (Python)
PostgreSQL (Database)
Machine Learning (FAQ System):

TF-IDF Vectorization – Converts text into numerical vectors.
Cosine Similarity – Finds the most relevant answers based on user queries.
Sentence Transformers – Provides deep learning-based text embeddings.

🛠️ Installation & Setup

🔧 Prerequisites

Python 3.8+
Django 4.x
PostgreSQL
pip (Package Manager)

📥 Installation Steps


# Clone the repository
git clone https://github.com/yourusername/football-turf-booking.git

# Navigate to the project directory
cd football-turf-booking

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the server
python manage.py runserver

🔗 API Endpoints

Endpoint	Method	Description
/register/	POST	Register a new user
/login/	POST	Authenticate user
/bookings/	GET	Fetch all bookings
/bookings/<id>/cancel/	PUT	Cancel a booking
/faq/	GET	Fetch FAQs using ML


🏆 Future Enhancements

✅ Online Payment Integration
✅ Mobile App Support
✅ Push Notifications for Booking Updates
✅ AI-based Personalized Recommendations

📌 Contributors
👨‍💻 Nibin Joseph - Developer & Maintainer
📩 Email: nibin.joseph.career@gmail.com

📜 License

Copyright (c) 2025 Nibin Joseph  

Permission is hereby granted, free of charge, to any person obtaining a copy  
of this software and associated documentation files (the "Software"), to deal  
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in  
all copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN  
THE SOFTWARE.  
