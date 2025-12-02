# WARP.md - Warp Agent Configuration

This file contains Warp-specific rules, patterns, and preferences for AI agents working on the chilo-sls project.

## Project Overview

**chilo-sls** is a serverless-first Lambda/API Gateway framework for Python that:
- Auto-routes from handler file structure (glob pattern `**/*.py`)
- Provides OpenAPI and decorator-based validation
- Maintains API parity with the Chilo framework for easy migration
- Supports multiple AWS event sources (API Gateway, SQS, SNS, S3, DynamoDB, etc.)

**Target Runtime:** AWS Lambda (Python 3.8-3.12)  
**Current Status:** Production-ready (9.99/10 Pylint score, 99% test coverage)

---

## Code Style and Conventions

### Python Standards
- **Python Version:** 3.12 (supports 3.8+)
- **Style Guide:** PEP 8 with project-specific `.pylintrc`
- **Line Length:** 140 characters (see `.pylintrc`)
- **Naming:**
  - Classes: `PascalCase` (e.g., `Router`, `ResolverCache`)
  - Functions/methods: `snake_case` (e.g., `get_endpoint`, `validate_request`)
  - Private attributes: `__double_underscore` (e.g., `self.__cache`, `self.__resolver`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `CACHE_ALL`, `CACHE_STATIC`)

### File Organization
```
chilo_sls/
├── apigateway/          # API Gateway router and handlers
│   ├── router.py        # Main Router class
│   ├── request.py       # Request wrapper
│   ├── response.py      # Response wrapper
│   ├── resolver/        # Route resolution logic
│   └── openapi/         # OpenAPI generation
├── common/              # Shared utilities
│   ├── validator.py     # Schema validation
│   ├── schema.py        # OpenAPI schema handling
│   └── logger/          # Logging utilities
├── <service>/           # AWS service-specific modules (sqs, sns, s3, etc.)
│   ├── event.py         # Event wrapper
│   ├── record.py        # Record wrapper
│   └── requirements.py  # Validation decorators
└── base/                # Base classes
```

---

## Development Workflow

### Testing
```bash
# Run all tests
pipenv run pytest --maxfail=20 --disable-warnings

# Run with coverage
pipenv run pytest --cov=chilo_sls --cov-report=term-missing

# Run specific test file
pipenv run pytest tests/chilo_sls/test_apigateway_router.py -v

# Run with verbose output
pipenv run pytest -vv --disable-warnings
```

### Code Quality
```bash
# Lint check (must maintain 9.99+ score)
pipenv run pylint chilo_sls --recursive=y

# Auto-format (PEP 8)
pipenv run autopep8 --in-place --recursive chilo_sls/

# Type checking (when type hints are added)
# mypy chilo_sls/
```

### Local Development
```bash
# Install in editable mode
pipenv install --dev
# or
pip install -e .

# Activate virtual environment
pipenv shell
```

---

## Common Patterns and Anti-Patterns

### ✅ DO

**Use Private Attributes for Internal State**
```python
class Router:
    def __init__(self, **kwargs):
        self.__resolver = Resolver(**kwargs)  # Private
        self.__cache = {}                      # Private
```

**Use Kwargs for Flexible Configuration**
```python
def __init__(self, **kwargs):
    self.__cors = kwargs.get('cors', True)  # Default values
    self.__timeout = kwargs.get('timeout', None)
```

**Use Properties for Computed Values**
```python
@property
def code(self):
    if isinstance(self.__body, dict) and self.__code == 200 and not self.__body:
        return 204  # No content
    return self.__code
```

**Use Context Managers for Proper Cleanup**
```python
with open(self.__schema, encoding='utf-8') as schema_file:
    return yaml.load(schema_file, Loader=yaml.FullLoader)
```

**Use Descriptive Exception Messages**
```python
raise ApiException(
    code=404,
    key_path=request.path,
    message='no route found; endpoint does not have required_route configured'
)
```

### ❌ DON'T

**Don't Use `print()` for Logging**
```python
# Bad
except Exception as error:
    print(error)  # Lost in production

# Good
import logging
logger = logging.getLogger(__name__)
logger.error("Failed to parse body", exc_info=True)
```

**Don't Import Unused Dependencies**
```python
# Bad - icecream was listed but never used
from icecream import ic

# Remove from setup.py if not used
```

**Don't Use Bare `except` Clauses**
```python
# Bad
try:
    risky_operation()
except:  # Too broad
    pass

# Good
try:
    risky_operation()
except ValueError as error:
    logger.error("Validation failed", exc_info=error)
```

**Don't Mutate Default Arguments**
```python
# Bad
def __init__(self, hooks=[]):  # Mutable default
    self.__hooks = hooks

# Good
def __init__(self, hooks=None):
    self.__hooks = hooks or []
```

---

## Architecture Patterns

### Router → Resolver → Endpoint Flow
```python
# 1. Router receives Lambda event
router = Router(base_path='v1', handlers='api/handlers')
result = router.route(event, context)

# 2. Resolver finds matching handler module
endpoint = resolver.get_endpoint(request)

# 3. Endpoint runs handler function
endpoint.run(request, response)
```

### Middleware Hooks (Execution Order)
```python
1. before_all(request, response, requirements)
2. when_auth_required(request, response, requirements)  # If auth required
3. validate_request(request, response)
4. handler(request, response)                          # Your handler
5. validate_response(response)
6. after_all(request, response, requirements)
```

### Dynamic Route Resolution
```
File structure → URL pattern:
api/handlers/
├── __init__.py              → /v1/
├── user/_user_id.py         → /v1/user/{user_id}
└── orders/_order_id/item.py → /v1/orders/{order_id}/item
```

### Validation Strategies
```python
# 1. OpenAPI validation (recommended for production)
router = Router(
    openapi='openapi.yml',
    openapi_validate_request=True,
    openapi_validate_response=True
)

# 2. Decorator-based validation (simple cases)
@requirements(
    required_body='v1-user-schema',
    required_query=['page', 'limit'],
    auth_required=True
)
def get(request, response):
    pass
```

---

## Performance Considerations

### Cold Start Optimization
- **Lazy load** heavy dependencies (boto3, pydantic)
- **Pre-warm** routes using `router.warmup()`
- **Cache** resolved endpoints (default: 128 LRU)
- **Minimize** handler module imports

### Runtime Optimization
- **Enable caching:** `cache_size=128` (default)
- **Choose cache mode:** `all|static-only|dynamic-only`
- **Use compression:** `response.compress = True` for large payloads
- **Validate selectively:** Only enable validation flags when needed

### Memory Management
- **Limit cache size:** Adjust `cache_size` based on handler count
- **Clear path params:** Use `request.clear_path_params()` when needed
- **Avoid deep copies:** Schema walker uses shallow copies where possible

---

## Testing Guidelines

### Test Structure
```
tests/
├── chilo_sls/               # Unit tests
│   ├── test_apigateway_*.py
│   ├── test_common_*.py
│   └── test_<service>_*.py
└── mocks/                   # Test fixtures
    ├── apigateway/
    │   ├── mock_event.py
    │   ├── mock_middleware.py
    │   └── openapi/         # Mock handlers
    └── <service>/
```

### Writing Tests
```python
# Use descriptive test names
def test_router_resolves_dynamic_route_with_path_params():
    pass

# Use fixtures for common setup
@pytest.fixture
def router():
    return Router(base_path='test', handlers='tests/mocks/apigateway/openapi')

# Test both success and failure paths
def test_validation_fails_with_invalid_body():
    response = router.route(invalid_event, {})
    assert response['statusCode'] == 400
    assert 'errors' in json.loads(response['body'])
```

### Coverage Requirements
- **Minimum:** 95% overall coverage
- **Target:** 99%+ (current status)
- **Exception:** Pragma comments for unreachable code
```python
if not section:  # pragma: no cover
    continue
```

---

## Deployment and Packaging

### Lambda Deployment
```python
# Minimal Lambda handler
from chilo_sls.apigateway.router import Router

router = Router(base_path='v1', handlers='handlers')

def handler(event, context):
    return router.route(event, context)
```

### Dependencies
**Production (Required):**
- `boto3` - AWS SDK
- `jsonschema` - Validation
- `pydantic` - Modern validation
- `pyyaml` - OpenAPI parsing
- `simplejson` - Decimal support
- `xmltodict` - XML content-type
- `jsonref` - OpenAPI $ref resolution
- `dynamodb_json` - DynamoDB serialization
- `jsonpickle` - Object serialization

**Development:**
- `pytest` - Testing
- `pytest-cov` - Coverage
- `pylint` - Linting
- `autopep8` - Formatting
- `moto` - AWS mocking

---

## Known Issues and Workarounds

### Issue: Print Statements in Production Code
**Location:** `chilo_sls/apigateway/request.py` (lines 115, 135)  
**Impact:** Silent failures, no CloudWatch logs  
**Fix:** See [QUICK_WINS.md](QUICK_WINS.md) Priority 2

### Issue: Unused Dependency
**Location:** `setup.py` line 25 (`icecream`)  
**Impact:** Larger deployment package, slower cold starts  
**Fix:** See [QUICK_WINS.md](QUICK_WINS.md) Priority 1

### Issue: No Cache Metrics
**Location:** `chilo_sls/apigateway/resolver/cache.py`  
**Impact:** No visibility into cache effectiveness  
**Fix:** See [QUICK_WINS.md](QUICK_WINS.md) Priority 3

---

## Migration Path from chilo-sls to Chilo

When ready to graduate from serverless to serverful:

**Keep (No Changes Required):**
- Handler signatures (`Request`, `Response`)
- Validation decorators (`@requirements`)
- Middleware hooks (`before_all`, `after_all`, etc.)
- Request/Response property names

**Change:**
- Import paths: `chilo_sls.*` → `chilo.*`
- Router initialization: Add server config
- Event source: Lambda event → WSGI/gRPC

---

## Resources and References

### Internal Documentation
- **[AGENTS.md](AGENTS.md)** - Usage guide for AI agents
- **[WARP_OPTIMIZATION_REPORT.md](WARP_OPTIMIZATION_REPORT.md)** - Optimization analysis
- **[QUICK_WINS.md](QUICK_WINS.md)** - Implementation guide
- **[CODEX.md](CODEX.md)** - Historical context

### External Links
- **Documentation:** https://syngenta.github.io/chilo-sls-docs/
- **Repository:** https://github.com/syngenta/chilo-sls
- **Issue Tracker:** https://github.com/syngenta/chilo-sls/issues
- **CI/CD:** https://circleci.com/gh/syngenta/chilo-sls

### Related Projects
- **chilo** - The parent serverful framework
- **acai-python** - Testing utilities for AWS services
- **daplug-*** - Data pipeline plugins

---

## Warp Agent Preferences

### When Writing Code
1. **Maintain 9.99+ Pylint score** - Don't introduce lint warnings
2. **Keep 99%+ test coverage** - Write tests for all new code
3. **Use existing patterns** - Follow conventions in similar modules
4. **Add docstrings** - For public methods (optional for private)
5. **Validate inputs** - Use ConfigValidator pattern for public APIs

### When Debugging
1. **Check tests first** - 416 tests likely cover the issue
2. **Run with verbose** - `pytest -vv` for detailed output
3. **Use mock fixtures** - Don't make real AWS calls in tests
4. **Check CloudWatch** - For production Lambda debugging
5. **Profile cold starts** - Use `time` command for imports

### When Optimizing
1. **Measure first** - Profile before optimizing
2. **Start with quick wins** - See QUICK_WINS.md
3. **Run benchmarks** - Before and after measurements
4. **Monitor cold starts** - Primary Lambda performance metric
5. **Check cache hit rate** - After adding cache metrics

### When Refactoring
1. **Run full test suite** - Before and after changes
2. **Check lint score** - Must remain 9.99+
3. **Update documentation** - Especially AGENTS.md
4. **Consider backwards compatibility** - This is a library
5. **Add migration notes** - If API changes

---

## Quick Command Reference

```bash
# Setup
pipenv install --dev
pipenv shell

# Development
pipenv run pytest --disable-warnings          # Run tests
pipenv run pylint chilo_sls --recursive=y     # Check quality
pipenv run pytest --cov=chilo_sls             # Check coverage

# Optimization Analysis
warp optimize                                  # Re-run Warp analysis
time python -c "from chilo_sls.apigateway.router import Router"  # Measure cold start

# Deployment
pip install -e .                              # Install locally
python setup.py sdist bdist_wheel            # Build distribution
```

---

**Last Updated:** Dec 2, 2025  
**Maintained By:** Warp AI Agents  
**Next Review:** After implementing Phase 1 optimizations
