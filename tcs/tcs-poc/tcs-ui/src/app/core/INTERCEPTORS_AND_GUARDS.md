# HTTP Interceptors and Guards Implementation

This document describes the HTTP interceptors and route guards implemented for the Trade Management UI.

## Overview

Three key pieces of infrastructure have been implemented:
1. **Error Interceptor** - Global HTTP error handling with user-friendly messages
2. **Loading Interceptor** - Automatic loading state management for HTTP requests
3. **Unsaved Changes Guard** - Prevents navigation when forms have unsaved data

## 1. Error Interceptor

### Location
`src/app/core/interceptors/error.interceptor.ts`

### Purpose
Catches all HTTP errors globally and displays user-friendly error messages via Material Snackbar.

### Features
- Maps HTTP status codes to readable messages
- Handles client-side and server-side errors
- Displays errors in a Material Snackbar (5-second duration)
- Supports custom error messages from API responses
- Re-throws errors for component-level handling if needed

### Error Message Mapping
- **0**: Connection failed (network error)
- **400**: Invalid request
- **401**: Unauthorized
- **403**: Access denied
- **404**: Resource not found
- **408**: Request timeout
- **409**: Conflict
- **422**: Validation failed
- **429**: Too many requests
- **500**: Server error
- **502**: Bad gateway
- **503**: Service unavailable
- **504**: Gateway timeout

### Usage
The interceptor is automatically applied to all HTTP requests once registered in `app.config.ts`.

## 2. Loading Interceptor

### Location
- Interceptor: `src/app/core/interceptors/loading.interceptor.ts`
- Service: `src/app/core/services/loading.service.ts`

### Purpose
Automatically manages loading state for all HTTP requests using Angular Signals.

### Features
- Signal-based reactive state management
- Tracks multiple concurrent requests
- Shows loading indicator when any request is active
- Hides loading indicator when all requests complete
- Provides `reset()` method for error recovery

### LoadingService API
```typescript
class LoadingService {
  // Public signal for loading state
  loading: Signal<boolean>;
  
  // Show loading indicator (called by interceptor)
  show(): void;
  
  // Hide loading indicator (called by interceptor)
  hide(): void;
  
  // Reset loading state
  reset(): void;
}
```

### Usage in Components
```typescript
import { LoadingService } from '@core/services';

export class MyComponent {
  private loadingService = inject(LoadingService);
  
  // Access loading state
  isLoading = this.loadingService.loading;
}
```

### Usage in Templates
```html
@if (loadingService.loading()) {
  <mat-spinner></mat-spinner>
}
```

## 3. Unsaved Changes Guard

### Location
`src/app/core/guards/unsaved-changes.guard.ts`

### Purpose
Prevents users from accidentally navigating away from forms with unsaved changes.

### Features
- Two implementations provided:
  1. **unsavedChangesGuard** - Uses native browser confirm dialog (simple)
  2. **unsavedChangesDialogGuard** - Uses Material Dialog (better UX)
- Components must implement `ComponentWithUnsavedChanges` interface
- Customizable dialog messages

### Component Interface
```typescript
interface ComponentWithUnsavedChanges {
  hasUnsavedChanges(): boolean;
}
```

### Usage in Routes
```typescript
// In app.routes.ts
import { unsavedChangesGuard } from '@core/guards';

export const routes: Routes = [
  {
    path: 'trades/new',
    component: TradeCreateComponent,
    canDeactivate: [unsavedChangesGuard]
  }
];
```

### Usage in Components
```typescript
import { ComponentWithUnsavedChanges } from '@core/guards';

export class TradeCreateComponent implements ComponentWithUnsavedChanges {
  private isDirty = signal<boolean>(false);
  
  hasUnsavedChanges(): boolean {
    return this.isDirty();
  }
}
```

### Using Material Dialog Version
```typescript
// In app.routes.ts
import { unsavedChangesDialogGuard } from '@core/guards';

export const routes: Routes = [
  {
    path: 'trades/new',
    component: TradeCreateComponent,
    canDeactivate: [unsavedChangesDialogGuard]
  }
];
```

## Registration in App Config

To activate these interceptors, update `src/app/app.config.ts`:

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { routes } from './app.routes';
import { errorInterceptor, loadingInterceptor } from '@core/interceptors';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(
      withInterceptors([
        loadingInterceptor,  // Applied first
        errorInterceptor     // Applied second
      ])
    ),
    provideAnimations()  // Required for Material components
  ]
};
```

## Testing

### Testing Error Interceptor
```typescript
describe('errorInterceptor', () => {
  it('should display error message in snackbar', () => {
    // Test implementation
  });
  
  it('should map 404 to "Resource not found"', () => {
    // Test implementation
  });
});
```

### Testing Loading Interceptor
```typescript
describe('loadingInterceptor', () => {
  it('should show loading on request start', () => {
    // Test implementation
  });
  
  it('should hide loading on request complete', () => {
    // Test implementation
  });
});
```

### Testing Unsaved Changes Guard
```typescript
describe('unsavedChangesGuard', () => {
  it('should allow navigation when no unsaved changes', () => {
    // Test implementation
  });
  
  it('should show confirmation when unsaved changes exist', () => {
    // Test implementation
  });
});
```

## Requirements Validation

### Requirement 6.4 (Loading Indicators)
✅ Implemented via `loadingInterceptor` and `LoadingService`
- Shows loading indicators during API calls
- Signal-based reactive state
- Handles multiple concurrent requests

### Requirement 6.5 (Error Handling)
✅ Implemented via `errorInterceptor`
- Handles API errors gracefully
- Displays user-friendly messages
- Maps status codes to readable text

### Requirement 2.1 (Navigation Guards)
✅ Implemented via `unsavedChangesGuard`
- Implements functional route guard using CanDeactivateFn
- Prevents navigation with unsaved data

### Requirement 15.2 (Error Recovery)
✅ Supported via `unsavedChangesGuard`
- Retains form data on navigation attempt
- Allows user to stay and save changes

## Next Steps

1. **Register interceptors** in `app.config.ts` (see example above)
2. **Apply guards** to routes in `app.routes.ts`
3. **Create loading spinner component** to display loading state
4. **Implement ComponentWithUnsavedChanges** in form components
5. **Add custom styling** for error snackbar (optional)

## Notes

- The error interceptor re-throws errors after displaying them, allowing components to handle errors if needed
- The loading service tracks concurrent requests using a counter
- The unsaved changes guard provides both simple (confirm) and advanced (dialog) implementations
- All implementations use modern Angular features (signals, functional guards, functional interceptors)
