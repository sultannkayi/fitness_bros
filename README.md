# Fitness Bros

REST API for booking fitness classes with dynamic pricing, developed for the CEN315 Test Engineering project. Includes end-to-end testing: unit, integration, mutation, property-based, performance, combinatorial, and security testing.

## Project Structure

```
fitness_bros/
├── fitness_bros_project/     # Django project settings
│   ├── settings.py           # Project configuration
│   ├── urls.py               # URL routing with DRF routers
│   └── wsgi.py               # WSGI application
├── memberships/              # Member management app
│   ├── models.py             # Member model
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # ViewSets
│   └── tests.py              # Unit and API tests
├── classes/                  # Fitness class management app
│   ├── models.py             # FitnessClass model
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # ViewSets
│   └── tests.py              # Unit and API tests
├── reservations/             # Reservation management app
│   ├── models.py             # Reservation model with capacity check
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # ViewSets
│   └── tests.py              # Unit, API, and integration tests
├── manage.py                 # Django management script
└── requirements.txt          # Python dependencies
```

## Features

- **Members Management**: CRUD operations for gym members with membership types (basic, premium, VIP)
- **Fitness Classes**: Manage fitness classes with scheduling, pricing, and capacity tracking
- **Reservations**: Book classes with automatic capacity validation
- **REST API**: Full REST API built with Django REST Framework
- **Capacity Check**: Prevents overbooking of fitness classes
- **Search & Filtering**: Search members and classes, filter by various criteria

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sultannkayi/fitness_bros.git
cd fitness_bros
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Members
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/members/` | List all members |
| POST | `/api/members/` | Create a new member |
| GET | `/api/members/{id}/` | Retrieve a member |
| PUT | `/api/members/{id}/` | Update a member |
| DELETE | `/api/members/{id}/` | Delete a member |
| GET | `/api/members/active/` | List active members |
| GET | `/api/members/{id}/reservations/` | List member's reservations |

### Fitness Classes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/classes/` | List all classes |
| POST | `/api/classes/` | Create a new class |
| GET | `/api/classes/{id}/` | Retrieve a class |
| PUT | `/api/classes/{id}/` | Update a class |
| DELETE | `/api/classes/{id}/` | Delete a class |
| GET | `/api/classes/available/` | List classes with available spots |
| GET | `/api/classes/{id}/reservations/` | List class reservations |

### Reservations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reservations/` | List all reservations |
| POST | `/api/reservations/` | Create a reservation (with capacity check) |
| GET | `/api/reservations/{id}/` | Retrieve a reservation |
| PUT | `/api/reservations/{id}/` | Update a reservation |
| DELETE | `/api/reservations/{id}/` | Delete a reservation |
| POST | `/api/reservations/{id}/cancel/` | Cancel a reservation |
| GET | `/api/reservations/confirmed/` | List confirmed reservations |

## Models

### Member
- `first_name`: CharField (max 100)
- `last_name`: CharField (max 100)
- `email`: EmailField (unique)
- `phone`: CharField (optional)
- `membership_type`: Choice field (basic, premium, vip)
- `is_active`: BooleanField (default True)
- `joined_date`: DateField (auto)
- `created_at`, `updated_at`: DateTimeField (auto)

### FitnessClass
- `name`: CharField (max 200)
- `class_type`: Choice field (yoga, pilates, spinning, hiit, strength, cardio, crossfit, dance)
- `description`: TextField (optional)
- `instructor`: CharField (max 100)
- `schedule`: DateTimeField
- `duration_minutes`: PositiveIntegerField (default 60)
- `capacity`: PositiveIntegerField (default 20)
- `price`: DecimalField
- `is_active`: BooleanField (default True)
- `created_at`, `updated_at`: DateTimeField (auto)

### Reservation
- `member`: ForeignKey to Member
- `fitness_class`: ForeignKey to FitnessClass
- `status`: Choice field (confirmed, cancelled, waitlist)
- `reserved_at`: DateTimeField (auto)
- `updated_at`: DateTimeField (auto)
- `notes`: TextField (optional)

## Testing

Run all tests:
```bash
python manage.py test
```

Run tests for a specific app:
```bash
python manage.py test memberships
python manage.py test classes
python manage.py test reservations
```

Run with verbosity:
```bash
python manage.py test -v 2
```

## Test Coverage

The project includes comprehensive tests covering:

- **Model Tests**: Creation, validation, properties, string representation
- **API Tests**: CRUD operations, search, filtering, custom endpoints
- **Integration Tests**: Capacity tracking across the system
- **Validation Tests**: Capacity checks, inactive member restrictions, unique constraints

## Advanced Test Engineering

This project is structured to support advanced testing methodologies:

- **Unit Testing**: Individual model and serializer tests
- **Integration Testing**: API endpoint and cross-app functionality
- **Mutation Testing**: Structure supports mutation testing tools
- **Property-based Testing**: Models designed for hypothesis testing
- **Performance Testing**: API endpoints ready for load testing
- **Security Testing**: Input validation and authorization ready for security testing

## License

MIT License

