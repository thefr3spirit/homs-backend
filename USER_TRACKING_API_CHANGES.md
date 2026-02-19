# Backend Changes: User Tracking System

**Date:** February 19, 2026  
**For:** Gift (Desktop App Developer)  
**Status:** ✅ Deployed to Production

---

## Overview

The backend now tracks which staff member performs each action. All API responses now include the **names** of users who created or modified records.

---

## What Changed

### 1. Customer API Changes

**Endpoint:** `GET /customers` and `GET /customers/{id}`

**New Response Fields:**
```json
{
  "id": "abc123",
  "full_name": "John Doe",
  "phone": "+256-123-456-789",
  "email": "john@example.com",
  "customer_type": "regular",
  "pending_balance": 50000.0,
  "total_spent": 200000.0,
  "total_visits": 5,
  "created_at": "2026-02-15T10:30:00Z",
  "updated_at": "2026-02-18T14:20:00Z",
  
  // *** NEW FIELDS ***
  "created_by": "user-uuid-here",           // User ID who created
  "updated_by": "user-uuid-here",           // User ID who last updated
  "created_by_name": "Sarah Mukasa",        // ✅ Display this name
  "updated_by_name": "John Okello"          // ✅ Display this name
}
```

**Desktop App Action:**
- Display `created_by_name` to show who added the customer
- Display `updated_by_name` to show who last edited the customer
- Show this info in customer details view or as a subtitle in lists

---

### 2. Booking API Changes

**Endpoint:** `GET /bookings` and `GET /bookings/{id}`

**New Response Fields:**
```json
{
  "id": "book123",
  "customer_id": "cust123",
  "room_id": "room101",
  "check_in_date": "2026-02-20",
  "check_out_date": "2026-02-22",
  "total_amount": 150000.0,
  "amount_paid": 50000.0,
  "booking_status": "checked_in",
  "created_by": "user-uuid-1",
  "checked_in_by": "user-uuid-2",
  "checked_out_by": null,
  
  // *** NEW FIELDS ***
  "created_by_name": "Sarah Mukasa",        // ✅ Who created the booking
  "checked_in_by_name": "John Okello",      // ✅ Who checked in the guest
  "checked_out_by_name": null               // ✅ Who checked out the guest (null if not checked out yet)
}
```

**Desktop App Action:**
- Show `created_by_name` when displaying booking details ("Booked by: Sarah Mukasa")
- Show `checked_in_by_name` after check-in ("Checked in by: John Okello")
- Show `checked_out_by_name` after check-out ("Checked out by: John Okello")

---

### 3. Payment API Changes

**Endpoint:** `GET /payments` and `GET /payments/{id}`

**New Response Fields:**
```json
{
  "id": "pay123",
  "booking_id": "book123",
  "customer_id": "cust123",
  "amount": 50000.0,
  "payment_method": "cash",
  "payment_type": "partial",
  "payment_status": "completed",
  "payment_date": "2026-02-19T15:30:00Z",
  "received_by": "user-uuid-here",
  
  // *** NEW FIELD ***
  "received_by_name": "Sarah Mukasa"        // ✅ Who received the payment
}
```

**Desktop App Action:**
- Display `received_by_name` in payment records ("Received by: Sarah Mukasa")
- Show this in payment history, receipts, and daily summaries

---

### 4. Room API Changes

**Endpoint:** `GET /rooms` and `GET /rooms/{id}`

**New Response Fields:**
```json
{
  "id": "room101",
  "room_number": "101",
  "room_type": "deluxe",
  "floor": 1,
  "daily_rate": 75000.0,
  "status": "available",
  
  // *** NEW FIELDS ***
  "created_by": "user-uuid-here",
  "updated_by": "user-uuid-here",
  "created_by_name": "Owner Name",          // ✅ Who created the room
  "updated_by_name": "Sarah Mukasa",        // ✅ Who last updated status/details
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-02-19T14:00:00Z"
}
```

**Desktop App Action:**
- Optionally display `updated_by_name` when showing room status changes
- Helps track who changed room status (e.g., "Set to maintenance by: John")

---

## How to Display This in Your Desktop App

### Recommended UI Locations:

#### **Customer List/Details:**
```
Customer: John Doe
Phone: +256-123-456-789
Total Visits: 5
Pending Balance: UGX 50,000

📝 Updated by: Sarah Mukasa on Feb 18, 2:20 PM
```

#### **Booking Details:**
```
Booking #12345
Guest: Jane Smith
Room: 101 (Deluxe)
Check-in: Feb 20, 2026
Check-out: Feb 22, 2026

👤 Created by: Sarah Mukasa
✅ Checked in by: John Okello
```

#### **Payment Receipt:**
```
PAYMENT RECEIPT
Amount: UGX 50,000
Method: Cash
Date: Feb 19, 2026 3:30 PM

💰 Received by: Sarah Mukasa
```

---

## Backward Compatibility

**Don't worry about old data!**

- Old records created before this update will have `null` for these new fields
- Your desktop app should handle `null` values gracefully
- Example: `if (created_by_name != null) { show("Created by: $created_by_name") }`

---

## When Creating New Records

When **creating** customers, bookings, or payments via POST requests, you don't need to send these fields. The backend automatically:

1. Reads the JWT token from the `Authorization` header
2. Extracts the current user's ID
3. Sets `created_by` to that user automatically
4. Returns the response with `created_by_name` filled in

**Example - Creating a Customer:**
```http
POST /customers
Authorization: Bearer your-jwt-token
Content-Type: application/json

{
  "full_name": "New Customer",
  "phone": "+256-999-888-777",
  "customer_type": "regular"
  // ❌ Don't send created_by - it's automatic!
}

Response:
{
  "id": "new-id",
  "full_name": "New Customer",
  "phone": "+256-999-888-777",
  "created_by": "your-user-id",
  "created_by_name": "Your Name",  // ✅ Automatically filled
  ...
}
```

---

## Database Migration

A database migration (`003_add_user_tracking.py`) was deployed that:

- Added `created_by` and `updated_by` columns to `customers` table
- Added `created_by` and `updated_by` columns to `rooms` table  
- Added timestamps (`created_at`, `updated_at`) to `rooms` table
- Created foreign key relationships to the `users` table

**No action needed** - this ran automatically on deployment.

---

## Testing

To test in your desktop app:

1. **Login** as any user (owner/receptionist/admin)
2. **Create a new customer** - should see your name in response
3. **Create a booking** - should see your name as creator
4. **Record a payment** - should see your name as receiver
5. **View existing records** - old ones will have `null`, new ones will show names

---

## Benefits for Users

✅ **Accountability** - See who performed each action  
✅ **Audit Trail** - Track all changes by staff member  
✅ **Quality Control** - Identify who needs training  
✅ **Transparency** - Staff know their work is recorded  
✅ **Error Resolution** - Quickly find who to ask about a record  

---

## Questions?

If you have questions or need help implementing this in the desktop app:

1. Check the mobile app code at `homs_app/lib/models/` for reference
2. All fields are **optional** (can be `null`), so handle gracefully
3. Only display these fields if you have space in your UI
4. Priority: Show `received_by_name` for payments (most important for cash handling)

---

## API Endpoint Reference

All endpoints are at: `https://homs-backend-txs8.onrender.com`

- `GET /customers` - List customers (paginated)
- `GET /customers/{id}` - Get customer details
- `POST /customers` - Create customer (auto-tracks creator)
- `PUT /customers/{id}` - Update customer (auto-tracks updater)
- `GET /bookings` - List bookings
- `GET /bookings/{id}` - Get booking details  
- `GET /payments` - List payments
- `GET /payments/{id}` - Get payment details
- `GET /rooms` - List rooms

All responses now include the user tracking fields described above.

---

**Happy Coding!** 🚀

If you need any clarification or examples, just ask!
