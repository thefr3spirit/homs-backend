# Hotel Management System - API Quick Reference

## 🔐 Authentication

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@lemihotel.com","password":"admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "...",
  "email": "owner@lemihotel.com",
  "full_name": "Hotel Owner",
  "role": "owner"
}
```

### Using Authentication in Requests

Add the Bearer token to the Authorization header:

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## 👤 User Management

### Get Current User Info
```bash
GET /auth/me
Authorization: Bearer {token}
```

### Register New User (Owner Only)
```bash
POST /auth/register
Authorization: Bearer {owner_token}
Content-Type: application/json

{
  "email": "receptionist@lemihotel.com",
  "password": "secure_password",
  "full_name": "Jane Receptionist",
  "phone": "+251911234567",
  "role": "receptionist"
}
```

### Update Profile
```bash
PUT /auth/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "Updated Name",
  "phone": "+251911111111"
}
```

### Change Password
```bash
PUT /auth/password
Authorization: Bearer {token}
Content-Type: application/json

{
  "old_password": "current_password",
  "new_password": "new_secure_password"
}
```

---

## 📊 Daily Summary (Original - Still Working for Gift's App)

### Submit Daily Summary
```bash
POST /summary
Content-Type: application/json

{
  "summary_date": "2026-02-18",
  "cash_received": 25000.00,
  "momo_received": 15000.00,
  "debit_received": 8000.00,
  "cheque_collected": 5000.00,
  "total_food": 12000.00,
  "total_rooms": 8,
  "total_bookings": 6
}
```

### Get Today's Summary
```bash
GET /summary/today
```

### Get Latest Summary
```bash
GET /summary/latest
```

### Get Summary History
```bash
GET /summary/history?limit=30&offset=0
```

### Get Summary by Date
```bash
GET /summary/date/2026-02-18
```

### Get Summaries by Date Range
```bash
GET /summary/range?start_date=2026-02-01&end_date=2026-02-18
```

---

## 🔒 Role-Based Access Control

### User Roles

1. **OWNER**
   - Full system access
   - Can register new users
   - Can approve expenses
   - Can view all reports

2. **RECEPTIONIST**
   - Create bookings
   - Check-in/check-out guests
   - Record payments
   - View customers and rooms
   - Record expenses (pending approval)

3. **ACCOUNTANT**
   - View-only access to financial data
   - Generate reports
   - View audit logs
   - No create/update permissions

---

## 💡 Implementation Examples

### Protected Route Example (in your routes file)

```python
from fastapi import APIRouter, Depends
from middleware.auth import get_current_user, require_role
from models.user import User, UserRole

router = APIRouter(prefix="/customers", tags=["customers"])

# All authenticated users can view
@router.get("/")
def list_customers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    customers = db.query(Customer).all()
    return customers

# Only owner and receptionist can create
@router.post("/", dependencies=[Depends(require_role(UserRole.OWNER, UserRole.RECEPTIONIST))])
def create_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    customer = Customer(**customer_data.dict())
    db.add(customer)
    db.commit()
    return customer
```

### Tracking Which Receptionist Performed Action

```python
@router.post("/bookings")
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = Booking(
        **booking_data.dict(),
        created_by=current_user.id  # ← Automatically track creator
    )
    db.add(booking)
    db.commit()
    return booking

@router.post("/bookings/{booking_id}/checkin")
def checkin(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    booking.checked_in_by = current_user.id  # ← Track who checked in
    booking.actual_checkin = datetime.now()
    booking.booking_status = BookingStatus.CHECKED_IN
    db.commit()
    return booking
```

### Updating Customer Pending Balance

```python
@router.post("/payments")
def record_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create payment record
    payment = Payment(
        **payment_data.dict(),
        received_by=current_user.id,  # ← Track who received payment
        payment_date=datetime.now(),
        status=PaymentStatus.COMPLETED
    )
    
    # Update customer pending balance
    customer = db.query(Customer).filter(Customer.id == payment.customer_id).first()
    if customer:
        customer.pending_balance -= payment.amount
        customer.total_spent += payment.amount
    
    # Update booking amount paid
    if payment.booking_id:
        booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
        if booking:
            booking.amount_paid += payment.amount
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
```

---

## 📱 Mobile App Integration

### Flutter HTTP Client with Authentication

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'http://localhost:8000';
  static String? _token;
  
  // Login and store token
  static Future<void> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _token = data['access_token'];
      // Store token securely (use flutter_secure_storage)
    }
  }
  
  // Make authenticated request
  static Future<http.Response> getWithAuth(String endpoint) async {
    return await http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: {
        'Authorization': 'Bearer $_token',
        'Content-Type': 'application/json',
      },
    );
  }
  
  static Future<http.Response> postWithAuth(String endpoint, Map<String, dynamic> data) async {
    return await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: {
        'Authorization': 'Bearer $_token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(data),
    );
  }
}
```

---

## 🧪 Testing Endpoints

### Using cURL

```bash
# 1. Login and save token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@lemihotel.com","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Use token in subsequent requests
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "owner@lemihotel.com", "password": "admin123"}
)
token = response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print(response.json())
```

---

## 🗄️ Database Models Reference

### User
- `id` (UUID)
- `email` (unique)
- `password_hash`
- `full_name`
- `phone`
- `role`: owner | receptionist | accountant
- `is_active` (boolean)
- `last_login`

### Customer
- `id` (UUID)
- `full_name`
- `email`
- `phone`
- `id_number`
- `address`
- `customer_type`: regular | vip | corporate
- **`pending_balance`** (amount owed)
- **`total_spent`** (lifetime spending)
- `total_visits`

### Room
- `id` (UUID)
- `room_number` (unique)
- `room_type`: standard | deluxe | suite | executive
- `floor`
- `capacity`
- `daily_rate`
- `status`: available | occupied | maintenance | reserved | cleaning
- `amenities` (JSON)

### Booking
- `id` (UUID)
- `customer_id` (FK → Customer)
- `room_id` (FK → Room)
- **`created_by`** (FK → User)
- **`checked_in_by`** (FK → User)
- **`checked_out_by`** (FK → User)
- `check_in_date`
- `check_out_date`
- `actual_checkin`
- `actual_checkout`
- `num_guests`
- `total_amount`
- `amount_paid`
- **`balance_due`** (computed: total_amount - amount_paid)
- `booking_status`: pending | confirmed | checked_in | checked_out | cancelled | no_show

### Payment
- `id` (UUID)
- `booking_id` (FK → Booking)
- `customer_id` (FK → Customer)
- **`received_by`** (FK → User)
- `amount`
- `payment_method`: cash | momo | cheque | card | bank_transfer
- `payment_type`: deposit | partial | full | refund
- `transaction_ref`
- `payment_date`
- `status`: pending | completed | refunded | failed

### Expense
- `id` (UUID)
- **`recorded_by`** (FK → User)
- **`approved_by`** (FK → User)
- `category`: utilities | salary | supplies | maintenance | marketing | food | cleaning | other
- `amount`
- `description`
- `vendor_name`
- `expense_date`
- `receipt_url`
- `status`: pending | approved | rejected

### AuditLog
- `id` (UUID)
- `user_id` (FK → User)
- `action`
- `entity_type`
- `entity_id`
- `changes` (JSON)
- `ip_address`
- `user_agent`
- `timestamp`

---

## 🚀 Deployment Commands

### Local Development
```bash
cd d:\HoMS\backend
python main.py
# Server runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Run Migrations
```bash
cd d:\HoMS\backend
alembic upgrade head
```

### Seed Initial Data
```bash
cd d:\HoMS\backend
python seed_owner.py
```

### View API Documentation
Open browser: http://localhost:8000/docs

---

## 📞 Support & References

- **Backend URL (Local)**: http://localhost:8000
- **Backend URL (Production)**: https://homs-backend-txs8.onrender.com
- **API Docs**: /docs
- **ReDoc**: /redoc
- **OpenAPI JSON**: /openapi.json

**Initial Owner Account:**
- Email: owner@lemihotel.com
- Password: admin123
- ⚠️ Change password after first login!
