/**
 * Common Section Component
 * 
 * Presentational component for displaying and editing common trade fields.
 * Supports both view and edit modes with required field validation.
 */

import { Component, Input, Output, EventEmitter, signal, computed, effect, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { CommonSection } from '@core/models/trade-core.model';

@Component({
  selector: 'app-common-section',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCardModule,
    MatExpansionModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  template: `
    <mat-expansion-panel [expanded]="true">
      <mat-expansion-panel-header>
        <mat-panel-title>
          Common Information
        </mat-panel-title>
      </mat-expansion-panel-header>

      <div class="section-content">
        @if (commonData()) {
          <form [formGroup]="form" class="common-form">
            <!-- Core Fields -->
            <div class="form-section">
              <h3 class="section-title">Core Information</h3>
              
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Book *</mat-label>
                @if (editMode()) {
                  <mat-select formControlName="book">
                    @for (book of bookOptions; track book) {
                      <mat-option [value]="book">{{ book }}</mat-option>
                    }
                  </mat-select>
                } @else {
                  <input matInput [value]="form.get('book')?.value" readonly>
                }
                @if (form.get('book')?.hasError('required') && form.get('book')?.touched) {
                  <mat-error>Book is required</mat-error>
                }
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Counterparty *</mat-label>
                @if (editMode()) {
                  <mat-select formControlName="counterparty">
                    @for (cp of counterpartyOptions; track cp) {
                      <mat-option [value]="cp">{{ cp }}</mat-option>
                    }
                  </mat-select>
                } @else {
                  <input matInput [value]="form.get('counterparty')?.value" readonly>
                }
                @if (form.get('counterparty')?.hasError('required') && form.get('counterparty')?.touched) {
                  <mat-error>Counterparty is required</mat-error>
                }
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Trade Date *</mat-label>
                @if (editMode()) {
                  <input 
                    matInput 
                    [matDatepicker]="tradeDatePicker"
                    formControlName="tradeDate">
                  <mat-datepicker-toggle matIconSuffix [for]="tradeDatePicker"></mat-datepicker-toggle>
                  <mat-datepicker #tradeDatePicker></mat-datepicker>
                  @if (form.get('tradeDate')?.hasError('required') && form.get('tradeDate')?.touched) {
                    <mat-error>Trade Date is required</mat-error>
                  }
                } @else {
                  <input matInput [value]="form.get('tradeDate')?.value" readonly>
                }
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Input Date</mat-label>
                @if (editMode()) {
                  <input 
                    matInput 
                    [matDatepicker]="inputDatePicker"
                    formControlName="inputDate">
                  <mat-datepicker-toggle matIconSuffix [for]="inputDatePicker"></mat-datepicker-toggle>
                  <mat-datepicker #inputDatePicker></mat-datepicker>
                } @else {
                  <input matInput [value]="form.get('inputDate')?.value" readonly>
                }
              </mat-form-field>
            </div>

            <!-- Additional Fields -->
            <mat-expansion-panel [expanded]="false" class="subsection-panel">
              <mat-expansion-panel-header>
                <mat-panel-title>Additional Information</mat-panel-title>
              </mat-expansion-panel-header>
              
              <div class="form-section">
                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Account Reference</mat-label>
                  <input 
                    matInput 
                    formControlName="accountReference"
                    [readonly]="!editMode()">
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Novated To Counterparty</mat-label>
                  <input 
                    matInput 
                    formControlName="novatedToCounterparty"
                    [readonly]="!editMode()">
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Counterparty Account Reference</mat-label>
                  <input 
                    matInput 
                    formControlName="counterpartyAccountReference"
                    [readonly]="!editMode()">
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width span-2">
                  <mat-label>Comment</mat-label>
                  <textarea 
                    matInput 
                    formControlName="comment"
                    [readonly]="!editMode()"
                    rows="3"></textarea>
                </mat-form-field>
              </div>
            </mat-expansion-panel>

            <!-- Trading Details -->
            <mat-expansion-panel [expanded]="false" class="subsection-panel">
              <mat-expansion-panel-header>
                <mat-panel-title>Trading Details</mat-panel-title>
              </mat-expansion-panel-header>
              
              <div class="form-section">
                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Trading Strategy</mat-label>
                  <input 
                    matInput 
                    formControlName="tradingStrategy"
                    [readonly]="!editMode()">
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Sales Group</mat-label>
                  <input 
                    matInput 
                    formControlName="salesGroup"
                    [readonly]="!editMode()">
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Region or Account</mat-label>
                  <input 
                    matInput 
                    formControlName="regionOrAccount"
                    [readonly]="!editMode()">
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Originating System</mat-label>
                  <input 
                    matInput 
                    formControlName="originatingSystem"
                    [readonly]="!editMode()">
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>Source System</mat-label>
                  <input 
                    matInput 
                    formControlName="sourceSystem"
                    [readonly]="!editMode()">
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>DDE Eligible</mat-label>
                  <input 
                    matInput 
                    formControlName="ddeEligible"
                    [readonly]="!editMode()">
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>STP</mat-label>
                  <input 
                    matInput 
                    formControlName="stp"
                    [readonly]="!editMode()">
                </mat-form-field>

                <mat-form-field appearance="outline" class="full-width">
                  <mat-label>ISDA Definition</mat-label>
                  <input 
                    matInput 
                    formControlName="ISDADefinition"
                    [readonly]="!editMode()">
                </mat-form-field>
              </div>
            </mat-expansion-panel>

            <!-- References -->
            <div class="form-section">
              <h3 class="section-title">References</h3>
              
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>External Reference</mat-label>
                <input 
                  matInput 
                  formControlName="externalReference"
                  [readonly]="!editMode()">
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Internal Reference</mat-label>
                <input 
                  matInput 
                  formControlName="internalReference"
                  [readonly]="!editMode()">
              </mat-form-field>
            </div>

            <!-- Flags -->
            <div class="form-section">
              <h3 class="section-title">Flags</h3>
              
              <div class="checkbox-field">
                <label>
                  <input 
                    type="checkbox" 
                    formControlName="cashflowHedgeNotification"
                    [disabled]="!editMode()">
                  Cashflow Hedge Notification
                </label>
              </div>

              <div class="checkbox-field">
                <label>
                  <input 
                    type="checkbox" 
                    formControlName="IRDAdvisory"
                    [disabled]="!editMode()">
                  IRD Advisory
                </label>
              </div>

              <div class="checkbox-field">
                <label>
                  <input 
                    type="checkbox" 
                    formControlName="isCustomBasket"
                    [disabled]="!editMode()">
                  Is Custom Basket
                </label>
              </div>
            </div>

            <!-- Events Display (Read-only) -->
            @if (commonData()?.events && commonData()?.events!.length > 0) {
              <div class="form-section">
                <h3 class="section-title">Events</h3>
                <div class="span-2">
                  @for (event of commonData()?.events; track event.correlationId) {
                    <div class="event-item">
                      <span class="event-code">{{ event.eventCode }}</span>
                      <span class="event-desc">{{ event.eventDescription }}</span>
                      <span class="event-app">{{ event.application }}</span>
                    </div>
                  }
                </div>
              </div>
            }
          </form>
        } @else {
          <p class="no-data">No common information available</p>
        }
      </div>
    </mat-expansion-panel>
  `,
  styles: [`
    .section-content {
      padding: 16px 0;
    }

    .common-form {
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

    .span-2 {
      grid-column: 1 / -1;
    }

    .checkbox-field {
      padding: 8px 0;

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

    .event-item {
      display: flex;
      gap: 12px;
      padding: 8px;
      background-color: white;
      border-radius: 4px;
      margin-bottom: 8px;
    }

    .event-code {
      font-weight: 500;
      color: #1976d2;
    }

    .event-desc {
      flex: 1;
      color: rgba(0, 0, 0, 0.87);
    }

    .event-app {
      color: rgba(0, 0, 0, 0.6);
      font-size: 12px;
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
    input[readonly],
    textarea[readonly] {
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
export class CommonSectionComponent implements OnInit {
  private fb = new FormBuilder();

  // ============================================================================
  // Data Options
  // ============================================================================

  /**
   * Book options for dropdown
   */
  bookOptions = [
    'RATES-DESK-NY',
    'RATES-DESK-LON',
    'RATES-DESK-TKY',
    'CREDIT-DESK-NY',
    'CREDIT-DESK-LON',
    'FX-DESK-NY',
    'FX-DESK-LON',
    'COMMODITIES-NY',
    'EQUITY-DESK-NY',
    'MEWEST01HS'
  ];

  /**
   * Counterparty options for dropdown
   */
  counterpartyOptions = [
    'Goldman Sachs',
    'JP Morgan',
    'Morgan Stanley',
    'Citigroup',
    'Bank of America',
    'Deutsche Bank',
    'Barclays',
    'UBS',
    'Credit Suisse',
    '02519916'
  ];

  // ============================================================================
  // Inputs & Outputs
  // ============================================================================

  /**
   * Common section data
   */
  @Input() set commonSection(value: CommonSection | undefined) {
    this.commonData.set(value || null);
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
  @Output() valueChange = new EventEmitter<CommonSection>();

  // ============================================================================
  // Signals
  // ============================================================================

  /**
   * Common section data signal
   */
  commonData = signal<CommonSection | null>(null);

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
   * Reactive form for common section
   */
  form: FormGroup;

  // ============================================================================
  // Constructor
  // ============================================================================

  constructor() {
    // Initialize form with required field validators
    this.form = this.fb.group({
      // Core Fields (Required)
      book: ['', Validators.required],
      counterparty: ['', Validators.required],
      tradeDate: ['', Validators.required],
      inputDate: [''],
      
      // Additional Fields
      accountReference: [''],
      novatedToCounterparty: [''],
      counterpartyAccountReference: [''],
      comment: [''],
      
      // Trading Details
      tradingStrategy: [''],
      salesGroup: [''],
      regionOrAccount: [''],
      originatingSystem: [''],
      sourceSystem: [''],
      ddeEligible: [''],
      stp: [''],
      ISDADefinition: [''],
      
      // References
      externalReference: [''],
      internalReference: [''],
      
      // Flags
      cashflowHedgeNotification: [false],
      IRDAdvisory: [false],
      isCustomBasket: [false]
    });

    // Effect to populate form when data changes
    effect(() => {
      const data = this.commonData();
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
    const data = this.commonData();
    if (data) {
      this.populateForm(data);
    }
  }

  // ============================================================================
  // Private Methods
  // ============================================================================

  /**
   * Populate form with common section data
   * 
   * @param data - Common section data
   */
  private populateForm(data: CommonSection): void {
    this.form.patchValue({
      // Core Fields
      book: data.book || '',
      counterparty: data.counterparty || '',
      tradeDate: data.tradeDate || '',
      inputDate: data.inputDate || '',
      
      // Additional Fields
      accountReference: data.accountReference || '',
      novatedToCounterparty: data.novatedToCounterparty || '',
      counterpartyAccountReference: data.counterpartyAccountReference || '',
      comment: data.comment || '',
      
      // Trading Details
      tradingStrategy: data.tradingStrategy || '',
      salesGroup: data.salesGroup || '',
      regionOrAccount: data.regionOrAccount || '',
      originatingSystem: data.originatingSystem || '',
      sourceSystem: data.sourceSystem || '',
      ddeEligible: data.ddeEligible || '',
      stp: data.stp || '',
      ISDADefinition: data.ISDADefinition || '',
      
      // References
      externalReference: data.externalReference || '',
      internalReference: data.internalReference || '',
      
      // Flags
      cashflowHedgeNotification: data.cashflowHedgeNotification || false,
      IRDAdvisory: data.IRDAdvisory || false,
      isCustomBasket: data.isCustomBasket || false
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
    const currentData = this.commonData();

    // Reconstruct common section with updated values
    const updatedCommon: CommonSection = {
      ...currentData,
      // Core Fields
      book: formValue.book,
      counterparty: formValue.counterparty,
      tradeDate: formValue.tradeDate,
      inputDate: formValue.inputDate,
      
      // Additional Fields
      accountReference: formValue.accountReference,
      novatedToCounterparty: formValue.novatedToCounterparty,
      counterpartyAccountReference: formValue.counterpartyAccountReference,
      comment: formValue.comment,
      
      // Trading Details
      tradingStrategy: formValue.tradingStrategy,
      salesGroup: formValue.salesGroup,
      regionOrAccount: formValue.regionOrAccount,
      originatingSystem: formValue.originatingSystem,
      sourceSystem: formValue.sourceSystem,
      ddeEligible: formValue.ddeEligible,
      stp: formValue.stp,
      ISDADefinition: formValue.ISDADefinition,
      
      // References
      externalReference: formValue.externalReference,
      internalReference: formValue.internalReference,
      
      // Flags
      cashflowHedgeNotification: formValue.cashflowHedgeNotification,
      IRDAdvisory: formValue.IRDAdvisory,
      isCustomBasket: formValue.isCustomBasket
    };

    this.valueChange.emit(updatedCommon);
  }
}
