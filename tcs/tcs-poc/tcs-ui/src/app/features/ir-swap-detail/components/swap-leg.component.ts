/**
 * Swap Leg Component
 * 
 * Displays and edits a single swap leg with its schedule.
 * Uses field configuration service to determine which fields to show.
 */

import { Component, Input, Output, EventEmitter, signal, computed, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatExpansionModule } from '@angular/material/expansion';
import { SwapLeg, SchedulePeriod } from '@core/models/swap.model';
import { TradeFieldConfigService } from '@core/services';
import { ScheduleGridComponent } from '../../trade-detail/components/schedule-grid.component';

@Component({
  selector: 'app-swap-leg',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatExpansionModule,
    ScheduleGridComponent
  ],
  template: `
    <mat-card class="swap-leg-card" [class.pay-leg]="legData()?.direction === 'pay'" [class.receive-leg]="legData()?.direction === 'receive'">
      <mat-card-header>
        <mat-card-title>
          <span class="leg-badge" [class.pay]="legData()?.direction === 'pay'" [class.receive]="legData()?.direction === 'receive'">
            {{ legData()?.direction === 'pay' ? 'PAY' : 'RECEIVE' }}
          </span>
          Leg {{ legData()?.legIndex }}
          <span class="leg-type">{{ legData()?.rateType === 'fixed' ? 'Fixed' : 'Floating' }}</span>
        </mat-card-title>
        @if (editMode()) {
          <button mat-icon-button color="warn" (click)="onDelete()" class="delete-button">
            <mat-icon>delete</mat-icon>
          </button>
        }
      </mat-card-header>
      
      <mat-card-content>
        <form [formGroup]="form" class="leg-form">
          <!-- Core Leg Information -->
          <div class="form-section">
            <h3 class="section-title">Leg Details</h3>

            <!-- Direction -->
            @if (hasField('direction')) {
              <mat-form-field appearance="outline">
                <mat-label>Direction</mat-label>
                @if (editMode()) {
                  <mat-select formControlName="direction">
                    <mat-option value="pay">Pay</mat-option>
                    <mat-option value="receive">Receive</mat-option>
                  </mat-select>
                } @else {
                  <input matInput [value]="legData()?.direction || ''" readonly />
                }
              </mat-form-field>
            }

            <!-- Currency -->
            @if (hasField('currency')) {
              <mat-form-field appearance="outline">
                <mat-label>Currency</mat-label>
                @if (editMode()) {
                  <input matInput formControlName="currency" />
                } @else {
                  <input matInput [value]="legData()?.currency || ''" readonly />
                }
              </mat-form-field>
            }

            <!-- Rate Type -->
            @if (hasField('rateType')) {
              <mat-form-field appearance="outline">
                <mat-label>Rate Type</mat-label>
                @if (editMode()) {
                  <mat-select formControlName="rateType">
                    <mat-option value="fixed">Fixed</mat-option>
                    <mat-option value="floating">Floating</mat-option>
                  </mat-select>
                } @else {
                  <input matInput [value]="legData()?.rateType || ''" readonly />
                }
              </mat-form-field>
            }

            <!-- Notional -->
            @if (hasField('notional')) {
              <mat-form-field appearance="outline">
                <mat-label>Notional</mat-label>
                @if (editMode()) {
                  <input matInput type="number" formControlName="notional" />
                } @else {
                  <input matInput [value]="legData()?.notional || 0" readonly />
                }
              </mat-form-field>
            }

            <!-- Start Date -->
            @if (hasField('startDate')) {
              <mat-form-field appearance="outline">
                <mat-label>Start Date</mat-label>
                @if (editMode()) {
                  <input matInput type="date" formControlName="startDate" />
                } @else {
                  <input matInput [value]="legData()?.startDate || ''" readonly />
                }
              </mat-form-field>
            }

            <!-- End Date -->
            @if (hasField('endDate')) {
              <mat-form-field appearance="outline">
                <mat-label>End Date</mat-label>
                @if (editMode()) {
                  <input matInput type="date" formControlName="endDate" />
                } @else {
                  <input matInput [value]="legData()?.endDate || ''" readonly />
                }
              </mat-form-field>
            }
          </div>

          <!-- Schedule Section -->
          <mat-expansion-panel class="schedule-panel" [expanded]="true">
            <mat-expansion-panel-header>
              <mat-panel-title>
                <mat-icon>calendar_today</mat-icon>
                Schedule ({{ legData()?.schedule?.length || 0 }} periods)
              </mat-panel-title>
            </mat-expansion-panel-header>

            <app-schedule-grid
              [scheduleData]="legData()?.schedule || []"
              [isEditable]="editMode()"
              (scheduleChange)="onScheduleChange($event)">
            </app-schedule-grid>
          </mat-expansion-panel>
        </form>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .swap-leg-card {
      border-left: 4px solid #ccc;
      
      &.pay-leg {
        border-left-color: #f44336;
      }

      &.receive-leg {
        border-left-color: #4caf50;
      }

      mat-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .delete-button {
        margin-left: auto;
      }
    }

    .leg-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 600;
      margin-right: 8px;

      &.pay {
        background-color: #ffebee;
        color: #c62828;
      }

      &.receive {
        background-color: #e8f5e9;
        color: #2e7d32;
      }
    }

    .leg-type {
      font-size: 14px;
      font-weight: 400;
      color: rgba(0, 0, 0, 0.6);
      margin-left: 8px;
    }

    .leg-form {
      width: 100%;
    }

    .form-section {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      margin-top: 16px;
    }

    .section-title {
      grid-column: span 2;
      font-size: 16px;
      font-weight: 500;
      margin: 8px 0;
      color: rgba(0, 0, 0, 0.87);
    }

    mat-form-field {
      width: 100%;
    }

    .schedule-panel {
      margin-top: 24px;
      
      mat-panel-title {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    @media (max-width: 768px) {
      .form-section {
        grid-template-columns: 1fr;
      }

      .section-title {
        grid-column: span 1;
      }
    }
  `]
})
export class SwapLegComponent implements OnInit {
  private fb = inject(FormBuilder);
  private fieldConfig = inject(TradeFieldConfigService);

  // ============================================================================
  // Inputs & Outputs
  // ============================================================================

  @Input() set leg(value: SwapLeg | undefined) {
    this._leg.set(value || null);
    if (value) {
      this.updateForm(value);
    }
  }

  @Input() set isEditMode(value: boolean) {
    this._isEditMode.set(value);
  }

  @Output() valueChange = new EventEmitter<SwapLeg>();
  @Output() deleteLeg = new EventEmitter<void>();

  // ============================================================================
  // Signals
  // ============================================================================

  private _leg = signal<SwapLeg | null>(null);
  private _isEditMode = signal<boolean>(false);

  legData = computed(() => this._leg());
  editMode = computed(() => this._isEditMode());

  // ============================================================================
  // Form
  // ============================================================================

  form: FormGroup = this.fb.group({
    direction: [''],
    currency: [''],
    rateType: [''],
    notional: [0],
    startDate: [''],
    endDate: ['']
  });

  // ============================================================================
  // Lifecycle
  // ============================================================================

  ngOnInit(): void {
    // Subscribe to form changes
    this.form.valueChanges.subscribe(value => {
      if (this._isEditMode()) {
        const currentLeg = this._leg();
        if (currentLeg) {
          const updatedLeg: SwapLeg = {
            ...currentLeg,
            ...value
          };
          this.valueChange.emit(updatedLeg);
        }
      }
    });
  }

  // ============================================================================
  // Event Handlers
  // ============================================================================

  onScheduleChange(updatedSchedule: SchedulePeriod[]): void {
    const currentLeg = this._leg();
    if (currentLeg) {
      const updatedLeg: SwapLeg = {
        ...currentLeg,
        schedule: updatedSchedule
      };
      this._leg.set(updatedLeg);
      this.valueChange.emit(updatedLeg);
    }
  }

  onDelete(): void {
    this.deleteLeg.emit();
  }

  // ============================================================================
  // Field Visibility
  // ============================================================================

  hasField(fieldName: string): boolean {
    return this.fieldConfig.hasField('swapLegs', fieldName);
  }

  // ============================================================================
  // Private Methods
  // ============================================================================

  private updateForm(leg: SwapLeg): void {
    this.form.patchValue({
      direction: leg.direction || '',
      currency: leg.currency || '',
      rateType: leg.rateType || '',
      notional: leg.notional || 0,
      startDate: leg.startDate || '',
      endDate: leg.endDate || ''
    }, { emitEvent: false });
  }
}
