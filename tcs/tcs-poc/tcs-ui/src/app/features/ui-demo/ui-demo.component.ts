/**
 * UI Capabilities Demo Component
 * 
 * Demonstrates advanced UI patterns and components available in the application.
 * This is a showcase of reusable UI components and their capabilities.
 * 
 * Current Demos:
 * - Docked Slide-Out Panels: Multiple independent panels with vertical title strips
 */

import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatDividerModule } from '@angular/material/divider';
import { MatTabsModule } from '@angular/material/tabs';
import { DockedSlideOutPanelComponent } from '@shared/components/docked-slide-out-panel.component';
import { DockedPanelHostComponent } from '@shared/components/docked-panel-host.component';
import { ValidationPanelComponent } from '@features/trade-detail/components/validation-panel.component';

@Component({
  selector: 'app-ui-demo',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatDividerModule,
    MatTabsModule,
    DockedSlideOutPanelComponent,
    DockedPanelHostComponent,
    ValidationPanelComponent
  ],
  template: `
    <div class="demo-container">
      <!-- Header -->
      <div class="demo-header">
        <button mat-icon-button routerLink="/" class="back-button">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <div class="header-content">
          <h1>UI Capabilities Demo</h1>
          <p class="subtitle">Interactive showcase of advanced UI components</p>
        </div>
      </div>

      <!-- Main Content -->
      <div class="demo-content">
        <mat-card class="info-card">
          <mat-card-header>
            <mat-card-title>Docked Slide-Out Panels</mat-card-title>
            <mat-card-subtitle>Multiple independent panels with persistent title strips</mat-card-subtitle>
          </mat-card-header>
          
          <mat-card-content>
            <h3>Features Demonstrated:</h3>
            <div class="features-grid">
              <div class="feature-item">
                <mat-icon>check_circle</mat-icon>
                <span>Persistent vertical title strips when collapsed</span>
              </div>
              <div class="feature-item">
                <mat-icon>check_circle</mat-icon>
                <span>Multiple panels on same view (left and right sides)</span>
              </div>
              <div class="feature-item">
                <mat-icon>check_circle</mat-icon>
                <span>Independent collapse/expand (no auto-close)</span>
              </div>
              <div class="feature-item">
                <mat-icon>check_circle</mat-icon>
                <span>Configurable size (width/height ratios)</span>
              </div>
              <div class="feature-item">
                <mat-icon>check_circle</mat-icon>
                <span>Smooth slide animations</span>
              </div>
              <div class="feature-item">
                <mat-icon>check_circle</mat-icon>
                <span>Controlled and uncontrolled modes</span>
              </div>
            </div>

            <mat-divider style="margin: 24px 0;"></mat-divider>

            <h3>Panel Controls:</h3>
            <div class="button-group">
              <button mat-raised-button color="primary" (click)="togglePanel1()">
                <mat-icon>{{ panel1Collapsed() ? 'open_in_new' : 'close' }}</mat-icon>
                {{ panel1Collapsed() ? 'Open' : 'Close' }} Settings
              </button>
              
              <button mat-raised-button (click)="togglePanel3()">
                <mat-icon>{{ panel3Collapsed() ? 'open_in_new' : 'close' }}</mat-icon>
                {{ panel3Collapsed() ? 'Open' : 'Close' }} Navigation
              </button>
            </div>

            <mat-divider style="margin: 24px 0;"></mat-divider>

            <h3>Validation Panel Examples:</h3>
            <p class="section-description">
              These panels demonstrate color-coded validation states with structured error and warning displays.
            </p>
            <div class="button-group">
              <button mat-raised-button color="warn" (click)="showErrorValidation()">
                <mat-icon>error</mat-icon>
                Show Errors + Warnings
              </button>
              
              <button mat-raised-button style="background-color: #ff9800; color: white;" (click)="showWarningValidation()">
                <mat-icon>warning</mat-icon>
                Show Warnings Only
              </button>
              
              <button mat-raised-button color="accent" (click)="showSuccessValidation()">
                <mat-icon>check_circle</mat-icon>
                Show Success
              </button>
            </div>

            <mat-divider style="margin: 24px 0;"></mat-divider>

            <h3>Instructions:</h3>
            <div class="instructions">
              <p>
                <mat-icon>info</mat-icon>
                Look at the edges of the viewport. You'll see title strips for each panel.
              </p>
              <p>
                <mat-icon>touch_app</mat-icon>
                Click the arrow or title strip to expand/collapse panels.
              </p>
              <p>
                <mat-icon>layers</mat-icon>
                <strong>Right side:</strong> Settings panel and validation examples<br>
                <strong>Left side:</strong> Navigation panel
              </p>
              <p>
                <mat-icon>palette</mat-icon>
                <strong>Validation colors:</strong> Red (errors), Orange (warnings), Green (success)
              </p>
            </div>
          </mat-card-content>
        </mat-card>
      </div>

      <!-- Panel Host with Multiple Panels -->
      <app-docked-panel-host>
        
        <!-- Panel 1: Settings (Right, Small) -->
        <app-docked-slide-out-panel
          id="settings-panel"
          title="Settings"
          side="right"
          [widthRatio]="0.3"
          [heightRatio]="0.4"
          [collapsed]="panel1Collapsed()"
          (collapsedChange)="onPanel1Change($event)"
          [zIndex]="1001">
          
          <div panel-content class="panel-content">
            <div class="panel-header">
              <h2>Settings</h2>
              <p class="subtitle">Configure your preferences</p>
            </div>
            
            <div class="panel-body">
              <div class="setting-item">
                <h4>Theme</h4>
                <p>Light mode</p>
              </div>
              
              <div class="setting-item">
                <h4>Language</h4>
                <p>English</p>
              </div>
              
              <div class="setting-item">
                <h4>Notifications</h4>
                <p>Enabled</p>
              </div>
              
              <div class="setting-item">
                <h4>Auto-save</h4>
                <p>Every 5 minutes</p>
              </div>
            </div>
          </div>
        </app-docked-slide-out-panel>

        <!-- Panel 2: Validation with Errors (Right) -->
        @if (validationErrorResponse() !== null) {
          <app-validation-panel
            [validationResponse]="validationErrorResponse()"
            (closed)="onValidationErrorClosed()">
          </app-validation-panel>
        }

        <!-- Panel 3: Validation with Warnings Only (Right) -->
        @if (validationWarningResponse() !== null) {
          <app-validation-panel
            [validationResponse]="validationWarningResponse()"
            (closed)="onValidationWarningClosed()">
          </app-validation-panel>
        }

        <!-- Panel 4: Validation Success (Right) -->
        @if (validationSuccessResponse() !== null) {
          <app-validation-panel
            [validationResponse]="validationSuccessResponse()"
            (closed)="onValidationSuccessClosed()">
          </app-validation-panel>
        }

        <!-- Panel 5: Navigation (Left, Medium) -->
        <app-docked-slide-out-panel
          id="navigation-panel"
          title="Navigation"
          side="left"
          [widthRatio]="0.35"
          [heightRatio]="0.6"
          [collapsed]="panel3Collapsed()"
          (collapsedChange)="onPanel3Change($event)"
          [zIndex]="1000">
          
          <div panel-content class="panel-content">
            <div class="panel-header">
              <h2>Navigation</h2>
              <p class="subtitle">Quick links</p>
            </div>
            
            <div class="panel-body">
              <nav class="nav-menu">
                <a routerLink="/" class="nav-item">
                  <mat-icon>home</mat-icon>
                  <span>Home</span>
                </a>
                <a routerLink="/trades" class="nav-item">
                  <mat-icon>list</mat-icon>
                  <span>Trades</span>
                </a>
                <a routerLink="/trades/new" class="nav-item">
                  <mat-icon>add_circle</mat-icon>
                  <span>Create Trade</span>
                </a>
                <a routerLink="/demo/panels" class="nav-item active">
                  <mat-icon>widgets</mat-icon>
                  <span>UI Demo</span>
                </a>
              </nav>
            </div>
          </div>
        </app-docked-slide-out-panel>

      </app-docked-panel-host>
    </div>
  `,
  styles: [`
    .demo-container {
      min-height: 100vh;
      background-color: #f5f5f5;
    }

    .demo-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 32px 40px;
      display: flex;
      align-items: center;
      gap: 16px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    .back-button {
      color: white;
    }

    .header-content h1 {
      margin: 0 0 8px 0;
      font-size: 2rem;
      font-weight: 500;
    }

    .header-content .subtitle {
      margin: 0;
      font-size: 1rem;
      opacity: 0.9;
    }

    .demo-content {
      max-width: 1200px;
      margin: 0 auto;
      padding: 40px 20px;
    }

    .info-card {
      margin-bottom: 32px;
    }

    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 16px;
      margin: 16px 0;
    }

    .feature-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px;
      background-color: #f5f5f5;
      border-radius: 4px;
    }

    .feature-item mat-icon {
      color: #4caf50;
      font-size: 20px;
      width: 20px;
      height: 20px;
      flex-shrink: 0;
    }

    .feature-item span {
      font-size: 14px;
      color: rgba(0, 0, 0, 0.87);
      line-height: 1.4;
    }

    .button-group {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin: 16px 0;
    }

    .instructions {
      background-color: #e3f2fd;
      padding: 20px;
      border-radius: 4px;
      border-left: 4px solid #1976d2;
    }

    .instructions p {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      margin: 12px 0;
      line-height: 1.6;
    }

    .instructions mat-icon {
      color: #1976d2;
      font-size: 20px;
      width: 20px;
      height: 20px;
      flex-shrink: 0;
      margin-top: 2px;
    }

    .section-description {
      margin: 8px 0 16px 0;
      font-size: 14px;
      color: rgba(0, 0, 0, 0.7);
      line-height: 1.5;
    }

    /* Panel Content Styling */
    .panel-content {
      display: flex;
      flex-direction: column;
      height: 100%;
      background-color: white;
    }

    .panel-header {
      padding: 24px;
      background-color: #e3f2fd;
      border-bottom: 2px solid #1976d2;
      flex-shrink: 0;
    }

    .panel-header h2 {
      margin: 0 0 8px 0;
      color: #1976d2;
      font-size: 20px;
      font-weight: 500;
    }

    .panel-header .subtitle {
      margin: 0;
      color: #666;
      font-size: 13px;
    }

    .panel-body {
      flex: 1;
      overflow: auto;
      padding: 24px;
    }

    /* Settings Panel Styling */
    .setting-item {
      padding: 16px 0;
      border-bottom: 1px solid #e0e0e0;
    }

    .setting-item:last-child {
      border-bottom: none;
    }

    .setting-item h4 {
      margin: 0 0 8px 0;
      font-size: 14px;
      font-weight: 500;
      color: #333;
    }

    .setting-item p {
      margin: 0;
      font-size: 13px;
      color: #666;
    }

    /* Validation Response Styling */
    .json-response {
      background-color: #263238;
      color: #aed581;
      padding: 20px;
      border-radius: 4px;
      font-family: 'Courier New', Courier, monospace;
      font-size: 13px;
      line-height: 1.6;
      margin: 0;
      overflow-x: auto;
    }

    /* Navigation Menu Styling */
    .nav-menu {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 12px 16px;
      color: #333;
      text-decoration: none;
      border-radius: 4px;
      transition: background-color 0.2s ease;
    }

    .nav-item:hover {
      background-color: #f5f5f5;
    }

    .nav-item.active {
      background-color: #e3f2fd;
      color: #1976d2;
    }

    .nav-item mat-icon {
      color: #1976d2;
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .nav-item span {
      font-size: 14px;
      font-weight: 500;
    }

    @media (max-width: 768px) {
      .demo-header {
        padding: 24px 20px;
      }

      .header-content h1 {
        font-size: 1.5rem;
      }

      .features-grid {
        grid-template-columns: 1fr;
      }

      .button-group {
        flex-direction: column;
      }

      .button-group button {
        width: 100%;
      }
    }
  `]
})
export class UiDemoComponent {
  
  // ============================================================================
  // Panel State (Controlled Mode)
  // ============================================================================

  panel1Collapsed = signal<boolean>(true);
  panel3Collapsed = signal<boolean>(true);

  // Validation response signals
  validationErrorResponse = signal<any>(null);
  validationWarningResponse = signal<any>(null);
  validationSuccessResponse = signal<any>(null);

  // ============================================================================
  // Demo Data
  // ============================================================================

  currentTime = new Date().toLocaleString();

  // Sample validation response with errors and warnings
  errorValidationData = {
    status: 'error',
    timestamp: new Date().toISOString(),
    errors: [
      { field: 'tradeId', message: 'Trade ID is required and cannot be empty' },
      { field: 'notional', message: 'Notional amount must be greater than zero' },
      { message: 'Counterparty credit limit exceeded' }
    ],
    warnings: [
      { field: 'effectiveDate', message: 'Effective date is in the past' },
      { message: 'Trade settlement date falls on a weekend' }
    ],
    validations: {
      tradeId: { valid: false, message: 'Trade ID is required and cannot be empty' },
      counterparty: { valid: true, message: 'Valid counterparty' },
      notional: { valid: false, message: 'Notional amount must be greater than zero' },
      effectiveDate: { valid: true, message: 'Valid date format' }
    },
    summary: {
      totalChecks: 12,
      passed: 8,
      failed: 3,
      warnings: 2
    }
  };

  // Sample validation response with warnings only
  warningValidationData = {
    status: 'warning',
    timestamp: new Date().toISOString(),
    warnings: [
      { field: 'effectiveDate', message: 'Trade date is more than 30 days in the past' },
      { field: 'counterparty', message: 'Counterparty has high exposure (>80% of limit)' },
      { message: 'Market data is older than 1 hour' }
    ],
    validations: {
      tradeId: { valid: true, message: 'Valid trade ID' },
      counterparty: { valid: true, status: 'warning', message: 'Counterparty has high exposure' },
      notional: { valid: true, message: 'Amount within limits' },
      effectiveDate: { valid: true, status: 'warning', message: 'Date is in the past' }
    },
    summary: {
      totalChecks: 12,
      passed: 12,
      failed: 0,
      warnings: 3
    }
  };

  // Sample validation response with success
  successValidationData = {
    status: 'success',
    timestamp: new Date().toISOString(),
    validations: {
      tradeId: { valid: true, message: 'Valid trade ID format' },
      counterparty: { valid: true, message: 'Counterparty verified and active' },
      notional: { valid: true, message: 'Amount within acceptable limits' },
      effectiveDate: { valid: true, message: 'Valid trade date' },
      maturityDate: { valid: true, message: 'Valid maturity date' },
      currency: { valid: true, message: 'Supported currency' }
    },
    summary: {
      totalChecks: 15,
      passed: 15,
      failed: 0,
      warnings: 0
    }
  };

  // ============================================================================
  // Panel Controls
  // ============================================================================

  onPanel1Change(collapsed: boolean): void {
    console.log('[Demo] onPanel1Change called with:', collapsed);
    this.panel1Collapsed.set(collapsed);
    console.log('[Demo] panel1Collapsed after set:', this.panel1Collapsed());
  }

  onPanel3Change(collapsed: boolean): void {
    console.log('[Demo] onPanel3Change called with:', collapsed);
    this.panel3Collapsed.set(collapsed);
    console.log('[Demo] panel3Collapsed after set:', this.panel3Collapsed());
  }

  togglePanel1(): void {
    console.log('[Demo] togglePanel1 called. Current:', this.panel1Collapsed());
    this.panel1Collapsed.update(collapsed => !collapsed);
    console.log('[Demo] togglePanel1 after update:', this.panel1Collapsed());
  }

  togglePanel3(): void {
    console.log('[Demo] togglePanel3 called. Current:', this.panel3Collapsed());
    this.panel3Collapsed.update(collapsed => !collapsed);
    console.log('[Demo] togglePanel3 after update:', this.panel3Collapsed());
  }

  // ============================================================================
  // Validation Panel Controls
  // ============================================================================

  showErrorValidation(): void {
    // Close other validation panels
    this.validationWarningResponse.set(null);
    this.validationSuccessResponse.set(null);
    // Show error validation
    this.validationErrorResponse.set(this.errorValidationData);
  }

  showWarningValidation(): void {
    // Close other validation panels
    this.validationErrorResponse.set(null);
    this.validationSuccessResponse.set(null);
    // Show warning validation
    this.validationWarningResponse.set(this.warningValidationData);
  }

  showSuccessValidation(): void {
    // Close other validation panels
    this.validationErrorResponse.set(null);
    this.validationWarningResponse.set(null);
    // Show success validation
    this.validationSuccessResponse.set(this.successValidationData);
  }

  onValidationErrorClosed(): void {
    this.validationErrorResponse.set(null);
  }

  onValidationWarningClosed(): void {
    this.validationWarningResponse.set(null);
  }

  onValidationSuccessClosed(): void {
    this.validationSuccessResponse.set(null);
  }
}
