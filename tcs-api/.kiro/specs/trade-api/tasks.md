# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - [x] 1.1 Initialize Poetry project with proper configuration
    - Run `poetry init` and configure pyproject.toml with project metadata
    - Add core dependencies: FastAPI, Pydantic, orjson, jmespath, glom, Hypothesis, pytest
    - Add ASGI server dependencies: uvicorn (development), gunicorn (production option)
    - Set up development dependencies and virtual environment management
    - _Requirements: All requirements depend on proper project setup_
  
  - [x] 1.2 Create FastAPI project structure with proper package organization
    - Create src/trade_api package structure following Poetry conventions
    - Set up configuration management for different environments
    - Create basic application factory pattern for scalability
    - _Requirements: All requirements depend on proper project setup_

- [ ] 2. Implement core Trade class and data structures
  - [x] 2.1 Create Trade class with JSON composition pattern
    - Implement Trade class with direct JSON data access
    - Use jmespath for powerful query capabilities (filters, projections)
    - Use glom for robust nested property writes
    - Use orjson for fast JSON parsing and serialization
    - Implement ReadOnlyTrade class with cached properties for read-only contexts
    - Ensure minimal object overhead while preserving flexibility
    - _Requirements: 5.3, 5.5_

  - [ ]* 2.2 Write property test for Trade class JSON access
    - **Property 9: JSON flexibility preservation**
    - **Validates: Requirements 5.3**

  - [x] 2.3 Implement TradeAssembler for component-based trade composition
    - Create TradeAssembler class with deep merge capabilities
    - Support configurable list merge strategies (replace, append, extend)
    - Implement immutable assembly (deepcopy to avoid shared references)
    - Add optional validation hooks
    - Provide fluent API for configuration
    - _Requirements: 1.5, 5.3, 5.5_

  - [x] 2.4 REFACTOR: Create two-layer template component system
    - Set up new template directory structure with schema versioning
    - **Layer 1 - Administrative Core:**
      - Create `core/general.json` (shared by all trades)
      - Create `core/common.json` (shared by all trades)
    - **Layer 2 - Economic Blocks:**
      - Create IR Swap templates: `trade-types/ir-swap/`
        - `swap-details.json`
        - `swap-leg-fixed.json`
        - `swap-leg-floating-ois.json`
        - `swap-leg-floating-ibor.json`
      - Create Commodity Option templates: `trade-types/commodity-option/`
        - `commodity-details.json`
        - `schedule-details.json`
        - `exercise-payment.json`
        - `premium.json`
      - Create Index Swap templates: `trade-types/index-swap/`
        - `leg-base.json`
        - `underlying-asset.json`
        - `fixed-fee-leg.json`
        - `floating-index-leg.json`
        - `payment.json`
    - Remove old hierarchical template structure
    - _Requirements: 1.5_

  - [x] 2.5 REFACTOR: Implement TradeTemplateFactory with two-layer composition
    - Refactor factory class to use two-layer architecture
    - Implement administrative core loading (general + common)
    - Implement trade-specific economic block loading
    - Support three trade types: ir-swap, commodity-option, index-swap
    - Update component discovery and validation
    - Remove old hierarchical inheritance logic
    - _Requirements: 1.1, 1.5, 5.3_

  - [ ]* 2.6 Write unit tests for TradeAssembler
    - Test deep merge with various data structures
    - Test list merge strategies
    - Test immutability and validation hooks
    - _Requirements: 5.3, 5.5_

  - [ ]* 2.7 Write unit tests for TradeTemplateFactory
    - Test component loading and caching
    - Test two-layer composition for all three trade types
    - Test schema versioning
    - _Requirements: 1.5_

- [ ] 2.8 Checkpoint - Verify refactored template system
  - Test all three trade types can be created via /new endpoint
  - Verify administrative core is shared across all trade types
  - Verify economic blocks are trade-specific
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 3. Implement pipeline architecture
  - [ ] 3.1 Create PipelineStage abstract base class
    - Define stage interface with execute method and validation
    - Implement stage registration and discovery mechanisms
    - _Requirements: 4.4_

  - [ ] 3.2 Implement PipelineEngine for stage orchestration
    - Create pipeline execution logic with error handling
    - Implement stage-to-stage data passing
    - Add pipeline halt on error functionality
    - _Requirements: 4.2, 4.3_

  - [ ]* 3.3 Write property test for pipeline execution order
    - **Property 5: Pipeline stage execution order**
    - **Validates: Requirements 4.2**

  - [ ]* 3.4 Write property test for pipeline error handling
    - **Property 8: Pipeline error handling**
    - **Validates: Requirements 4.3**

  - [ ] 3.5 Create StageRegistry for dynamic stage management
    - Implement stage registration and lookup functionality
    - Support runtime stage addition without core modifications
    - _Requirements: 4.4_

  - [ ]* 3.6 Write unit tests for pipeline components
    - Test stage registration and execution
    - Test error propagation and handling
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 4. Implement trade store and persistence
  - [ ] 4.1 Create TradeStore abstract interface
    - Define storage interface with save, get, exists, list methods
    - Ensure interface supports future database implementations
    - _Requirements: 6.1, 6.2_

  - [ ] 4.2 Implement InMemoryTradeStore
    - Create thread-safe in-memory storage using Python dict
    - Add basic statistics and monitoring capabilities
    - Implement proper error handling for storage operations
    - _Requirements: 6.1, 6.2, 6.4, 6.5_

  - [ ]* 4.3 Write property test for storage round-trip
    - **Property 3: JSON round-trip preservation**
    - **Validates: Requirements 6.3**

  - [ ]* 4.4 Write property test for trade store key uniqueness
    - **Property 7: Trade store key uniqueness**
    - **Validates: Requirements 6.2**

  - [ ]* 4.5 Write unit tests for trade store
    - Test concurrent access patterns
    - Test memory statistics functionality
    - _Requirements: 6.4, 6.5_

- [ ] 5. Create pipeline stages for core operations
  - [ ] 5.1 Implement TradeIdGenerationStage
    - Generate unique trade IDs following SWAP-YYYYMMDD-TYPE-NNNN format
    - Handle date formatting and sequence numbering
    - _Requirements: 1.2_

  - [ ]* 5.2 Write property test for trade ID generation
    - **Property 1: Trade ID generation consistency**
    - **Validates: Requirements 1.2**

  - [ ] 5.3 Implement TradeTemplateStage
    - Create trade templates based on trade type
    - Populate optional fields when provided (user ID, counterparties)
    - Set appropriate defaults and empty placeholders
    - _Requirements: 1.1, 1.3, 1.4, 1.5_

  - [ ]* 5.4 Write property test for template field population
    - **Property 2: Template field population**
    - **Validates: Requirements 1.3, 1.4**

  - [ ] 5.5 Implement VersionManagementStage
    - Handle version incrementing for trade updates
    - Add lifecycle entries with proper metadata
    - _Requirements: 2.2_

  - [ ]* 5.6 Write property test for version increment consistency
    - **Property 4: Version increment consistency**
    - **Validates: Requirements 2.2**

  - [ ] 5.7 Implement ValidationStage
    - Create flexible validation logic for trade structure
    - Implement business rule validation (dates, consistency checks)
    - Collect all validation errors before returning
    - _Requirements: 3.1, 3.4, 3.5_

  - [ ]* 5.8 Write property test for validation error completeness
    - **Property 6: Validation error completeness**
    - **Validates: Requirements 3.3**

  - [ ]* 5.9 Write unit tests for pipeline stages
    - Test each stage with various input scenarios
    - Test error conditions and edge cases
    - _Requirements: 1.1, 1.2, 2.2, 3.1_

- [ ] 6. Implement pipeline factory and configuration
  - [ ] 6.1 Create PipelineFactory for dynamic pipeline construction
    - Implement trade type and operation-based pipeline selection
    - Support configurable pipeline composition
    - _Requirements: 4.1_

  - [ ]* 6.2 Write property test for trade type pipeline selection
    - **Property 10: Trade type pipeline selection**
    - **Validates: Requirements 4.1**

  - [ ] 6.3 Define pipeline configurations for each endpoint
    - Configure 'new' endpoint pipeline: ID generation, template creation, metadata
    - Configure 'save' endpoint pipeline: validation, version management, storage
    - Configure 'validate' endpoint pipeline: comprehensive validation only
    - _Requirements: 1.1, 2.1, 3.1_

  - [ ]* 6.4 Write unit tests for pipeline factory
    - Test pipeline construction for different scenarios
    - Test configuration loading and validation
    - _Requirements: 4.1_

- [ ] 7. Implement FastAPI endpoints and request handling
  - [ ] 7.1 Create Pydantic models for API requests and responses
    - Define minimal models for request validation only
    - Ensure models don't enforce rigid schemas on trade data
    - _Requirements: 5.4_

  - [x] 7.2 REFACTOR: Implement /new endpoint for three trade types
    - Accept trade type parameter: "ir-swap", "commodity-option", "index-swap"
    - Accept trade-specific optional parameters
    - Execute new trade pipeline and return template
    - Handle errors and return appropriate responses
    - Update endpoint to work with refactored template system
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ] 7.3 Implement /save endpoint
    - Accept trade JSON data and optional metadata
    - Execute save pipeline with validation and storage
    - Return updated trade with confirmation metadata
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ] 7.4 Implement /validate endpoint
    - Accept trade JSON data for validation
    - Execute validation pipeline and return results
    - Provide detailed error messages and warnings
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ]* 7.5 Write unit tests for API endpoints
    - Test request/response handling
    - Test error scenarios and edge cases
    - _Requirements: 1.1, 2.1, 3.1_

- [ ] 8. Integrate components and add error handling
  - [ ] 8.1 Wire together all components in main application
    - Initialize trade store, pipeline engine, and stage registry
    - Configure dependency injection for FastAPI
    - Set up proper error handling and logging
    - _Requirements: All requirements_

  - [ ] 8.2 Implement comprehensive error handling
    - Add proper exception handling throughout the system
    - Create consistent error response formats
    - Implement logging for debugging and monitoring
    - _Requirements: 2.5, 3.3, 4.3_

  - [ ] 8.3 Add application startup and configuration
    - Initialize in-memory store and load configurations
    - Set up FastAPI application with proper middleware
    - _Requirements: 6.1_

  - [ ]* 8.4 Write integration tests
    - Test complete workflows end-to-end
    - Test error propagation through the system
    - _Requirements: All requirements_

- [ ] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Create sample data and basic testing utilities
  - [ ] 10.1 Create sample trade data based on JSON examples
    - Generate test data for all four swap types
    - Create both valid and invalid examples for testing
    - _Requirements: All requirements for testing_

  - [ ] 10.2 Add basic API testing and demonstration script
    - Create script to demonstrate all three endpoints
    - Show complete workflow from new trade to save and validate
    - _Requirements: 1.1, 2.1, 3.1_

  - [ ]* 10.3 Write property-based test generators
    - Create Hypothesis strategies for generating trade data
    - Implement smart generators that create realistic financial data
    - _Requirements: All requirements for comprehensive testing_

- [ ] 11. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.