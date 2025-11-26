# 📚 Code Flow Guide - People Manager

> **Purpose**: Complete guide for developers to understand the application architecture, request flow, and code organization.

---

## 🎯 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Request Flow](#request-flow)
3. [Layer-by-Layer Breakdown](#layer-by-layer-breakdown)
4. [Complete Flow Examples](#complete-flow-examples)
5. [Key Design Patterns](#key-design-patterns)
6. [File Structure](#file-structure)
7. [Adding New Features](#adding-new-features)

---

## 🏗️ Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Browser (Client)                        │
│                   HTML + CSS + JavaScript                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP Requests (JSON)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     Flask Application                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ app.py - Application Factory & Entry Point          │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼─────────────────────────────┐  │
│  │         Routes Layer (HTTP Handlers)                 │  │
│  │  • auth_routes.py   - Login/Register/Logout          │  │
│  │  • person_routes.py - CRUD operations                │  │
│  │  • ai_routes.py     - AI features                    │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼─────────────────────────────┐  │
│  │        Middleware (Cross-Cutting Concerns)           │  │
│  │  • auth_middleware.py - @login_required decorator    │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼─────────────────────────────┐  │
│  │       Services Layer (Business Logic)                │  │
│  │  • auth_service.py   - User authentication           │  │
│  │  • person_service.py - Person management             │  │
│  │  • ai_service.py     - AI operations                 │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼─────────────────────────────┐  │
│  │    Repositories Layer (Data Access)                  │  │
│  │  • user_repository.py   - User data                  │  │
│  │  • person_repository.py - Person data                │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼─────────────────────────────┐  │
│  │           Models (Domain Entities)                   │  │
│  │  • user.py   - User dataclass                        │  │
│  │  • person.py - Person dataclass                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Utils (Helpers & Utilities)                  │  │
│  │  • validators.py - Input validation                  │  │
│  │  • response.py   - API responses                     │  │
│  │  • logger.py     - Logging                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Config (Settings)                         │  │
│  │  • config.py - Centralized configuration             │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Storage                               │
│          MongoDB (Cloud) OR JSON Files (Local)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow

### Example: Adding a New Person

Let's trace a complete request from browser to database and back:

```
1. USER ACTION (Browser)
   │
   ├─► User fills form: Name = "John Doe", Details = "Met at conference"
   ├─► Clicks "Save Person" button
   └─► JavaScript captures form submit event
       │
       └─► script.js:handleSubmit()
           │
           └─► fetch('/api/people', { method: 'POST', body: JSON })
               │
               ▼

2. NETWORK
   │
   └─► HTTP POST /api/people
       Headers: Content-Type: application/json
       Body: {"name": "John Doe", "details": "Met at conference"}
       │
       ▼

3. FLASK ROUTING (app.py)
   │
   ├─► Flask receives request at /api/people
   ├─► Matches route: person_bp.route('', methods=['POST'])
   └─► Calls: person_routes.add_person()
       │
       ▼

4. MIDDLEWARE (middleware/auth_middleware.py)
   │
   ├─► @login_required decorator executes
   ├─► Checks: session.get('logged_in')
   ├─► If True: Continue to route handler
   └─► If False: Redirect to /login
       │
       ▼

5. ROUTE HANDLER (routes/person_routes.py)
   │
   └─► add_person() function
       │
       ├─► Extract user_id from session
       ├─► Parse JSON body: request.get_json()
       ├─► Extract: name, details
       │
       └─► Call: person_service.create_person(name, details, user_id)
           │
           ▼

6. VALIDATION (utils/validators.py)
   │
   └─► Validator.validate_person_data(name, details)
       │
       ├─► Check: name is not empty
       ├─► Check: name meets length requirements
       ├─► Raise ValidationError if invalid
       └─► Return: Valid ✓
           │
           ▼

7. SERVICE LAYER (services/person_service.py)
   │
   └─► PersonService.create_person()
       │
       ├─► Create Person object from data
       ├─► Set user_id for ownership
       ├─► Generate timestamps
       │
       └─► Call: person_repository.create(person)
           │
           ▼

8. REPOSITORY LAYER (repositories/person_repository.py)
   │
   └─► PersonRepository.create()
       │
       ├─► Check: USE_MONGODB?
       ├─► If MongoDB: _create_mongodb()
       │   ├─► people_collection.insert_one(person.to_dict())
       │   └─► Return created person with ID
       │
       └─► If JSON: _create_json()
           ├─► Read existing data from data.json
           ├─► Append new person
           ├─► Write back to data.json
           └─► Return created person
               │
               ▼

9. RESPONSE BUILDING (routes/person_routes.py)
   │
   └─► APIResponse.created(person.to_dict())
       │
       ├─► Convert Person object to dict
       ├─► Build JSON response: {"id": "...", "name": "...", ...}
       ├─► Set status code: 201 Created
       └─► Return response
           │
           ▼

10. NETWORK
    │
    └─► HTTP Response
        Status: 201 Created
        Body: {"id": "1234", "name": "John Doe", ...}
        │
        ▼

11. BROWSER (script.js)
    │
    └─► fetch() promise resolves
        │
        ├─► if (response.ok): Success!
        ├─► showSuccess("John Doe added successfully!")
        ├─► closeModal()
        └─► loadPeople() - Refresh the list
```

---

## 📦 Layer-by-Layer Breakdown

### Layer 1: Configuration (`config/config.py`)

**Purpose**: Centralize all application settings in one place.

```python
class Config:
    # Environment variables loaded once at startup
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    MONGO_URI = os.environ.get('MONGO_URI')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Derived settings
    USE_MONGODB = MONGO_URI is not None
    AI_ENABLED = GEMINI_API_KEY is not None
```

**Key Concepts**:
- Single source of truth for all settings
- Environment variable support for 12-factor app compliance
- Validation method to check configuration at startup

---

### Layer 2: Models (`models/`)

**Purpose**: Define domain entities (data structures).

```python
@dataclass
class Person:
    name: str
    user_id: str
    id: Optional[str] = None
    details: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict"""
        return {...}
    
    @staticmethod
    def from_dict(data: dict) -> 'Person':
        """Deserialize from dict"""
        return Person(...)
```

**Key Concepts**:
- Use Python `dataclass` for clean data objects
- Type hints for better IDE support
- Serialization/deserialization methods
- No business logic (just data)

---

### Layer 3: Repositories (`repositories/`)

**Purpose**: Abstract data access. Hide whether we're using MongoDB or JSON files.

```python
class PersonRepository(BaseRepository[Person]):
    def __init__(self, people_collection=None, data_file=None):
        self.use_mongodb = Config.USE_MONGODB
        self.people_collection = people_collection
        self.data_file = data_file
    
    def find_all(self, filters: Optional[dict] = None) -> List[Person]:
        """Get all people with optional filters"""
        if self.use_mongodb:
            return self._find_all_mongodb(filters)
        return self._find_all_json(filters)
    
    def _find_all_mongodb(self, filters) -> List[Person]:
        """MongoDB implementation"""
        people_data = list(self.people_collection.find(filters or {}))
        return [Person.from_dict(data) for data in people_data]
    
    def _find_all_json(self, filters) -> List[Person]:
        """JSON file implementation"""
        with open(self.data_file, 'r') as f:
            all_data = json.load(f)
        # Apply filters...
        return [Person.from_dict(data) for data in filtered_data]
```

**Key Concepts**:
- **Repository Pattern**: Single interface for data access
- **Dual Implementation**: MongoDB for production, JSON for local dev
- **Dependency Inversion**: Services depend on repository interface, not implementation
- Methods: `find_all()`, `find_by_id()`, `create()`, `update()`, `delete()`

---

### Layer 4: Services (`services/`)

**Purpose**: Encapsulate business logic. Orchestrate between repositories and add rules.

```python
class PersonService:
    def __init__(self, person_repository: PersonRepository):
        self.person_repository = person_repository
    
    def create_person(self, name: str, details: str, user_id: str) -> Person:
        """Create a new person with business rules"""
        
        # 1. Validate input
        Validator.validate_person_data(name, details)
        
        # 2. Apply business logic
        person = Person(
            name=name.strip(),
            details=details.strip(),
            user_id=user_id  # Set ownership
        )
        
        # 3. Persist to database
        created_person = self.person_repository.create(person)
        
        # 4. Log activity
        logger.info(f"Person created: {created_person.name}")
        
        return created_person
    
    def get_person_by_id(self, person_id: str, user_id: str) -> Optional[Person]:
        """Get person with authorization check"""
        person = self.person_repository.find_by_id(person_id)
        
        # Business rule: Users can only access their own data
        if person and person.user_id != user_id:
            logger.warning(f"Unauthorized access attempt")
            return None
        
        return person
```

**Key Concepts**:
- **Business Logic**: Validation, authorization, data transformation
- **Single Responsibility**: Each service handles one domain
- **Dependency Injection**: Services receive repositories via constructor
- **Pure Functions**: Testable, no hidden dependencies

---

### Layer 5: Routes (`routes/`)

**Purpose**: HTTP request/response handling. Parse input, call services, return JSON.

```python
person_bp = Blueprint('person_routes', __name__, url_prefix='/api/people')

@person_bp.route('', methods=['POST'])
@login_required
def add_person():
    """Add a new person endpoint"""
    try:
        # 1. Get user from session
        user_id = session.get('user_id')
        
        # 2. Parse JSON request body
        data = request.get_json()
        name = data.get('name', '').strip()
        details = data.get('details', '').strip()
        
        # 3. Call service (business logic)
        person = person_service.create_person(name, details, user_id)
        
        # 4. Return JSON response
        return APIResponse.created(person.to_dict(), "Person created")
    
    except ValidationError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error creating person: {e}")
        return APIResponse.server_error(str(e))
```

**Key Concepts**:
- **Blueprints**: Modular route organization
- **Decorators**: `@login_required` for authentication
- **Error Handling**: Try-except blocks with proper HTTP status codes
- **Thin Layer**: Minimal logic, delegates to services

---

### Layer 6: Middleware (`middleware/`)

**Purpose**: Cross-cutting concerns that apply to multiple routes.

```python
def login_required(f):
    """Decorator to protect routes requiring authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth_routes.login'))
        return f(*args, **kwargs)
    return decorated_function

# Usage:
@app.route('/protected')
@login_required
def protected_route():
    return "You must be logged in to see this"
```

**Key Concepts**:
- **Decorators**: Wrap functions to add functionality
- **Session Management**: Check authentication state
- **Reusability**: Apply to any route with `@login_required`

---

### Layer 7: Utils (`utils/`)

**Purpose**: Reusable helper functions used across the application.

```python
# validators.py
class Validator:
    @staticmethod
    def validate_person_data(name: str, details: Optional[str]) -> None:
        if not name or not name.strip():
            raise ValidationError("Name is required")
        if len(name.strip()) < 2:
            raise ValidationError("Name must be at least 2 characters")

# response.py
class APIResponse:
    @staticmethod
    def created(data: dict, message: str = "Created"):
        return jsonify({'data': data, 'message': message}), 201
    
    @staticmethod
    def validation_error(message: str):
        return jsonify({'error': message}), 400

# logger.py
def get_logger(name: str):
    logger = logging.getLogger(name)
    # Configure logger...
    return logger
```

---

## 🔍 Complete Flow Examples

### Example 1: User Login Flow

```
1. User opens browser → GET /login
   ├─► routes/auth_routes.py:login() [GET]
   └─► render_template('login.html')

2. User submits form → POST /login
   ├─► routes/auth_routes.py:login() [POST]
   ├─► Validate: Validator.validate_login_data()
   ├─► Service: auth_service.authenticate_user(username, password)
   │   ├─► Repository: user_repo.find_by_username(username)
   │   ├─► Check: bcrypt.check_password_hash(hash, password)
   │   └─► Return: User object or None
   ├─► If valid:
   │   ├─► session['logged_in'] = True
   │   ├─► session['user_id'] = user.id
   │   └─► redirect('/')
   └─► If invalid:
       └─► render_template('login.html', error='Invalid credentials')
```

### Example 2: Search People Flow

```
1. User types in search box → 'input' event
   ├─► script.js:handleSearch(e)
   ├─► query = e.target.value
   └─► fetch(`/api/people/search/${query}`)

2. Backend processes search
   ├─► routes/person_routes.py:search_people(query)
   ├─► @login_required checks authentication
   ├─► user_id = session.get('user_id')
   ├─► Service: person_service.search_people(query, user_id)
   │   └─► Repository: person_repo.search_by_name(query, user_id)
   │       ├─► Get all people for user
   │       ├─► Filter: query_lower in person.name.lower()
   │       └─► Return: List[Person]
   └─► Return: JSON array of matching people

3. Frontend updates UI
   ├─► script.js:renderPeople(results)
   ├─► Update DOM with matching cards
   └─► Show "No results" if empty
```

### Example 3: AI Blueprint Generation Flow

```
1. User clicks AI button → onclick="generateAISummary(id)"
   ├─► script.js:generateAISummary(id)
   ├─► Show loading spinner
   └─► fetch(`/api/people/${id}/summary`, {method: 'POST'})

2. Backend generates AI summary
   ├─► routes/ai_routes.py:generate_summary(person_id)
   ├─► @login_required checks auth
   ├─► Service: ai_service.generate_person_blueprint(person_id, user_id)
   │   ├─► Repository: person_repo.find_by_id(person_id)
   │   ├─► Build prompt with person's details
   │   ├─► Call: gemini_model.generate_content(prompt)
   │   └─► Return: AI-generated text
   └─► Return: JSON {summary: "...", generated_at: "..."}

3. Frontend displays result
   ├─► script.js: Show summary in collapsible section
   ├─► Format markdown-like text
   └─► Show success toast
```

---

## 🎨 Key Design Patterns

### 1. **Repository Pattern**
- **What**: Abstracts data access behind an interface
- **Why**: Easy to swap MongoDB ↔ JSON, easy to mock for testing
- **Where**: `repositories/person_repository.py`

### 2. **Service Layer Pattern**
- **What**: Business logic separated from HTTP handling
- **Why**: Reusable, testable, single responsibility
- **Where**: `services/person_service.py`

### 3. **Dependency Injection**
- **What**: Pass dependencies via constructor instead of creating them inside
- **Why**: Loose coupling, easier testing, flexible
- **Where**: `app.py:create_app()` injects services into routes

```python
# Bad (tight coupling):
class PersonService:
    def __init__(self):
        self.repo = PersonRepository()  # Hard-coded dependency

# Good (dependency injection):
class PersonService:
    def __init__(self, person_repository: PersonRepository):
        self.repo = person_repository  # Injected dependency
```

### 4. **Factory Pattern**
- **What**: Function that creates and configures objects
- **Why**: Centralize app creation, easier testing
- **Where**: `app.py:create_app()`

### 5. **Decorator Pattern**
- **What**: Wrap functions to add behavior
- **Why**: Reusable cross-cutting concerns (auth, logging)
- **Where**: `middleware/auth_middleware.py:@login_required`

---

## 📁 File Structure

```
People-Manager/
│
├── app.py                    # Application factory & entry point
│   └─► create_app()          # Initializes all dependencies
│   └─► initialize_repositories()
│   └─► register_main_routes()
│
├── config/
│   └── config.py             # Centralized configuration
│       └─► class Config      # All environment variables
│
├── models/
│   ├── person.py             # Person domain entity
│   │   └─► @dataclass Person
│   │   └─► to_dict(), from_dict()
│   └── user.py               # User domain entity
│       └─► @dataclass User
│
├── repositories/
│   ├── base_repository.py    # Abstract base for all repos
│   ├── person_repository.py  # Person data access
│   │   └─► find_all(), find_by_id(), create(), update(), delete()
│   │   └─► _find_all_mongodb(), _find_all_json()
│   └── user_repository.py    # User data access
│       └─► find_by_username()
│
├── services/
│   ├── auth_service.py       # Authentication business logic
│   │   └─► register_user(), authenticate_user()
│   ├── person_service.py     # Person business logic
│   │   └─► get_all_people(), create_person(), update_person()
│   │   └─► Authorization checks (user_id ownership)
│   └── ai_service.py         # AI features business logic
│       └─► generate_person_blueprint(), ask_about_contacts()
│
├── routes/
│   ├── auth_routes.py        # Authentication endpoints
│   │   └─► /login, /register, /logout
│   ├── person_routes.py      # Person CRUD endpoints
│   │   └─► /api/people [GET, POST]
│   │   └─► /api/people/<id> [GET, PUT, DELETE]
│   │   └─► /api/people/search/<query>
│   └── ai_routes.py          # AI feature endpoints
│       └─► /api/people/<id>/summary
│       └─► /api/ask
│
├── middleware/
│   └── auth_middleware.py    # Authentication decorator
│       └─► @login_required   # Protect routes
│
├── utils/
│   ├── validators.py         # Input validation
│   │   └─► Validator.validate_person_data()
│   │   └─► Raises ValidationError
│   ├── response.py           # Standardized API responses
│   │   └─► APIResponse.created(), .validation_error()
│   └── logger.py             # Logging configuration
│       └─► get_logger()
│
├── templates/
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   └── index.html            # Main application UI
│
├── static/
│   ├── style.css             # Styles
│   └── script.js             # Frontend logic
│       └─► loadPeople(), renderPeople()
│       └─► handleSubmit(), deletePerson()
│       └─► generateAISummary(), askCentralQuestion()
│
├── data.json                 # Local data storage (if not MongoDB)
├── users.json                # Local user storage (if not MongoDB)
└── requirements.txt          # Python dependencies
```

---

## 🚀 Adding New Features

### How to Add a New Entity (e.g., "Tasks")

#### Step 1: Create Model
```python
# models/task.py
@dataclass
class Task:
    title: str
    user_id: str
    id: Optional[str] = None
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {...}
    
    @staticmethod
    def from_dict(data: dict) -> 'Task':
        return Task(...)
```

#### Step 2: Create Repository
```python
# repositories/task_repository.py
class TaskRepository(BaseRepository[Task]):
    def __init__(self, task_collection=None, data_file='tasks.json'):
        # Similar to PersonRepository
        pass
    
    def find_all(self, filters=None) -> List[Task]:
        # Implementation...
        pass
```

#### Step 3: Create Service
```python
# services/task_service.py
class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
    
    def create_task(self, title: str, user_id: str) -> Task:
        # Validation
        # Business logic
        # Repository call
        return created_task
```

#### Step 4: Create Routes
```python
# routes/task_routes.py
task_bp = Blueprint('task_routes', __name__, url_prefix='/api/tasks')

@task_bp.route('', methods=['GET'])
@login_required
def get_tasks():
    user_id = session.get('user_id')
    tasks = task_service.get_all_tasks(user_id)
    return jsonify([t.to_dict() for t in tasks])
```

#### Step 5: Register in app.py
```python
# app.py
from repositories.task_repository import TaskRepository
from services.task_service import TaskService
from routes.task_routes import task_bp, init_task_routes

def create_app():
    # ... existing code ...
    
    # Initialize task repository
    task_repo = TaskRepository(db['tasks'] if USE_MONGODB else None)
    
    # Initialize task service
    task_service = TaskService(task_repo)
    
    # Initialize routes
    init_task_routes(task_service)
    
    # Register blueprint
    app.register_blueprint(task_bp)
    
    return app
```

#### Step 6: Add Frontend
```javascript
// static/script.js
async function loadTasks() {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    renderTasks(tasks);
}
```

---

## 🔐 Security Considerations

### 1. **Authentication Check**
- Every protected route uses `@login_required`
- Session-based authentication with server-side storage

### 2. **Authorization Check**
- Services verify `user_id` ownership before operations
- Example: `person.user_id != user_id` → Access denied

### 3. **Input Validation**
- All user input validated in services layer
- Prevents SQL injection (MongoDB parameterized queries)
- Prevents XSS (frontend escapes HTML)

### 4. **Password Security**
- Passwords hashed with bcrypt
- Never store plaintext passwords
- Salt automatically generated per password

---

## 📊 Data Flow Summary

### CREATE Operation
```
Browser → Routes → Validation → Service → Repository → Database
        ←         ←             ←         ←            ←
```

### READ Operation
```
Browser → Routes → Service → Repository → Database
        ←         ←         ←            ←
```

### UPDATE Operation
```
Browser → Routes → Validation → Service → Repository → Database
        ←         ←             ←         ←            ←
        (Check ownership in service layer)
```

### DELETE Operation
```
Browser → Confirmation → Routes → Service → Repository → Database
        ←               ←         ←         ←            ←
        (Check ownership in service layer)
```

---

## 🧪 Testing Strategy

### Unit Tests
- **Models**: Test serialization/deserialization
- **Validators**: Test validation rules
- **Services**: Mock repositories, test business logic

### Integration Tests
- **Repositories**: Test with test database
- **Routes**: Test HTTP endpoints with test client

### Example Test
```python
def test_create_person():
    # Arrange
    mock_repo = MagicMock()
    service = PersonService(mock_repo)
    
    # Act
    person = service.create_person("John Doe", "Details", "user123")
    
    # Assert
    mock_repo.create.assert_called_once()
    assert person.name == "John Doe"
    assert person.user_id == "user123"
```

---

## 📚 Further Reading

- **SOLID Principles**: See `SOLID_COMPLIANCE_REPORT.md`
- **Architecture Details**: See `ARCHITECTURE.md`
- **Refactoring History**: See `REFACTORING_SUMMARY.md`
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Repository Pattern**: https://martinfowler.com/eaaCatalog/repository.html

---

## 🎯 Quick Reference

### Common Tasks

**Add a new route:**
1. Add function to appropriate blueprint
2. Add `@login_required` if protected
3. Call service method
4. Return standardized response

**Add validation:**
1. Add method to `utils/validators.py`
2. Call from service layer
3. Raise `ValidationError` on failure

**Add configuration:**
1. Add to `config/config.py`
2. Access via `Config.SETTING_NAME`
3. Support environment variable

**Add logging:**
```python
from utils.logger import get_logger
logger = get_logger(__name__)
logger.info("Something happened")
```

---

**Questions?** Review the layer diagrams above or check the specific file mentioned!

