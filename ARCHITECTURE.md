# Architecture Documentation

## Overview

This project follows **SOLID principles** and implements a **clean architecture** with clear separation of concerns.

## SOLID Principles Implementation

### 1. Single Responsibility Principle (SRP)
Each module has a single, well-defined responsibility:

- **Config**: Configuration management only
- **Models**: Entity definitions only
- **Repositories**: Data access only
- **Services**: Business logic only
- **Routes**: HTTP handling only
- **Middleware**: Cross-cutting concerns (auth)
- **Utils**: Shared utilities (validation, logging, response formatting)

### 2. Open/Closed Principle (OCP)
- Base repository can be extended without modification
- New storage backends can be added by implementing `BaseRepository`
- New services can be added without changing existing code

### 3. Liskov Substitution Principle (LSP)
- `PersonRepository` and `UserRepository` can be substituted with any implementation of `BaseRepository`
- MongoDB and JSON implementations are interchangeable

### 4. Interface Segregation Principle (ISP)
- Services depend only on methods they use
- Thin, focused interfaces (e.g., `BaseRepository`)

### 5. Dependency Inversion Principle (DIP)
- High-level modules (services) depend on abstractions (base repository)
- Low-level modules (repositories) implement abstractions
- Dependencies are injected, not hard-coded

## Architecture Layers

```
┌─────────────────────────────────────┐
│          Presentation Layer          │
│         (Routes/Templates)          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│        Business Logic Layer          │
│            (Services)                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│        Data Access Layer             │
│         (Repositories)               │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│         Data Storage                 │
│      (MongoDB / JSON Files)          │
└─────────────────────────────────────┘
```

## Project Structure

```
People-Manager/
├── app.py                      # Application entry point (minimal)
├── config/
│   └── config.py              # Centralized configuration
├── models/
│   ├── person.py              # Person entity
│   └── user.py                # User entity
├── repositories/
│   ├── base_repository.py     # Abstract base repository
│   ├── person_repository.py   # Person data access
│   └── user_repository.py     # User data access
├── services/
│   ├── auth_service.py        # Authentication logic
│   ├── person_service.py      # Person management logic
│   └── ai_service.py          # AI integration logic
├── routes/
│   ├── auth_routes.py         # Authentication endpoints
│   ├── person_routes.py       # Person CRUD endpoints
│   └── ai_routes.py           # AI feature endpoints
├── middleware/
│   └── auth_middleware.py     # Auth decorators
├── utils/
│   ├── logger.py              # Logging utility
│   ├── validators.py          # Input validation
│   └── response.py            # API response formatting
├── templates/                  # HTML templates
└── static/                     # CSS, JS, images
```

## Design Patterns

### 1. Repository Pattern
Abstracts data access logic, making it easy to switch between storage backends.

```python
# Abstract interface
class BaseRepository(ABC):
    @abstractmethod
    def find_all(self, filters): pass
    
    @abstractmethod
    def create(self, entity): pass
    # ... more methods

# Concrete implementations
class PersonRepository(BaseRepository):
    # MongoDB or JSON implementation
```

### 2. Service Layer Pattern
Encapsulates business logic, keeping controllers thin.

```python
class PersonService:
    def __init__(self, person_repository):
        self.person_repository = person_repository
    
    def create_person(self, name, details, user_id):
        # Validation
        # Business logic
        # Data access via repository
```

### 3. Dependency Injection
Services receive dependencies rather than creating them.

```python
# In app.py
person_repo = PersonRepository(...)
person_service = PersonService(person_repo)
init_person_routes(person_service)
```

### 4. Application Factory Pattern
Creates configured application instance.

```python
def create_app() -> Flask:
    app = Flask(__name__)
    # Configure and wire dependencies
    return app

app = create_app()
```

## Benefits

1. **Maintainability**: Each module has a clear purpose
2. **Testability**: Easy to mock dependencies
3. **Scalability**: Easy to add new features
4. **Flexibility**: Easy to swap implementations
5. **Code Quality**: Type hints, validation, logging throughout
6. **Error Handling**: Centralized error responses
7. **Security**: Proper validation and authorization checks

## Extension Points

### Adding a New Storage Backend
1. Implement `BaseRepository` interface
2. Update `initialize_repositories()` in `app.py`

### Adding a New Feature
1. Create model (if needed)
2. Create repository (if needed)
3. Create service with business logic
4. Create routes with HTTP handling
5. Wire dependencies in `app.py`

### Adding Validation Rules
1. Add method to `Validator` class in `utils/validators.py`
2. Use in service layer

## Best Practices

1. **Always validate input** in services before processing
2. **Use type hints** throughout the codebase
3. **Log important operations** (create, update, delete, errors)
4. **Handle errors gracefully** with proper HTTP status codes
5. **Keep routes thin** - delegate to services
6. **Keep services focused** - single responsibility
7. **Use dependency injection** - don't create dependencies internally
8. **Write documentation** for complex logic

