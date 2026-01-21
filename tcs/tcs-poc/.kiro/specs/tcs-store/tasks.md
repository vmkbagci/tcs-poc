# Implementation Plan: TCS Store

## Overview

This implementation plan breaks down the TCS Store API into discrete coding tasks. The approach is incremental: we'll build the core storage and service layers first, then add API endpoints, and finally implement comprehensive testing. Each task builds on previous work, with checkpoints to ensure quality.

**Important**: Every API call must include context metadata (user, agent, action, intent) for lifecycle tracing and audit purposes.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python package structure with `src/tcs_store/` directory
  - Configure Poetry with dependencies: FastAPI, Uvicorn, Pydantic, Hypothesis, pytest
  - Set up basic FastAPI application in `src/tcs_store/main.py`
  - Create `__init__.py` files for package structure
  - _Requirements: 12.1_

- [ ] 2. Implement in-memory storage layer
  - [x] 2.1 Create `InMemoryStore` class in `src/tcs_store/storage/in_memory_store.py`
    - Implement thread-safe dictionary storage with `threading.RLock`
    - Implement methods: `save()`, `get()`, `exists()`, `delete()`, `get_all()`, `clear()`
    - Add operation log storage for lifecycle tracing (list of operations with timestamp and context)
    - Implement `get_operation_log()` method to retrieve operation history
    - _Requirements: 12.1, 12.3, 15.3_
  
  - [x] 2.2 Write property test for thread-safe concurrent access
    - **Property 19: Thread-Safe Operations**
    - **Validates: Requirements 12.3**
    - Test concurrent save/load/delete operations
    - _Requirements: 12.3_

- [ ] 3. Implement data models
  - [x] 3.1 Create Pydantic models in `src/tcs_store/models/`
    - Create `Context` model with user, agent, action, intent fields (all required, non-empty strings)
    - Create `TradeFilter` model with flexible filter structure
    - Create request/response models with context: `SaveNewRequest`, `SaveUpdateRequest`, `PartialUpdateRequest`, `LoadGroupRequest`, `LoadFilterRequest`, `ListRequest`, `CountRequest`, `DeleteGroupRequest`
    - Create response models: `LoadGroupResponse`, `DeleteGroupResponse`, `CountResponse`, `ErrorResponse`, `HealthResponse`
    - _Requirements: 11.1, 11.4, 15.5_
  
  - [x] 3.2 Write unit tests for model validation
    - Test model serialization/deserialization
    - Test validation error handling
    - Test context validation (missing fields, empty fields, invalid types)
    - _Requirements: 11.1, 11.2, 15.2_
  
  - [x] 3.3 Write property test for context metadata required
    - **Property 20: Context Metadata Required**
    - **Validates: Requirements 15.1, 15.2**
    - Test that requests without context are rejected
    - _Requirements: 15.1, 15.2_

- [ ] 4. Implement service layer core operations
  - [x] 4.1 Create `TradeService` class in `src/tcs_store/services/trade_service.py`
    - Implement `_validate_context()` helper method
    - Implement `save_new()` method with duplicate detection (accepts context parameter)
    - Implement `save_update()` method with existence check (accepts context parameter)
    - Implement `load_by_id()` method (accepts context parameter)
    - Implement `delete_by_id()` method with idempotency (accepts context parameter)
    - Pass context to storage layer for all mutating operations
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 4.1, 4.2, 9.1, 9.2, 15.1, 15.3_
  
  - [x] 4.2 Write property test for save-load round trip
    - **Property 1: Save-Load Round Trip**
    - **Validates: Requirements 1.1, 4.1**
    - _Requirements: 1.1, 4.1_
  
  - [x] 4.3 Write property test for duplicate prevention
    - **Property 2: Duplicate Prevention**
    - **Validates: Requirements 1.2**
    - _Requirements: 1.2_
  
  - [x] 4.4 Write property test for full update replacement
    - **Property 3: Full Update Replacement**
    - **Validates: Requirements 2.1**
    - _Requirements: 2.1_
  
  - [x] 4.5 Write property test for delete removes trade
    - **Property 5: Delete Removes Trade**
    - **Validates: Requirements 9.1**
    - _Requirements: 9.1_
  
  - [x] 4.6 Write property test for delete idempotency
    - **Property 6: Delete Idempotency**
    - **Validates: Requirements 9.2**
    - _Requirements: 9.2_
  
  - [x] 4.7 Write unit tests for error conditions
    - Test not found errors (404)
    - Test duplicate errors (409)
    - Test context validation errors (422)
    - _Requirements: 2.2, 4.2, 13.2, 15.2_
  
  - [x] 4.8 Write property test for context metadata logged
    - **Property 21: Context Metadata Logged**
    - **Validates: Requirements 15.3, 15.4**
    - Test that mutating operations log context with timestamp
    - _Requirements: 15.3, 15.4_

- [x] 5. Checkpoint - Ensure core operations work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement deep merge logic for partial updates
  - [x] 6.1 Implement `_deep_merge()` helper method in `TradeService`
    - Handle recursive dictionary merging
    - Implement smart null handling: remove objects, set primitives to null
    - Handle list replacement (not merging)
    - _Requirements: 3.1, 3.3_
  
  - [x] 6.2 Implement `save_partial()` method using deep merge
    - Call `_deep_merge()` to merge updates onto existing trade
    - Accept context parameter and pass to storage
    - _Requirements: 3.1, 3.2, 3.3, 15.3_
  
  - [x] 6.3 Write property test for deep merge preservation
    - **Property 4: Deep Merge Preservation**
    - **Validates: Requirements 3.1, 3.3**
    - Test field preservation, override, and null handling
    - _Requirements: 3.1, 3.3_
  
  - [x] 6.4 Write unit tests for specific deep merge scenarios
    - Test nested object removal with null
    - Test primitive field set to null
    - Test deeply nested merges (5+ levels)
    - Test list replacement
    - _Requirements: 3.1, 3.3_

- [x] 7. Implement filtering logic
  - [x] 7.1 Implement `_apply_filter()` helper method in `TradeService`
    - Support equality operator (`eq`)
    - Support comparison operators (`gt`, `gte`, `lt`, `lte`)
    - Support regex operator with Python `re` module
    - Support list operators (`in`, `nin`)
    - Support nested field paths (e.g., `data.leg1.notional`)
    - Combine multiple conditions with AND logic
    - _Requirements: 6.1_
  
  - [x] 7.2 Implement filter-based methods
    - Implement `load_by_filter()` method (accepts context parameter)
    - Implement `list_by_filter()` method (accepts context parameter)
    - Implement `count_by_filter()` method (accepts context parameter)
    - _Requirements: 6.1, 7.1, 8.1, 15.1_
  
  - [x] 7.3 Write property test for filter correctness
    - **Property 9: Filter Correctness**
    - **Validates: Requirements 6.1**
    - _Requirements: 6.1_
  
  - [x] 7.4 Write property test for equality filter
    - **Property 12: Equality Filter**
    - **Validates: Requirements 6.1**
    - _Requirements: 6.1_
  
  - [x] 7.5 Write property test for range filter
    - **Property 13: Range Filter**
    - **Validates: Requirements 6.1**
    - _Requirements: 6.1_
  
  - [x] 7.6 Write property test for regex filter
    - **Property 14: Regex Filter**
    - **Validates: Requirements 6.1**
    - _Requirements: 6.1_
  
  - [x] 7.7 Write property test for multiple filter conditions
    - **Property 15: Multiple Filter Conditions (AND Logic)**
    - **Validates: Requirements 6.1**
    - _Requirements: 6.1_
  
  - [x] 7.8 Write property test for count matches filter
    - **Property 10: Count Matches Filter**
    - **Validates: Requirements 8.1**
    - _Requirements: 8.1_
  
  - [x] 7.9 Write property test for list matches filter
    - **Property 11: List Matches Filter**
    - **Validates: Requirements 7.1**
    - _Requirements: 7.1_
  
  - [x] 7.10 Write unit tests for filter edge cases
    - Test empty filter (returns all trades)
    - Test filter with no matches
    - Test invalid filter structure
    - _Requirements: 6.2, 6.3_

- [x] 8. Implement bulk operations
  - [x] 8.1 Implement bulk load and delete methods
    - Implement `load_by_ids()` method with missing ID tracking (accepts context parameter)
    - Implement `delete_by_ids()` method with missing ID tracking (accepts context parameter)
    - _Requirements: 5.1, 5.2, 10.1, 10.2, 15.1_
  
  - [x] 8.2 Write property test for group load completeness
    - **Property 7: Group Load Completeness**
    - **Validates: Requirements 5.1, 5.2**
    - _Requirements: 5.1, 5.2_
  
  - [x] 8.3 Write property test for group delete completeness
    - **Property 8: Group Delete Completeness**
    - **Validates: Requirements 10.1, 10.2**
    - _Requirements: 10.1, 10.2_
  
  - [x] 8.4 Write unit tests for bulk operation edge cases
    - Test empty ID list
    - Test all IDs missing
    - Test mix of existing and missing IDs
    - _Requirements: 5.3, 10.3_

- [x] 9. Checkpoint - Ensure service layer is complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement API endpoints for save operations
  - [x] 10.1 Create save routes in `src/tcs_store/api/save.py`
    - Implement POST `/save/new` endpoint (accepts SaveNewRequest with context)
    - Implement POST `/save/update` endpoint (accepts SaveUpdateRequest with context)
    - Implement POST `/save/partial` endpoint (accepts PartialUpdateRequest with context)
    - Wire up `TradeService` via dependency injection
    - Extract context from request and pass to service methods
    - _Requirements: 1.1, 1.2, 1.5, 2.1, 2.2, 2.4, 3.1, 3.2, 3.4, 15.1_
  
  - [x] 10.2 Write integration tests for save endpoints
    - Test successful save operations with valid context
    - Test error responses for missing/invalid context (422)
    - Test error responses (409, 404, 422)
    - Test HTTP status codes
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.4, 15.1, 15.2_

- [x] 11. Implement API endpoints for load operations
  - [x] 11.1 Create load routes in `src/tcs_store/api/load.py`
    - Implement POST `/load/id` endpoint (accepts context in body, trade ID in body)
    - Implement POST `/load/group` endpoint (accepts LoadGroupRequest with context)
    - Implement POST `/load/filter` endpoint (accepts LoadFilterRequest with context)
    - Wire up `TradeService` via dependency injection
    - Extract context from request and pass to service methods
    - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.4, 6.1, 6.4, 15.1_
  
  - [x] 11.2 Write integration tests for load endpoints
    - Test successful load operations with valid context
    - Test error responses for missing/invalid context (422)
    - Test error responses (404, 422)
    - Test HTTP status codes
    - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.4, 6.1, 6.3, 6.4, 15.1, 15.2_

- [x] 12. Implement API endpoints for list operations
  - [x] 12.1 Create list routes in `src/tcs_store/api/list.py`
    - Implement POST `/list` endpoint (accepts ListRequest with context)
    - Implement POST `/list/count` endpoint (accepts CountRequest with context)
    - Wire up `TradeService` via dependency injection
    - Extract context from request and pass to service methods
    - _Requirements: 7.1, 7.4, 8.1, 8.4, 15.1_
  
  - [x] 12.2 Write integration tests for list endpoints
    - Test successful list operations with valid context
    - Test error responses for missing/invalid context (422)
    - Test error responses (422)
    - Test HTTP status codes
    - _Requirements: 7.1, 7.3, 7.4, 8.1, 8.3, 8.4, 15.1, 15.2_

- [x] 13. Implement API endpoints for delete operations
  - [x] 13.1 Create delete routes in `src/tcs_store/api/delete.py`
    - Implement POST `/delete/id` endpoint (accepts context and ID in body)
    - Implement POST `/delete/group` endpoint (accepts DeleteGroupRequest with context)
    - Wire up `TradeService` via dependency injection
    - Extract context from request and pass to service methods
    - Implement idempotent behavior for delete operations
    - _Requirements: 9.1, 9.2, 9.3, 10.1, 10.2, 10.4, 15.1_
  
  - [x] 13.2 Write integration tests for delete endpoints
    - Test successful delete operations with valid context
    - Test error responses for missing/invalid context (422)
    - Test idempotent behavior (deleting non-existent trades)
    - Test HTTP status codes
    - _Requirements: 9.1, 9.2, 9.3, 10.1, 10.2, 10.3, 10.4, 15.1, 15.2_

- [x] 14. Implement health check and error handling
  - [x] 14.1 Create health check endpoint in `src/tcs_store/api/health.py`
    - Implement GET `/health` endpoint (no context required for health check)
    - Return service status and version information
    - _Requirements: 14.1, 14.2, 14.3_
  
  - [x] 14.2 Implement global exception handlers in `main.py`
    - Add handler for `TradeNotFoundError` → 404
    - Add handler for `TradeAlreadyExistsError` → 409
    - Add handler for `InvalidFilterError` → 422
    - Add handler for `ValidationError` → 422 (including context validation errors)
    - Add handler for generic exceptions → 500
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 15.2_
  
  - [x] 14.3 Write property test for error response format
    - **Property 18: Error Response Format**
    - **Validates: Requirements 13.1**
    - _Requirements: 13.1_
  
  - [x] 14.4 Write property test for not found errors
    - **Property 16: Not Found Errors**
    - **Validates: Requirements 2.2, 3.2, 4.2**
    - _Requirements: 2.2, 3.2, 4.2_
  
  - [x] 14.5 Write property test for validation errors
    - **Property 17: Validation Errors**
    - **Validates: Requirements 1.3, 2.3, 6.3, 7.3, 8.3, 11.2**
    - _Requirements: 1.3, 2.3, 6.3, 7.3, 8.3, 11.2_
  
  - [x] 14.6 Write unit tests for health check
    - Test health endpoint returns 200
    - Test response includes service information
    - _Requirements: 14.1, 14.2, 14.3_

- [x] 15. Wire all components together in main application
  - [x] 15.1 Complete `main.py` setup
    - Create singleton `InMemoryStore` instance
    - Create `TradeService` instance with store dependency
    - Register all API routers (save, load, list, delete, health)
    - Configure CORS if needed
    - Add startup/shutdown events
    - _Requirements: 12.1_
  
  - [x] 15.2 Write end-to-end integration tests
    - Test complete workflows with context (save → load → update → delete)
    - Test multiple operations in sequence
    - Test API with realistic trade payloads and context
    - Verify operation log contains context metadata
    - _Requirements: All, 15.3, 15.4_

- [x] 16. Final checkpoint - Comprehensive testing
  - Run all unit tests and ensure they pass
  - Run all property tests and ensure they pass
  - Run all integration tests and ensure they pass
  - Verify test coverage meets goals (90% line coverage)
  - Verify all operations log context metadata
  - Ask the user if questions arise.

- [x] 17. Add documentation and configuration
  - [x] 17.1 Create README.md with setup and usage instructions
    - Document API endpoints with examples including context metadata
    - Document filter syntax and operators
    - Document deep merge behavior with examples
    - Document context metadata requirements (user, agent, action, intent)
    - Include Poetry setup instructions
    - _Requirements: 15.5_
  
  - [x] 17.2 Add OpenAPI customization
    - Add endpoint descriptions and examples with context
    - Add request/response examples showing context metadata
    - Add tags for endpoint grouping
    - Document context metadata schema
    - _Requirements: 11.4, 15.5_
  
  - [x] 17.3 Create example scripts
    - Create example client script demonstrating all operations with context
    - Create example trade payloads for testing
    - Create example context metadata for different scenarios

- [ ] 18. Set up HTML test reporting
  - [ ] 18.1 Install pytest-html plugin
    - Add pytest-html to dev dependencies using Poetry
    - _Requirements: Testing infrastructure_
  
  - [ ] 18.2 Configure HTML report generation
    - Update pyproject.toml or create pytest.ini with HTML report settings
    - Configure report output location (e.g., `test-reports/report.html`)
    - Enable self-contained HTML reports for easy sharing
    - _Requirements: Testing infrastructure_
  
  - [ ] 18.3 Create test report generation script
    - Create a shell script or make target to run tests with HTML output
    - Include commands for running all tests (unit, property, integration)
    - Add instructions to README for generating and viewing reports
    - _Requirements: Testing infrastructure_
  
  - [ ] 18.4 Verify HTML report functionality
    - Run tests and generate HTML report
    - Open report in browser and verify all test results are visible
    - Verify pass/fail status, execution times, and error details are displayed
    - _Requirements: Testing infrastructure_

- [ ] 19. Docker containerization
  - [ ] 19.1 Create Dockerfile for TCS Store
    - Create multi-stage Dockerfile based on Python 3.11-slim
    - Install Poetry and dependencies in builder stage
    - Copy application code to production stage
    - Create non-root user for security
    - Expose port 5500 (default TCS Store port)
    - Add health check endpoint verification
    - Set CMD to run Gunicorn with Uvicorn workers
    - _Requirements: Deployment infrastructure_
  
  - [ ] 19.2 Create docker-compose.yml
    - Define tcs-store service with build context
    - Configure port mapping (5500:5500)
    - Set environment variables (HOST, PORT, WORKERS)
    - Add health check configuration
    - Configure restart policy
    - Add volume mounts if needed for logs
    - _Requirements: Deployment infrastructure_
  
  - [ ] 19.3 Create .dockerignore file
    - Exclude .hypothesis directory
    - Exclude .pytest_cache directory
    - Exclude htmlcov directory
    - Exclude __pycache__ directories
    - Exclude .coverage files
    - Exclude test files and directories
    - Exclude development files (.env, .vscode, etc.)
    - _Requirements: Deployment infrastructure_
  
  - [ ] 19.4 Test Docker build and run
    - Build Docker image: `docker build -t tcs-store:latest .`
    - Run container: `docker run -p 5500:5500 tcs-store:latest`
    - Verify API is accessible at http://localhost:5500
    - Test health endpoint: `curl http://localhost:5500/health`
    - Test API docs: http://localhost:5500/docs
    - Verify container logs show proper startup
    - _Requirements: Deployment infrastructure_
  
  - [ ] 19.5 Test docker-compose deployment
    - Start service: `docker-compose up -d`
    - Verify service is running: `docker-compose ps`
    - Test API endpoints through Docker network
    - Check logs: `docker-compose logs tcs-store`
    - Stop service: `docker-compose down`
    - _Requirements: Deployment infrastructure_
  
  - [ ] 19.6 Update documentation for Docker deployment
    - Add Docker deployment section to README.md
    - Document Docker build and run commands
    - Document docker-compose usage
    - Document environment variables for configuration
    - Add troubleshooting section for common Docker issues
    - _Requirements: Deployment infrastructure_

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- All tests must pass before moving to the next checkpoint
- The implementation uses Python with FastAPI, Poetry, Pydantic, and Hypothesis
- **CRITICAL**: Every API call (except /health) must include context metadata with user, agent, action, and intent fields
- Context metadata is logged for all mutating operations to enable lifecycle tracing
