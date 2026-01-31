# Switching to Production

## 1. Authentication (OTP)
Currently, OTPs are printed to the console (`users/models.py`).
To use real SMS:
1. Sign up for **Twilio** or **Msg91**.
2. Install `twilio` package: `pip install twilio`.
3. Update `users/models.py`:
   ```python
   def generate_demo_otp(self):
       # ... logic ...
       # send_sms(self.phone_number, otp) 
   ```

## 2. Payments (Razorpay)
Currently, `bookings/views.py` mocks success.
To use **Razorpay**:
1. Sign up for Razorpay.
2. Install `razorpay` package.
3. In `settings.py`, add `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`.
4. Update `bookings/views.py`:
   - `payment_view`: Create Razorpay Order API call.
   - Render a template with Checkout.js.
   - Handle Webhook or Verify callback.

## 3. Database (PostgreSQL)
Currently using `db.sqlite3`.
To switch:
1. Update `DATABASES` in `settings.py`.
2. Install `psycopg2`.
3. Run `python manage.py migrate`.

## 4. Deployment
- Use `gunicorn` instead of `runserver`.
- Set `DEBUG = False`.
- Set `ALLOWED_HOSTS` to your domain.
- Serve static files via Nginx.
