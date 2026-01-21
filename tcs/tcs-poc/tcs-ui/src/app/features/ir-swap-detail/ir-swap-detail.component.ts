/**
 * IR Swap Detail Component
 * 
 * Container component for IR Swap specific data.
 * Displays SwapDetails and SwapLegs sections.
 */

import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { IRSwapTrade } from '@core/models/ir-swap.model';
import { SwapDetailsComponent } from './components/swap-details.component';
import { SwapLegsComponent } from './components/swap-legs.component';

@Component({
  selector: 'app-ir-swap-detail',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    SwapDetailsComponent,
    SwapLegsComponent
  ],
  template: `
    <div class="ir-swap-detail-container">
      <!-- Swap Details Section -->
      <app-swap-details
        [swapDetails]="trade()?.swapDetails"
        [isEditMode]="isEditMode()"
        (valueChange)="onSwapDetailsChange($event)">
      </app-swap-details>

      <!-- Swap Legs Section -->
      <app-swap-legs
        [swapLegs]="trade()?.swapLegs || []"
        [isEditMode]="isEditMode()"
        (valueChange)="onSwapLegsChange($event)">
      </app-swap-legs>
    </div>
  `,
  styles: [`
    .ir-swap-detail-container {
      display: flex;
      flex-direction: column;
      gap: 24px;
      width: 100%;
    }
  `]
})
export class IRSwapDetailComponent {
  
  /**
   * IR Swap trade data
   */
  @Input() set tradeData(value: IRSwapTrade | null) {
    this.trade.set(value);
  }

  /**
   * Edit mode flag
   */
  @Input() set editMode(value: boolean) {
    this.isEditMode.set(value);
  }

  /**
   * Event emitted when trade data changes
   */
  @Output() valueChange = new EventEmitter<IRSwapTrade>();

  // ============================================================================
  // Signals
  // ============================================================================

  trade = signal<IRSwapTrade | null>(null);
  isEditMode = signal<boolean>(false);

  // ============================================================================
  // Event Handlers
  // ============================================================================

  /**
   * Handle swap details changes
   */
  onSwapDetailsChange(updatedDetails: any): void {
    const currentTrade = this.trade();
    if (!currentTrade) return;

    const updatedTrade: IRSwapTrade = {
      ...currentTrade,
      swapDetails: updatedDetails
    };

    this.trade.set(updatedTrade);
    this.valueChange.emit(updatedTrade);
  }

  /**
   * Handle swap legs changes
   */
  onSwapLegsChange(updatedLegs: any[]): void {
    const currentTrade = this.trade();
    if (!currentTrade) return;

    const updatedTrade: IRSwapTrade = {
      ...currentTrade,
      swapLegs: updatedLegs
    };

    this.trade.set(updatedTrade);
    this.valueChange.emit(updatedTrade);
  }
}
