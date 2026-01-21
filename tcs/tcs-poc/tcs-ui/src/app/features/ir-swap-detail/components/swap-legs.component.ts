/**
 * Swap Legs Component
 * 
 * Container component for displaying all swap legs.
 * Each leg is displayed using SwapLegComponent.
 */

import { Component, Input, Output, EventEmitter, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { SwapLeg } from '@core/models/swap.model';
import { SwapLegComponent } from './swap-leg.component';

@Component({
  selector: 'app-swap-legs',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    SwapLegComponent
  ],
  template: `
    <mat-card class="swap-legs-card">
      <mat-card-header>
        <mat-card-title>Swap Legs</mat-card-title>
        @if (editMode()) {
          <button mat-icon-button color="primary" (click)="onAddLeg()" class="add-leg-button">
            <mat-icon>add</mat-icon>
          </button>
        }
      </mat-card-header>
      
      <mat-card-content>
        @if (swapLegsData().length > 0) {
          <div class="legs-container">
            @for (leg of swapLegsData(); track leg.legIndex) {
              <app-swap-leg
                [leg]="leg"
                [isEditMode]="editMode()"
                (valueChange)="onLegChange($index, $event)"
                (deleteLeg)="onDeleteLeg($index)">
              </app-swap-leg>
            }
          </div>
        } @else {
          <div class="no-legs">
            <mat-icon>info</mat-icon>
            <p>No swap legs available</p>
            @if (editMode()) {
              <button mat-raised-button color="primary" (click)="onAddLeg()">
                <mat-icon>add</mat-icon>
                Add Leg
              </button>
            }
          </div>
        }
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .swap-legs-card {
      margin-bottom: 16px;

      mat-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .add-leg-button {
        margin-left: auto;
      }
    }

    .legs-container {
      display: flex;
      flex-direction: column;
      gap: 24px;
      margin-top: 16px;
    }

    .no-legs {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px 24px;
      text-align: center;
      background-color: #fafafa;
      border: 1px dashed #ccc;
      border-radius: 4px;
      margin-top: 16px;

      mat-icon {
        font-size: 48px;
        width: 48px;
        height: 48px;
        color: rgba(0, 0, 0, 0.38);
        margin-bottom: 16px;
      }

      p {
        margin: 8px 0 16px 0;
        color: rgba(0, 0, 0, 0.6);
        font-size: 14px;
      }
    }
  `]
})
export class SwapLegsComponent {
  
  /**
   * Swap legs data
   */
  @Input() set swapLegs(value: SwapLeg[]) {
    this._swapLegs.set(value || []);
  }

  /**
   * Edit mode flag
   */
  @Input() set isEditMode(value: boolean) {
    this._isEditMode.set(value);
  }

  /**
   * Event emitted when legs change
   */
  @Output() valueChange = new EventEmitter<SwapLeg[]>();

  // ============================================================================
  // Signals
  // ============================================================================

  private _swapLegs = signal<SwapLeg[]>([]);
  private _isEditMode = signal<boolean>(false);

  swapLegsData = computed(() => this._swapLegs());
  editMode = computed(() => this._isEditMode());

  // ============================================================================
  // Event Handlers
  // ============================================================================

  /**
   * Handle leg change
   */
  onLegChange(index: number, updatedLeg: SwapLeg): void {
    const currentLegs = this._swapLegs();
    const updatedLegs = [...currentLegs];
    updatedLegs[index] = updatedLeg;
    
    this._swapLegs.set(updatedLegs);
    this.valueChange.emit(updatedLegs);
  }

  /**
   * Handle add leg
   */
  onAddLeg(): void {
    const currentLegs = this._swapLegs();
    const newLegIndex = currentLegs.length;
    
    const newLeg: SwapLeg = {
      legIndex: newLegIndex,
      direction: 'pay',
      currency: 'USD',
      rateType: 'fixed',
      notional: 0,
      startDate: '',
      endDate: '',
      schedule: []
    };

    const updatedLegs = [...currentLegs, newLeg];
    this._swapLegs.set(updatedLegs);
    this.valueChange.emit(updatedLegs);
  }

  /**
   * Handle delete leg
   */
  onDeleteLeg(index: number): void {
    const currentLegs = this._swapLegs();
    const updatedLegs = currentLegs.filter((_, i) => i !== index);
    
    // Reindex legs
    const reindexedLegs = updatedLegs.map((leg, i) => ({
      ...leg,
      legIndex: i
    }));

    this._swapLegs.set(reindexedLegs);
    this.valueChange.emit(reindexedLegs);
  }
}
