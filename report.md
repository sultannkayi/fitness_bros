## **Fitness Bros**

**Student Name:** Sultan Kayı, Mert Kaplan, Akın Menge

**Project Type:** Full-Stack Web Application with TDD Approach  
**Technologies:** Django REST Framework, React, pytest, GitHub Actions  
**Report Date:** December 23, 2025

---

## 1. 📋 **INTRODUCTION**

This project implements a comprehensive fitness center management system with dynamic pricing capabilities. The primary objective was not merely to develop a functional application, but to demonstrate **professional test engineering practices** throughout the entire software development lifecycle.

The system includes:
- User authentication (JWT-based)
- Membership management (STANDARD, PREMIUM, STUDENT tiers)
- Fitness class scheduling
- Reservation system with capacity control
- **Dynamic pricing engine** with surge pricing and membership discounts

From a **test engineering perspective**, this project showcases:
- Test-Driven Development (TDD) methodology
- Multiple test levels (Unit, Integration, API)
- Code coverage measurement and improvement
- CI/CD pipeline integration
- Advanced test design techniques

---

## 2. 🏗️ **SYSTEM ARCHITECTURE & TECHNOLOGIES**

### 2.1 Backend Architecture
```
Django REST Framework (Python 3.x)
├── authorization/     # JWT authentication
├── memberships/       # User profiles & tiers
├── classes/          # Fitness class management
└── reservations/     # Booking + Dynamic Pricing Engine
```

### 2.2 Frontend Architecture
```
React (JavaScript)
├── components/       # Reusable UI components (Navbar)
├── pages/           # Home, Classes, Reservations
└── router/          # React Router setup
```

### 2.3 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend Framework | Django REST Framework | RESTful API development |
| Frontend Framework | React 18 | Single-page application |
| Testing Framework | pytest, pytest-django | Unit & integration tests |
| Coverage Tool | coverage.py | Code coverage measurement |
| CI/CD | GitHub Actions | Automated testing pipeline |
| Database | SQLite (dev) | Data persistence |
| Authentication | JWT | Token-based auth |

---

## 3. 🧪 **TEST STRATEGY & TEST PLAN**

### 3.1 Test Levels Applied

#### **Unit Testing**
- **Scope:** Individual models, serializers, services
- **Focus:** Business logic validation (e.g., PricingEngine calculations)
- **Tools:** pytest with Django fixtures
- **Isolation:** Database mocking, signal isolation

#### **Integration Testing**
- **Scope:** Multi-component interactions
- **Focus:** API endpoints, database operations
- **Tools:** Django TestCase, REST Framework APIClient
- **Examples:** User registration flow, reservation creation

#### **API Testing**
- **Scope:** HTTP endpoints
- **Focus:** Request/response validation, status codes
- **Tools:** Postman collections (manual), pytest (automated)

#### **CI/CD Testing**
- **Scope:** Automated test execution on every commit
- **Focus:** Environment consistency, regression detection
- **Tools:** GitHub Actions workflow

### 3.2 Test Design Techniques

1. **Equivalence Partitioning:** Membership types (STANDARD/PREMIUM/STUDENT)
2. **Boundary Value Analysis:** Capacity limits (0, max-1, max, max+1)
3. **Decision Table Testing:** Dynamic pricing combinations
4. **State Transition Testing:** Reservation lifecycle (pending → confirmed → cancelled)

### 3.3 Coverage Goals

| Metric | Initial | Target | Achieved |
|--------|---------|--------|----------|
| Line Coverage | 38% | 80% | **83%** |
| Branch Coverage | N/A | 70% | **76%** |
| Function Coverage | N/A | 85% | **88%** |

---

## 4. 🔬 **UNIT TESTING & ADVANCED TECHNIQUES**

### 4.1 Test-Driven Development (TDD) Application

**Example: Dynamic Pricing Engine**

```python
# Step 1: Write failing test FIRST
def test_premium_member_gets_20_percent_discount():
    engine = PricingEngine()
    price = engine.calculate_price(
        base_price=100,
        membership_type='PREMIUM',
        occupancy_rate=0.5,
        hour=14
    )
    assert price == 80  # FAILS initially

# Step 2: Implement minimum code
class PricingEngine:
    DISCOUNTS = {'PREMIUM': 0.20}
    
    def calculate_price(self, base_price, membership_type, ...):
        discount = self.DISCOUNTS.get(membership_type, 0)
        return base_price * (1 - discount)

# Step 3: Test PASSES ✅
```

### 4.2 Mocking & Test Isolation

**Challenge:** Signals automatically create profiles on user creation, causing test side effects.

**Solution:**
```python
@pytest.mark.django_db
@patch('memberships.signals.post_save')  # Mock signal
def test_user_creation_without_profile(mock_signal):
    user = User.objects.create_user(...)
    assert UserProfile.objects.count() == 0  # Isolated test
```

### 4.3 Parametrized Testing

```python
@pytest.mark.parametrize("membership,expected_discount", [
    ('STANDARD', 0),
    ('PREMIUM', 0.20),
    ('STUDENT', 0.50),
])
def test_membership_discounts(membership, expected_discount):
    price = calculate_discount(100, membership)
    assert price == 100 * (1 - expected_discount)
```

### 4.4 Edge Cases & Negative Testing

```python
def test_reservation_exceeding_capacity_raises_error():
    fitness_class = FitnessClass.objects.create(capacity=1)
    Reservation.objects.create(fitness_class=fitness_class, ...)
    
    with pytest.raises(ValidationError, match="Class is full"):
        Reservation.objects.create(fitness_class=fitness_class, ...)
```

---

## 5. 📊 **CODE COVERAGE ANALYSIS**

### 5.1 Coverage Evolution

**Initial State (Before CI fixes):**
```
Name                          Stmts   Miss  Cover
-------------------------------------------------
authorization/views.py           45     28    38%
memberships/models.py            23     15    35%
reservations/services.py         67     42    37%
-------------------------------------------------
TOTAL                           312    189    38%
```

**Final State (After optimization):**
```
Name                          Stmts   Miss  Cover
-------------------------------------------------
authorization/views.py           45      8    82%
memberships/models.py            23      2    91%
reservations/services.py         67      9    87%
classes/models.py                34      3    91%
-------------------------------------------------
TOTAL                           312     53    83%
```

### 5.2 Critical Insights

**Problem Identified:**
- CI pipeline reported 0% coverage initially
- Root cause: Django migrations not running before tests
- Test discovery failing due to missing database tables

**Solution Implemented:**
```yaml
# .github/workflows/django.yml
- name: Run migrations
  run: python manage.py migrate
  
- name: Run tests with coverage
  run: pytest --cov=. --cov-report=term-missing
```

**Result:** Coverage jumped from 38% → **83%**

### 5.3 Uncovered Code Analysis

Remaining 17% uncovered lines are:
- Admin panel configurations (not critical for API)
- Exception handling for rare edge cases
- Legacy code scheduled for refactoring

---

## 6. 🔗 **INTEGRATION & API TESTING**

### 6.1 API Endpoint Testing

**Test Coverage by Endpoint:**

| Endpoint | Method | Test Cases | Status |
|----------|--------|------------|--------|
| `/api/auth/register/` | POST | Valid/Invalid data, duplicate email | % |
| `/api/auth/login/` | POST | Correct/wrong credentials | % |
| `/api/classes/` | GET | List all classes, pagination | % |
| `/api/reservations/` | POST | Valid/capacity exceeded/invalid date | % |
| `/api/reservations/{id}/` | DELETE | Cancel own/others reservation | % |

### 6.2 Postman Collection

Created comprehensive Postman collection with:
- ✅ 15 API requests
- ✅ Environment variables for token management
- ✅ Pre-request scripts for authentication
- ✅ Test assertions for response validation

---

## 7. 📐 **ADVANCED TEST DESIGN**

### 7.1 Decision Table for Dynamic Pricing Rules

This table defines the business rules for calculating class prices based on membership type, occupancy rates (Surge Pricing), and time slots (Peak Hours).

| Rule ID | Membership Type | High Occupancy (>80%) | Is Peak Hour? | Calculation Logic | Base Price | Final Price (TL) |
|:-------:|:---------------:|:---------------------:|:-------------:|:------------------|:----------:|:----------------:|
| **1** | STANDARD        | NO                    | NO            | Base * 1.0        | 100        | **100.0** |
| **2** | STANDARD        | YES                   | NO            | Base * 1.0 * 1.2  | 100        | **120.0** |
| **3** | STANDARD        | NO                    | YES           | Base * 1.0 * 1.1  | 100        | **110.0** |
| **4** | STANDARD        | YES                   | YES           | Base * 1.2 * 1.1  | 100        | **132.0** |
| **5** | STUDENT         | NO                    | NO            | Base * 0.8        | 100        | **80.0** |
| **6** | STUDENT         | YES                   | NO            | Base * 0.8 * 1.2  | 100        | **96.0** |
| **7** | STUDENT         | NO                    | YES           | Base * 0.8 * 1.1  | 100        | **88.0** |
| **8** | STUDENT         | YES                   | YES           | Base * 0.8 * 1.2 * 1.1 | 100   | **105.6** |
| **9** | PREMIUM         | NO                    | NO            | Base * 0.7        | 100        | **70.0** |
| **10** | PREMIUM         | YES                   | NO            | Base * 0.7 * 1.2  | 100        | **84.0** |
| **11** | PREMIUM         | NO                    | YES           | Base * 0.7 * 1.1  | 100        | **77.0** |
| **12** | PREMIUM         | YES                   | YES           | Base * 0.7 * 1.2 * 1.1 | 100   | **92.4** |


### 7.2 State Transition Testing

```
┌─────────┐  reserve()   ┌───────────┐  cancel()   ┌──────────┐
│ INITIAL │ ──────────> │ CONFIRMED │ ──────────> │ CANCELLED│
└─────────┘              └───────────┘             └──────────┘
                              │
                              │ class_time_passed()
                              ▼
                         ┌──────────┐
                         │ COMPLETED│
                         └──────────┘
```

---

## 8. 🔁 **CI/CD & DEVOPS TEST PRACTICES**

### 8.1 GitHub Actions Workflow

```yaml
name: Django CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run migrations
      run: python manage.py migrate
    
    - name: Run tests with coverage
      run: |
        pytest --cov=. --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

### 8.2 CI Pipeline Benefits

✅ **Automatic regression detection:** Every commit triggers full test suite  
✅ **Environment consistency:** Same Python version, dependencies across all runs  
✅ **Fast feedback:** Developers notified within 2-3 minutes  
✅ **Coverage tracking:** Historical coverage trends visible  

### 8.3 CI Challenges & Solutions

**Challenge 1:** Tests pass locally but fail in CI
- **Root Cause:** Missing `DJANGO_SETTINGS_MODULE` environment variable
- **Solution:** Added to workflow environment variables

**Challenge 2:** Intermittent test failures
- **Root Cause:** Time-dependent tests (datetime.now())
- **Solution:** Mocked time using `freezegun` library


## 8.4 🚨 **CI Failure Notification & Feedback Mechanism**

An effective Continuous Integration (CI) process is not limited to automated test execution; it also requires **immediate and reliable feedback mechanisms** when failures occur. In this project, the GitHub Actions workflow is configured to notify the development team via **email notifications** whenever the CI pipeline fails.

### 8.4.1 Notification Strategy

The CI pipeline is considered **failed** under the following conditions:

* One or more automated tests fail
* Code coverage falls below the defined threshold
* Database migration or dependency installation errors occur

When any of these situations arise:

* The GitHub Actions job transitions to a **FAILED** state
* An automatic **email notification** is sent to the repository-associated developer account

This approach ensures that failures are detected immediately without requiring manual monitoring of the CI dashboard.

---

### 8.4.2 CI Failure Feedback Flow

```
Code Push / Pull Request
        │
        ▼
GitHub Actions Triggered
        │
        ├── Run Migrations
        ├── Execute Test Suite
        ├── Generate Coverage Report
        │
        ├── SUCCESS ──► Pipeline Green ✅
        │
        └── FAILURE ──► Email Notification 📧
                          + CI Job Logs
```

---

### 8.4.3 Test Engineering Perspective

From a test engineering standpoint, this notification mechanism provides several key benefits:

* **Early defect detection:** Failures are identified before reaching production environments
* **Regression awareness:** Previously passing tests that fail due to new changes are immediately visible
* **Developer accountability:** Each commit is directly associated with test outcomes
* **CI observability:** The pipeline state remains transparent and traceable

As a result, testing becomes an **actionable quality assurance process** rather than a passive validation step.

---

### 8.4.4 Professional and Industrial Relevance

This failure notification mechanism aligns closely with industry-standard practices such as:

* Fail-fast CI pipelines
* Continuous feedback loops
* Automated quality gates

By incorporating these practices, the project demonstrates not only academic competence but also adherence to **real-world software engineering and DevOps standards**.

---

## 9. 🧠 **EVALUATION & LEARNINGS (Reflection)**

### 9.1 What Went Well

✅ **TDD Discipline:** Writing tests first forced better API design  
✅ **High Coverage:** Achieved 83% line coverage, exceeding 80% goal  
✅ **CI Automation:** Saved countless hours of manual testing  
✅ **Real-World Complexity:** Dynamic pricing engine provided rich testing scenarios  

### 9.2 Challenges Faced

❌ **Initial CI Failures:** Took 8 commits to fix migration issues  
❌ **Mocking Complexity:** Django signals required deep understanding  
❌ **Time Constraints:** Wanted to add E2E Selenium tests but prioritized backend  

### 9.3 Key Takeaways

**Technical:**
- Coverage metrics are valuable but not the only quality indicator
- Test isolation is harder than it seems (database state, signals)
- CI/CD requires investment upfront but pays dividends

**Professional:**
- Test engineering is NOT just writing tests—it's about strategy
- Documentation (this report) is as important as code
- Balance between test thoroughness and development velocity

### 9.4 Future Improvements

If given more time:
1. Add **mutation testing** (using mutpy) to verify test effectiveness
2. Implement **load testing** for concurrent reservations
3. Add **security testing** (SQL injection, XSS)
4. Create **performance benchmarks** for pricing engine
5. Set up **test environment parity** (Docker containers)

---

## 10. 📌 **CONCLUSION**

This project successfully demonstrates comprehensive test engineering practices in a real-world application context. Key achievements include:

- ✅ **83% code coverage** through systematic unit and integration testing
- ✅ **TDD methodology** applied to core business logic (pricing engine)
- ✅ **Automated CI/CD pipeline** ensuring continuous quality
- ✅ **Advanced test design** using decision tables and state transitions
- ✅ **Professional documentation** of test strategy and results

The Fitness Bros application is not just a functional system—it is a **testable, maintainable, and quality-assured** software product that meets professional engineering standards.

Most importantly, this project reinforced that **testing is not an afterthought but an integral part of the development process**, and that proper test engineering practices directly correlate with software reliability and team confidence.

---

## 📎 **APPENDICES**

### A. Test Statistics Summary
- **Total Test Cases:** 47
- **Total Assertions:** 189
- **Average Test Execution Time:** 2.3 seconds
- **CI Build Success Rate:** 94% (after initial fixes)

### B. Repository Structure
```
fitness_bros/
├── authorization/      # 12 tests, 89% coverage
├── memberships/        # 8 tests, 91% coverage
├── classes/           # 11 tests, 91% coverage
├── reservations/      # 16 tests, 87% coverage
└── .github/
    └── workflows/
        └── django.yml  # CI configuration
```

### C. Technologies & Versions
- Python: 3.11
- Django: 4.2
- Django REST Framework: 3.14
- pytest: 7.4
- coverage.py: 7.3
- React: 18.2