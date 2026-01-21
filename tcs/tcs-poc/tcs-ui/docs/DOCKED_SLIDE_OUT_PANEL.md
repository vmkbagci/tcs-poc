# Docked Slide-Out Panel Component

A reusable Angular component that provides a slide-out panel anchored to the viewport edge.

## Features

- **Partial Size**: Configurable width and height (percentage of viewport)
- **Side Anchoring**: Can be positioned on left or right side
- **Smooth Animation**: Customizable duration and easing
- **Keyboard Accessible**: ESC key support (optional)
- **Non-Blocking**: Does not prevent interaction with rest of page
- **No Auto-Close**: Only closes via handle or ESC key
- **Responsive**: Adapts to mobile screens

## Basic Usage

```typescript
import { Component } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';

@Component({
  selector: 'app-my-component',
  standalone: true,
  imports: [DockedSlideOutPanelComponent],
  template: `
    <app-docked-slide-out-panel
      [side]="'right'"
      [widthPercent]="50"
      [heightPercent]="50">
      <div panel-content>
        <h2>Panel Content</h2>
        <p>Your content goes here</p>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class MyComponent {}
```

## Configuration Options

### Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `side` | `'left' \| 'right'` | `'right'` | Which side of viewport to anchor panel |
| `widthPercent` | `number` | `50` | Panel width as percentage of viewport width |
| `heightPercent` | `number` | `50` | Panel height as percentage of viewport height |
| `initialState` | `'collapsed' \| 'expanded'` | `'collapsed'` | Initial state of panel |
| `animationDuration` | `number` | `300` | Animation duration in milliseconds |
| `animationEasing` | `string` | `'cubic-bezier(0.4, 0.0, 0.2, 1)'` | CSS easing function |
| `enableEscapeKey` | `boolean` | `true` | Whether ESC key collapses panel |
| `handleTooltip` | `string` | Auto-generated | Custom tooltip text for handle |
| `handleAriaLabel` | `string` | Auto-generated | Custom aria-label for handle |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `stateChange` | `EventEmitter<'collapsed' \| 'expanded'>` | Emitted when panel state changes |

## Examples

### Example 1: Right-Side Panel (Default)

```html
<app-docked-slide-out-panel>
  <div panel-content>
    <h2>Settings</h2>
    <p>Configure your preferences here</p>
  </div>
</app-docked-slide-out-panel>
```

### Example 2: Left-Side Panel with Custom Size

```html
<app-docked-slide-out-panel
  [side]="'left'"
  [widthPercent]="40"
  [heightPercent]="60">
  <div panel-content>
    <h2>Navigation</h2>
    <ul>
      <li>Home</li>
      <li>About</li>
      <li>Contact</li>
    </ul>
  </div>
</app-docked-slide-out-panel>
```

### Example 3: Initially Expanded Panel

```html
<app-docked-slide-out-panel
  [initialState]="'expanded'"
  [widthPercent]="45"
  [heightPercent]="70">
  <div panel-content>
    <h2>Welcome!</h2>
    <p>This panel starts expanded</p>
  </div>
</app-docked-slide-out-panel>
```

### Example 4: Custom Animation

```html
<app-docked-slide-out-panel
  [animationDuration]="500"
  [animationEasing]="'ease-in-out'">
  <div panel-content>
    <h2>Slow Animation</h2>
    <p>This panel slides in slowly</p>
  </div>
</app-docked-slide-out-panel>
```

### Example 5: Disable ESC Key

```html
<app-docked-slide-out-panel
  [enableEscapeKey]="false">
  <div panel-content>
    <h2>Persistent Panel</h2>
    <p>ESC key won't close this panel</p>
  </div>
</app-docked-slide-out-panel>
```

### Example 6: Listen to State Changes

```typescript
@Component({
  template: `
    <app-docked-slide-out-panel
      (stateChange)="onPanelStateChange($event)">
      <div panel-content>
        <h2>Panel with Events</h2>
        <p>Current state: {{ panelState }}</p>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class MyComponent {
  panelState: string = 'collapsed';

  onPanelStateChange(state: 'collapsed' | 'expanded'): void {
    this.panelState = state;
    console.log('Panel state changed to:', state);
  }
}
```

### Example 7: Programmatic Control

```typescript
import { Component, ViewChild } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';

@Component({
  template: `
    <button (click)="openPanel()">Open Panel</button>
    <button (click)="closePanel()">Close Panel</button>
    <button (click)="togglePanel()">Toggle Panel</button>

    <app-docked-slide-out-panel #panel>
      <div panel-content>
        <h2>Controlled Panel</h2>
        <p>This panel is controlled programmatically</p>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class MyComponent {
  @ViewChild('panel') panel!: DockedSlideOutPanelComponent;

  openPanel(): void {
    this.panel.expand();
  }

  closePanel(): void {
    this.panel.collapse();
  }

  togglePanel(): void {
    this.panel.toggle();
  }
}
```

### Example 8: Complex Content with Styling

```html
<app-docked-slide-out-panel
  [side]="'right'"
  [widthPercent]="55"
  [heightPercent]="80">
  <div panel-content style="display: flex; flex-direction: column; height: 100%;">
    <!-- Header -->
    <div style="padding: 20px; background-color: #e3f2fd; border-bottom: 2px solid #1976d2;">
      <h2 style="margin: 0; color: #1976d2;">API Response</h2>
    </div>
    
    <!-- Scrollable Content -->
    <div style="flex: 1; overflow: auto; padding: 20px; background-color: #fafafa;">
      <pre style="background-color: #263238; color: #aed581; padding: 20px; border-radius: 4px;">
        {{ jsonData | json }}
      </pre>
    </div>
    
    <!-- Footer -->
    <div style="padding: 16px; background-color: #f5f5f5; border-top: 1px solid #ddd;">
      <button mat-raised-button color="primary">Copy to Clipboard</button>
    </div>
  </div>
</app-docked-slide-out-panel>
```

## Styling the Content

The component uses content projection with the `panel-content` selector. You can style your content however you like:

```html
<app-docked-slide-out-panel>
  <div panel-content class="my-custom-panel">
    <!-- Your styled content -->
  </div>
</app-docked-slide-out-panel>
```

```css
.my-custom-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: white;
}
```

## Accessibility

The component includes proper ARIA attributes:
- `aria-label`: Describes the handle button
- `aria-expanded`: Indicates current panel state
- Keyboard support: ESC key to collapse (configurable)
- Focus management: Handle is keyboard accessible

## Responsive Behavior

On mobile devices (< 768px):
- Panel automatically adjusts to 90vw width and 80vh height
- Maintains all functionality
- Handle remains accessible

## Best Practices

1. **Content Height**: Ensure your content handles overflow properly
2. **Z-Index**: Panel has z-index of 1000; adjust if needed
3. **Performance**: Avoid heavy content that might slow animation
4. **Accessibility**: Provide meaningful `handleAriaLabel` for context
5. **State Management**: Use `stateChange` event to sync with parent state

## Differences from Modal/Dialog

This component is NOT:
- A modal (no backdrop, no focus trap)
- A dialog (no auto-close on outside click)
- A navigation drawer (partial size, not full-height)
- A hamburger menu (no menu semantics)

## Browser Support

Works in all modern browsers that support:
- CSS transforms
- CSS transitions
- Flexbox
- Angular 17+ signals

## Migration from ValidationPanelComponent

If you're migrating from the old `ValidationPanelComponent`:

**Before:**
```html
<app-validation-panel
  [validationResponse]="response()"
  (closed)="onClosed()">
</app-validation-panel>
```

**After:**
```html
<app-docked-slide-out-panel
  [side]="'right'"
  [widthPercent]="50"
  [heightPercent]="50">
  <div panel-content>
    <!-- Your validation response content -->
  </div>
</app-docked-slide-out-panel>
```
