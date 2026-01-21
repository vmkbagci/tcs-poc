/**
 * Trade Detail Component
 * 
 * Smart component for displaying and editing trade details.
 * Handles loading trades by ID, edit mode toggle, and save operations.
 */

import { Component, signal, computed, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { TradeService, TradeFieldConfigService } from '@core/services';
import { TradeCore } from '@core/models/trade-core.model';
import { IRSwapTrade } from '@core/models/ir-swap.model';
import { TradeCoreComponent } from './components/trade-core.component';
import { IRSwapDetailComponent } from '../ir-swap-detail/ir-swap-detail.component';
import { JsonPreviewDialogComponent } from './components/json-preview-dialog.component';
import { ValidationPanelComponent } from './components/validation-panel.component';

@Component({
  selector: 'app-trade-detail',
  standalone: true,
  imports: [
    CommonModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    MatSnackBarModule,
    MatDialogModule,
    TradeCoreComponent,
    IRSwapDetailComponent,
    ValidationPanelComponent
  ],
  providers: [TradeFieldConfigService], // ← New instance per trade
  templateUrl: './trade-detail.component.html',
  styleUrls: ['./trade-detail.component.scss']
})
export class TradeDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private tradeService = inject(TradeService);
  private snackBar = inject(MatSnackBar);
  private dialog = inject(MatDialog);
  private fieldConfig = inject(TradeFieldConfigService); // ← Inject instance

  // ============================================================================
  // Signals
  // ============================================================================

  /**
   * Current trade being viewed
   */
  trade = signal<TradeCore | null>(null);

  /**
   * Trade type from route query params
   */
  tradeType = signal<string>('ir-swap');

  /**
   * Edit mode flag
   */
  editMode = signal<boolean>(false);

  /**
   * Loading state
   */
  loading = computed(() => this.tradeService.loading());

  /**
   * Error state
   */
  error = computed(() => this.tradeService.error());

  /**
   * Trade ID from route params
   */
  tradeId = signal<string | null>(null);

  /**
   * Computed signal for checking if trade is loaded
   */
  tradeLoaded = computed(() => this.trade() !== null);

  /**
   * Computed signal for checking if form is dirty
   */
  hasUnsavedChanges = signal<boolean>(false);

  /**
   * API validation response
   */
  validationResponse = signal<any>(null);

  // ============================================================================
  // Lifecycle Hooks
  // ============================================================================

  ngOnInit(): void {
    // Get trade ID from route params
    this.route.params.subscribe(params => {
      const id = params['id'];
      
      if (id) {
        this.tradeId.set(id);
        
        // Special handling for new trade creation
        if (id === 'new-trade') {
          // Use the trade from the service (loaded by TradeCreateComponent)
          const currentTrade = this.tradeService.currentTrade();
          
          if (currentTrade) {
            this.trade.set(currentTrade);
            // Automatically enable edit mode for new trades
            this.editMode.set(true);
            // Set trade type for field configuration
            this.setTradeTypeFromRoute();
          } else {
            // No trade in service, redirect back to create page
            this.snackBar.open('No trade template loaded', 'Close', {
              duration: 3000
            });
            this.router.navigate(['/trades/new']);
          }
        } else {
          // Load existing trade by ID
          this.loadTrade(id);
        }
      }
    });
  }

  // ============================================================================
  // Private Helper Methods
  // ============================================================================

  /**
   * Set trade type in field config service based on route query params
   */
  private setTradeTypeFromRoute(): void {
    this.route.queryParams.subscribe(params => {
      const tradeType = params['trade_type'] || 'ir-swap'; // Default to ir-swap
      this.tradeType.set(tradeType);
      this.fieldConfig.setTradeType(tradeType);
    });
  }

  // ============================================================================
  // Event Handlers
  // ============================================================================

  /**
   * Handle back to home button click
   * Navigates back to home page
   */
  onBackToHome(): void {
    this.router.navigate(['/']);
  }

  /**
   * Toggle edit mode
   */
  onToggleEdit(): void {
    this.editMode.update(mode => !mode);
  }

  /**
   * Handle trade core value changes
   * 
   * @param updatedTrade - Updated trade core data
   */
  onTradeChange(updatedTrade: TradeCore): void {
    this.trade.set(updatedTrade);
    this.hasUnsavedChanges.set(true);
  }

  /**
   * Save trade changes
   */
  onSave(): void {
    const currentTrade = this.trade();
    if (!currentTrade) {
      return;
    }

    // TODO: Implement save to API
    this.snackBar.open('Save functionality not yet implemented', 'Close', {
      duration: 3000
    });
    
    // For now, just mark as saved
    this.hasUnsavedChanges.set(false);
    this.editMode.set(false);
  }

  /**
   * Validate trade by sending to API
   */
  onValidate(): void {
    const currentTrade = this.trade();
    if (!currentTrade) {
      this.snackBar.open('No trade data to validate', 'Close', {
        duration: 3000
      });
      return;
    }

    // Prepare JSON payload
    const payload = currentTrade;

    // Send to /validate endpoint
    this.tradeService.validateTrade(payload).subscribe({
      next: (response) => {
        this.validationResponse.set(response);
        this.snackBar.open('Validation complete', 'Close', {
          duration: 2000
        });
      },
      error: (error) => {
        console.error('Validation error:', error);
        // Still show the error response
        this.validationResponse.set(error.error || { error: error.message });
        this.snackBar.open('Validation request completed (see response panel)', 'Close', {
          duration: 3000
        });
      }
    });
  }

  /**
   * Handle validation panel close
   */
  onValidationPanelClosed(): void {
    this.validationResponse.set(null);
  }

  /**
   * Show trade data as JSON in a dialog
   */
  onShowAsJson(): void {
    const currentTrade = this.trade();
    if (!currentTrade) {
      this.snackBar.open('No trade data to display', 'Close', {
        duration: 3000
      });
      return;
    }

    // Prepare the payload that would be sent to validate endpoint
    const payload = {
      trade_data: currentTrade
    };

    // Open dialog with JSON preview
    this.dialog.open(JsonPreviewDialogComponent, {
      width: '800px',
      maxWidth: '95vw',
      maxHeight: '90vh',
      data: {
        title: 'Trade JSON Payload',
        jsonData: payload
      }
    });
  }

  /**
   * Cancel edit mode
   */
  onCancel(): void {
    if (this.hasUnsavedChanges()) {
      const confirmed = confirm('You have unsaved changes. Are you sure you want to cancel?');
      if (!confirmed) {
        return;
      }
    }
    
    // Reload the trade to discard changes
    const id = this.tradeId();
    if (id && id !== 'new-trade') {
      this.loadTrade(id);
    } else {
      // For new trades, reload from service
      const currentTrade = this.tradeService.currentTrade();
      if (currentTrade) {
        this.trade.set(currentTrade);
      }
    }
    
    this.editMode.set(false);
    this.hasUnsavedChanges.set(false);
  }

  // ============================================================================
  // API Methods
  // ============================================================================

  /**
   * Load trade by ID from API
   * 
   * @param tradeId - The ID of the trade to load
   */
  private loadTrade(tradeId: string): void {
    this.tradeService.getTrade(tradeId).subscribe({
      next: (trade) => {
        this.trade.set(trade);
        // Set trade type for field configuration
        this.setTradeTypeFromRoute();
        this.snackBar.open('Trade loaded successfully', 'Close', {
          duration: 2000
        });
      },
      error: (error) => {
        console.error('Error loading trade:', error);
        this.snackBar.open('Error loading trade. This endpoint may not be implemented yet.', 'Close', {
          duration: 5000
        });
      }
    });
  }
}
