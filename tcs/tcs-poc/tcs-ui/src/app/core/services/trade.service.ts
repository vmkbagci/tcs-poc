import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { tap, catchError, shareReplay } from 'rxjs/operators';
import { environment } from '@environments/environment';
import { TradeCore } from '@core/models/trade-core.model';

export type TradeType = 'ir-swap' | 'commodity-option' | 'index-swap';

export interface TradeResponse {
  success: boolean;
  trade_data?: TradeCore;
  errors?: string[];
  warnings?: string[];
  metadata?: Record<string, any>;
}

@Injectable({
  providedIn: 'root'
})
export class TradeService {
  private http = inject(HttpClient);
  private readonly apiUrl = environment.apiBaseUrl;

  // ============================================================================
  // Signal-based State
  // ============================================================================

  /**
   * Current trade being viewed
   */
  currentTrade = signal<TradeCore | null>(null);

  /**
   * List of trades (for trade list view)
   */
  trades = signal<TradeCore[]>([]);

  /**
   * Loading state for API operations
   */
  loading = signal<boolean>(false);

  /**
   * Error state for API operations
   */
  error = signal<string | null>(null);

  /**
   * Computed signal for checking if a trade is loaded
   */
  hasCurrentTrade = computed(() => this.currentTrade() !== null);

  // ============================================================================
  // Request Caching
  // ============================================================================

  /**
   * Cache for GET /new template requests
   * Key: trade_type, Value: Observable<TradeResponse>
   */
  private templateCache = new Map<string, Observable<TradeResponse>>();

  // ============================================================================
  // API Methods
  // ============================================================================

  /**
   * Get a new trade template for the specified trade type
   * Implements caching to avoid redundant API calls
   * 
   * @param tradeType - The type of trade (ir-swap, commodity-option, index-swap)
   * @returns Observable of TradeResponse containing the template
   */
  getNewTrade(tradeType: TradeType): Observable<TradeResponse> {
    // Check cache first
    if (this.templateCache.has(tradeType)) {
      return this.templateCache.get(tradeType)!;
    }

    this.loading.set(true);
    this.error.set(null);

    const params = new HttpParams().set('trade_type', tradeType);
    
    // Create the request and cache it using shareReplay
    const request$ = this.http.get<TradeResponse>(`${this.apiUrl}/trades/new`, { params })
      .pipe(
        tap(response => {
          if (response.success && response.trade_data) {
            this.currentTrade.set(response.trade_data);
          }
          this.loading.set(false);
        }),
        catchError(error => {
          this.loading.set(false);
          this.error.set(this.extractErrorMessage(error));
          return throwError(() => error);
        }),
        shareReplay(1) // Cache the result
      );

    // Store in cache
    this.templateCache.set(tradeType, request$);

    return request$;
  }

  /**
   * Get a trade by ID
   * Note: This endpoint may not be implemented in the current API
   * 
   * @param tradeId - The ID of the trade to retrieve
   * @returns Observable of TradeCore
   */
  getTrade(tradeId: string): Observable<TradeCore> {
    this.loading.set(true);
    this.error.set(null);

    return this.http.get<TradeCore>(`${this.apiUrl}/trades/${tradeId}`)
      .pipe(
        tap(trade => {
          this.currentTrade.set(trade);
          this.loading.set(false);
        }),
        catchError(error => {
          this.loading.set(false);
          this.error.set(this.extractErrorMessage(error));
          return throwError(() => error);
        })
      );
  }

  /**
   * Validate a trade by sending it to the /validate endpoint
   * 
   * @param tradeData - The trade data to validate
   * @returns Observable of the validation response (any type to capture full API response)
   */
  validateTrade(tradeData: any): Observable<any> {
    this.loading.set(true);
    this.error.set(null);

    // Wrap trade data in the expected format
    const payload = {
      trade_data: tradeData
    };

    return this.http.post<any>(`${this.apiUrl}/trades/validate`, payload)
      .pipe(
        tap(() => {
          this.loading.set(false);
        }),
        catchError(error => {
          this.loading.set(false);
          this.error.set(this.extractErrorMessage(error));
          return throwError(() => error);
        })
      );
  }

  // ============================================================================
  // State Management Methods
  // ============================================================================

  /**
   * Set the current trade
   * 
   * @param trade - The trade to set as current
   */
  setCurrentTrade(trade: TradeCore | null): void {
    this.currentTrade.set(trade);
  }

  /**
   * Clear the current trade
   */
  clearCurrentTrade(): void {
    this.currentTrade.set(null);
  }

  /**
   * Clear error state
   */
  clearError(): void {
    this.error.set(null);
  }

  /**
   * Clear template cache
   * Useful when you want to force a fresh fetch
   */
  clearTemplateCache(): void {
    this.templateCache.clear();
  }

  /**
   * Clear template cache for a specific trade type
   * 
   * @param tradeType - The trade type to clear from cache
   */
  clearTemplateCacheForType(tradeType: TradeType): void {
    this.templateCache.delete(tradeType);
  }

  // ============================================================================
  // Private Helper Methods
  // ============================================================================

  /**
   * Extract error message from HTTP error response
   * 
   * @param error - The error object
   * @returns User-friendly error message
   */
  private extractErrorMessage(error: any): string {
    if (error.error?.message) {
      return error.error.message;
    }
    if (error.error?.errors && Array.isArray(error.error.errors)) {
      return error.error.errors.join(', ');
    }
    if (error.message) {
      return error.message;
    }
    if (error.statusText) {
      return `${error.status}: ${error.statusText}`;
    }
    return 'An unexpected error occurred';
  }
}
