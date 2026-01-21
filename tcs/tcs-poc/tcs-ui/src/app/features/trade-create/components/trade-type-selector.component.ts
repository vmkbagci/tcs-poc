/**
 * Trade Type Selector Component
 * 
 * Presentational component for selecting trade type during trade creation.
 * Displays available trade types and emits the selected type to parent component.
 */

import { Component, output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatRadioModule } from '@angular/material/radio';
import { MatCardModule } from '@angular/material/card';
import { FormsModule } from '@angular/forms';
import { TradeType } from '@core/models';

/**
 * Trade type option with display information
 */
interface TradeTypeOption {
  value: TradeType;
  label: string;
  description: string;
}

@Component({
  selector: 'app-trade-type-selector',
  standalone: true,
  imports: [
    CommonModule,
    MatRadioModule,
    MatCardModule,
    FormsModule
  ],
  template: `
    <mat-card class="trade-type-selector">
      <mat-card-header>
        <mat-card-title>Select Trade Type</mat-card-title>
        <mat-card-subtitle>Choose the type of trade you want to create</mat-card-subtitle>
      </mat-card-header>
      
      <mat-card-content>
        <mat-radio-group 
          [(ngModel)]="selectedType"
          (ngModelChange)="onSelectionChange($event)"
          class="trade-type-options">
          <mat-radio-button 
            *ngFor="let option of tradeTypeOptions" 
            [value]="option.value"
            class="trade-type-option">
            <div class="option-content">
              <span class="option-label">{{ option.label }}</span>
              <span class="option-description">{{ option.description }}</span>
            </div>
          </mat-radio-button>
        </mat-radio-group>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .trade-type-selector {
      max-width: 600px;
      margin: 20px auto;
    }

    .trade-type-options {
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin-top: 16px;
    }

    .trade-type-option {
      padding: 12px;
      border: 1px solid #e0e0e0;
      border-radius: 4px;
      transition: all 0.2s ease;
    }

    .trade-type-option:hover {
      background-color: #f5f5f5;
      border-color: #1976d2;
    }

    .trade-type-option.mat-mdc-radio-button-checked {
      background-color: #e3f2fd;
      border-color: #1976d2;
    }

    .option-content {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-left: 8px;
    }

    .option-label {
      font-weight: 500;
      font-size: 16px;
      color: #333;
    }

    .option-description {
      font-size: 14px;
      color: #666;
    }

    ::ng-deep .trade-type-option .mdc-radio {
      align-self: flex-start;
      margin-top: 4px;
    }
  `]
})
export class TradeTypeSelectorComponent {
  /**
   * Available trade type options
   */
  tradeTypeOptions: TradeTypeOption[] = [
    {
      value: 'ir-swap',
      label: 'Interest Rate Swap',
      description: 'Exchange fixed and floating interest rate payments'
    },
    {
      value: 'commodity-option',
      label: 'Commodity Option',
      description: 'Option contract on commodity prices'
    },
    {
      value: 'index-swap',
      label: 'Index Swap',
      description: 'Swap based on equity or commodity index performance'
    }
  ];

  /**
   * Currently selected trade type
   */
  selectedType = signal<TradeType | null>(null);

  /**
   * Output event when trade type is selected
   */
  tradeTypeSelected = output<TradeType>();

  /**
   * Handle selection change
   * 
   * @param tradeType - The selected trade type
   */
  onSelectionChange(tradeType: TradeType): void {
    this.selectedType.set(tradeType);
    this.tradeTypeSelected.emit(tradeType);
  }

  /**
   * Get the currently selected trade type
   * 
   * @returns The selected trade type or null
   */
  getSelectedType(): TradeType | null {
    return this.selectedType();
  }
}
