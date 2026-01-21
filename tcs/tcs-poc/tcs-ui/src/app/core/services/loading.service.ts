import { Injectable, signal } from '@angular/core';

/**
 * Service for managing global loading state
 * Uses Angular Signals for reactive state management
 */
@Injectable({
  providedIn: 'root'
})
export class LoadingService {
  // Track the number of active HTTP requests
  private activeRequests = signal<number>(0);

  // Public signal for loading state
  public readonly loading = signal<boolean>(false);

  /**
   * Increment the active request counter and set loading to true
   */
  show(): void {
    this.activeRequests.update(count => count + 1);
    this.loading.set(true);
  }

  /**
   * Decrement the active request counter
   * Set loading to false when no active requests remain
   */
  hide(): void {
    this.activeRequests.update(count => {
      const newCount = Math.max(0, count - 1);
      if (newCount === 0) {
        this.loading.set(false);
      }
      return newCount;
    });
  }

  /**
   * Reset the loading state (useful for error recovery)
   */
  reset(): void {
    this.activeRequests.set(0);
    this.loading.set(false);
  }
}
