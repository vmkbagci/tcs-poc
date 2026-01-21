/**
 * Trade Create Component
 * 
 * Smart component for creating new trades from templates.
 * Handles trade type selection and navigation to trade detail.
 */

import { Component, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { TradeService, TradeType } from '@core/services';
import { TradeTypeSelectorComponent } from './components/trade-type-selector.component';

@Component({
  selector: 'app-trade-create',
  standalone: true,
  imports: [
    CommonModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatCardModule,
    MatSnackBarModule,
    TradeTypeSelectorComponent
  ],
  templateUrl: './trade-create.component.html',
  styleUrls: ['./trade-create.component.scss']
})
export class TradeCreateComponent {
  private tradeService = inject(TradeService);
  private router = inject(Router);
  private snackBar = inject(MatSnackBar);

  // ============================================================================
  // Signals
  // ============================================================================

  /**
   * Selected trade type
   */
  selectedTradeType = signal<TradeType | null>(null);

  /**
   * Loading state
   */
  loading = computed(() => this.tradeService.loading());

  /**
   * Error state
   */
  error = computed(() => this.tradeService.error());

  // ============================================================================
  // Event Handlers
  // ============================================================================

  /**
   * Handle trade type selection
   * Loads the trade template from the API and navigates to trade detail
   * 
   * @param tradeType - The selected trade type
   */
  onTradeTypeSelected(tradeType: TradeType): void {
    this.selectedTradeType.set(tradeType);
    this.loadTradeTemplateAndNavigate(tradeType);
  }

  /**
   * Handle cancel action
   * Navigates back to home
   */
  onCancel(): void {
    this.router.navigate(['/']);
  }

  // ============================================================================
  // API Methods
  // ============================================================================

  /**
   * Load trade template from API and navigate to trade detail component
   * 
   * @param tradeType - The trade type to load
   */
  private loadTradeTemplateAndNavigate(tradeType: TradeType): void {
    this.tradeService.getNewTrade(tradeType).subscribe({
      next: (response) => {
        if (response.success && response.trade_data) {
          // The TradeService already sets currentTrade in its tap operator
          // Navigate to trade detail component with 'new-trade' as the ID
          this.router.navigate(['/trades', 'new-trade']).then(
            (success) => {
              if (success) {
                this.snackBar.open('Trade template loaded', 'Close', {
                  duration: 2000
                });
              } else {
                this.snackBar.open('Navigation failed', 'Close', {
                  duration: 3000
                });
              }
            },
            (error) => {
              console.error('TradeCreateComponent - Navigation error:', error);
              this.snackBar.open('Navigation error', 'Close', {
                duration: 3000
              });
            }
          );
        } else {
          this.snackBar.open('Failed to load trade template', 'Close', {
            duration: 5000
          });
        }
      },
      error: (error) => {
        console.error('Error loading trade template:', error);
        this.snackBar.open('Error loading trade template', 'Close', {
          duration: 5000
        });
      }
    });
  }
}
