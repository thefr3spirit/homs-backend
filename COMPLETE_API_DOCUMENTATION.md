# Hotel Management System - Complete API Documentation

**Document Version:** 1.0  
**Date:** February 19, 2026  
**For:** Desktop Counter Application Integration

---

## Overview

This document provides comprehensive API documentation for the Hotel Management System backend. The system manages:

- **Daily Summaries**: Daily operational metrics (already in use)
- **Customers**: Guest information and balance tracking
- **Rooms**: Room inventory management
- **Bookings**: Reservation and check-in/out tracking
- **Payments**: Payment collection records
- **Users**: Staff member accounts

---

## Authentication

All API endpoints (except login) require JWT authentication.

**User Roles:**  
- **Owner** - Full system access, can delete records and manage all operations
- **Receptionist** - Daily operations: bookings, check-in/out, payments, customer management
- **Admin** - Elevated staff role with extended permissions

### Login

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "receptionist@lemihotel.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "uuid-here",
  "email": "receptionist@lemihotel.com",
  "full_name": "Receptionist Name",
  "role": "receptionist"
}
```

**Using the Token:**
Include in all subsequent requests:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Important:** Login requires **email** (not username) and password.

---

## 1. Daily Summaries API

**(Already in use by Gift's counter app)**

### Submit Daily Summary

**Endpoint:** `POST /summary`  
**Authentication:** Required  
**Description:** Submit or update daily operational metrics

**Request Body:**
```json
{
  "date": "2026-02-19",
  "rooms_total": 24,
  "rooms_occupied": 18,
  "rooms_available": 6,
  "cash_collected": 450000,
  "momo_collected": 300000,
  "cheque_collected": 150000,
  "total_collected": 900000,
  "expected_balance": 1200000,
  "expenses_logged": 75000
}
```

**Response:**
```json
{
  "id": "uuid",
  "date": "2026-02-19",
  "rooms_total": 24,
  "rooms_occupied": 18,
  "rooms_available": 6,
  "cash_collected": 450000,
  "momo_collected": 300000,
  "cheque_collected": 150000,
  "total_collected": 900000,
  "expected_balance": 1200000,
  "expenses_logged": 75000,
  "last_updated": "2026-02-19T10:30:00Z",
  "created_by": "user-uuid",
  "updated_by": "user-uuid",
  "created_by_name": "Receptionist Name",
  "updated_by_name": "Receptionist Name"
}
```

**User Tracking:** Automatically tracks who submitted/updated the summary using JWT token.

### Get Today's Summary

**Endpoint:** `GET /summary/today`  
**Returns:** Today's summary (if exists)

### Get Latest Summary

**Endpoint:** `GET /summary/latest`  
**Returns:** Most recent summary

### Get Summary History

**Endpoint:** `GET /summary/history?limit=30&offset=0`  
**Returns:** List of summaries (paginated)

### Get Summary by Date

**Endpoint:** `GET /summary/date/2026-02-19`  
**Returns:** Summary for specific date

---

## 2. Customers API

**NEW - Gift can now send customer data here!**

### Create Customer

**Endpoint:** `POST /customers/`  
**Authentication:** Required (Receptionist/Owner)  
**Description:** Add a new customer to the system

**Request Body:**
```json
{
  "name": "John Doe",
  "phone": "0712345678",
  "email": "john@example.com",
  "room_number": "101",
  "balance": 0
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "phone": "0712345678",
  "email": "john@example.com",
  "room_number": "101",
  "balance": 0,
  "visit_count": 1,
  "last_visit": "2026-02-19T10:30:00Z",
  "created_at": "2026-02-19T10:30:00Z",
  "updated_at": "2026-02-19T10:30:00Z",
  "created_by": "user-uuid",
  "created_by_name": "Receptionist Name"
}
```

**User Tracking:** Automatically sets `created_by` from JWT token.

### Update Customer

**Endpoint:** `PUT /customers/{customer_id}`  
**Description:** Update customer information or balance

**Request Body:**
```json
{
  "name": "John Doe Updated",
  "phone": "0712345679",
  "balance": -50000
}
```

**Response:** Same as create, with `updated_by_name` showing who made the change.

### Get All Customers

**Endpoint:** `GET /customers/?limit=50&offset=0`  
**Returns:** Paginated list of all customers

### Get Customer by Phone

**Endpoint:** `GET /customers/phone/0712345678`  
**Returns:** Customer details by phone number

### Search Customers

**Endpoint:** `GET /customers/search?q=John`  
**Returns:** Customers matching name or phone

### Add Payment to Balance

**Endpoint:** `POST /customers/{customer_id}/add-payment`  
**Request Body:**
```json
{
  "amount": 100000,
  "payment_method": "cash"
}
```
**Description:** Adds payment and reduces balance (if negative)

---

## 3. Rooms API

**NEW - Gift can now send room data here!**

### Create Room

**Endpoint:** `POST /rooms/`  
**Authentication:** Required (Owner only)  
**Description:** Add a new room to inventory

**Request Body:**
```json
{
  "room_number": "101",
  "room_type": "single",
  "daily_rate": 50000,
  "status": "available"
}
```

**Room Types:** `single`, `double`, `suite`, `deluxe`  
**Room Status:** `available`, `occupied`, `maintenance`, `reserved`

**Response:**
```json
{
  "id": "uuid",
  "room_number": "101",
  "room_type": "single",
  "daily_rate": 50000,
  "status": "available",
  "created_by": "user-uuid",
  "created_by_name": "Owner Name",
  "created_at": "2026-02-19T10:30:00Z"
}
```

### Update Room

**Endpoint:** `PUT /rooms/{room_id}`  
**Description:** Update room details or status

### Get All Rooms

**Endpoint:** `GET /rooms/?limit=50&offset=0`  
**Returns:** Paginated list of all rooms

### Get Room by Number

**Endpoint:** `GET /rooms/number/101`  
**Returns:** Room details by room number

---

## 4. Bookings API

**NEW - Gift can now send booking data here!**

### Create Booking

**Endpoint:** `POST /bookings/`  
**Authentication:** Required  
**Description:** Create a new room booking

**Request Body:**
```json
{
  "customer_id": "customer-uuid",
  "room_id": "room-uuid",
  "check_in_date": "2026-02-19",
  "check_out_date": "2026-02-22",
  "total_amount": 150000,
  "advance_payment": 50000,
  "payment_method": "cash",
  "notes": "Early check-in requested"
}
```

**Payment Methods:** `cash`, `momo`, `cheque`

**Response:**
```json
{
  "id": "uuid",
  "customer_id": "customer-uuid",
  "room_id": "room-uuid",
  "check_in_date": "2026-02-19",
  "check_out_date": "2026-02-22",
  "actual_check_in": null,
  "actual_check_out": null,
  "total_amount": 150000,
  "advance_payment": 50000,
  "balance": 100000,
  "payment_method": "cash",
  "notes": "Early check-in requested",
  "status": "pending",
  "created_at": "2026-02-19T10:30:00Z",
  "created_by": "user-uuid",
  "created_by_name": "Receptionist Name",
  "checked_in_by": null,
  "checked_in_by_name": null,
  "checked_out_by": null,
  "checked_out_by_name": null
}
```

**Booking Status:** `pending`, `checked_in`, `checked_out`, `cancelled`

### Check In Guest

**Endpoint:** `POST /bookings/{booking_id}/check-in`  
**Description:** Mark guest as checked in (updates `actual_check_in` and `checked_in_by`)

**Request Body:** `{}` (empty - just triggers check-in)

### Check Out Guest

**Endpoint:** `POST /bookings/{booking_id}/check-out`  
**Description:** Mark guest as checked out (updates `actual_check_out` and `checked_out_by`)

**Request Body:** `{}` (empty - just triggers check-out)

### Get All Bookings

**Endpoint:** `GET /bookings/?limit=50&offset=0`  
**Returns:** Paginated list of all bookings with user tracking

### Get Today's Check-ins

**Endpoint:** `GET /bookings/today/check-in`  
**Returns:** Bookings scheduled to check in today

### Get Today's Check-outs

**Endpoint:** `GET /bookings/today/check-out`  
**Returns:** Bookings scheduled to check out today

---

## 5. Payments API

**NEW - Gift can now send payment data here!**

### Record Payment

**Endpoint:** `POST /payments/`  
**Authentication:** Required  
**Description:** Record a payment received

**Request Body:**
```json
{
  "booking_id": "booking-uuid",
  "amount": 100000,
  "payment_method": "momo",
  "notes": "Balance payment"
}
```

**Response:**
```json
{
  "id": "uuid",
  "booking_id": "booking-uuid",
  "amount": 100000,
  "payment_method": "momo",
  "notes": "Balance payment",
  "received_at": "2026-02-19T10:30:00Z",
  "received_by": "user-uuid",
  "received_by_name": "Receptionist Name"
}
```

**User Tracking:** Automatically tracks who received the payment - critical for cash handling accountability!

### Get All Payments

**Endpoint:** `GET /payments/?limit=50&offset=0`  
**Returns:** Paginated list of all payments

### Get Today's Payments

**Endpoint:** `GET /payments/today`  
**Returns:** All payments received today

### Get Payments for Booking

**Endpoint:** `GET /payments/booking/{booking_id}`  
**Returns:** All payments for a specific booking

---

## 6. Users API

**(Read-only for Gift - users created by owner only)**

### Get Current User

**Endpoint:** `GET /users/me`  
**Returns:** Currently logged-in user details

---

## User Tracking System

**How it works:**

1. When Gift's app sends data to any endpoint (customers, rooms, bookings, payments, summaries), the backend automatically:
   - Reads the JWT token from `Authorization` header
   - Extracts the user ID
   - Sets `created_by` field (for new records)
   - Sets `updated_by` field (for updates)
   - Sets `received_by` field (for payments)
   - Sets `checked_in_by`/`checked_out_by` fields (for bookings)

2. When retrieving data, the backend automatically:
   - Looks up the user's full name
   - Returns `*_by_name` fields in the response
   - Mobile app displays these names to show who performed each action

**No extra work needed from Gift's desktop app!** Just send the data normally with JWT authentication.

---

## Typical Workflow Examples

### Example 1: New Guest Check-In

1. **Create Customer** (if new):
   ```
   POST /customers/
   Body: {name, phone, email}
   ```

2. **Get Available Room**:
   ```
   GET /rooms/?status=available
   ```

3. **Create Booking**:
   ```
   POST /bookings/
   Body: {customer_id, room_id, check_in_date, check_out_date, total_amount, advance_payment}
   ```

4. **Check In Guest** (when they arrive):
   ```
   POST /bookings/{booking_id}/check-in
   ```

5. **Record Payment** (if balance paid):
   ```
   POST /payments/
   Body: {booking_id, amount, payment_method}
   ```

### Example 2: Returning Guest

1. **Search Customer**:
   ```
   GET /customers/phone/0712345678
   ```

2. **Create Booking** (using existing customer_id)

3. **Check In** when ready

### Example 3: Daily Summary

1. **Get Today's Summary**:
   ```
   GET /summary/today
   ```

2. **Submit/Update Summary**:
   ```
   POST /summary
   Body: {date, rooms_total, rooms_occupied, etc.}
   ```

---

## Testing Examples (Python)

### Login and Get Token

```python
import requests

# Login (use EMAIL, not username)
response = requests.post('https://homs-backend-txs8.onrender.com/auth/login', json={
    'email': 'receptionist@lemihotel.com',
    'password': 'your-password'
})
token = response.json()['access_token']

# Headers for all subsequent requests
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
```

### Create Customer

```python
response = requests.post('https://homs-backend-txs8.onrender.com/customers/', 
    headers=headers,
    json={
        'name': 'Jane Doe',
        'phone': '0787654321',
        'email': 'jane@example.com',
        'room_number': '102',
        'balance': 0
    }
)
customer = response.json()
print(f"Created customer: {customer['name']}")
print(f"Added by: {customer['created_by_name']}")
```

### Create Booking

```python
response = requests.post('https://homs-backend-txs8.onrender.com/bookings/',
    headers=headers,
    json={
        'customer_id': customer['id'],
        'room_id': 'room-uuid-here',
        'check_in_date': '2026-02-19',
        'check_out_date': '2026-02-22',
        'total_amount': 150000,
        'advance_payment': 50000,
        'payment_method': 'cash'
    }
)
booking = response.json()
print(f"Booking created by: {booking['created_by_name']}")
```

### Record Payment

```python
response = requests.post('https://homs-backend-txs8.onrender.com/payments/',
    headers=headers,
    json={
        'booking_id': booking['id'],
        'amount': 100000,
        'payment_method': 'cash',
        'notes': 'Balance payment'
    }
)
payment = response.json()
print(f"Payment received by: {payment['received_by_name']}")
```

---

## Important Notes

### For Daily Summaries

- If you submit for a date that already exists, it **updates** instead of creating duplicate
- All fields are required
- User tracking shows who submitted/updated

### For Customers

- Phone number is used for searching returning guests
- Balance can be negative (guest owes money) or positive (prepaid)
- `visit_count` increments automatically on new bookings

### For Rooms

- Room number must be unique
- Only Owner role can create/update rooms
- Status automatically updates based on bookings

### For Bookings

- Creates records for `created_by` (who made booking)
- Updates `checked_in_by` when checking in
- Updates `checked_out_by` when checking out
- Mobile app shows all these names for accountability

### For Payments

- **Critical for cash handling!** Always shows `received_by_name`
- Owner can verify who received each payment
- Links to booking for balance tracking

---

## Currency

All amounts are in **Ugandan Shillings (UGX)**.

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing/invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource doesn't exist
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

---

## Support

For questions or issues:
- Contact backend developer
- Check `https://homs-backend-txs8.onrender.com/docs` for interactive API documentation (Swagger UI)
- Check `https://homs-backend-txs8.onrender.com/redoc` for alternative documentation view

---

## Summary for Gift

**What you can do now:**

✅ Continue submitting daily summaries to `/summary` (already working)  
✅ Create customers via `/customers/` (track guest info)  
✅ Create rooms via `/rooms/` (if owner account)  
✅ Create bookings via `/bookings/` (track reservations)  
✅ Record payments via `/payments/` (track payment collection)

**What happens automatically:**

✅ Your user name is tracked on all actions (from JWT token)  
✅ Owner can see who performed each action in mobile app  
✅ No extra code needed - just authenticate and send data  
✅ Old approach (daily summaries only) still works perfectly

**Migration Status:**

The backend has been updated (February 19, 2026) with migration **004_daily_summary_tracking** which adds user tracking columns (`created_by`, `updated_by`) to the daily_summaries table. This migration should already be applied, but if you encounter issues, contact the owner to run it via the `/admin/run-migrations` endpoint.

**API Base URL:** `https://homs-backend-txs8.onrender.com`

---

**End of Documentation**
