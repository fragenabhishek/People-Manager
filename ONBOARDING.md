# 🚀 Developer Onboarding Guide

Welcome to the **People Manager** project! This guide will help you understand the codebase in 15 minutes.

---

## 📖 Quick Start

### 1. Read These Documents (in order)
1. **README.md** - Project overview, features, setup
2. **THIS FILE** - Quick architecture overview
3. **CODE_FLOW_GUIDE.md** - Deep dive into code flow
4. **ARCHITECTURE.md** - Detailed architecture documentation

---

## 🏗️ Architecture in 60 Seconds

### The Big Picture

```
┌─────────────┐
│   Browser   │  User interacts with HTML/CSS/JS
│  (Frontend) │
└──────┬──────┘
       │ HTTP (JSON)
       ▼
┌─────────────┐
│   Routes    │  Handle HTTP requests (thin layer)
│  (HTTP I/O) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Services   │  Business logic & validation
│  (Logic)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Repositories│  Data access abstraction
│   (Data)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  MongoDB /  │  Persistent storage
│   JSON      │
└─────────────┘
```

### SOLID Principles Applied
✅ **S**ingle Responsibility - Each class has one job  
✅ **O**pen/Closed - Easy to extend, no modification needed  
✅ **L**iskov Substitution - MongoDB ↔ JSON swappable  
✅ **I**nterface Segregation - Small, focused interfaces  
✅ **D**ependency Inversion - Depend on abstractions, not implementations

---

## 📂 File Structure (Priority Order)

### Start Here
1. **`app.py`** - Application entry point (120 lines)
2. **`config/config.py`** - All settings in one place
3. **`models/person.py`** - Data structure for a person

### Then Explore
4. **`repositories/person_repository.py`** - How data is stored/retrieved
5. **`services/person_service.py`** - Business logic
6. **`routes/person_routes.py`** - HTTP endpoints

### Supporting Files
7. **`middleware/auth_middleware.py`** - Authentication decorator
8. **`utils/validators.py`** - Input validation
9. **`static/script.js`** - Frontend logic

---

## 🔍 How a Request Works (Example: Add Person)

### Step-by-Step Flow

```
1️⃣ USER ACTION
   User fills form and clicks "Save"

2️⃣ FRONTEND (script.js)
   fetch('/api/people', {
     method: 'POST',
     body: JSON.stringify({name: "John", details: "..."})
   })

3️⃣ ROUTE HANDLER (routes/person_routes.py)
   @person_bp.route('', methods=['POST'])
   @login_required  ← Check if user is logged in
   def add_person():
       user_id = session.get('user_id')  ← Who is this?
       data = request.get_json()         ← Parse JSON
       
       # Delegate to service
       person = person_service.create_person(
           data['name'], 
           data['details'], 
           user_id
       )
       
       return APIResponse.created(person.to_dict())

4️⃣ SERVICE LAYER (services/person_service.py)
   def create_person(self, name, details, user_id):
       # Validate input
       Validator.validate_person_data(name, details)
       
       # Create entity
       person = Person(name=name, details=details, user_id=user_id)
       
       # Save to database
       return self.person_repository.create(person)

5️⃣ REPOSITORY LAYER (repositories/person_repository.py)
   def create(self, entity: Person) -> Person:
       if self.use_mongodb:
           # Save to MongoDB
           self.people_collection.insert_one(entity.to_dict())
       else:
           # Save to JSON file
           with open('data.json', 'w') as f:
               json.dump(all_people, f)
       
       return entity

6️⃣ RESPONSE
   Frontend receives JSON: {id: "123", name: "John", ...}
   Shows success message: "John added successfully!"
```

---

## 🎯 Key Concepts to Understand

### 1. Dependency Injection
Instead of creating dependencies inside classes, we **inject** them:

```python
# ❌ Bad (tight coupling)
class PersonService:
    def __init__(self):
        self.repo = PersonRepository()  # Hard-coded

# ✅ Good (dependency injection)
class PersonService:
    def __init__(self, person_repository: PersonRepository):
        self.repo = person_repository  # Injected
```

**Why?** Easy to test (mock the repo), easy to swap implementations.

---

### 2. Repository Pattern
Hide database details behind a simple interface:

```python
class PersonRepository:
    def find_all(self, filters) -> List[Person]:
        # Could be MongoDB, PostgreSQL, JSON, Redis...
        # Service doesn't care!
        pass
```

**Why?** Swap MongoDB ↔ JSON without changing service code.

---

### 3. Service Layer
Business logic lives here, not in routes or repositories:

```python
class PersonService:
    def create_person(self, name, details, user_id):
        # ✅ Validation
        if not name:
            raise ValidationError("Name required")
        
        # ✅ Authorization
        # (user_id ensures ownership)
        
        # ✅ Business rules
        person = Person(name=name.upper(), ...)  # Example rule
        
        # ✅ Data access
        return self.repo.create(person)
```

**Why?** Reusable, testable, clear separation of concerns.

---

### 4. Blueprints (Flask)
Organize routes into modules:

```python
# routes/person_routes.py
person_bp = Blueprint('person_routes', __name__, url_prefix='/api/people')

@person_bp.route('', methods=['GET'])
def get_people():
    # ...

# app.py
app.register_blueprint(person_bp)
# Now /api/people endpoint is registered
```

---

## 🔐 Authentication Flow

### Session-Based Auth
```
1. Login: POST /login {username, password}
   ├─► Verify credentials
   ├─► session['logged_in'] = True
   └─► session['user_id'] = user.id

2. Access Protected Route: GET /api/people
   ├─► @login_required checks session['logged_in']
   ├─► If False: redirect to /login
   └─► If True: continue to route handler

3. Authorization (Ownership Check)
   ├─► Service checks: person.user_id == session['user_id']
   └─► Users can only access their own data
```

---

## 🛠️ Development Workflow

### Making Changes

1. **Add a field to Person?**
   - Update: `models/person.py`
   - Update: `to_dict()` and `from_dict()`
   - Frontend will automatically receive it

2. **Add a new validation rule?**
   - Update: `utils/validators.py`
   - It will automatically apply in services

3. **Add a new endpoint?**
   - Add route function in appropriate `routes/*.py`
   - Call the service method
   - Return standardized response

4. **Add a new feature (e.g., Tags)?**
   - Model → Repository → Service → Route → Frontend
   - See "Adding New Features" in CODE_FLOW_GUIDE.md

---

## 📝 Code Style

### Type Hints (Required)
```python
def create_person(self, name: str, user_id: str) -> Person:
    # Return type and parameters are explicit
    pass
```

### Error Handling
```python
try:
    person = service.create_person(name, details, user_id)
    return APIResponse.created(person.to_dict())
except ValidationError as e:
    return APIResponse.validation_error(str(e))
except Exception as e:
    logger.error(f"Error: {e}")
    return APIResponse.server_error(str(e))
```

### Logging
```python
from utils.logger import get_logger
logger = get_logger(__name__)

logger.info("Person created")
logger.warning("Unauthorized access attempt")
logger.error("Database connection failed")
```

---

## 🧪 Testing

### Quick Test (Manual)
```bash
# Start server
python app.py

# Test endpoint
curl http://localhost:5000/api/people \
  -H "Cookie: session=..." \
  -H "Content-Type: application/json"
```

### Unit Test Structure
```python
def test_create_person_service():
    # Arrange: Set up test data
    mock_repo = MagicMock()
    service = PersonService(mock_repo)
    
    # Act: Call the method
    person = service.create_person("John", "Details", "user123")
    
    # Assert: Verify results
    assert person.name == "John"
    mock_repo.create.assert_called_once()
```

---

## 🐛 Common Issues

### Issue: "KeyError: 'user_id'"
**Cause**: User not logged in, but accessing protected route  
**Fix**: Ensure `@login_required` decorator is present

### Issue: "Person not found"
**Cause**: Trying to access someone else's person (authorization check)  
**Fix**: Verify `user_id` matches in service layer

### Issue: "ValidationError: Name is required"
**Cause**: Frontend sending empty name  
**Fix**: Add client-side validation or fix API call

---

## 🎓 Learning Path

### Day 1: Understand Flow
- Read this file
- Trace one request end-to-end (use browser DevTools)
- Add a `print()` statement in each layer to see flow

### Day 2: Make Small Change
- Add a new field to Person (e.g., "email")
- Update model, repository serialization
- Test it works

### Day 3: Add New Feature
- Implement "Mark as Favorite" toggle
- Follow the layer pattern: Model → Repo → Service → Route → Frontend

### Day 4: Study Patterns
- Read `CODE_FLOW_GUIDE.md` completely
- Understand why each pattern is used
- Compare to alternative approaches

---

## 💡 Pro Tips

1. **Always start at the route** when debugging - that's where requests enter
2. **Use type hints** - they catch bugs before runtime
3. **Log liberally** - `logger.info()` is your friend
4. **Test in layers** - Unit test services, integration test routes
5. **Think in terms of responsibilities** - "Does this belong in service or route?"

---

## 🔗 Quick Links

- **Live App**: https://people-manager-kebr.onrender.com/
- **GitHub**: https://github.com/fragenabhishek/People-Manager
- **Flask Docs**: https://flask.palletsprojects.com/
- **MongoDB Docs**: https://www.mongodb.com/docs/

---

## ❓ FAQ

**Q: Why so many layers? Isn't this over-engineered?**  
A: Each layer has a purpose:
- Routes: HTTP → Python conversion
- Services: Business logic
- Repositories: Database abstraction
This makes testing, scaling, and maintenance much easier.

**Q: Can I access the repository directly from routes?**  
A: Technically yes, but don't! Services contain business logic (validation, authorization) that you'd bypass.

**Q: Where do I add AI features?**  
A: Add to `services/ai_service.py`, expose via `routes/ai_routes.py`.

**Q: How do I add real-time features?**  
A: Current: REST API. Future: WebSockets (Flask-SocketIO) for live updates.

---

**Ready to code?** Start by reading one file at a time, tracing a request, then make a small change! 🚀

**Questions?** Check `CODE_FLOW_GUIDE.md` for detailed explanations or ask the team!

