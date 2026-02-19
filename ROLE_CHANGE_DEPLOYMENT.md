# User Role Changes - Deployment Instructions

## Summary of Changes

As requested, the following changes have been made to the User Role system:

### Backend Changes (Python/FastAPI)

1. **UserRole Enum Updated** (`backend/models/user.py`)
   - ❌ Removed: `ACCOUNTANT` 
   - ✅ Added: `ADMIN`
   - Final roles: `OWNER`, `RECEPTIONIST`, `ADMIN`

2. **Database Migration Created** (`backend/alembic/versions/002_update_user_roles.py`)
   - Automatically migrates any existing `ACCOUNTANT` users to `RECEPTIONIST`
   - Updates the PostgreSQL enum type
   - Safe to run on production without data loss

3. **API Endpoints Updated** (`backend/routes/auth.py`)
   - `POST /auth/register` - Now accepts `"admin"` and `"receptionist"` (lowercase)
   - `GET /auth/me` - Returns role in lowercase (e.g., `"admin"`, `"receptionist"`, `"owner"`)

4. **Documentation Updated**
   - Comments and docstrings updated to reference `admin` instead of `accountant`

### Mobile App Changes (Flutter/Dart)

1. **User Model Updated** (`homs_app/lib/models/user.dart`)
   - Changed `isAccountant` getter to `isAdmin`
   - Now correctly recognizes `admin` role

---

## What These Changes Result In

### 1. **Simplified Role Structure**
- ✅ **Owner**: Full system access (creates other users, manages everything)
- ✅ **Admin**: Elevated staff role (approves expenses, manages operations)
- ✅ **Receptionist**: Front-desk staff (bookings, check-ins, payments)

### 2. **No Data Loss**
- Any existing accountant users are automatically converted to receptionists
- All historical data (bookings, payments, audit logs) remains intact
- No business continuity impact

### 3. **Clearer Permissions**
The system now has a more logical hierarchy:
```
Owner (highest)
  └─ Can register Admin and Receptionist users
  └─ Full system control

Admin (elevated staff)
  └─ Approve expenses
  └─ Generate reports
  └─ Manage room pricing

Receptionist (daily operations)
  └─ Handle check-ins/check-outs
  └─ Process payments
  └─ Manage customer records
```

### 4. **API Consistency**
- All role values are now lowercase in API responses
- `POST /auth/register` accepts: `"admin"` or `"receptionist"`
- `GET /auth/me` returns: `{"role": "admin"}` (always lowercase)

### 5. **Mobile App Compatibility**
- App now displays "Admin" badge correctly (instead of "Accountant")
- Role-based UI features work with new admin role
- No app reinstallation needed (just redeploy backend)

---

## How to Deploy These Changes

### Step 1: Backup (CRITICAL)
Before running any migration, backup your production database:
```bash
# On Render dashboard, create a manual backup
# Or use PostgreSQL backup command
pg_dump -U postgres homs_production > backup_before_role_change.sql
```

### Step 2: Deploy Backend Code
Since your backend is on Render:

1. **Commit and push the changes:**
   ```bash
   cd backend
   git add .
   git commit -m "Update UserRole: Remove accountant, add admin"
   git push origin main
   ```

2. **Render will automatically detect the new commit and redeploy**

### Step 3: Run the Migration
After the deployment completes, run the migration:

1. **Access Render Shell:**
   - Go to your Render dashboard
   - Click on your `homs-backend` service
   - Click "Shell" tab
   - Run:
   ```bash
   alembic upgrade head
   ```

2. **Verify Migration:**
   You should see output like:
   ```
   ✅ Successfully migrated UserRole enum:
      - Removed ACCOUNTANT
      - Added ADMIN
      - Migrated existing ACCOUNTANT users to RECEPTIONIST
   ```

### Step 4: Verify Data
Check that users were migrated correctly:

```bash
# In Render Shell, open Python:
python

# Then run:
from database import SessionLocal
from models.user import User
db = SessionLocal()

# Check all users
users = db.query(User).all()
for u in users:
    print(f"{u.email}: {u.role}")

# Should show something like:
# owner@lemihotel.com: owner
# staff@lemihotel.com: receptionist  (was accountant before)
```

### Step 5: Test the API
Use the API to verify everything works:

```bash
# Test login
curl -X POST https://homs-backend-txs8.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@lemihotel.com","password":"admin123"}'

# Response should show lowercase role:
# {"access_token":"...","role":"owner", ...}

# Test creating admin user (as owner)
curl -X POST https://homs-backend-txs8.onrender.com/auth/register \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"admin@lemihotel.com",
    "password":"secure123",
    "full_name":"Hotel Admin",
    "role":"admin"
  }'
```

### Step 6: Update Mobile App
The mobile app changes are already made. No reinstallation needed - the app will automatically recognize the new `admin` role when users log in.

---

## Rollback Plan (If Needed)

If something goes wrong, you can rollback the migration:

```bash
# In Render Shell:
alembic downgrade -1
```

This will:
- Remove the `ADMIN` role
- Add back the `ACCOUNTANT` role
- Migrate any `ADMIN` users back to `RECEPTIONIST`

Then restore your database backup if needed.

---

## Testing Checklist

After deployment, verify:

- [ ] Owner can log in successfully
- [ ] Owner can create new "admin" users via the app
- [ ] Admin users can log in
- [ ] Receptionist users can log in
- [ ] Mobile app displays "Admin" badge (not "Accountant")
- [ ] All existing bookings/payments are intact
- [ ] No error logs in Render dashboard

---

## Questions?

If you encounter any issues during deployment:

1. Check Render logs: Dashboard → Logs tab
2. Check migration output for errors
3. Verify database connection is active
4. Message me with the specific error message

---

**Prepared for:** Gift - Lemi Hotel Management System  
**Date:** February 19, 2026  
**Changes:** UserRole enum update (accountant → admin)
