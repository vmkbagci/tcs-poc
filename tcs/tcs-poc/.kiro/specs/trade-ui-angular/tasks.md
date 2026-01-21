# Implementation Plan: Trade Management UI

## Overview

This implementation plan breaks down the development of the Angular 18+ Trade Management UI into discrete, incremental tasks. Each task builds on previous work, ensuring continuous integration and early validation of core functionality.

## Tasks

- [x] 1. Project Setup and Infrastructure
  - Initialize Angular 18+ project in tcs-ui/ directory
  - Configure Angular Material and theming
  - Set up project structure (core, features, shared folders)
  - Configure environment files for API endpoints
  - Set up testing infrastructure (Jest/Jasmine, Cypress/Playwright configs)
  - Configure build and development scripts
  - _Requirements: 1.1, 1.2, 19.1, 19.2, 19.3, 19.4_

- [x] 2. Core Services and Models
  - [x] 2.1 Create TypeScript interfaces for Trade models
    - Define Trade, GeneralSection, SwapLeg, SchedulePeriod interfaces
    - Define API response models (TradeResponse, ValidationResponse)
    - Define filter and preference models
    - _Requirements: 1.1, 1.2_

  - [x] 2.2 Implement TradeService with HTTP client
    - Create getNewTrade(), saveTrade(), validateTrade() methods
    - Implement signal-based state (currentTrade, trades, loading, error)
    - Add request caching for GET /new templates
    - Configure API base URL from environment
    - _Requirements: 3.1, 3.4, 3.5, 6.1, 6.2_

  - [x] 2.3 Implement ValidationService
    - Create validateField() for client-side validation
    - Implement validateTradeAsync() with debouncing (300ms)
    - Add validation result caching
    - Create getFieldErrors() signal accessor
    - _Requirements: 6.3, 7.1, 7.2, 14.1, 14.2, 14.3_

  - [x] 2.4 Implement AutoSaveService with pluggable storage
    - Define IAutoSaveStorage interface for storage backends
    - Implement LocalStorageBackend (default)
    - Create startAutoSave() with 30-second interval
    - Add getAutoSavedData() and clearAutoSavedData() methods
    - Implement setStorageBackend() for future API storage
    - Handle auto-save key generation (trade-autosave-{id})
    - Document ApiStorageBackend interface for future Redis integration
    - _Requirements: 15.1, 15.3, 15.4, 15.5_

  - [x] 2.5 Create stub services for future features
    - Implement PreferencesService interface and stub
    - Implement RealtimeService interface and stub
    - Document integration points for future implementation
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 18.1, 18.2, 18.3, 18.4, 18.5_

- [x] 3. HTTP Interceptors and Guards
  - [x] 3.1 Create error interceptor
    - Implement HttpInterceptorFn for error handling
    - Add user-friendly error message mapping
    - Integrate with MatSnackBar for notifications
    - _Requirements: 6.5_

  - [x] 3.2 Create loading interceptor
    - Implement HttpInterceptorFn for loading state
    - Create LoadingService with signal-based state
    - Show/hide loading indicators
    - _Requirements: 6.4_

  - [x] 3.3 Create unsaved changes guard
    - Implement CanDeactivateFn functional guard
    - Check for unsaved form data
    - Show confirmation dialog before navigation
    - _Requirements: 2.1, 15.2_

- [x] 4. Routing Configuration
  - [x] 4.1 Set up app routes with lazy loading
    - Configure routes for /, /trades, /trades/new, /trades/:id
    - Implement lazy loading for feature components
    - Add route guards to prevent data loss
    - Set up route titles
    - _Requirements: 2.2, 2.3, 2.4, 2.5_

- [x] 5. Shared Components and Utilities
  - [x] 5.1 Create shared UI components
    - LoadingSpinnerComponent
    - ErrorMessageComponent
    - ConfirmationDialogComponent
    - _Requirements: 6.4, 6.5_

  - [x] 5.2 Create pipes for formatting
    - DateFormatPipe for readable dates
    - CurrencyFormatPipe for numeric values
    - _Requirements: 5.3, 5.4, 16.3_

  - [x] 5.3 Create utility directives
    - AutoFocusDirective for form fields
    - _Requirements: 8.5_

- [x] 6. Trade List Feature
  - [x] 6.1 Create TradeListComponent
    - Implement component with signal-based state
    - Load trades on init using TradeService
    - Display trades in Material table
    - Add pagination controls
    - Handle row click navigation
    - _Requirements: 11.1, 11.4, 11.5_

  - [x] 6.2 Create TradeFilterComponent
    - Implement filter controls (trade type, date range, counterparty, book)
    - Use reactive forms for filter inputs
    - Emit filter changes to parent
    - _Requirements: 11.2_

  - [x] 6.3 Implement filter logic
    - Create computed signal for filtered trades
    - Apply filters reactively
    - Update table when filters change
    - _Requirements: 11.3_

- [x] 7. Trade Creation Feature
  - [x] 7.1 Create TradeTypeSelector Component
    - Display trade type options (ir-swap, commodity-option, index-swap)
    - Use Material radio buttons or select
    - Emit selected trade type
    - _Requirements: 9.1, 9.5_

  - [x] 7.2 Create TradeCreateComponent
    - Implement trade type selection
    - Call TradeService.getNewTrade() with selected type
    - Display loading state during template fetch
    - Render trade form when template loaded
    - _Requirements: 3.1, 3.2_

  - [x] 7.3 Implement save workflow
    - Validate form on submit
    - Call validateTrade() then saveTrade()
    - Handle validation errors
    - Navigate to detail view on success
    - _Requirements: 3.3, 3.4, 3.5, 3.6_

- [x] 8. Trade Detail/Edit Feature - General Section
  - [x] 8.1 Create TradeDetailComponent shell
    - Set up component with route parameter handling
    - Load trade by ID from TradeService
    - Implement edit mode toggle
    - Add Edit, Save, Cancel buttons
    - _Requirements: 2.4, 12.1, 12.2_

  - [x] 8.2 Create GeneralSectionComponent
    - Display general trade fields (tradeId, label, transactionRoles)
    - Use Material form fields
    - Support view and edit modes
    - Implement field validation
    - _Requirements: 4.1, 7.1, 7.2_

  - [x] 8.3 Create CommonSectionComponent
    - Display common fields (book, counterparty, tradeDate, etc.)
    - Support view and edit modes
    - Implement required field validation
    - _Requirements: 4.1, 7.1, 7.2_

- [x] 9. Trade Detail/Edit Feature - Swap Details
  - [x] 9.1 Create SwapDetailsSectionComponent
    - Display swap-specific fields (underlying, settlementType, swapType)
    - Conditionally render based on trade_type
    - Support view and edit modes
    - _Requirements: 4.1, 9.2, 9.3, 9.4_

  - [x] 9.2 Create SwapLegComponent
    - Display leg details (direction, currency, rateType, notional, dates)
    - Render in tabs or accordion (one per leg)
    - Support view and edit modes
    - Integrate ScheduleGridComponent for schedule display
    - _Requirements: 4.2, 4.3_

- [x] 10. Schedule Grid Component
  - [x] 10.1 Create ScheduleGridComponent with fixed columns
    - Create grid component to display schedule summary
    - Show fixed columns: periodIndex, startDate, endDate, paymentDate, notional, rate, interest
    - Render schedule data in Material table
    - Apply date formatting to date columns
    - Apply numeric formatting to number columns
    - Implement column sorting
    - Handle click on row to open detail editor
    - Note: Each leg has its own schedule array
    - _Requirements: 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 10.2 Implement add/remove schedule controls
    - Add "Add Schedule Period" button above grid
    - Add "Delete" button/icon per row in grid
    - Create new empty schedule period on add (with default values)
    - Remove schedule period from array on delete
    - Update schedule array indices after add/remove
    - Emit changes to parent component
    - Note: No auto-generation - schedules come from API or manual creation
    - _Requirements: 13.3, 13.4_

  - [x] 10.3 Create SchedulePeriodDetailComponent
    - Create detailed editor component for individual schedule periods
    - Display all schedule period fields in organized form sections
    - Support view and edit modes
    - Implement field validation
    - Open in Material Dialog when row is clicked
    - Show all fields from SchedulePeriod interface (not just summary columns)
    - Emit changes back to parent grid component
    - Close dialog and update grid on save
    - _Requirements: 13.1, 13.2_

  - [x] 10.4 Integrate ScheduleGridComponent into SwapLegComponent
    - Replace schedule placeholder in SwapLegComponent
    - Pass leg's schedule array to ScheduleGridComponent
    - Handle schedule changes from grid
    - Update leg data when schedules are modified
    - Show/hide grid based on whether schedule exists
    - _Requirements: 4.2, 4.3_
    - _Requirements: 13.3, 13.4_

- [ ] 11. Events Section Component
  - [ ] 11.1 Create EventsSectionComponent
    - Implement expandable section using Material expansion panel
    - Display events array from POSTSAVE trades
    - Format businessDateTime as readable dates
    - Display eventCode, eventDescription, application
    - Sort events by businessDateTime descending
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

- [ ] 12. Validation Integration
  - [ ] 12.1 Implement field-level validation
    - Add validators to form controls (required, pattern, etc.)
    - Display inline error messages
    - Validate on blur for required fields
    - Validate on change for format fields
    - _Requirements: 7.1, 7.2, 14.1, 14.2, 14.4_

  - [ ] 12.2 Implement async backend validation
    - Debounce validation requests
    - Call ValidationService.validateTradeAsync()
    - Display server-side errors inline
    - Show success indicator on valid
    - _Requirements: 7.3, 7.5, 14.3_

  - [ ] 12.3 Implement form-level validation
    - Validate entire form on submit
    - Disable Save button when invalid
    - Highlight all invalid fields
    - Scroll to first error
    - _Requirements: 7.4, 14.5_

- [ ] 13. Auto-Save and Error Recovery
  - [ ] 13.1 Integrate auto-save in forms
    - Start auto-save on form value changes
    - Save to localStorage every 30 seconds
    - Stop auto-save on component destroy
    - _Requirements: 15.1_

  - [ ] 13.2 Implement auto-save restoration
    - Check for auto-saved data on component init
    - Show dialog to restore or discard
    - Load auto-saved data if user confirms
    - _Requirements: 15.3_

  - [ ] 13.3 Implement error recovery
    - Retain form data on save failure
    - Display error details to user
    - Clear auto-save on successful save
    - Add "Discard Changes" button
    - _Requirements: 15.2, 15.4, 15.5_

- [ ] 14. Edit Workflow Integration
  - [ ] 14.1 Implement edit mode toggle
    - Enable form fields when Edit clicked
    - Disable fields in view mode
    - Track dirty state with signal
    - _Requirements: 12.2, 12.3_

  - [ ] 14.2 Implement save edited trade
    - Validate before save
    - Preserve original tradeId
    - Call validate then save APIs
    - Update view with saved data
    - _Requirements: 12.4, 12.5_

- [ ] 15. Styling and Theming
  - [ ] 15.1 Configure Material theme
    - Set up custom color palette
    - Configure typography
    - Add global styles
    - _Requirements: 8.1, 8.4_

  - [ ] 15.2 Implement responsive layouts
    - Use CSS Grid or Flexbox for layouts
    - Add responsive breakpoints
    - Test on mobile and desktop viewports
    - _Requirements: 8.2, 8.3_

- [ ] 16. Final Integration and Polish
  - [ ] 16.1 Connect all routes and navigation
    - Test navigation between all views
    - Verify route guards work correctly
    - Test browser back/forward buttons
    - _Requirements: 2.2, 2.3, 2.4_

  - [ ] 16.2 End-to-end workflow testing
    - Test complete create workflow (NEW → fill → validate → save)
    - Test complete edit workflow (load → edit → save)
    - Test filter and search in list view
    - Test schedule editing
    - Test auto-save and restoration
    - Test error handling scenarios
    - _Requirements: All_

  - [ ] 16.3 Performance optimization
    - Verify lazy loading works
    - Check bundle sizes
    - Test with large trade lists
    - Test with large schedules
    - _Requirements: 2.5, 6.2, 6.3_

  - [ ] 16.4 Documentation
    - Update README with setup instructions
    - Document API configuration
    - Document component architecture
    - Add inline code comments
    - _Requirements: All_

## Notes

- All tasks build incrementally on previous work
- Testing infrastructure is set up but no tests are implemented
- Stub services (Preferences, Realtime) provide interfaces only
- Focus on core functionality first, polish later
- Each task should result in working, integrated code
- Auto-save and validation are critical for user experience
- Dynamic column generation is key for schedule flexibility
