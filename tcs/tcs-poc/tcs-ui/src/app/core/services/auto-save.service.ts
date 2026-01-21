/**
 * Auto-Save Service
 * 
 * Manages automatic saving of form data with pluggable storage backend.
 * Default implementation uses browser localStorage, but can be configured
 * to use API storage (Redis cache) for future implementations.
 */

import { Injectable, Signal, effect, inject, EffectRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { TradeCore } from '@core/models/trade-core.model';
import { environment } from '@environments/environment';

// ============================================================================
// Storage Backend Interface
// ============================================================================

/**
 * Interface for auto-save storage backends
 * Allows pluggable storage implementations (localStorage, API, etc.)
 */
export interface IAutoSaveStorage {
  /**
   * Save trade data to storage
   * @param key - Storage key
   * @param data - Trade data to save
   */
  save(key: string, data: TradeCore): Promise<void> | void;

  /**
   * Load trade data from storage
   * @param key - Storage key
   * @returns Trade data or null if not found
   */
  load(key: string): Promise<TradeCore | null> | TradeCore | null;

  /**
   * Clear trade data from storage
   * @param key - Storage key
   */
  clear(key: string): Promise<void> | void;
}

// ============================================================================
// LocalStorage Backend (Default)
// ============================================================================

/**
 * LocalStorage implementation of IAutoSaveStorage
 * Stores trade data in browser's localStorage
 */
export class LocalStorageBackend implements IAutoSaveStorage {
  save(key: string, data: TradeCore): void {
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  }

  load(key: string): TradeCore | null {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Failed to load from localStorage:', error);
      return null;
    }
  }

  clear(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to clear from localStorage:', error);
    }
  }
}

// ============================================================================
// API Storage Backend (Future Implementation)
// ============================================================================

/**
 * API-based implementation of IAutoSaveStorage
 * Stores trade data on the server (e.g., Redis cache)
 * 
 * FUTURE IMPLEMENTATION:
 * This backend will communicate with the Trade API to store auto-save data
 * on the server, enabling cross-device auto-save synchronization.
 * 
 * Required API endpoints:
 * - POST /api/v1/trades/autosave - Save draft
 * - GET /api/v1/trades/autosave/:key - Load draft
 * - DELETE /api/v1/trades/autosave/:key - Clear draft
 */
export class ApiStorageBackend implements IAutoSaveStorage {
  private readonly apiUrl = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  async save(key: string, data: TradeCore): Promise<void> {
    try {
      await this.http.post(`${this.apiUrl}/trades/autosave`, { key, data }).toPromise();
    } catch (error) {
      console.error('Failed to save to API storage:', error);
      throw error;
    }
  }

  async load(key: string): Promise<TradeCore | null> {
    try {
      const response = await this.http.get<{ data: TradeCore }>(`${this.apiUrl}/trades/autosave/${key}`).toPromise();
      return response?.data || null;
    } catch (error) {
      console.error('Failed to load from API storage:', error);
      return null;
    }
  }

  async clear(key: string): Promise<void> {
    try {
      await this.http.delete(`${this.apiUrl}/trades/autosave/${key}`).toPromise();
    } catch (error) {
      console.error('Failed to clear from API storage:', error);
      throw error;
    }
  }
}

// ============================================================================
// Auto-Save Service
// ============================================================================

@Injectable({
  providedIn: 'root'
})
export class AutoSaveService {
  private http = inject(HttpClient);

  /**
   * Current storage backend
   * Default: LocalStorageBackend
   */
  private storageBackend: IAutoSaveStorage = new LocalStorageBackend();

  /**
   * Auto-save interval in milliseconds
   * Default: 30 seconds
   */
  private readonly AUTO_SAVE_INTERVAL = 30000;

  /**
   * Auto-save timer reference
   */
  private autoSaveTimer: any = null;

  /**
   * Current trade signal being auto-saved
   */
  private currentTradeSignal: Signal<TradeCore> | null = null;

  /**
   * Effect reference for cleanup
   */
  private effectRef: EffectRef | null = null;

  // ============================================================================
  // Configuration Methods
  // ============================================================================

  /**
   * Set the storage backend
   * Allows switching between localStorage and API storage
   * 
   * @param backend - The storage backend to use
   * 
   * @example
   * // Use localStorage (default)
   * autoSaveService.setStorageBackend(new LocalStorageBackend());
   * 
   * @example
   * // Use API storage
   * autoSaveService.setStorageBackend(new ApiStorageBackend(httpClient));
   */
  setStorageBackend(backend: IAutoSaveStorage): void {
    this.storageBackend = backend;
  }

  // ============================================================================
  // Auto-Save Methods
  // ============================================================================

  /**
   * Start auto-saving form data
   * Sets up a periodic timer to save trade data every 30 seconds
   * 
   * @param formData - Signal containing the trade data to auto-save
   * 
   * @example
   * const tradeSignal = signal<TradeCore>(initialTrade);
   * autoSaveService.startAutoSave(tradeSignal);
   */
  startAutoSave(formData: Signal<TradeCore>): void {
    // Stop any existing auto-save
    this.stopAutoSave();

    this.currentTradeSignal = formData;

    // Set up periodic auto-save
    this.autoSaveTimer = setInterval(() => {
      this.performAutoSave();
    }, this.AUTO_SAVE_INTERVAL);

    // Also set up an effect to save on changes (debounced by the interval)
    this.effectRef = effect(() => {
      // Access the signal to track changes
      const trade = formData();
      // The actual save happens in the interval timer
    });
  }

  /**
   * Stop auto-saving
   * Clears the auto-save timer and effect
   */
  stopAutoSave(): void {
    if (this.autoSaveTimer) {
      clearInterval(this.autoSaveTimer);
      this.autoSaveTimer = null;
    }

    if (this.effectRef) {
      this.effectRef.destroy();
      this.effectRef = null;
    }

    this.currentTradeSignal = null;
  }

  /**
   * Perform an immediate auto-save
   * Saves the current trade data to storage
   */
  private async performAutoSave(): Promise<void> {
    if (!this.currentTradeSignal) {
      return;
    }

    const trade = this.currentTradeSignal();
    const key = this.generateAutoSaveKey(trade);

    try {
      await this.storageBackend.save(key, trade);
      console.log('Auto-save successful:', key);
    } catch (error) {
      console.error('Auto-save failed:', error);
    }
  }

  // ============================================================================
  // Data Retrieval Methods
  // ============================================================================

  /**
   * Get auto-saved data for a trade
   * 
   * @param tradeId - Optional trade ID. If not provided, uses 'new'
   * @returns Promise resolving to Trade data or null if not found
   * 
   * @example
   * // Get auto-saved data for a new trade
   * const data = await autoSaveService.getAutoSavedData();
   * 
   * @example
   * // Get auto-saved data for an existing trade
   * const data = await autoSaveService.getAutoSavedData('TRADE-123');
   */
  async getAutoSavedData(tradeId?: string): Promise<TradeCore | null> {
    const key = this.generateAutoSaveKey(tradeId);
    
    try {
      return await this.storageBackend.load(key);
    } catch (error) {
      console.error('Failed to get auto-saved data:', error);
      return null;
    }
  }

  /**
   * Check if auto-saved data exists for a trade
   * 
   * @param tradeId - Optional trade ID. If not provided, uses 'new'
   * @returns Promise resolving to true if auto-saved data exists
   */
  async hasAutoSavedData(tradeId?: string): Promise<boolean> {
    const data = await this.getAutoSavedData(tradeId);
    return data !== null;
  }

  // ============================================================================
  // Data Cleanup Methods
  // ============================================================================

  /**
   * Clear auto-saved data for a trade
   * 
   * @param tradeId - Optional trade ID. If not provided, uses 'new'
   * 
   * @example
   * // Clear auto-saved data for a new trade
   * await autoSaveService.clearAutoSavedData();
   * 
   * @example
   * // Clear auto-saved data for an existing trade
   * await autoSaveService.clearAutoSavedData('TRADE-123');
   */
  async clearAutoSavedData(tradeId?: string): Promise<void> {
    const key = this.generateAutoSaveKey(tradeId);
    
    try {
      await this.storageBackend.clear(key);
      console.log('Auto-saved data cleared:', key);
    } catch (error) {
      console.error('Failed to clear auto-saved data:', error);
    }
  }

  // ============================================================================
  // Private Helper Methods
  // ============================================================================

  /**
   * Generate auto-save key for a trade
   * 
   * @param tradeOrId - Trade object or trade ID string
   * @returns Auto-save key in format: trade-autosave-{id}
   */
  private generateAutoSaveKey(tradeOrId?: TradeCore | string): string {
    let tradeId = 'new';

    if (typeof tradeOrId === 'string') {
      tradeId = tradeOrId;
    } else if (tradeOrId && typeof tradeOrId === 'object') {
      const trade = tradeOrId as TradeCore;
      tradeId = trade.general?.tradeId || 'new';
    }

    return `trade-autosave-${tradeId}`;
  }
}

// ============================================================================
// Usage Examples and Documentation
// ============================================================================

/**
 * USAGE EXAMPLES:
 * 
 * 1. Basic usage with localStorage (default):
 * ```typescript
 * const tradeSignal = signal<TradeCore>(initialTrade);
 * autoSaveService.startAutoSave(tradeSignal);
 * 
 * // Later, when component is destroyed
 * autoSaveService.stopAutoSave();
 * ```
 * 
 * 2. Check for auto-saved data on component init:
 * ```typescript
 * async ngOnInit() {
 *   const autoSavedData = await this.autoSaveService.getAutoSavedData();
 *   if (autoSavedData) {
 *     // Show dialog to restore
 *     const restore = await this.showRestoreDialog();
 *     if (restore) {
 *       this.trade.set(autoSavedData);
 *     } else {
 *       await this.autoSaveService.clearAutoSavedData();
 *     }
 *   }
 * }
 * ```
 * 
 * 3. Clear auto-save after successful save:
 * ```typescript
 * this.tradeService.saveTrade(trade).subscribe({
 *   next: async (response) => {
 *     if (response.success) {
 *       await this.autoSaveService.clearAutoSavedData(trade.general?.tradeId);
 *     }
 *   }
 * });
 * ```
 * 
 * 4. Switch to API storage backend:
 * ```typescript
 * const apiBackend = new ApiStorageBackend(this.http);
 * this.autoSaveService.setStorageBackend(apiBackend);
 * ```
 * 
 * FUTURE API INTEGRATION:
 * 
 * When the backend API implements auto-save endpoints, you can switch to
 * API storage by creating an instance of ApiStorageBackend:
 * 
 * ```typescript
 * // In app initialization or configuration
 * const httpClient = inject(HttpClient);
 * const apiBackend = new ApiStorageBackend(httpClient);
 * autoSaveService.setStorageBackend(apiBackend);
 * ```
 * 
 * This will enable:
 * - Cross-device auto-save synchronization
 * - Server-side storage with Redis cache
 * - Better data persistence and recovery
 * - Centralized auto-save management
 */
