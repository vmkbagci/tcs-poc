/**
 * Validation Panel Component
 * 
 * Displays API validation response in a docked slide-out panel.
 * Uses the reusable DockedSlideOutPanelComponent.
 * 
 * Shows structured errors and warnings with color-coded chrome:
 * - Red: Has errors
 * - Yellow/Orange: Has warnings only
 * - Green: Success (no errors or warnings)
 */

import { Component, Input, Output, EventEmitter, signal, computed, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatListModule } from '@angular/material/list';
import { DockedSlideOutPanelComponent } from '@shared/components';

interface ValidationError {
  field?: string;
  message: string;
  severity?: 'error' | 'warning';
}

@Component({
  selector: 'app-validation-panel',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatExpansionModule,
    MatListModule,
    DockedSlideOutPanelComponent
  ],
  template: `
    <app-docked-slide-out-panel
      #slidePanel
      id="validation-panel"
      title="Validation"
      [side]="'right'"
      [widthRatio]="0.5"
      [heightRatio]="0.8"
      [collapsed]="isCollapsed()"
      [chromeColor]="chromeColor()"
      (collapsedChange)="onCollapsedChange($event)">
      
      <div panel-content class="validation-content">
        <!-- Panel Header -->
        <div class="panel-header" [class.panel-header--error]="hasErrors()" 
             [class.panel-header--warning]="hasWarningsOnly()"
             [class.panel-header--success]="isSuccess()">
          <div class="header-title">
            <mat-icon>{{ statusIcon() }}</mat-icon>
            <div class="header-text">
              <h3>{{ statusTitle() }}</h3>
              <p class="subtitle">{{ statusSubtitle() }}</p>
            </div>
          </div>
          <button 
            mat-icon-button 
            class="close-button"
            (click)="onClose()">
            <mat-icon>close</mat-icon>
          </button>
        </div>

        <!-- Panel Body -->
        <div class="panel-body">
          @if (response()) {
            <!-- Errors Section -->
            @if (errors().length > 0) {
              <mat-expansion-panel class="error-section" [expanded]="true">
                <mat-expansion-panel-header>
                  <mat-panel-title>
                    <mat-icon class="section-icon error-icon">error</mat-icon>
                    <span>Errors ({{ errors().length }})</span>
                  </mat-panel-title>
                </mat-expansion-panel-header>
                
                <mat-list>
                  @for (error of errors(); track $index) {
                    <mat-list-item class="error-item">
                      <mat-icon matListItemIcon class="item-icon">close</mat-icon>
                      <div matListItemTitle class="item-title">
                        @if (error.field) {
                          <strong>{{ error.field }}:</strong>
                        }
                        {{ error.message }}
                      </div>
                    </mat-list-item>
                  }
                </mat-list>
              </mat-expansion-panel>
            }

            <!-- Warnings Section -->
            @if (warnings().length > 0) {
              <mat-expansion-panel class="warning-section" [expanded]="true">
                <mat-expansion-panel-header>
                  <mat-panel-title>
                    <mat-icon class="section-icon warning-icon">warning</mat-icon>
                    <span>Warnings ({{ warnings().length }})</span>
                  </mat-panel-title>
                </mat-expansion-panel-header>
                
                <mat-list>
                  @for (warning of warnings(); track $index) {
                    <mat-list-item class="warning-item">
                      <mat-icon matListItemIcon class="item-icon">info</mat-icon>
                      <div matListItemTitle class="item-title">
                        @if (warning.field) {
                          <strong>{{ warning.field }}:</strong>
                        }
                        {{ warning.message }}
                      </div>
                    </mat-list-item>
                  }
                </mat-list>
              </mat-expansion-panel>
            }

            <!-- Success Message -->
            @if (isSuccess()) {
              <div class="success-message">
                <mat-icon>check_circle</mat-icon>
                <h4>Validation Successful</h4>
                <p>No errors or warnings found</p>
              </div>
            }

            <!-- Raw Response (Collapsible) -->
            <mat-expansion-panel class="raw-response-section">
              <mat-expansion-panel-header>
                <mat-panel-title>
                  <mat-icon class="section-icon">code</mat-icon>
                  <span>Raw Response</span>
                </mat-panel-title>
              </mat-expansion-panel-header>
              
              <pre class="json-response">{{ formattedResponse() }}</pre>
            </mat-expansion-panel>
          } @else {
            <div class="no-response">
              <mat-icon>info</mat-icon>
              <p>No validation response yet</p>
              <p class="hint">Click "Validate" to see the API response</p>
            </div>
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

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      border-bottom: 2px solid;
      flex-shrink: 0;
      transition: background-color 0.3s ease;
    }

    .panel-header--error {
      background-color: #ffebee;
      border-bottom-color: #f44336;
    }

    .panel-header--warning {
      background-color: #fff3e0;
      border-bottom-color: #ff9800;
    }

    .panel-header--success {
      background-color: #e8f5e9;
      border-bottom-color: #4caf50;
    }

    .panel-header .header-title {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .panel-header .header-title mat-icon {
      font-size: 32px;
      width: 32px;
      height: 32px;
    }

    .panel-header--error .header-title mat-icon {
      color: #f44336;
    }

    .panel-header--warning .header-title mat-icon {
      color: #ff9800;
    }

    .panel-header--success .header-title mat-icon {
      color: #4caf50;
    }

    .panel-header .header-text h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 500;
      white-space: nowrap;
    }

    .panel-header--error .header-text h3 {
      color: #c62828;
    }

    .panel-header--warning .header-text h3 {
      color: #e65100;
    }

    .panel-header--success .header-text h3 {
      color: #2e7d32;
    }

    .panel-header .header-text .subtitle {
      margin: 4px 0 0 0;
      font-size: 12px;
      color: rgba(0, 0, 0, 0.6);
    }

    .panel-header .close-button {
      flex-shrink: 0;
    }

    .panel-body {
      flex: 1;
      overflow: auto;
      background-color: #fafafa;
    }

    /* Expansion Panels */
    mat-expansion-panel {
      margin: 16px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    mat-expansion-panel:first-child {
      margin-top: 16px;
    }

    .section-icon {
      margin-right: 8px;
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .error-section .section-icon {
      color: #f44336;
    }

    .warning-section .section-icon {
      color: #ff9800;
    }

    .raw-response-section .section-icon {
      color: #757575;
    }

    /* List Items */
    mat-list {
      padding: 0;
    }

    mat-list-item {
      height: auto !important;
      min-height: 48px;
      padding: 12px 16px;
      border-bottom: 1px solid #e0e0e0;
    }

    mat-list-item:last-child {
      border-bottom: none;
    }

    .item-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
      margin-right: 12px;
    }

    .error-item .item-icon {
      color: #f44336;
    }

    .warning-item .item-icon {
      color: #ff9800;
    }

    .item-title {
      font-size: 14px;
      line-height: 1.5;
      color: rgba(0, 0, 0, 0.87);
      white-space: normal;
      word-wrap: break-word;
    }

    .item-title strong {
      color: rgba(0, 0, 0, 0.95);
      font-weight: 600;
    }

    /* Success Message */
    .success-message {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px 24px;
      text-align: center;
      margin: 16px;
      background-color: white;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .success-message mat-icon {
      font-size: 64px;
      width: 64px;
      height: 64px;
      color: #4caf50;
      margin-bottom: 16px;
    }

    .success-message h4 {
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 500;
      color: #2e7d32;
    }

    .success-message p {
      margin: 0;
      font-size: 14px;
      color: rgba(0, 0, 0, 0.6);
    }

    /* Raw JSON Response */
    .json-response {
      margin: 0;
      padding: 16px;
      background-color: #263238;
      color: #aed581;
      font-family: 'Courier New', Courier, monospace;
      font-size: 12px;
      line-height: 1.6;
      white-space: pre-wrap;
      word-wrap: break-word;
      overflow-x: auto;
    }

    /* No Response State */
    .no-response {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px 24px;
      text-align: center;
      min-height: 300px;
    }

    .no-response mat-icon {
      font-size: 64px;
      width: 64px;
      height: 64px;
      color: rgba(0, 0, 0, 0.26);
      margin-bottom: 16px;
    }

    .no-response p {
      margin: 8px 0;
      color: rgba(0, 0, 0, 0.6);
      font-size: 14px;
    }

    .no-response p.hint {
      font-size: 13px;
      font-style: italic;
      color: rgba(0, 0, 0, 0.4);
    }
  `]
})
export class ValidationPanelComponent implements AfterViewInit {
  
  @ViewChild('slidePanel') slidePanel!: DockedSlideOutPanelComponent;
  
  /**
   * Validation response data
   */
  @Input() set validationResponse(value: any) {
    this._response.set(value);
    // Auto-expand when new response arrives
    if (value && this.slidePanel) {
      this.slidePanel.expand();
    }
  }

  /**
   * Event emitted when panel is closed
   */
  @Output() closed = new EventEmitter<void>();

  // ============================================================================
  // Signals
  // ============================================================================

  private _response = signal<any>(null);
  private _isCollapsed = signal<boolean>(true);

  response = computed(() => this._response());
  isCollapsed = computed(() => this._isCollapsed());

  /**
   * Formatted JSON response
   */
  formattedResponse = computed(() => {
    const resp = this._response();
    return resp ? JSON.stringify(resp, null, 2) : '';
  });

  /**
   * Parse errors from response
   */
  errors = computed(() => {
    const resp = this._response();
    if (!resp) return [];

    const errorList: ValidationError[] = [];

    // Check for errors array
    if (Array.isArray(resp.errors)) {
      errorList.push(...resp.errors.map((e: any) => ({
        field: e.field || e.path,
        message: e.message || String(e),
        severity: 'error' as const
      })));
    }

    // Check for failed validations
    if (resp.validations) {
      Object.entries(resp.validations).forEach(([field, validation]: [string, any]) => {
        if (validation.valid === false || validation.status === 'error') {
          errorList.push({
            field,
            message: validation.message || 'Validation failed',
            severity: 'error'
          });
        }
      });
    }

    // Check for error status
    if (resp.status === 'error' && resp.message) {
      errorList.push({
        message: resp.message,
        severity: 'error'
      });
    }

    return errorList;
  });

  /**
   * Parse warnings from response
   */
  warnings = computed(() => {
    const resp = this._response();
    if (!resp) return [];

    const warningList: ValidationError[] = [];

    // Check for warnings array
    if (Array.isArray(resp.warnings)) {
      warningList.push(...resp.warnings.map((w: any) => ({
        field: w.field || w.path,
        message: w.message || String(w),
        severity: 'warning' as const
      })));
    }

    // Check for warning validations
    if (resp.validations) {
      Object.entries(resp.validations).forEach(([field, validation]: [string, any]) => {
        if (validation.status === 'warning') {
          warningList.push({
            field,
            message: validation.message || 'Warning',
            severity: 'warning'
          });
        }
      });
    }

    return warningList;
  });

  /**
   * Check if response has errors
   */
  hasErrors = computed(() => this.errors().length > 0);

  /**
   * Check if response has warnings only (no errors)
   */
  hasWarningsOnly = computed(() => !this.hasErrors() && this.warnings().length > 0);

  /**
   * Check if response is successful (no errors or warnings)
   */
  isSuccess = computed(() => {
    const resp = this._response();
    if (!resp) return false;
    return !this.hasErrors() && !this.hasWarningsOnly();
  });

  /**
   * Determine chrome color based on validation status
   */
  chromeColor = computed(() => {
    if (this.hasErrors()) return '#f44336'; // Red
    if (this.hasWarningsOnly()) return '#ff9800'; // Orange
    return '#4caf50'; // Green
  });

  /**
   * Status icon based on validation result
   */
  statusIcon = computed(() => {
    if (this.hasErrors()) return 'error';
    if (this.hasWarningsOnly()) return 'warning';
    return 'check_circle';
  });

  /**
   * Status title based on validation result
   */
  statusTitle = computed(() => {
    if (this.hasErrors()) return 'Validation Failed';
    if (this.hasWarningsOnly()) return 'Validation Warnings';
    return 'Validation Passed';
  });

  /**
   * Status subtitle with counts
   */
  statusSubtitle = computed(() => {
    const errorCount = this.errors().length;
    const warningCount = this.warnings().length;
    
    if (errorCount > 0 && warningCount > 0) {
      return `${errorCount} error${errorCount > 1 ? 's' : ''}, ${warningCount} warning${warningCount > 1 ? 's' : ''}`;
    } else if (errorCount > 0) {
      return `${errorCount} error${errorCount > 1 ? 's' : ''} found`;
    } else if (warningCount > 0) {
      return `${warningCount} warning${warningCount > 1 ? 's' : ''} found`;
    }
    return 'No issues found';
  });

  // ============================================================================
  // Lifecycle
  // ============================================================================

  ngAfterViewInit(): void {
    // Auto-expand if response already exists
    if (this._response() && this.slidePanel) {
      this.slidePanel.expand();
    }
  }

  // ============================================================================
  // Event Handlers
  // ============================================================================

  /**
   * Handle collapsed state changes from panel
   */
  onCollapsedChange(collapsed: boolean): void {
    this._isCollapsed.set(collapsed);
  }

  /**
   * Close panel and clear response
   */
  onClose(): void {
    this._response.set(null);
    if (this.slidePanel) {
      this.slidePanel.collapse();
    }
    this.closed.emit();
  }
}
