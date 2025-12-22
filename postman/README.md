# Fitness Bros - Postman API Testing

This folder contains Postman collection and environment files for testing the Fitness Bros API.

## Files

- **Fitness_Bros_API_Collection.postman_collection.json** - Complete API test collection
- **Fitness_Bros_Local_Development.postman_environment.json** - Environment variables for local development

## Setup Instructions

### 1. Start Django Backend
```bash
cd /Users/sultankayi/Documents/GitHub/fitness_bros
python manage.py runserver
```

### 2. Import to Postman

#### Method 1: Using Postman Desktop App
1. Open Postman
2. Click "Import" button (top left)
3. Select both JSON files:
   - `Fitness_Bros_API_Collection.postman_collection.json`
   - `Fitness_Bros_Local_Development.postman_environment.json`
4. Click "Import"

#### Method 2: Using Drag & Drop
1. Open Postman
2. Drag and drop both JSON files into the Postman window

### 3. Select Environment
1. In Postman, click the environment dropdown (top right)
2. Select "Fitness Bros - Local Development"

### 4. Run Tests

#### Test Order (Recommended)
Run tests in this sequence:

1. **Authentication → Register User**
   - Creates a new test user account
   - Validates registration response

2. **Authentication → Login User**
   - Logs in with test user credentials
   - Automatically saves authentication token

3. **Classes → Get All Fitness Classes**
   - Retrieves list of available classes
   - Automatically saves first class ID for reservations

4. **Reservations → Create Reservation**
   - Creates a reservation using saved class_id
   - Requires authentication token
   - Automatically saves reservation ID

5. **Reservations → Delete Reservation (Cancel)**
   - Cancels the created reservation
   - Uses saved reservation_id

6. **Health Check → API Health Check**
   - Verifies Django backend is running

#### Run All Tests
1. Click on "Fitness Bros API Tests" collection
2. Click "Run" button
3. Select "Run Fitness Bros API Tests"
4. Tests will run in sequence

## API Endpoints Overview

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get token

### Classes
- `GET /api/classes/` - List all active fitness classes (no auth required)

### Reservations
- `POST /api/reservations/` - Create reservation (auth required)
- `DELETE /api/reservations/{id}/` - Cancel reservation (auth required)

### Health Check
- `GET /admin/` - Verify backend is running

## Environment Variables

The environment includes the following variables:

| Variable | Description | Auto-set |
|----------|-------------|----------|
| `base_url` | API base URL | Manual |
| `token` | Authentication token | ✓ Login |
| `class_id` | Fitness class ID | ✓ Get Classes |
| `reservation_id` | Reservation ID | ✓ Create Reservation |

Variables marked with ✓ are automatically set by test scripts.

## Test Assertions

Each endpoint includes automated tests that verify:

### Register User
- Status code is 201 Created
- Response contains email and name
- Response time < 500ms

### Login User
- Status code is 200 OK
- Response contains valid token
- Response contains user data
- Token is saved to environment

### Get All Classes
- Status code is 200 OK
- Response is an array
- Classes have required fields (id, name, instructor, capacity, date_time)
- First class ID is saved to environment
- Response time < 300ms

### Create Reservation
- Status code is 201 Created
- Response contains reservation ID
- Reservation ID is saved to environment

### Delete Reservation
- Status code is 204 No Content
- Response body is empty

### Health Check
- Status code is 200 OK
- Admin page is accessible

## Troubleshooting

### "Connection refused" error
- Make sure Django server is running: `python manage.py runserver`
- Verify base_url is set to `http://localhost:8000`

### "401 Unauthorized" error
- Run Login request first to get authentication token
- Check that token is saved in environment variables

### "Class not found" error
- Run "Get All Fitness Classes" first to populate class_id
- Check that database has active fitness classes

### Tests failing
- Check Django console for error messages
- Verify database migrations are applied: `python manage.py migrate`
- Ensure test data exists in database

## Creating Test Data

If you need to create test fitness classes:

```bash
python manage.py shell
```

```python
from classes.models import FitnessClass
from datetime import datetime, timedelta

# Create sample classes
FitnessClass.objects.create(
    name="Morning Yoga",
    description="Relaxing yoga session",
    instructor="John Doe",
    capacity=20,
    date_time=datetime.now() + timedelta(days=1, hours=9),
    duration=60,
    is_active=True
)
```

## Business Logic Notes

### Dynamic Pricing
Reservation pricing depends on:
- User's membership type (STUDENT/STANDARD/PREMIUM)
- Class occupancy rate (surge pricing if >80% full)
- Peak hours (6-8am, 5-8pm)

### Cancellation Policy
- Free cancellation: >24 hours before class
- 50% refund: 12-24 hours before class
- No refund: <12 hours before class

### Reservation Rules
- Must book at least 1 hour in advance
- Cannot double-book same time slot
- Class must not be at full capacity

## Support

For issues or questions:
1. Check Django server logs
2. Verify database state
3. Review test assertions in Postman
4. Check API endpoint responses in Postman console
