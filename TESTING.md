# Testing Guide

## Running Tests

### Install Test Dependencies
```bash
uv sync --group dev
```

### Run All Tests
```bash
uv run pytest
```

### Run Specific Test Files
```bash
# API tests
uv run pytest tests/test_api.py -v

# Data service tests
uv run pytest tests/test_data_service.py -v

# Pydantic model tests
uv run pytest tests/test_models.py -v

# Crew runner tests (existing)
uv run pytest tests/test_crew_runner.py -v
```

### Run with Coverage
```bash
uv run pytest --cov=contentagency --cov-report=html
```

## Test Structure

### 1. API Endpoint Tests (`test_api.py`)

Tests all FastAPI endpoints with mocked dependencies:

**Test Classes:**
- `TestHealthEndpoint` - Health check functionality
- `TestUpdateInterests` - Interest update validation
- `TestUpdatePosts` - Post update validation
- `TestRunBrainstorm` - Brainstorm crew execution
- `TestGetResults` - Results retrieval

**Example:**
```python
def test_brainstorm_success(client, mock_data_service, mock_crew_runner):
    """Should run brainstorm successfully."""
    mock_data_service.get_user_interests.return_value = {...}
    response = client.post("/api/v1/brainstorm", json={"user_id": "test"})
    assert response.status_code == 200
```

### 2. Data Service Tests (`test_data_service.py`)

Tests file-based data operations with temporary directories:

**Test Classes:**
- `TestFileDataService` - Core data operations
- `TestCreateDataService` - Factory pattern

**Example:**
```python
def test_save_and_get_user_interests(data_service):
    """Should save and retrieve user interests."""
    data_service.save_user_interests(interests_data)
    result = data_service.get_user_interests()
    assert result["interests"][0]["topic"] == "AI"
```

### 3. Pydantic Model Tests (`test_models.py`)

Tests request/response validation:

**Test Classes:**
- `TestInterestItem` - Interest validation rules
- `TestUserInterestsRequest` - Request validation
- `TestPostItem` - Post validation
- `TestBrainstormRequest` - Brainstorm request
- Response model tests

**Example:**
```python
def test_empty_topic_rejected():
    """Should reject empty topic."""
    with pytest.raises(ValidationError):
        InterestItem(topic="")
```

### 4. Crew Runner Tests (`test_crew_runner.py`)

Tests crew execution logic and edge cases:

**Test Classes:**
- `TestFormatInterestsForPrompt` - Interest formatting
- `TestFormatPostsForPrompt` - Post formatting
- `TestRunBrainstormCrew` - Crew execution

## Test Coverage

### Current Coverage:
- ✅ API endpoints (all routes)
- ✅ Data service (file operations)
- ✅ Pydantic models (validation rules)
- ✅ Crew runner (business logic)
- ✅ Edge cases (empty data, errors)

### Not Covered (Expected):
- ❌ Web UI (templates, JavaScript)
- ❌ CLI commands (main.py functions)
- ❌ Database service (placeholder)
- ❌ Integration tests (end-to-end)

## Fixtures

### Common Fixtures

```python
@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def temp_data_dir():
    """Temporary data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def mock_data_service():
    """Mocked data service."""
    with patch('contentagency.api.main.data_service') as mock:
        yield mock
```

## Testing Best Practices

### 1. Use Mocks for External Dependencies
```python
@patch('contentagency.api.main.run_brainstorm_crew')
def test_endpoint(mock_crew_runner):
    mock_crew_runner.return_value = "result"
    # Test without running actual crew
```

### 2. Test Edge Cases
```python
def test_empty_interests_rejected():
    """Should reject empty interests."""
    with pytest.raises(ValidationError):
        UserInterestsRequest(user_id="test", interests=[])
```

### 3. Use Temporary Directories
```python
def test_file_operations(temp_data_dir):
    """Should save to temp directory."""
    service = FileDataService(data_dir=temp_data_dir)
    # No side effects on real data
```

### 4. Test Both Success and Failure
```python
def test_success_case():
    assert response.status_code == 200

def test_validation_error():
    assert response.status_code == 422
```

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --group dev
      - name: Run tests
        run: uv run pytest --cov
```

## Debugging Tests

### Run Specific Test
```bash
uv run pytest tests/test_api.py::TestHealthEndpoint::test_health_check -v
```

### Show Print Statements
```bash
uv run pytest -s
```

### Stop on First Failure
```bash
uv run pytest -x
```

### Verbose Output
```bash
uv run pytest -vv
```

## Manual Testing

### Test API Manually
```bash
# Start API
uv run api

# In another terminal
python test_api.py
```

### Test with cURL
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/brainstorm \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'
```

### Test with Postman
Import `postman_collection.json` for pre-configured requests.

## Test Data

### Sample Interests
```json
{
  "user_id": "test_user",
  "interests": [
    {"topic": "Artificial Intelligence"},
    {"topic": "Machine Learning"}
  ]
}
```

### Sample Posts
```json
{
  "user_id": "test_user",
  "posts": [
    {
      "id": "post_1",
      "platform": "linkedin",
      "content": "Test content",
      "topics": ["AI"]
    }
  ]
}
```

## Adding New Tests

### 1. Create Test File
```python
# tests/test_new_feature.py
import pytest

def test_new_feature():
    """Test description."""
    assert True
```

### 2. Run New Tests
```bash
uv run pytest tests/test_new_feature.py
```

### 3. Add to CI Pipeline
Tests run automatically on git push with CI setup.

## Troubleshooting

### Import Errors
```bash
# Ensure project is installed
uv sync
```

### Fixture Not Found
```bash
# Check fixture is defined in conftest.py or test file
```

### Mock Not Working
```python
# Use correct import path
@patch('contentagency.api.main.data_service')  # ✅
@patch('data_service')  # ❌
```

## Next Steps

1. **Add Integration Tests** - Test full workflows end-to-end
2. **Add Performance Tests** - Test response times
3. **Add Load Tests** - Test concurrent requests
4. **Add Security Tests** - Test authentication, input validation
