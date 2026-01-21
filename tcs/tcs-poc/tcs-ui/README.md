# Trade Management UI (TCS-UI)

A modern Angular 18+ application for managing financial trades (Interest Rate Swaps, Commodity Options, Index Swaps).

## Technology Stack

- **Framework**: Angular 21 (latest stable)
- **UI Library**: Angular Material 21
- **State Management**: Angular Signals
- **HTTP Client**: Angular HttpClient with RxJS
- **Routing**: Angular Router with functional guards
- **Forms**: Reactive Forms with Signal integration
- **Build Tool**: Angular CLI with esbuild
- **Package Manager**: npm

## Project Structure

```
tcs-ui/
├── src/
│   ├── app/
│   │   ├── core/              # Core services, guards, interceptors, models
│   │   ├── features/          # Feature modules (trade-list, trade-detail, trade-create)
│   │   ├── shared/            # Shared components, directives, pipes
│   │   ├── app.ts             # Root component
│   │   ├── app.config.ts      # App configuration
│   │   └── app.routes.ts      # Route definitions
│   ├── environments/          # Environment configurations
│   ├── styles/                # Global styles and Material theme
│   └── main.ts
├── cypress/                   # E2E tests
├── angular.json
├── jest.config.js             # Jest configuration
├── cypress.config.ts          # Cypress configuration
└── package.json
```

## Prerequisites

- Node.js 18+ and npm
- Angular CLI 21+

## Installation

```bash
npm install
```

## Development

### Start Development Server

```bash
npm start
```

Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

### Build

```bash
npm run build
```

Build artifacts will be stored in the `dist/` directory.

### Production Build

```bash
npm run build:prod
```

## Testing

### Unit Tests (Jest)

```bash
# Run tests once
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### E2E Tests (Cypress)

```bash
# Open Cypress Test Runner
npm run e2e

# Run Cypress tests headlessly
npm run e2e:headless
```

## API Configuration

The application connects to the Trade API backend. Configure the API endpoint in:

- Development: `src/environments/environment.ts`
- Production: `src/environments/environment.prod.ts`

Default API endpoint: `http://localhost:5000/api/v1`

## Features

- Create new trades from templates (ir-swap, commodity-option, index-swap)
- View and edit existing trades
- Dynamic schedule grid with inline editing
- Real-time validation with backend integration
- Auto-save functionality for error recovery
- Responsive design with Angular Material
- Trade list with filtering and search

## Architecture

The application follows a modern Angular architecture:

- **Standalone Components**: No NgModules, using standalone components
- **Signal-Based State**: Angular Signals for reactive state management
- **Functional Guards**: Using CanActivateFn and CanDeactivateFn
- **HTTP Interceptors**: Error handling and loading state management
- **Lazy Loading**: Feature routes are lazy-loaded for performance

## Development Guidelines

- Use Angular Signals for component state
- Use computed() for derived state
- Use effect() for side effects
- Follow the project structure conventions
- Write tests for new features (when explicitly requested)
- Use Angular Material components for UI consistency

## License

Private - Internal Use Only
