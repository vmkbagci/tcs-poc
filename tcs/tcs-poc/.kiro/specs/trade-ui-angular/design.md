# Design Document: Trade Management UI

## Overview

The Trade Management UI is a modern Angular 18+ single-page application (SPA) that provides a comprehensive interface for creating, viewing, editing, and managing financial trades. The application will be built using standalone components, Angular Signals for state management, and Angular Material for UI components.

The UI will be located in the `tcs-ui/` directory at the project root, alongside the existing `tcs-api/` backend service.

### Technology Stack

- **Framework**: Angular 18+ (latest stable)
- **UI Library**: Angular Material 18+
- **State Management**: Angular Signals
- **HTTP Client**: Angular HttpClient with RxJS
- **Routing**: Angular Router with functional guards
- **Forms**: Reactive Forms with Signal integration
- **Build Tool**: Angular CLI with esbuild
- **Package Manager**: npm or pnpm

## Architecture

### High-Level Architecture


```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Angular App)                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Presentation Layer                        │ │
│  │  - Components (Smart & Presentational)                 │ │
│  │  - Angular Material UI                                 │ │
│  │  - Reactive Forms                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              State Management Layer                    │ │
│  │  - Signals (component state)                           │ │
│  │  - Computed Signals (derived state)                    │ │
│  │  - Effects (side effects)                              │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Service Layer                             │ │
│  │  - TradeService (API calls)                            │ │
│  │  - ValidationService                                   │ │
│  │  - AutoSaveService                                     │ │
│  │  - PreferencesService (stub)                           │ │
│  │  - RealtimeService (stub)                              │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              HTTP Layer                                │ │
│  │  - HttpClient                                          │ │
│  │  - Interceptors (error handling, loading)              │ │
│  │  - Request caching                                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Trade API (FastAPI)                        │
│                   http://localhost:5000                      │
│  - GET  /api/v1/trades/new                                  │
│  - POST /api/v1/trades/save                                 │
│  - POST /api/v1/trades/validate                             │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure


```
tcs-ui/
├── src/
│   ├── app/
│   │   ├── core/                          # Core services and utilities
│   │   │   ├── services/
│   │   │   │   ├── trade.service.ts       # Main API service
│   │   │   │   ├── validation.service.ts  # Validation logic
│   │   │   │   ├── auto-save.service.ts   # Auto-save functionality
│   │   │   │   ├── preferences.service.ts # User preferences (stub)
│   │   │   │   └── realtime.service.ts    # Real-time updates (stub)
│   │   │   ├── interceptors/
│   │   │   │   ├── error.interceptor.ts   # Global error handling
│   │   │   │   └── loading.interceptor.ts # Loading state management
│   │   │   ├── guards/
│   │   │   │   └── unsaved-changes.guard.ts # Prevent navigation with unsaved data
│   │   │   └── models/
│   │   │       ├── trade.model.ts         # Trade interfaces
│   │   │       ├── api-response.model.ts  # API response types
│   │   │       └── preferences.model.ts   # User preferences types
│   │   │
│   │   ├── features/                      # Feature modules
│   │   │   ├── trade-list/
│   │   │   │   ├── trade-list.component.ts
│   │   │   │   ├── trade-list.component.html
│   │   │   │   ├── trade-list.component.scss
│   │   │   │   └── components/
│   │   │   │       ├── trade-filter.component.ts
│   │   │   │       └── trade-table.component.ts
│   │   │   │
│   │   │   ├── trade-detail/
│   │   │   │   ├── trade-detail.component.ts
│   │   │   │   ├── trade-detail.component.html
│   │   │   │   ├── trade-detail.component.scss
│   │   │   │   └── components/
│   │   │   │       ├── general-section.component.ts
│   │   │   │       ├── common-section.component.ts
│   │   │   │       ├── swap-details-section.component.ts
│   │   │   │       ├── swap-leg.component.ts
│   │   │   │       ├── schedule-grid.component.ts
│   │   │   │       └── events-section.component.ts
│   │   │   │
│   │   │   └── trade-create/
│   │   │       ├── trade-create.component.ts
│   │   │       ├── trade-create.component.html
│   │   │       ├── trade-create.component.scss
│   │   │       └── components/
│   │   │           └── trade-type-selector.component.ts
│   │   │
│   │   ├── shared/                        # Shared components and utilities
│   │   │   ├── components/
│   │   │   │   ├── loading-spinner.component.ts
│   │   │   │   ├── error-message.component.ts
│   │   │   │   └── confirmation-dialog.component.ts
│   │   │   ├── directives/
│   │   │   │   └── auto-focus.directive.ts
│   │   │   └── pipes/
│   │   │       ├── date-format.pipe.ts
│   │   │       └── currency-format.pipe.ts
│   │   │
│   │   ├── app.component.ts               # Root component
│   │   ├── app.config.ts                  # App configuration
│   │   └── app.routes.ts                  # Route definitions
│   │
│   ├── assets/                            # Static assets
│   ├── environments/                      # Environment configs
│   │   ├── environment.ts
│   │   └── environment.prod.ts
│   ├── styles/                            # Global styles
│   │   ├── _variables.scss
│   │   ├── _material-theme.scss
│   │   └── styles.scss
│   ├── index.html
│   └── main.ts
│
├── angular.json
├── package.json
├── tsconfig.json
└── README.md
```

## Components and Interfaces

### Core Services


#### TradeService

Primary service for all trade-related API operations.

**Methods:**
- `getNewTrade(tradeType: string): Observable<TradeResponse>`
- `saveTrade(tradeData: Trade): Observable<TradeResponse>`
- `validateTrade(tradeData: Trade): Observable<ValidationResponse>`
- `getTrade(tradeId: string): Observable<Trade>`
- `listTrades(filters?: TradeFilters): Observable<Trade[]>`

**Signals:**
- `currentTrade = signal<Trade | null>(null)`
- `trades = signal<Trade[]>([])`
- `loading = signal<boolean>(false)`
- `error = signal<string | null>(null)`

#### ValidationService

Handles client-side and server-side validation with debouncing.

**Methods:**
- `validateField(fieldName: string, value: any): ValidationResult`
- `validateTradeAsync(trade: Trade): Observable<ValidationResponse>`
- `getFieldErrors(fieldName: string): Signal<string[]>`

**Features:**
- Debounced async validation (300ms)
- Caching of validation results
- Field-level and form-level validation

#### AutoSaveService

Manages automatic saving of form data with pluggable storage backend.

**Interface:**
```typescript
interface IAutoSaveStorage {
  save(key: string, data: Trade): Promise<void> | void;
  load(key: string): Promise<Trade | null> | Trade | null;
  clear(key: string): Promise<void> | void;
}
```

**Methods:**
- `startAutoSave(formData: Signal<Trade>): void`
- `stopAutoSave(): void`
- `getAutoSavedData(tradeId?: string): Promise<Trade | null>`
- `clearAutoSavedData(tradeId?: string): Promise<void>`
- `setStorageBackend(backend: IAutoSaveStorage): void`

**Configuration:**
- Auto-save interval: 30 seconds
- Default storage: LocalStorageBackend (browser localStorage)
- Key format: `trade-autosave-{tradeId || 'new'}`

**Storage Backends:**

**LocalStorageBackend (Default):**
```typescript
class LocalStorageBackend implements IAutoSaveStorage {
  save(key: string, data: Trade): void {
    localStorage.setItem(key, JSON.stringify(data));
  }
  
  load(key: string): Trade | null {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
  }
  
  clear(key: string): void {
    localStorage.removeItem(key);
  }
}
```

**ApiStorageBackend (Future Implementation):**
```typescript
class ApiStorageBackend implements IAutoSaveStorage {
  constructor(private http: HttpClient) {}
  
  async save(key: string, data: Trade): Promise<void> {
    // POST to /api/v1/trades/autosave with Redis cache
    await this.http.post('/api/v1/trades/autosave', { key, data }).toPromise();
  }
  
  async load(key: string): Promise<Trade | null> {
    // GET from /api/v1/trades/autosave/:key
    const response = await this.http.get<Trade>(`/api/v1/trades/autosave/${key}`).toPromise();
    return response || null;
  }
  
  async clear(key: string): Promise<void> {
    // DELETE /api/v1/trades/autosave/:key
    await this.http.delete(`/api/v1/trades/autosave/${key}`).toPromise();
  }
}
```

**Benefits:**
- Easy to switch between localStorage and API storage
- Can implement hybrid approach (localStorage + API sync)
- Future-proof for Redis cache integration
- Testable with mock storage backends

#### PreferencesService (Stub)

Interface for future user preferences implementation.

**Interface:**
```typescript
interface IPreferencesService {
  getPreference<T>(key: string): T | null;
  setPreference<T>(key: string, value: T): void;
  getTheme(): 'light' | 'dark';
  getColumnVisibility(gridId: string): Record<string, boolean>;
}
```

**Stub Implementation:**
- Returns default values
- Does not persist data
- Documented for future cookie/config integration

#### RealtimeService (Stub)

Interface for future real-time updates implementation.

**Interface:**
```typescript
interface IRealtimeService {
  subscribe(tradeId: string): Observable<TradeUpdate>;
  unsubscribe(tradeId: string): void;
  connect(): void;
  disconnect(): void;
}
```

**Stub Implementation:**
- Returns empty observables
- Does not establish connections
- Documented for future WebSocket/polling integration

## Data Models


### Trade Model

```typescript
interface Trade {
  general: GeneralSection;
  common: CommonSection;
  swapDetails?: SwapDetails;
  swapLegs?: SwapLeg[];
  commodityDetails?: CommodityDetails;
  leg?: IndexSwapLeg;
}

interface GeneralSection {
  trade_type?: string;  // 'ir-swap' | 'commodity-option' | 'index-swap'
  tradeId: string;
  label: string;
  coLocatedId?: string;
  transactionRoles: TransactionRoles;
  executionDetails: ExecutionDetails;
  packageTradeDetails: PackageTradeDetails;
  blockAllocationDetails: any;
}

interface SwapLeg {
  legIndex: number;
  direction: 'pay' | 'receive';
  currency: string;
  rateType: 'fixed' | 'floating';
  notional: number | null;
  scheduleType: string;
  interestRate?: number | null;
  ratesetRef?: string | null;
  startDate: string;
  endDate: string;
  schedule?: SchedulePeriod[];
  // ... additional fields
}

interface SchedulePeriod {
  periodIndex: number;
  startDate: string;
  endDate: string;
  paymentDate: string;
  rate?: number;
  notional: number;
  interest?: number;
  // ... additional fields (dynamic based on leg type)
}

interface TradeEvent {
  schemaVersion: string;
  eventDescription: string;
  eventCode: string;
  businessDateTime: number;
  application: string;
  correlationId: string;
}
```

### API Response Models

```typescript
interface TradeResponse {
  success: boolean;
  trade_data?: Trade;
  errors?: string[];
  warnings?: string[];
  metadata?: Record<string, any>;
}

interface ValidationResponse {
  success: boolean;
  errors: ValidationError[];
  warnings: string[];
}

interface ValidationError {
  field: string;
  message: string;
  code?: string;
}
```

## Component Design


### TradeListComponent (Smart Component)

**Purpose:** Display list of trades with filtering and search.

**Signals:**
```typescript
trades = signal<Trade[]>([]);
filteredTrades = computed(() => this.applyFilters(this.trades(), this.filters()));
filters = signal<TradeFilters>({});
loading = signal<boolean>(false);
```

**Template Structure:**
- Material toolbar with filters
- TradeFilterComponent (presentational)
- TradeTableComponent (presentational)
- Pagination controls

**Interactions:**
- Load trades on init
- Apply filters reactively
- Navigate to detail on row click

### TradeDetailComponent (Smart Component)

**Purpose:** Display and edit trade details.

**Signals:**
```typescript
trade = signal<Trade | null>(null);
editMode = signal<boolean>(false);
isDirty = signal<boolean>(false);
validationErrors = signal<ValidationError[]>([]);
```

**Template Structure:**
- Material card with tabs/accordion
- GeneralSectionComponent
- CommonSectionComponent
- SwapDetailsSectionComponent
- SwapLegComponent (repeated for each leg)
- EventsSectionComponent (expandable)
- Action buttons (Edit, Save, Cancel)

**Interactions:**
- Load trade by ID from route params
- Toggle edit mode
- Auto-save on changes
- Validate before save
- Handle unsaved changes on navigation

### TradeCreateComponent (Smart Component)

**Purpose:** Create new trade from template.

**Signals:**
```typescript
selectedTradeType = signal<string | null>(null);
trade = signal<Trade | null>(null);
loading = signal<boolean>(false);
```

**Template Structure:**
- TradeTypeSelectorComponent
- Trade form (reuses detail components)
- Action buttons (Save, Cancel)

**Interactions:**
- Select trade type
- Load NEW template from API
- Populate form
- Validate and save

### ScheduleGridComponent (Presentational Component)

**Purpose:** Display and edit schedule data in a grid.

**Inputs:**
```typescript
@Input() schedule: SchedulePeriod[] = [];
@Input() editable: boolean = false;
@Output() scheduleChange = new EventEmitter<SchedulePeriod[]>();
```

**Features:**
- Dynamic column generation from schedule data
- Inline editing (if editable)
- Add/remove rows
- Column sorting
- Date and number formatting

**Implementation:**
- Uses MatTable with dynamic columns
- Reactive forms for inline editing
- Custom cell renderers for dates/numbers

## Routing Configuration


```typescript
export const routes: Routes = [
  {
    path: '',
    redirectTo: '/trades',
    pathMatch: 'full'
  },
  {
    path: 'trades',
    loadComponent: () => import('./features/trade-list/trade-list.component')
      .then(m => m.TradeListComponent),
    title: 'Trade List'
  },
  {
    path: 'trades/new',
    loadComponent: () => import('./features/trade-create/trade-create.component')
      .then(m => m.TradeCreateComponent),
    canDeactivate: [unsavedChangesGuard],
    title: 'Create Trade'
  },
  {
    path: 'trades/:id',
    loadComponent: () => import('./features/trade-detail/trade-detail.component')
      .then(m => m.TradeDetailComponent),
    canDeactivate: [unsavedChangesGuard],
    title: 'Trade Detail'
  },
  {
    path: '**',
    redirectTo: '/trades'
  }
];
```

### Route Guards

**unsavedChangesGuard (Functional Guard):**
```typescript
export const unsavedChangesGuard: CanDeactivateFn<ComponentWithUnsavedChanges> = 
  (component) => {
    if (component.hasUnsavedChanges()) {
      return confirm('You have unsaved changes. Do you want to leave?');
    }
    return true;
  };
```

## State Management Strategy

### Signal-Based Architecture

**Component State:**
- Use `signal()` for mutable state
- Use `computed()` for derived state
- Use `effect()` for side effects

**Example Pattern:**
```typescript
export class TradeDetailComponent {
  private tradeService = inject(TradeService);
  
  // Signals
  trade = signal<Trade | null>(null);
  editMode = signal<boolean>(false);
  
  // Computed signals
  isValid = computed(() => this.validateTrade(this.trade()));
  canSave = computed(() => this.isValid() && this.editMode());
  
  // Effects
  constructor() {
    effect(() => {
      const trade = this.trade();
      if (trade && this.editMode()) {
        this.autoSaveService.startAutoSave(this.trade);
      }
    });
  }
}
```

### Form State Management

**Reactive Forms with Signals:**
```typescript
export class TradeFormComponent {
  form = new FormGroup({
    tradeId: new FormControl(''),
    book: new FormControl('', Validators.required),
    counterparty: new FormControl('', Validators.required),
    // ...
  });
  
  // Convert form value to signal
  formValue = toSignal(this.form.valueChanges, { initialValue: this.form.value });
  
  // Computed validation state
  isFormValid = computed(() => this.form.valid);
}
```

## Error Handling


### Error Interceptor

```typescript
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'An error occurred';
      
      if (error.error instanceof ErrorEvent) {
        // Client-side error
        errorMessage = `Error: ${error.error.message}`;
      } else {
        // Server-side error
        errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
      }
      
      // Show error notification
      inject(MatSnackBar).open(errorMessage, 'Close', { duration: 5000 });
      
      return throwError(() => error);
    })
  );
};
```

### Loading Interceptor

```typescript
export const loadingInterceptor: HttpInterceptorFn = (req, next) => {
  const loadingService = inject(LoadingService);
  
  loadingService.show();
  
  return next(req).pipe(
    finalize(() => loadingService.hide())
  );
};
```

## Testing Strategy

### Testing Infrastructure Setup

**Unit Testing:**
- Framework: Jest (preferred) or Jasmine
- Test runner: Angular CLI
- Coverage: Istanbul

**E2E Testing:**
- Framework: Cypress (preferred) or Playwright
- Test scenarios: Critical user flows

**Configuration Files:**
- `jest.config.js` or `karma.conf.js`
- `cypress.config.ts` or `playwright.config.ts`
- `.spec.ts` files for each component (empty templates)

**Example Test Structure (Not Implemented):**
```typescript
// trade-detail.component.spec.ts
describe('TradeDetailComponent', () => {
  // Test setup only, no actual tests
  beforeEach(() => {
    // TestBed configuration
  });
  
  it('should create', () => {
    // Placeholder test
  });
});
```

## Correctness Properties


*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: API Call with Correct Trade Type Parameter

*For any* trade type selection, when a user selects that trade type, the UI should call GET /api/v1/trades/new with the trade_type parameter matching the selected value.

**Validates: Requirements 3.1**

### Property 2: Form Displays All Editable Fields from Template

*For any* NEW_Trade response received from the API, the UI should render form fields for all editable properties in the trade data structure.

**Validates: Requirements 3.2**

### Property 3: Validation Before Save Workflow

*For any* save operation (create or edit), the UI should call POST /api/v1/trades/validate before calling POST /api/v1/trades/save, and only proceed with save if validation succeeds.

**Validates: Requirements 3.4, 3.5, 12.4**

### Property 4: Navigation After Successful Save

*For any* successful save operation, the UI should navigate to the trade detail view and display the POSTSAVE_Trade data returned from the API.

**Validates: Requirements 3.6**

### Property 5: Separate Panel for Each Swap Leg

*For any* trade with swap legs, the UI should render each leg in a separate tab or panel, with the number of panels matching the number of legs.

**Validates: Requirements 4.2**

### Property 6: Grid Display for Schedules

*For any* swap leg containing a schedule array, the UI should render a data grid displaying the schedule data.

**Validates: Requirements 4.3**

### Property 7: Dynamic Column Generation from Schedule Structure

*For any* schedule array, the UI should generate grid columns dynamically by extracting property names from the schedule objects, ensuring all properties are represented as columns.

**Validates: Requirements 4.4, 5.1, 5.2**

### Property 8: Required Field Highlighting

*For any* required field that is empty or invalid, the UI should apply visual highlighting to indicate the validation state.

**Validates: Requirements 4.5**

### Property 9: Date Formatting in Grids

*For any* date value in a schedule grid column, the UI should format it as a human-readable date string.

**Validates: Requirements 5.3**

### Property 10: Numeric Formatting with Precision

*For any* numeric value in a schedule grid column, the UI should format it with appropriate decimal precision based on the field type.

**Validates: Requirements 5.4**

### Property 11: Column Sorting Functionality

*For any* grid column, the UI should support sorting the grid rows by that column's values in ascending or descending order.

**Validates: Requirements 5.5**

### Property 12: Template Request Caching

*For any* repeated request for the same trade type template (GET /new with same trade_type), the UI should return the cached response without making additional network calls.

**Validates: Requirements 6.2**

### Property 13: Validation Request Debouncing

*For any* rapid sequence of form input changes within a short time window, the UI should debounce validation requests to ensure only one validation call is made after input stabilizes.

**Validates: Requirements 6.3, 14.3**

### Property 14: Loading Indicator During API Calls

*For any* API request in progress, the UI should display a loading indicator until the request completes or fails.

**Validates: Requirements 6.4**

### Property 15: User-Friendly Error Messages

*For any* API error response, the UI should display a user-friendly error message derived from the error details.

**Validates: Requirements 6.5**

### Property 16: Required Field Validation on Blur

*For any* required field, when the user leaves the field (blur event), the UI should validate the field and display an error if it is empty.

**Validates: Requirements 7.1, 14.1**

### Property 17: Format Validation on Change

*For any* field with format requirements, when the user modifies the field value, the UI should validate the format and display requirements if invalid.

**Validates: Requirements 7.2, 14.2**

### Property 18: Success Indicator After Validation

*For any* successful validation operation, the UI should display a success indicator to confirm the validation passed.

**Validates: Requirements 7.3**

### Property 19: Save Button Disabled When Invalid

*For any* form state where validation fails, the UI should disable the Save button to prevent invalid submissions.

**Validates: Requirements 7.4**

### Property 20: Server-Side Error Display

*For any* API validation failure response, the UI should extract and display the server-side error messages to the user.

**Validates: Requirements 7.5**

### Property 21: Trade Type Conditional Field Display

*For any* trade with a trade_type field, the UI should show or hide fields based on the trade type, displaying only fields relevant to that specific trade type.

**Validates: Requirements 9.2, 9.3, 9.4**

### Property 22: Filter Application Updates List

*For any* filter values applied by the user, the UI should update the displayed trade list to show only trades matching the filter criteria.

**Validates: Requirements 11.3**

### Property 23: Trade Click Navigation

*For any* trade in the list, when the user clicks on it, the UI should navigate to the trade detail view with the correct trade ID in the route.

**Validates: Requirements 11.4**

### Property 24: Pagination Support

*For any* trade list exceeding the page size, the UI should provide pagination controls and display only the current page of results.

**Validates: Requirements 11.5**

### Property 25: Edit Button for POSTSAVE Trades

*For any* POSTSAVE_Trade displayed in detail view, the UI should render an Edit button that enables form fields when clicked.

**Validates: Requirements 12.1, 12.2**

### Property 26: Real-Time Validation During Editing

*For any* field modification during edit mode, the UI should trigger validation and display results in real-time.

**Validates: Requirements 12.3**

### Property 27: Trade ID Preservation on Edit

*For any* edited trade that is saved, the UI should preserve the original tradeId in the saved data.

**Validates: Requirements 12.5**

### Property 28: Inline Schedule Editing

*For any* schedule grid in edit mode, the UI should allow inline editing of cell values with validation.

**Validates: Requirements 13.1, 13.2**

### Property 29: Schedule Array Updates

*For any* add or remove operation on schedule rows, the UI should update the underlying schedule array to reflect the changes.

**Validates: Requirements 13.3**

### Property 30: Dependent Field Recalculation

*For any* schedule data change, the UI should recalculate dependent fields that rely on schedule values.

**Validates: Requirements 13.4**

### Property 31: Modified Row Highlighting

*For any* schedule row that has been modified, the UI should apply visual highlighting to indicate the change.

**Validates: Requirements 13.5**

### Property 32: Inline Validation Error Display

*For any* validation error, the UI should display the error message inline near the relevant field immediately.

**Validates: Requirements 14.4**

### Property 33: Full Validation on Submit

*For any* form submission attempt, the UI should perform complete validation of all fields before allowing the save operation.

**Validates: Requirements 14.5**

### Property 34: Periodic Auto-Save

*For any* form with unsaved modifications, the UI should automatically save the form data to browser storage every 30 seconds.

**Validates: Requirements 15.1**

### Property 35: Data Retention on Save Failure

*For any* failed save operation, the UI should retain all form data and display the error details without losing user input.

**Validates: Requirements 15.2**

### Property 36: Auto-Save Restoration Offer

*For any* user returning to a trade with auto-saved data, the UI should prompt the user to restore the auto-saved version.

**Validates: Requirements 15.3**

### Property 37: Auto-Save Cleanup After Success

*For any* successful save operation, the UI should clear the corresponding auto-saved data from browser storage.

**Validates: Requirements 15.4**

### Property 38: Manual Discard Changes

*For any* form with auto-saved data, the UI should provide a "Discard Changes" option that clears the auto-saved data when invoked.

**Validates: Requirements 15.5**

### Property 39: Expandable Events Section

*For any* POSTSAVE_Trade, the UI should render an expandable Events section that displays all events when expanded.

**Validates: Requirements 16.1, 16.2**

### Property 40: Event Timestamp Formatting

*For any* event in the events array, the UI should format the businessDateTime as a readable date string.

**Validates: Requirements 16.3**

### Property 41: Event Detail Display

*For any* event, the UI should display the eventCode, eventDescription, and application fields.

**Validates: Requirements 16.4**

### Property 42: Event Sorting by Date

*For any* events array, the UI should sort and display events by businessDateTime in descending order (newest first).

**Validates: Requirements 16.5**

## Error Handling


### Error Recovery Strategy

**Auto-Save Mechanism:**
- Trigger: Form value changes
- Frequency: Every 30 seconds
- Storage: localStorage with key `trade-autosave-{tradeId || 'new'}`
- Restoration: Prompt user on component init if auto-saved data exists

**API Error Handling:**
- Network errors: Display "Connection failed" message with retry option
- Validation errors: Display field-specific errors inline
- Server errors: Display error message with error code
- Timeout errors: Display "Request timed out" with retry option

**Form State Preservation:**
- On error: Keep form data intact
- On navigation: Warn if unsaved changes exist
- On browser close: Auto-saved data persists

## Testing Strategy

### Unit Testing Approach

**Framework:** Jest (preferred) or Jasmine with Karma

**Test Coverage:**
- Components: Test signal state, computed values, user interactions
- Services: Test API calls, caching, error handling
- Pipes: Test formatting logic
- Guards: Test navigation prevention logic

**Test Structure:**
```typescript
describe('ComponentName', () => {
  let component: ComponentName;
  let fixture: ComponentFixture<ComponentName>;
  
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ComponentName, ...dependencies]
    }).compileComponents();
    
    fixture = TestBed.createComponent(ComponentName);
    component = fixture.componentInstance;
  });
  
  // Tests will be added when explicitly requested
});
```

### E2E Testing Approach

**Framework:** Cypress (preferred) or Playwright

**Test Scenarios:**
- Trade creation workflow (NEW → fill form → validate → save)
- Trade editing workflow (load → edit → save)
- Trade list filtering and navigation
- Schedule grid editing
- Error handling and recovery

**Test Structure:**
```typescript
describe('Trade Management', () => {
  beforeEach(() => {
    cy.visit('/trades');
  });
  
  // Tests will be added when explicitly requested
});
```

### Property-Based Testing

**Note:** Property-based testing is more applicable to backend logic. For the UI, we focus on:
- Example-based tests for specific user flows
- Integration tests for API interactions
- Visual regression tests for UI consistency

**Testing Infrastructure Only:**
- Configuration files will be created
- Example test files will be scaffolded
- No actual test implementations until requested

## Performance Considerations

### Optimization Strategies

**Signal-Based Change Detection:**
- Use `OnPush` change detection strategy
- Leverage computed signals to minimize recalculations
- Use `effect()` sparingly for side effects only

**Lazy Loading:**
- Feature routes loaded on demand
- Reduces initial bundle size
- Improves first contentful paint

**Request Optimization:**
- Cache GET /new templates
- Debounce validation requests (300ms)
- Cancel in-flight requests on component destroy

**Virtual Scrolling:**
- For large trade lists (>100 items)
- For large schedule grids (>50 rows)
- Use CDK Virtual Scroll

### Bundle Size Targets

- Initial bundle: < 500KB (gzipped)
- Lazy-loaded routes: < 200KB each (gzipped)
- Total app: < 2MB (gzipped)

## Deployment Considerations

### Build Configuration

**Production Build:**
```bash
ng build --configuration production
```

**Build Optimizations:**
- Ahead-of-Time (AOT) compilation
- Tree shaking
- Minification
- Source maps (optional for debugging)

### Environment Configuration

**Development:**
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000/api/v1'
};
```

**Production:**
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.example.com/api/v1'
};
```

### Hosting Options

- Static hosting (Nginx, Apache)
- CDN (CloudFront, Cloudflare)
- Container (Docker with Nginx)
- Cloud platforms (Vercel, Netlify, AWS S3 + CloudFront)

## Security Considerations

### XSS Prevention

- Angular's built-in sanitization
- Avoid `innerHTML` with user data
- Use `DomSanitizer` when necessary

### CORS Configuration

- API must allow requests from UI origin
- Credentials handling if needed
- Preflight request support

### Content Security Policy

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self'; 
               style-src 'self' 'unsafe-inline'; 
               connect-src 'self' http://localhost:5000">
```

## Future Enhancements

### Planned Hooks (Not Implemented)

**Real-Time Updates:**
- WebSocket connection service
- Trade update notifications
- Live data synchronization

**User Preferences:**
- Cookie-based persistence
- Theme selection (light/dark)
- Column visibility preferences
- Default filter values

**Auto-Save API Backend:**
- Server-side auto-save storage (Redis cache)
- Cross-device auto-save synchronization
- Auto-save conflict resolution
- API endpoints:
  - `POST /api/v1/trades/autosave` - Save draft
  - `GET /api/v1/trades/autosave/:key` - Load draft
  - `DELETE /api/v1/trades/autosave/:key` - Clear draft
- Implementation: Switch AutoSaveService to use ApiStorageBackend

**Authentication:**
- Login/logout functionality
- JWT token management
- Role-based access control
- Session timeout handling

**Advanced Features:**
- Trade comparison view
- Bulk operations
- Export to Excel/CSV
- Import from files
- Audit trail visualization
- Advanced search with query builder

## Conclusion

This design provides a comprehensive blueprint for a modern Angular 18+ trade management UI. The architecture leverages the latest Angular features (signals, standalone components, functional guards) while maintaining clean separation of concerns and extensibility for future enhancements.

The application is structured to be:
- **Performant**: Signal-based reactivity, lazy loading, request optimization
- **Maintainable**: Clear component hierarchy, service layer abstraction
- **Testable**: Comprehensive testing infrastructure (setup only)
- **Extensible**: Hooks for real-time updates and user preferences
- **User-Friendly**: Auto-save, validation feedback, error recovery

Implementation will follow the tasks defined in the tasks.md document, building incrementally from core infrastructure to feature completion.
