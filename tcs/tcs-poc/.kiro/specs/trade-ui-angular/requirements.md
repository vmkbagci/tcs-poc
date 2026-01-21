# Requirements Document

## Introduction

This document specifies the requirements for a modern Angular-based Trade Management UI that displays and manages financial trade data (Interest Rate Swaps, Commodity Options, Index Swaps). The application will interact with the Trade API to create, view, and validate trades through a responsive, performant user interface.

## Glossary

- **Trade_UI**: The Angular web application for managing trades
- **Trade_API**: The FastAPI backend service providing trade operations
- **NEW_Trade**: A skeletal trade template returned by GET /new endpoint
- **PRESAVE_Trade**: A user-populated trade ready for validation/saving
- **POSTSAVE_Trade**: A persisted trade with system-generated fields
- **Trade_Type**: One of: ir-swap, commodity-option, index-swap
- **Schedule**: Array of payment/calculation periods within a trade leg
- **Swap_Leg**: A component of a swap defining payment terms (fixed or floating)

## Requirements

### Requirement 1: Modern Angular Architecture

**User Story:** As a developer, I want the application built with latest Angular features, so that it is maintainable, performant, and follows current best practices.

#### Acceptance Criteria

1. THE Trade_UI SHALL use Angular 18 or later (latest stable version)
2. THE Trade_UI SHALL use standalone components (no NgModules)
3. THE Trade_UI SHALL use Angular Signals for reactive state management
4. THE Trade_UI SHALL use the new inject() function for dependency injection
5. THE Trade_UI SHALL use the HttpClient with modern interceptors for API calls

### Requirement 2: Routing and Navigation

**User Story:** As a user, I want to navigate between different views, so that I can access trade creation, viewing, and listing features.

#### Acceptance Criteria

1. THE Trade_UI SHALL implement functional route guards using CanActivateFn
2. WHEN a user navigates to the root path, THE Trade_UI SHALL redirect to the trade list view
3. WHEN a user navigates to /trades/new, THE Trade_UI SHALL display the trade creation form
4. WHEN a user navigates to /trades/:id, THE Trade_UI SHALL display the trade detail view
5. THE Trade_UI SHALL use lazy loading for feature routes

### Requirement 3: Trade Creation Workflow

**User Story:** As a trader, I want to create new trades from templates, so that I can enter trade details efficiently.

#### Acceptance Criteria

1. WHEN a user selects a trade type, THE Trade_UI SHALL call GET /api/v1/trades/new with the trade_type parameter
2. WHEN the NEW_Trade is received, THE Trade_UI SHALL display a form with all editable fields
3. WHEN a user fills in required fields, THE Trade_UI SHALL enable real-time validation
4. WHEN a user clicks Save, THE Trade_UI SHALL call POST /api/v1/trades/validate before saving
5. IF validation succeeds, THEN THE Trade_UI SHALL call POST /api/v1/trades/save
6. WHEN save succeeds, THE Trade_UI SHALL navigate to the trade detail view with the POSTSAVE_Trade

### Requirement 4: Trade Display and Visualization

**User Story:** As a trader, I want to view trade details in an organized layout, so that I can understand the trade structure quickly.

#### Acceptance Criteria

1. THE Trade_UI SHALL display trade data organized in collapsible sections (General, Common, Swap Details, Legs)
2. WHEN displaying swap legs, THE Trade_UI SHALL show each leg in a separate tab or panel
3. WHEN a leg contains a schedule, THE Trade_UI SHALL display it in a data grid
4. THE Trade_UI SHALL dynamically generate grid columns based on schedule data structure
5. THE Trade_UI SHALL highlight required fields that are empty or invalid

### Requirement 5: Dynamic Grid for Schedules

**User Story:** As a trader, I want to see payment schedules in a grid format, so that I can review calculated periods and amounts.

#### Acceptance Criteria

1. WHEN a schedule array exists in trade data, THE Trade_UI SHALL detect column names from the first schedule object
2. THE Trade_UI SHALL render a data grid with columns matching the schedule properties
3. THE Trade_UI SHALL format date columns as readable dates
4. THE Trade_UI SHALL format numeric columns with appropriate precision
5. THE Trade_UI SHALL support sorting on grid columns

### Requirement 6: API Integration with Performance

**User Story:** As a developer, I want efficient API communication, so that the UI remains responsive under load.

#### Acceptance Criteria

1. THE Trade_UI SHALL use HttpClient with RxJS operators for API calls
2. THE Trade_UI SHALL implement request caching for GET /new templates
3. THE Trade_UI SHALL debounce validation requests during form input
4. THE Trade_UI SHALL show loading indicators during API calls
5. THE Trade_UI SHALL handle API errors gracefully with user-friendly messages

### Requirement 7: Form Validation and Feedback

**User Story:** As a trader, I want immediate feedback on form inputs, so that I can correct errors before saving.

#### Acceptance Criteria

1. WHEN a required field is empty, THE Trade_UI SHALL display a validation error
2. WHEN a field has invalid format, THE Trade_UI SHALL display format requirements
3. WHEN validation succeeds, THE Trade_UI SHALL display a success indicator
4. THE Trade_UI SHALL disable the Save button when form is invalid
5. WHEN API validation fails, THE Trade_UI SHALL display server-side error messages

### Requirement 8: Responsive Design with Angular Material

**User Story:** As a user, I want a modern, responsive interface, so that I can use the application on different screen sizes.

#### Acceptance Criteria

1. THE Trade_UI SHALL use Angular Material components for UI elements
2. THE Trade_UI SHALL implement responsive layouts using Angular Flex Layout or CSS Grid
3. WHEN viewed on mobile devices, THE Trade_UI SHALL adapt layout for smaller screens
4. THE Trade_UI SHALL use Material Design theming for consistent styling
5. THE Trade_UI SHALL provide accessible UI elements following ARIA guidelines

### Requirement 9: Multi-Trade Type Support

**User Story:** As a trader, I want to work with different trade types, so that I can manage various financial instruments.

#### Acceptance Criteria

1. THE Trade_UI SHALL support ir-swap, commodity-option, and index-swap trade types
2. WHEN displaying a trade, THE Trade_UI SHALL adapt the form/view based on trade_type
3. THE Trade_UI SHALL show/hide fields specific to each trade type
4. THE Trade_UI SHALL use the trade_type field from JSON to determine trade structure
5. THE Trade_UI SHALL provide a trade type selector in the creation workflow

### Requirement 10: State Management with Signals

**User Story:** As a developer, I want reactive state management, so that UI updates are efficient and predictable.

#### Acceptance Criteria

1. THE Trade_UI SHALL use Angular Signals for component state
2. THE Trade_UI SHALL use computed signals for derived state
3. THE Trade_UI SHALL use effect() for side effects based on signal changes
4. THE Trade_UI SHALL minimize unnecessary re-renders through signal-based change detection
5. THE Trade_UI SHALL use signal-based forms (if available) or reactive forms with signal integration

### Requirement 11: Trade List and Search

**User Story:** As a trader, I want to view and search existing trades, so that I can find and manage trades efficiently.

#### Acceptance Criteria

1. THE Trade_UI SHALL display a list view showing all trades
2. THE Trade_UI SHALL provide filters for trade type, date range, counterparty, and book
3. WHEN a user applies filters, THE Trade_UI SHALL update the trade list dynamically
4. WHEN a user clicks on a trade, THE Trade_UI SHALL navigate to the trade detail view
5. THE Trade_UI SHALL support pagination for large trade lists

### Requirement 12: Trade Editing

**User Story:** As a trader, I want to edit existing trades, so that I can correct errors or update trade details.

#### Acceptance Criteria

1. WHEN viewing a POSTSAVE_Trade, THE Trade_UI SHALL provide an Edit button
2. WHEN a user clicks Edit, THE Trade_UI SHALL enable form fields for editing
3. WHEN a user modifies fields, THE Trade_UI SHALL validate changes in real-time
4. WHEN a user saves changes, THE Trade_UI SHALL call POST /api/v1/trades/validate then POST /api/v1/trades/save
5. THE Trade_UI SHALL preserve the original tradeId when saving edited trades

### Requirement 13: Schedule Editing

**User Story:** As a trader, I want to edit schedule rows, so that I can customize payment periods and amounts.

#### Acceptance Criteria

1. WHEN displaying a schedule grid, THE Trade_UI SHALL allow inline editing of schedule rows
2. WHEN a user edits a schedule cell, THE Trade_UI SHALL validate the input
3. WHEN a user adds or removes schedule rows, THE Trade_UI SHALL update the schedule array
4. THE Trade_UI SHALL recalculate dependent fields when schedule data changes
5. THE Trade_UI SHALL highlight modified schedule rows

### Requirement 14: Validation Strategy

**User Story:** As a trader, I want flexible validation feedback, so that I can catch errors early without disrupting my workflow.

#### Acceptance Criteria

1. THE Trade_UI SHALL validate required fields on blur (when user leaves field)
2. THE Trade_UI SHALL validate format/type on change for critical fields
3. WHEN validation requires backend logic, THE Trade_UI SHALL debounce and call POST /api/v1/trades/validate asynchronously
4. THE Trade_UI SHALL display inline validation errors immediately
5. THE Trade_UI SHALL perform full validation on submit before saving

### Requirement 15: Error Recovery and Auto-Save

**User Story:** As a trader, I want my work preserved if errors occur, so that I don't lose data during failures.

#### Acceptance Criteria

1. WHEN a user modifies form data, THE Trade_UI SHALL auto-save to browser storage every 30 seconds
2. WHEN a save operation fails, THE Trade_UI SHALL retain form data and display error details
3. WHEN a user returns to an incomplete trade, THE Trade_UI SHALL offer to restore auto-saved data
4. THE Trade_UI SHALL clear auto-saved data after successful save
5. THE Trade_UI SHALL provide a manual "Discard Changes" option to clear auto-saved data

### Requirement 16: Audit Trail Display

**User Story:** As a trader, I want to view trade lifecycle events, so that I can track changes and actions on trades.

#### Acceptance Criteria

1. WHEN displaying a POSTSAVE_Trade, THE Trade_UI SHALL show an expandable Events section
2. WHEN a user expands the Events section, THE Trade_UI SHALL display all events from the events array
3. THE Trade_UI SHALL format event timestamps as readable dates
4. THE Trade_UI SHALL display event details including eventCode, eventDescription, and application
5. THE Trade_UI SHALL sort events by businessDateTime in descending order (newest first)

### Requirement 17: Real-Time Updates Hook

**User Story:** As a developer, I want infrastructure for real-time updates, so that future implementations can add live data synchronization.

#### Acceptance Criteria

1. THE Trade_UI SHALL define a service interface for real-time update subscriptions
2. THE Trade_UI SHALL provide a stub implementation that does nothing
3. THE Trade_UI SHALL structure components to accept update notifications
4. THE Trade_UI SHALL document the integration points for WebSocket or polling implementations
5. THE Trade_UI SHALL allow future implementations without refactoring component code

### Requirement 18: User Preferences Hook

**User Story:** As a developer, I want infrastructure for user preferences, so that future implementations can persist settings.

#### Acceptance Criteria

1. THE Trade_UI SHALL define a service interface for loading and saving user preferences
2. THE Trade_UI SHALL provide a stub implementation that returns default values
3. THE Trade_UI SHALL structure components to use preference values (theme, column visibility, etc.)
4. THE Trade_UI SHALL document the preference schema for future cookie/config implementations
5. THE Trade_UI SHALL allow future implementations without refactoring component code

### Requirement 19: Testing Infrastructure

**User Story:** As a developer, I want testing infrastructure in place, so that tests can be added when needed.

#### Acceptance Criteria

1. THE Trade_UI SHALL include Jest or Jasmine configuration for unit tests
2. THE Trade_UI SHALL include Cypress or Playwright configuration for e2e tests
3. THE Trade_UI SHALL provide example test files with proper setup
4. THE Trade_UI SHALL configure test coverage reporting
5. THE Trade_UI SHALL NOT implement actual test cases until explicitly requested
