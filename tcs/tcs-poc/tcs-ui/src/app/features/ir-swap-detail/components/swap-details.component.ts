/**
 * Swap Details Component
 * 
 * Displays and edits swap-level details (swapDetails section).
 * Uses field configuration service to determine which fields to show.
 */

import { Component, Input, Output, EventEmitter, signal, computed, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { SwapDetails } from '@core/models/swap.model';
import { TradeFieldConfigService } from '@core/services';

@Component({
  selector: 'app-swap-details',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule
  ],
  template: `
    <mat-card class="swap-details-card">
      <mat-card-header>
        <mat-card-title>Swap Details</mat-card-title>
      </mat-card-header>
      
      <mat-card-content>
        <form [formGroup]="form" class="swap-details-form">
          <div class="form-section">
            <!-- Underlying -->
            @if (hasField('underlying')) {
              <mat-form-field appearance="outline">
                <mat-label>Underlying</mat-label>
                @if (editMode()) {
                  <input matInput formControlName="underlying" />
                } @else {
                  <input matInput [value]="swapDetailsData()?.underlying || ''" readonly />
                }
              </mat-form-field>
            }

            <!-- Settlement Type -->
            @if (hasField('settlementType')) {
              <mat-form-field appearance="outline">
                <mat-label>Settlement Type</mat-label>
                @if (editMode()) {
                  <mat-select formControlName="settlementType">
                    <mat-option value="physical">Physical</mat-option>
                    <mat-option value="cash">Cash</mat-option>
                  </mat-select>
                } @else {
                  <input matInput [value]="swapDetailsData()?.settlementType || ''" readonly />
                }
              </mat-form-field>
            }

            <!-- Swap Type -->
            @if (hasField('swapType')) {
              <mat-form-field appearance="outline">
                <mat-label>Swap Type</mat-label>
                @if (editMode()) {
                  <mat-select formControlName="swapType">
                    <mat-option value="irsOis">IRS OIS</mat-option>
                    <mat-option value="irsVanilla">IRS Vanilla</mat-option>
                    <mat-option value="irsBasis">IRS Basis</mat-option>
                  </mat-select>
                } @else {
                  <input matInput [value]="swapDetailsData()?.swapType || ''" readonly />
                }
              </mat-form-field>
            }

            <!-- Is Cleared -->
            @if (hasField('isCleared')) {
              <div class="checkbox-field">
                @if (editMode()) {
                  <mat-checkbox formControlName="isCleared">
                    Is Cleared
                  </mat-checkbox>
                } @else {
                  <mat-checkbox [checked]="swapDetailsData()?.isCleared || false" disabled>
                    Is Cleared
                  </mat-checkbox>
                }
              </div>
            }

            <!-- Principal Exchange (IR Swap specific) -->
            @if (hasField('principalExchange')) {
              <mat-form-field appearance="outline">
                <mat-label>Principal Exchange</mat-label>
                @if (editMode()) {
                  <mat-select formControlName="principalExchange">
                    <mat-option value="none">None</mat-option>
                    <mat-option value="firstLastLegs">First & Last Legs</mat-option>
                    <mat-option value="allLegs">All Legs</mat-option>
                  </mat-select>
                } @else {
                  <input matInput [value]="swapDetailsData()?.principalExchange || ''" readonly />
                }
              </mat-form-field>
            }

            <!-- Is ISDA Fallback (IR Swap specific) -->
            @if (hasField('isIsdaFallback')) {
              <div class="checkbox-field">
                @if (editMode()) {
                  <mat-checkbox formControlName="isIsdaFallback">
                    Is ISDA Fallback
                  </mat-checkbox>
                } @else {
                  <mat-checkbox [checked]="swapDetailsData()?.isIsdaFallback || false" disabled>
                    Is ISDA Fallback
                  </mat-checkbox>
                }
              </div>
            }
          </div>
        </form>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .swap-details-card {
      margin-bottom: 16px;
    }

    .swap-details-form {
      width: 100%;
    }

    .form-section {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      margin-top: 16px;
    }

    .checkbox-field {
      grid-column: span 2;
      padding: 8px 0;
    }

    mat-form-field {
      width: 100%;
    }

    @media (max-width: 768px) {
      .form-section {
        grid-template-columns: 1fr;
      }

      .checkbox-field {
        grid-column: span 1;
      }
    }
  `]
})
export class SwapDetailsComponent implements OnInit {
  private fb = inject(FormBuilder);
  private fieldConfig = inject(TradeFieldConfigService);

  // ============================================================================
  // Inputs & Outputs
  // ============================================================================

  @Input() set swapDetails(value: SwapDetails | undefined) {
    this._swapDetails.set(value || null);
    if (value) {
      this.updateForm(value);
    }
  }

  @Input() set isEditMode(value: boolean) {
    this._isEditMode.set(value);
  }

  @Output() valueChange = new EventEmitter<SwapDetails>();

  // ============================================================================
  // Signals
  // ============================================================================

  private _swapDetails = signal<SwapDetails | null>(null);
  private _isEditMode = signal<boolean>(false);

  swapDetailsData = computed(() => this._swapDetails());
  editMode = computed(() => this._isEditMode());

  // ============================================================================
  // Form
  // ============================================================================

  form: FormGroup = this.fb.group({
    underlying: [''],
    settlementType: [''],
    swapType: [''],
    isCleared: [false],
    principalExchange: [''],
    isIsdaFallback: [false]
  });

  // ============================================================================
  // Lifecycle
  // ============================================================================

  ngOnInit(): void {
    // Subscribe to form changes
    this.form.valueChanges.subscribe(value => {
      if (this._isEditMode()) {
        this.valueChange.emit(value);
      }
    });
  }

  // ============================================================================
  // Field Visibility
  // ============================================================================

  hasField(fieldName: string): boolean {
    return this.fieldConfig.hasField('swapDetails', fieldName);
  }

  // ============================================================================
  // Private Methods
  // ============================================================================

  private updateForm(details: SwapDetails): void {
    this.form.patchValue({
      underlying: details.underlying || '',
      settlementType: details.settlementType || '',
      swapType: details.swapType || '',
      isCleared: details.isCleared || false,
      principalExchange: details.principalExchange || '',
      isIsdaFallback: details.isIsdaFallback || false
    }, { emitEvent: false });
  }
}
