/**
 * Schedule Period Detail Component
 * 
 * Dialog component for viewing and editing individual schedule period details.
 * Displays all fields from SchedulePeriod interface in organized form sections.
 * Supports view and edit modes with field validation.
 * 
 * Requirements:
 * - 13.1: Inline schedule editing
 * - 13.2: Schedule cell validation
 */

import { Component, Inject, OnInit, signal, computed, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { SchedulePeriod } from '@core/models';

export interface SchedulePeriodDetailData {
  period: SchedulePeriod;
  editable: boolean;
}

@Component({
  selector: 'app-schedule-period-detail',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule
  ],
  template: `
    <div class="dialog-container">
      <!-- Dialog Header -->
      <div class="dialog-header">
        <h2 mat-dialog-title>
          <mat-icon>calendar_today</mat-icon>
          Schedule Period {{ periodIndex() }}
        </h2>
        <button 
          mat-icon-button 
          mat-dialog-close
          class="close-button">
          <mat-icon>close</mat-icon>
        </button>
      </div>

      <mat-divider></mat-divider>

      <!-- Dialog Content -->
      <mat-dialog-content class="dialog-content">
        <form [formGroup]="form" class="period-form">
          <!-- Core Period Information -->
          <div class="form-section">
            <h3 class="section-title">
              <mat-icon>info</mat-icon>
              Period Information
            </h3>
            
            <div class="form-row">
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Period Index</mat-label>
                <input 
                  matInput 
                  type="number"
                  formControlName="periodIndex"
                  [readonly]="!editable()">
                @if (form.get('periodIndex')?.hasError('required') && form.get('periodIndex')?.touched) {
                  <mat-error>Period index is required</mat-error>
                }
              </mat-form-field>
            </div>
          </div>

          <!-- Date Information -->
          <div class="form-section">
            <h3 class="section-title">
              <mat-icon>date_range</mat-icon>
              Dates
            </h3>
            
            <div class="form-row">
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Start Date</mat-label>
                <input 
                  matInput 
                  type="date"
                  formControlName="startDate"
                  [readonly]="!editable()">
                @if (form.get('startDate')?.hasError('required') && form.get('startDate')?.touched) {
                  <mat-error>Start date is required</mat-error>
                }
              </mat-form-field>

              <mat-form-field appearance="outline" class="form-field">
                <mat-label>End Date</mat-label>
                <input 
                  matInput 
                  type="date"
                  formControlName="endDate"
                  [readonly]="!editable()">
                @if (form.get('endDate')?.hasError('required') && form.get('endDate')?.touched) {
                  <mat-error>End date is required</mat-error>
                }
              </mat-form-field>
            </div>

            <div class="form-row">
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Payment Date</mat-label>
                <input 
                  matInput 
                  type="date"
                  formControlName="paymentDate"
                  [readonly]="!editable()">
                @if (form.get('paymentDate')?.hasError('required') && form.get('paymentDate')?.touched) {
                  <mat-error>Payment date is required</mat-error>
                }
              </mat-form-field>
            </div>
          </div>

          <!-- Financial Information -->
          <div class="form-section">
            <h3 class="section-title">
              <mat-icon>attach_money</mat-icon>
              Financial Details
            </h3>
            
            <div class="form-row">
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Notional</mat-label>
                <input 
                  matInput 
                  type="number"
                  step="0.01"
                  formControlName="notional"
                  [readonly]="!editable()">
                @if (form.get('notional')?.hasError('required') && form.get('notional')?.touched) {
                  <mat-error>Notional is required</mat-error>
                }
                @if (form.get('notional')?.hasError('min') && form.get('notional')?.touched) {
                  <mat-error>Notional must be positive</mat-error>
                }
              </mat-form-field>

              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Rate (%)</mat-label>
                <input 
                  matInput 
                  type="number"
                  step="0.0001"
                  formControlName="rate"
                  [readonly]="!editable()">
              </mat-form-field>
            </div>

            <div class="form-row">
              <mat-form-field appearance="outline" class="form-field">
                <mat-label>Interest</mat-label>
                <input 
                  matInput 
                  type="number"
                  step="0.01"
                  formControlName="interest"
                  [readonly]="!editable()">
              </mat-form-field>
            </div>
          </div>

          <!-- Additional Fields (Dynamic) -->
          @if (hasAdditionalFields()) {
            <div class="form-section">
              <h3 class="section-title">
                <mat-icon>more_horiz</mat-icon>
                Additional Fields
              </h3>
              
              @for (field of additionalFields(); track field.key) {
                <div class="form-row">
                  <mat-form-field appearance="outline" class="form-field">
                    <mat-label>{{ formatFieldName(field.key) }}</mat-label>
                    <input 
                      matInput 
                      [value]="field.value"
                      [readonly]="true">
                  </mat-form-field>
                </div>
              }
            </div>
          }
        </form>
      </mat-dialog-content>

      <mat-divider></mat-divider>

      <!-- Dialog Actions -->
      <mat-dialog-actions class="dialog-actions">
        <button 
          mat-button 
          mat-dialog-close
          class="cancel-button">
          {{ editable() ? 'Cancel' : 'Close' }}
        </button>
        
        @if (editable()) {
          <button 
            mat-raised-button 
            color="primary"
            [disabled]="!form.valid || !form.dirty"
            (click)="onSave()"
            class="save-button">
            <mat-icon>save</mat-icon>
            Save Changes
          </button>
        }
      </mat-dialog-actions>
    </div>
  `,
  styles: [`
    .dialog-container {
      display: flex;
      flex-direction: column;
      max-height: 90vh;
    }

    .dialog-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 24px;

      h2 {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 0;
        font-size: 20px;
        font-weight: 500;

        mat-icon {
          color: #1976d2;
        }
      }

      .close-button {
        margin-right: -12px;
      }
    }

    .dialog-content {
      padding: 24px;
      overflow-y: auto;
    }

    .period-form {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .form-section {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 16px;
      background-color: #f9f9f9;
      border-radius: 8px;
      border: 1px solid #e0e0e0;
    }

    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 8px 0;
      font-size: 16px;
      font-weight: 500;
      color: rgba(0, 0, 0, 0.87);

      mat-icon {
        font-size: 20px;
        width: 20px;
        height: 20px;
        color: #1976d2;
      }
    }

    .form-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 16px;
    }

    .form-field {
      width: 100%;
    }

    .dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      padding: 16px 24px;
      background-color: #fafafa;

      .save-button {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    // Readonly input styling
    input[readonly] {
      cursor: default;
      color: rgba(0, 0, 0, 0.6);
    }

    // Responsive adjustments
    @media (max-width: 768px) {
      .form-row {
        grid-template-columns: 1fr;
      }

      .dialog-header h2 {
        font-size: 18px;
      }
    }
  `]
})
export class SchedulePeriodDetailComponent implements OnInit {
  private fb = new FormBuilder();

  // ============================================================================
  // Signals
  // ============================================================================

  /**
   * Period data signal
   */
  periodData = signal<SchedulePeriod>({} as SchedulePeriod);

  /**
   * Editable mode signal
   */
  editable = signal<boolean>(false);

  /**
   * Period index for display
   */
  periodIndex = computed(() => this.periodData().periodIndex ?? 0);

  /**
   * Check if there are additional fields beyond the standard ones
   */
  hasAdditionalFields = computed(() => {
    return this.additionalFields().length > 0;
  });

  /**
   * Get additional fields (non-standard fields)
   */
  additionalFields = computed(() => {
    const period = this.periodData();
    const standardFields = [
      'periodIndex',
      'startDate',
      'endDate',
      'paymentDate',
      'notional',
      'rate',
      'interest'
    ];

    const additionalFields: Array<{ key: string; value: any }> = [];

    for (const key in period) {
      if (!standardFields.includes(key) && period.hasOwnProperty(key)) {
        additionalFields.push({
          key,
          value: period[key]
        });
      }
    }

    return additionalFields;
  });

  // ============================================================================
  // Form
  // ============================================================================

  /**
   * Reactive form for schedule period
   */
  form: FormGroup;

  // ============================================================================
  // Constructor
  // ============================================================================

  constructor(
    public dialogRef: MatDialogRef<SchedulePeriodDetailComponent>,
    @Inject(MAT_DIALOG_DATA) public data: SchedulePeriodDetailData
  ) {
    // Initialize signals with data
    this.periodData.set(data.period);
    this.editable.set(data.editable);

    // Initialize form
    this.form = this.fb.group({
      periodIndex: [
        { value: 0, disabled: true },
        [Validators.required, Validators.min(0)]
      ],
      startDate: ['', Validators.required],
      endDate: ['', Validators.required],
      paymentDate: ['', Validators.required],
      notional: [0, [Validators.required, Validators.min(0)]],
      rate: [0],
      interest: [0]
    });

    // Effect to enable/disable form based on edit mode
    effect(() => {
      if (this.editable()) {
        this.form.enable();
        // Keep periodIndex disabled even in edit mode
        this.form.get('periodIndex')?.disable();
      } else {
        this.form.disable();
      }
    });
  }

  // ============================================================================
  // Lifecycle Hooks
  // ============================================================================

  ngOnInit(): void {
    this.populateForm();
  }

  // ============================================================================
  // Event Handlers
  // ============================================================================

  /**
   * Handle save button click
   */
  onSave(): void {
    if (!this.form.valid) {
      return;
    }

    const formValue = this.form.getRawValue();
    const updatedPeriod: SchedulePeriod = {
      ...this.periodData(),
      ...formValue
    };

    this.dialogRef.close(updatedPeriod);
  }

  // ============================================================================
  // Private Methods
  // ============================================================================

  /**
   * Populate form with period data
   */
  private populateForm(): void {
    const period = this.periodData();

    this.form.patchValue({
      periodIndex: period.periodIndex ?? 0,
      startDate: period.startDate || '',
      endDate: period.endDate || '',
      paymentDate: period.paymentDate || '',
      notional: period.notional ?? 0,
      rate: period.rate ?? 0,
      interest: period.interest ?? 0
    }, { emitEvent: false });
  }

  /**
   * Format field name for display
   * Converts camelCase to Title Case
   */
  formatFieldName(fieldName: string): string {
    return fieldName
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, (str) => str.toUpperCase())
      .trim();
  }
}
