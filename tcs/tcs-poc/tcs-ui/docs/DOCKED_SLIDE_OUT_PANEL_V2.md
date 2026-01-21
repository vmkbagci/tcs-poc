# Docked Slide-Out Panel - Complete Implementation Guide

## Overview

A complete Angular 18+ implementation of docked slide-out panels with persistent vertical title strips. Supports multiple independent panels on the same view.

**This is NOT:**
- A hamburger menu
- A full-height sidenav
- A modal dialog
- An accordion (panels are independent)

## Key Features

✅ **Persistent Vertical Title Strip** - Always visible when collapsed  
✅ **Multiple Panels** - Support for multiple panels on same view  
✅ **Independent Operation** - Each panel collapses/expands independently  
✅ **Configurable Size** - Width and height as viewport ratios  
✅ **Smooth Animations** - Horizontal slide with CSS transitions  
✅ **Controlled/Uncontrolled** - Flexible state management  
✅ **Accessibility** - ARIA labels and keyboard support  

## Architecture

### Components

1. **DockedSlideOutPanelComponent** - Individual panel
2. **DockedPanelHostComponent** - Coordinates multiple panels
3. **DockedPanelDemoComponent** - Demo showing all features

### File Structure

```
tcs-ui/src/app/shared/components/
├── docked-slide-out-panel.component.ts  # Core panel component
├── docked-panel-host.component.ts       # Multi-panel coordinator
├── docked-panel-demo.component.ts       # Demo component
└── index.ts                             # Barrel export
```

## Component API

### DockedSlideOutPanelComponent

#### Inputs

| Input | Type | Default | Required | Description |
|-------|------|---------|----------|-------------|
| `id` | `string` | - | ✅ | Unique identifier for panel |
| `title` | `string` | - | ✅ | Title displayed on vertical strip |
| `side` | `'left' \| 'right'` | `'right'` | ❌ | Which viewport edge to dock to |
| `widthRatio` | `number` | `0.5` | ❌ | Width as ratio of viewport (0.0-1.0) |
| `heightRatio` | `number` | `0.5` | ❌ | Height as ratio of viewport (0.0-1.0) |
| `collapsed` | `boolean` | `undefined` | ❌ | Controlled state (if provided) |
| `toggleOnTitleClick` | `boolean` | `true` | ❌ | Whether clicking title strip toggles panel |
| `zIndex` | `number` | `1000` | ❌ | Z-index for stacking |
| `animationDuration` | `number` | `300` | ❌ | Animation duration (ms) |
| `animationEasing` | `string` | `'cubic-bezier(0.4, 0.0, 0.2, 1)'` | ❌ | CSS easing function |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `collapsedChange` | `EventEmitter<boolean>` | Emitted when collapsed state changes |
| `opened` | `EventEmitter<void>` | Emitted when panel opens |
| `closed` | `EventEmitter<void>` | Emitted when panel closes |

#### Public Methods

| Method | Description |
|--------|-------------|
| `toggle()` | Toggle between collapsed and expanded |
| `expand()` | Expand the panel |
| `collapse()` | Collapse the panel |

## Usage Examples

### Example 1: Basic Single Panel

```typescript
import { Component } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';

@Component({
  selector: 'app-my-page',
  standalone: true,
  imports: [DockedSlideOutPanelComponent],
  template: `
    <div class="page-content">
      <h1>My Page</h1>
      <p>Main content here...</p>
    </div>

    <app-docked-slide-out-panel
      id="settings"
      title="Settings"
      [side]="'right'"
      [widthRatio]="0.4"
      [heightRatio]="0.6">
      
      <div panel-content style="padding: 20px;">
        <h2>Settings</h2>
        <p>Your settings content here</p>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class MyPageComponent {}
```

### Example 2: Multiple Panels with Host

```typescript
import { Component, signal } from '@angular/core';
import { 
  DockedSlideOutPanelComponent,
  DockedPanelHostComponent 
} from '@shared/components';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    DockedSlideOutPanelComponent,
    DockedPanelHostComponent
  ],
  template: `
    <div class="dashboard">
      <h1>Dashboard</h1>
    </div>

    <app-docked-panel-host>
      <!-- Left Panel: Navigation -->
      <app-docked-slide-out-panel
        id="nav"
        title="Navigation"
        [side]="'left'"
        [widthRatio]="0.3"
        [heightRatio]="0.6">
        <div panel-content>
          <nav>Navigation links...</nav>
        </div>
      </app-docked-slide-out-panel>

      <!-- Right Panel 1: Settings -->
      <app-docked-slide-out-panel
        id="settings"
        title="Settings"
        [side]="'right'"
        [widthRatio]="0.35"
        [heightRatio]="0.5"
        [zIndex]="1001">
        <div panel-content>
          <div>Settings...</div>
        </div>
      </app-docked-slide-out-panel>

      <!-- Right Panel 2: Details -->
      <app-docked-slide-out-panel
        id="details"
        title="Details"
        [side]="'right'"
        [widthRatio]="0.5"
        [heightRatio]="0.8"
        [zIndex]="1002">
        <div panel-content>
          <div>Details...</div>
        </div>
      </app-docked-slide-out-panel>
    </app-docked-panel-host>
  `
})
export class DashboardComponent {}
```

### Example 3: Controlled Mode with State Management

```typescript
import { Component, signal } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-controlled-panel',
  standalone: true,
  imports: [DockedSlideOutPanelComponent, MatButtonModule],
  template: `
    <button mat-raised-button (click)="togglePanel()">
      {{ panelCollapsed() ? 'Open' : 'Close' }} Panel
    </button>

    <app-docked-slide-out-panel
      id="controlled"
      title="Controlled Panel"
      [collapsed]="panelCollapsed()"
      (collapsedChange)="panelCollapsed.set($event)"
      (opened)="onPanelOpened()"
      (closed)="onPanelClosed()">
      
      <div panel-content>
        <p>This panel's state is controlled by the parent</p>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class ControlledPanelComponent {
  panelCollapsed = signal<boolean>(true);

  togglePanel(): void {
    this.panelCollapsed.update(collapsed => !collapsed);
  }

  onPanelOpened(): void {
    console.log('Panel opened!');
  }

  onPanelClosed(): void {
    console.log('Panel closed!');
  }
}
```

### Example 4: Programmatic Control

```typescript
import { Component, ViewChild } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-programmatic',
  standalone: true,
  imports: [DockedSlideOutPanelComponent, MatButtonModule],
  template: `
    <div class="controls">
      <button mat-raised-button (click)="panel.expand()">Open</button>
      <button mat-raised-button (click)="panel.collapse()">Close</button>
      <button mat-raised-button (click)="panel.toggle()">Toggle</button>
    </div>

    <app-docked-slide-out-panel
      #panel
      id="programmatic"
      title="Programmatic Panel">
      <div panel-content>
        <p>Controlled via ViewChild reference</p>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class ProgrammaticComponent {
  @ViewChild('panel') panel!: DockedSlideOutPanelComponent;
}
```

## Visual Design

### Collapsed State

```
┌─────────────────────────────────────────┐
│                                         │
│         Main Page Content               │
│                                         │
│                                         │
└─────────────────────────────────────────┘
                                    ┌─┬─┐
                                    │V│◄│ ← Title strip + arrow
                                    │a│ │
                                    │l│ │
                                    │i│ │
                                    │d│ │
                                    │a│ │
                                    │t│ │
                                    │i│ │
                                    │o│ │
                                    │n│ │
                                    └─┴─┘
```

### Expanded State

```
┌─────────────────────────────────────────┐
│                                         │
│         Main Page Content               │
│                                         │
│                                         │
└─────────────────────────────────────────┘
                    ┌───────────────┬─┬─┐
                    │               │V│►│ ← Arrow now points out
                    │  Panel        │a│ │
                    │  Content      │l│ │
                    │               │i│ │
                    │               │d│ │
                    │               │a│ │
                    │               │t│ │
                    │               │i│ │
                    │               │o│ │
                    │               │n│ │
                    └───────────────┴─┴─┘
```

## Implementation Details

### Positioning Strategy

Panels are positioned using:
- `position: fixed` - Anchored to viewport
- `top: 50%` + `transform: translateY(-50%)` - Vertically centered
- `left: 0` or `right: 0` - Docked to edge
- `transform: translate(±100%, -50%)` - Slide animation

### Arrow Orientation Logic

```typescript
// Collapsed state:
// - Left panel: chevron_right (points inward to expand)
// - Right panel: chevron_left (points inward to expand)

// Expanded state:
// - Left panel: chevron_left (points outward to collapse)
// - Right panel: chevron_right (points outward to collapse)

arrowIcon = computed(() => {
  const collapsed = this.isCollapsed();
  if (this.side === 'left') {
    return collapsed ? 'chevron_right' : 'chevron_left';
  } else {
    return collapsed ? 'chevron_left' : 'chevron_right';
  }
});
```

### Size Ratio Application

```typescript
// Width and height are calculated as viewport percentages
panelWidth = computed(() => `${this.widthRatio * 100}vw`);
panelHeight = computed(() => `${this.heightRatio * 100}vh`);

// Example: widthRatio=0.5 → width: 50vw
// Example: heightRatio=0.8 → height: 80vh
```

### Vertical Title Strip

```css
.docked-panel__title-strip {
  writing-mode: vertical-rl;      /* Vertical text, right-to-left */
  text-orientation: mixed;         /* Mixed orientation for characters */
  padding: 16px 8px;
  background-color: #1976d2;
  color: white;
  font-weight: 500;
  min-height: 120px;
}
```

### Multiple Panel Stacking

**Current Strategy:** Z-index based stacking
- Each panel gets incremented z-index
- Later panels appear on top when expanded
- Collapsed strips may overlap (limitation)

**Future Enhancement:** Vertical strip stacking
- Calculate total height needed for all strips
- Distribute strips vertically with spacing
- Apply custom top offset to each panel

## State Management

### Controlled Mode

Parent manages state:

```typescript
// Parent component
panelCollapsed = signal<boolean>(true);

// Template
<app-docked-slide-out-panel
  [collapsed]="panelCollapsed()"
  (collapsedChange)="panelCollapsed.set($event)">
</app-docked-slide-out-panel>
```

### Uncontrolled Mode

Component manages its own state:

```typescript
// No collapsed input provided
<app-docked-slide-out-panel
  id="panel"
  title="My Panel">
</app-docked-slide-out-panel>

// Component starts collapsed by default
// Use ViewChild to control programmatically
```

## Accessibility

### ARIA Attributes

- `aria-label`: Describes toggle button action
- `aria-expanded`: Indicates current panel state
- `role="button"`: Applied to title strip when clickable
- `tabindex="0"`: Makes title strip keyboard accessible

### Keyboard Support

- **Click title strip**: Toggle panel (if enabled)
- **Click arrow**: Toggle panel
- **Future**: ESC key support (not implemented yet)

## Demo

Visit `/demo/panels` to see a live demo with:
- 3 panels (2 right, 1 left)
- Different sizes and configurations
- Controlled state management
- Interactive controls

## Browser Support

Works in all modern browsers supporting:
- CSS `writing-mode` (vertical text)
- CSS `transform` (animations)
- CSS `position: fixed`
- Angular 18+ signals

## Known Limitations

1. **Strip Overlap**: Multiple panels on same side may have overlapping title strips when collapsed
2. **No Auto-Stacking**: Strips don't automatically stack vertically (future enhancement)
3. **No ESC Key**: ESC key support not implemented yet
4. **No Focus Management**: Keyboard focus management not implemented yet

## Migration from Old Implementation

If you're using the old implementation, update your code:

**Before:**
```html
<app-docked-slide-out-panel
  [side]="'right'"
  [widthPercent]="50"
  [heightPercent]="80"
  [initialState]="'collapsed'"
  [enableEscapeKey]="true">
</app-docked-slide-out-panel>
```

**After:**
```html
<app-docked-slide-out-panel
  id="my-panel"
  title="My Panel"
  [side]="'right'"
  [widthRatio]="0.5"
  [heightRatio]="0.8"
  [collapsed]="isCollapsed()">
</app-docked-slide-out-panel>
```

**Key Changes:**
- ✅ Added required `id` and `title`
- ✅ Changed `widthPercent`/`heightPercent` to `widthRatio`/`heightRatio` (0.0-1.0)
- ✅ Changed `initialState` to `collapsed` (controlled mode)
- ❌ Removed `enableEscapeKey` (not implemented yet)
- ❌ Removed `handleTooltip`/`handleAriaLabel` (not needed with title)

## Future Enhancements

1. **Vertical Strip Stacking** - Automatically stack strips to prevent overlap
2. **ESC Key Support** - Close panel with ESC key
3. **Focus Management** - Trap focus when panel opens
4. **Resize Handles** - Allow user to resize panels
5. **Minimize/Maximize** - Additional panel states
6. **Panel Groups** - Accordion-like behavior (optional)
7. **Persistence** - Remember panel state in localStorage
