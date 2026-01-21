/**
 * General Section Component
 * 
 * Presentational component for displaying and editing general trade fields.
 * Supports both view and edit modes with field validation.
 */

import { Component, Input, Output, EventEmitter, signal, computed, effect, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCardModule } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { GeneralSection } from '@core/models/trade-core.model';

@Component({
  selector: 'app-general-section',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatCardModule,
    MatExpansionModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  template: `
    <mat-expansion-panel [expanded]="true">
      <mat-expansion-panel-header>
        <mat-panel-title>
          General Information
        </mat-panel-title>
      </mat-expansion-panel-header>

      <div class="section-content">
        @if (generalData()) {
          <form [formGroup]="form" class="general-form">
            <!-- Trade Key Section -->
            <div class="form-section">
              <h3 class="section-title">Trade Key</h3>
              
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Trade ID</mat-label>
                <input 
                  matInput 
                  formControlName="tradeId"
                  [readonly]="!editMode()">
                @if (form.get('tradeId')?.hasError('required') && form.get('tradeId')?.touched) {
                  <mat-error>Trade ID is required</mat-error>
                }
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Label</mat-label>
                <input 
                  matInput 
                  formControlName="label"
                  [readonly]="!editMode()">
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Co-Located ID</mat-label>
                <input 
                  matInput 
                  formControlName="coLocatedId"
                  [readonly]="!editMode()">
              </mat-form-field>
            </div>

            <!-- Transaction Roles Section -->
            @if (generalData()?.transactionRoles) {
              <mat-expansion-panel [expanded]="false" class="subsection-panel">
                <mat-expansion-panel-header>
                  <mat-panel-title>Transaction Roles</mat-panel-title>
                </mat-expansion-panel-header>
                
                <div class="form-section">
                  <mat-form-field appearance="outline" class="full-width">
                    <mat-label>Price Maker</mat-label>
                    <input 
                      matInput 
                      formControlName="priceMaker"
                      [readonly]="!editMode()">
                  </mat-form-field>

                  <mat-form-field appearance="outline" class="full-width">
                    <mat-label>Marketer</mat-label>
                    <input 
                      matInput 
                      formControlName="marketer"
                      [readonly]="!editMode()">
                  </mat-form-field>

                  <mat-form-field appearance="outline" class="full-width">
                    <mat-label>Transaction Originator</mat-label>
                    <input 
                      matInput 
                      formControlName="transactionOriginator"
                      [readonly]="!editMode()">
                  </mat-form-field>

                  <mat-form-field appearance="outline" class="full-width">
                    <mat-label>Transaction Acceptor</mat-label>
                    <input 
                      matInput 
                      formControlName="transactionAcceptor"
                      [readonly]="!editMode()">
                  </mat-form-field>
                </div>
              </mat-expansion-panel>
            }

            <!-- Execution Details Section -->
            @if (generalData()?.executionDetails) {
              <div class="form-section">
                <h3 class="section-title">Execution Details</h3>
                
                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Execution Date Time</mat-label>
                  @if (editMode()) {
                    <input 
                      matInput 
                      [matDatepicker]="executionDateTimePicker"
                      formControlName="executionDateTime"
                      placeholder="Select date and time">
                    <mat-datepicker-toggle matIconSuffix [for]="executionDateTimePicker"></mat-datepicker-toggle>
                    <mat-datepicker #executionDateTimePicker></mat-datepicker>
                  } @else {
                    <input matInput [value]="formatDateTime(form.get('executionDateTime')?.value)" readonly>
                  }
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Execution Venue Type</mat-label>
                  <input 
                    matInput 
                    formControlName="executionVenueType"
                    [readonly]="!editMode()">
                </mat-form-field>

                <div class="checkbox-field">
                  <label>
                    <input 
                      type="checkbox" 
                      formControlName="isOffMarketPrice"
                      [disabled]="!editMode()">
                    Is Off Market Price
                  </label>
                </div>
              </div>
            }

            <!-- Package Trade Details Section -->
            @if (generalData()?.packageTradeDetails) {
              <div class="form-section">
                <h3 class="section-title">Package Trade Details</h3>
                
                <div class="checkbox-field">
                  <label>
                    <input 
                      type="checkbox" 
                      formControlName="isPackageTrade"
                      [disabled]="!editMode()">
                    Is Package Trade
                  </label>
                </div>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Package Identifier</mat-label>
                  <input 
                    matInput 
                    formControlName="packageIdentifier"
                    [readonly]="!editMode()">
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Package Type</mat-label>
                  <input 
                    matInput 
                    formControlName="packageType"
                    [readonly]="!editMode()">
                </mat-form-field>
              </div>
            }
          </form>
        } @else {
          <p class="no-data">No general information available</p>
        }
      </div>
    </mat-expansion-panel>
  `,
  styles: [`
    .section-content {
      padding: 16px 0;
    }

    .general-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .form-section {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      padding: 16px;
      background-color: #f9f9f9;
      border-radius: 4px;
    }

    .section-title {
      grid-column: 1 / -1;
      margin: 0 0 8px 0;
      font-size: 16px;
      font-weight: 500;
      color: rgba(0, 0, 0, 0.87);
    }

    .subsection-panel {
      margin-bottom: 16px;

      .form-section {
        margin: 0;
      }
    }

    .full-width {
      width: 100%;
    }

    .checkbox-field {
      padding: 8px 0;
      grid-column: 1 / -1;

      label {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        font-size: 14px;

        input[type="checkbox"] {
          width: 18px;
          height: 18px;
          cursor: pointer;
        }

        input[type="checkbox"]:disabled {
          cursor: not-allowed;
        }
      }
    }

    .no-data {
      padding: 24px;
      text-align: center;
      color: rgba(0, 0, 0, 0.6);
      font-style: italic;
    }

    mat-form-field {
      mat-error {
        font-size: 12px;
      }
    }

    // Readonly input styling
    input[readonly] {
      cursor: default;
      color: rgba(0, 0, 0, 0.6);
    }

    // Responsive layout
    @media (max-width: 768px) {
      .form-section {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class GeneralSectionComponent implements OnInit {
  private fb = new FormBuilder();

  // ============================================================================
  // Inputs & Outputs
  // ============================================================================

  /**
   * General section data
   */
  @Input() set generalSection(value: GeneralSection | undefined) {
    this.generalData.set(value || null);
  }

  /**
   * Edit mode flag
   */
  @Input() set isEditMode(value: boolean) {
    this.editMode.set(value);
  }

  /**
   * Event emitted when form values change
   */
  @Output() valueChange = new EventEmitter<GeneralSection>();

  // ============================================================================
  // Signals
  // ============================================================================

  /**
   * General section data signal
   */
  generalData = signal<GeneralSection | null>(null);

  /**
   * Edit mode signal
   */
  editMode = signal<boolean>(false);

  /**
   * Form validity signal
   */
  isValid = computed(() => this.form.valid);

  // ============================================================================
  // Form
  // ============================================================================

  /**
   * Reactive form for general section
   */
  form: FormGroup;

  // ============================================================================
  // Constructor
  // ============================================================================

  constructor() {
    // Initialize form
    this.form = this.fb.group({
      // Trade Key
      tradeId: ['', Validators.required],
      label: [''],
      coLocatedId: [''],
      
      // Transaction Roles
      priceMaker: [''],
      marketer: [''],
      transactionOriginator: [''],
      transactionAcceptor: [''],
      
      // Execution Details
      executionDateTime: [''],
      executionVenueType: [''],
      isOffMarketPrice: [false],
      
      // Package Trade Details
      isPackageTrade: [false],
      packageIdentifier: [''],
      packageType: ['']
    });

    // Effect to populate form when data changes
    effect(() => {
      const data = this.generalData();
      if (data) {
        this.populateForm(data);
      }
    });

    // Effect to enable/disable form based on edit mode
    effect(() => {
      if (this.editMode()) {
        this.form.enable();
      } else {
        this.form.disable();
      }
    });

    // Subscribe to form value changes
    this.form.valueChanges.subscribe(() => {
      if (this.editMode()) {
        this.emitChanges();
      }
    });
  }

  ngOnInit(): void {
    // Initial form population
    const data = this.generalData();
    if (data) {
      this.populateForm(data);
    }
  }

  // ============================================================================
  // Private Methods
  // ============================================================================

  /**
   * Format date-time for display
   * 
   * @param value - Date value (string or Date object)
   * @returns Formatted date-time string
   */
  formatDateTime(value: any): string {
    if (!value) {
      return '';
    }
    
    if (value instanceof Date) {
      return value.toISOString();
    }
    
    return value.toString();
  }

  /**
   * Populate form with general section data
   * 
   * @param data - General section data
   */
  private populateForm(data: GeneralSection): void {
    const transactionRoles = data.transactionRoles || {};
    const executionDetails = data.executionDetails || {};
    const packageTradeDetails = data.packageTradeDetails || {};

    this.form.patchValue({
      // Trade Key
      tradeId: data.tradeId || '',
      label: data.label || '',
      coLocatedId: data.coLocatedId || '',
      
      // Transaction Roles
      priceMaker: transactionRoles.priceMaker || '',
      marketer: transactionRoles.marketer || '',
      transactionOriginator: transactionRoles.transactionOriginator || '',
      transactionAcceptor: transactionRoles.transactionAcceptor || '',
      
      // Execution Details
      executionDateTime: executionDetails.executionDateTime || '',
      executionVenueType: executionDetails.executionVenue?.executionVenueType || '',
      isOffMarketPrice: executionDetails.isOffMarketPrice || false,
      
      // Package Trade Details
      isPackageTrade: packageTradeDetails.isPackageTrade || false,
      packageIdentifier: packageTradeDetails.packageIdentifier || '',
      packageType: packageTradeDetails.packageType || ''
    }, { emitEvent: false });
  }

  /**
   * Emit form changes to parent component
   */
  private emitChanges(): void {
    if (!this.form.valid) {
      return;
    }

    const formValue = this.form.value;
    const currentData = this.generalData();

    // Reconstruct general section with updated values
    const updatedGeneral: GeneralSection = {
      ...currentData,
      tradeId: formValue.tradeId,
      label: formValue.label,
      coLocatedId: formValue.coLocatedId,
      transactionRoles: {
        ...currentData?.transactionRoles,
        priceMaker: formValue.priceMaker || null,
        marketer: formValue.marketer || null,
        transactionOriginator: formValue.transactionOriginator || null,
        transactionAcceptor: formValue.transactionAcceptor || null
      },
      executionDetails: {
        ...currentData?.executionDetails,
        executionDateTime: formValue.executionDateTime,
        isOffMarketPrice: formValue.isOffMarketPrice,
        executionVenue: {
          ...currentData?.executionDetails?.executionVenue,
          executionVenueType: formValue.executionVenueType
        }
      },
      packageTradeDetails: {
        ...currentData?.packageTradeDetails,
        isPackageTrade: formValue.isPackageTrade,
        packageIdentifier: formValue.packageIdentifier,
        packageType: formValue.packageType
      }
    };

    this.valueChange.emit(updatedGeneral);
  }
}
