# Docked Slide-Out Panel - Code Examples

## Example 1: Basic Right-Side Panel

```typescript
import { Component } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';

@Component({
  selector: 'app-example-basic',
  standalone: true,
  imports: [DockedSlideOutPanelComponent],
  template: `
    <div class="page-content">
      <h1>My Page</h1>
      <p>Main content here...</p>
    </div>

    <app-docked-slide-out-panel>
      <div panel-content style="padding: 20px;">
        <h2>Side Panel</h2>
        <p>This is a basic right-side panel</p>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class ExampleBasicComponent {}
```

## Example 2: Left-Side Panel with Custom Size

```typescript
import { Component } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';

@Component({
  selector: 'app-example-left',
  standalone: true,
  imports: [DockedSlideOutPanelComponent],
  template: `
    <app-docked-slide-out-panel
      [side]="'left'"
      [widthPercent]="40"
      [heightPercent]="60">
      <div panel-content style="padding: 20px; background-color: #f5f5f5;">
        <h2>Left Panel</h2>
        <ul>
          <li>Item 1</li>
          <li>Item 2</li>
          <li>Item 3</li>
        </ul>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class ExampleLeftComponent {}
```

## Example 3: Initially Expanded Panel

```typescript
import { Component } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';

@Component({
  selector: 'app-example-expanded',
  standalone: true,
  imports: [DockedSlideOutPanelComponent],
  template: `
    <app-docked-slide-out-panel
      [initialState]="'expanded'"
      [widthPercent]="45"
      [heightPercent]="70">
      <div panel-content style="padding: 20px;">
        <h2>Welcome!</h2>
        <p>This panel starts expanded</p>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class ExampleExpandedComponent {}
```

## Example 4: Panel with State Change Events

```typescript
import { Component, signal } from '@angular/core';
import { DockedSlideOutPanelComponent, PanelState } from '@shared/components';

@Component({
  selector: 'app-example-events',
  standalone: true,
  imports: [DockedSlideOutPanelComponent],
  template: `
    <div class="status-bar">
      Panel State: {{ panelState() }}
    </div>

    <app-docked-slide-out-panel
      (stateChange)="onPanelStateChange($event)">
      <div panel-content style="padding: 20px;">
        <h2>Panel with Events</h2>
        <p>Watch the status bar above!</p>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class ExampleEventsComponent {
  panelState = signal<PanelState>('collapsed');

  onPanelStateChange(state: PanelState): void {
    this.panelState.set(state);
    console.log('Panel state changed to:', state);
  }
}
```

## Example 5: Programmatic Control

```typescript
import { Component, ViewChild } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-example-programmatic',
  standalone: true,
  imports: [DockedSlideOutPanelComponent, MatButtonModule],
  template: `
    <div class="controls">
      <button mat-raised-button (click)="openPanel()">Open</button>
      <button mat-raised-button (click)="closePanel()">Close</button>
      <button mat-raised-button (click)="togglePanel()">Toggle</button>
    </div>

    <app-docked-slide-out-panel #panel>
      <div panel-content style="padding: 20px;">
        <h2>Controlled Panel</h2>
        <p>Use the buttons above to control this panel</p>
      </div>
    </app-docked-slide-out-panel>
  `,
  styles: [`
    .controls {
      padding: 20px;
      display: flex;
      gap: 10px;
    }
  `]
})
export class ExampleProgrammaticComponent {
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

## Example 6: Validation Response Panel (Real-World)

```typescript
import { Component, signal, computed, ViewChild } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-validation-panel',
  standalone: true,
  imports: [
    DockedSlideOutPanelComponent,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <button mat-raised-button color="accent" (click)="validate()">
      <mat-icon>check_circle</mat-icon>
      Validate
    </button>

    <app-docked-slide-out-panel
      #slidePanel
      [side]="'right'"
      [widthPercent]="50"
      [heightPercent]="80"
      [handleTooltip]="'Validation Response'"
      [handleAriaLabel]="'Toggle validation response panel'">
      
      <div panel-content class="validation-content">
        <div class="header">
          <h3>Validation Response</h3>
          <button mat-icon-button (click)="clearResponse()">
            <mat-icon>close</mat-icon>
          </button>
        </div>
        
        <div class="body">
          @if (response()) {
            <pre>{{ formattedResponse() }}</pre>
          } @else {
            <p>No validation response yet</p>
          }
        </div>
      </div>
    </app-docked-slide-out-panel>
  `,
  styles: [`
    .validation-content {
      display: flex;
      flex-direction: column;
      height: 100%;
      background-color: white;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      background-color: #e3f2fd;
      border-bottom: 2px solid #1976d2;
    }

    .header h3 {
      margin: 0;
      color: #1976d2;
    }

    .body {
      flex: 1;
      overflow: auto;
      padding: 20px;
      background-color: #fafafa;
    }

    pre {
      background-color: #263238;
      color: #aed581;
      padding: 20px;
      border-radius: 4px;
      margin: 0;
    }
  `]
})
export class ValidationPanelComponent {
  @ViewChild('slidePanel') slidePanel!: DockedSlideOutPanelComponent;

  private _response = signal<any>(null);
  response = computed(() => this._response());
  
  formattedResponse = computed(() => {
    const resp = this._response();
    return resp ? JSON.stringify(resp, null, 2) : '';
  });

  validate(): void {
    // Simulate API call
    const mockResponse = {
      status: 'success',
      timestamp: new Date().toISOString(),
      data: { valid: true }
    };
    
    this._response.set(mockResponse);
    this.slidePanel.expand();
  }

  clearResponse(): void {
    this._response.set(null);
    this.slidePanel.collapse();
  }
}
```

## Example 7: Settings Panel with Sections

```typescript
import { Component } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

@Component({
  selector: 'app-settings-panel',
  standalone: true,
  imports: [
    DockedSlideOutPanelComponent,
    MatExpansionModule,
    MatSlideToggleModule
  ],
  template: `
    <app-docked-slide-out-panel
      [side]="'right'"
      [widthPercent]="35"
      [heightPercent]="90"
      [initialState]="'expanded'">
      
      <div panel-content style="display: flex; flex-direction: column; height: 100%;">
        <div style="padding: 20px; background-color: #f5f5f5; border-bottom: 1px solid #ddd;">
          <h2 style="margin: 0;">Settings</h2>
        </div>
        
        <div style="flex: 1; overflow: auto; padding: 16px;">
          <mat-expansion-panel>
            <mat-expansion-panel-header>
              <mat-panel-title>General</mat-panel-title>
            </mat-expansion-panel-header>
            <mat-slide-toggle>Enable notifications</mat-slide-toggle>
            <mat-slide-toggle>Dark mode</mat-slide-toggle>
          </mat-expansion-panel>

          <mat-expansion-panel>
            <mat-expansion-panel-header>
              <mat-panel-title>Privacy</mat-panel-title>
            </mat-expansion-panel-header>
            <mat-slide-toggle>Share analytics</mat-slide-toggle>
            <mat-slide-toggle>Allow cookies</mat-slide-toggle>
          </mat-expansion-panel>
        </div>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class SettingsPanelComponent {}
```

## Example 8: Custom Animation

```typescript
import { Component } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';

@Component({
  selector: 'app-example-animation',
  standalone: true,
  imports: [DockedSlideOutPanelComponent],
  template: `
    <app-docked-slide-out-panel
      [animationDuration]="500"
      [animationEasing]="'ease-in-out'">
      <div panel-content style="padding: 20px;">
        <h2>Slow Animation</h2>
        <p>This panel slides in slowly (500ms)</p>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class ExampleAnimationComponent {}
```

## Example 9: Disable ESC Key

```typescript
import { Component } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';

@Component({
  selector: 'app-example-no-esc',
  standalone: true,
  imports: [DockedSlideOutPanelComponent],
  template: `
    <app-docked-slide-out-panel
      [enableEscapeKey]="false">
      <div panel-content style="padding: 20px;">
        <h2>Persistent Panel</h2>
        <p>ESC key won't close this panel</p>
        <p>Use the handle to close it</p>
      </div>
    </app-docked-slide-out-panel>
  `
})
export class ExampleNoEscComponent {}
```

## Example 10: Multiple Panels (Left + Right)

```typescript
import { Component } from '@angular/core';
import { DockedSlideOutPanelComponent } from '@shared/components';

@Component({
  selector: 'app-example-multiple',
  standalone: true,
  imports: [DockedSlideOutPanelComponent],
  template: `
    <div class="page-content">
      <h1>Page with Two Panels</h1>
      <p>One on each side!</p>
    </div>

    <!-- Left Panel -->
    <app-docked-slide-out-panel
      [side]="'left'"
      [widthPercent]="30"
      [heightPercent]="60">
      <div panel-content style="padding: 20px; background-color: #e8f5e9;">
        <h3>Left Panel</h3>
        <p>Navigation or filters</p>
      </div>
    </app-docked-slide-out-panel>

    <!-- Right Panel -->
    <app-docked-slide-out-panel
      [side]="'right'"
      [widthPercent]="40"
      [heightPercent]="70">
      <div panel-content style="padding: 20px; background-color: #e3f2fd;">
        <h3>Right Panel</h3>
        <p>Details or settings</p>
      </div>
    </app-docked-slide-out-panel>
  `,
  styles: [`
    .page-content {
      padding: 40px;
      text-align: center;
    }
  `]
})
export class ExampleMultipleComponent {}
```
