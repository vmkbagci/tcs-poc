import { Component, OnInit, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltipModule } from '@angular/material/tooltip';

import { TradeService } from '@core/services/trade.service';
import { TradeCore } from '@core/models/trade-core.model';
import { TradeType } from '@core/services/trade.service';
import { TradeFilters } from '@core/models/filter.model';
import { TradeFilterComponent } from './components/trade-filter.component';

/**
 * Trade List Component
 * 
 * Displays a list of trades with filtering, sorting, and pagination capabilities.
 * Implements signal-based state management for reactive updates.
 * 
 * Features:
 * - Material table with sortable columns
 * - Pagination controls
 * - Row click navigation to trade detail
 * - Loading and error states
 * - Filter integration (via child component)
 */
@Component({
  selector: 'app-trade-list',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatProgressSpinnerModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatToolbarModule,
    MatTooltipModule,
    TradeFilterComponent
  ],
  templateUrl: './trade-list.component.html',
  styleUrls: ['./trade-list.component.scss']
})
export class TradeListComponent implements OnInit {
  private tradeService = inject(TradeService);
  private router = inject(Router);

  // ============================================================================
  // Signals - Component State
  // ============================================================================

  /**
   * All trades loaded from the service
   */
  trades = this.tradeService.trades;

  /**
   * Current filter criteria
   */
  filters = signal<TradeFilters>({});

  /**
   * Loading state
   */
  loading = this.tradeService.loading;

  /**
   * Error state
   */
  error = this.tradeService.error;

  /**
   * Current page index (0-based)
   */
  pageIndex = signal<number>(0);

  /**
   * Page size
   */
  pageSize = signal<number>(10);

  /**
   * Sort field and direction
   */
  sortField = signal<string>('');
  sortDirection = signal<'asc' | 'desc' | ''>('');

  // ============================================================================
  // Computed Signals - Derived State
  // ============================================================================

  /**
   * Filtered trades based on current filter criteria
   */
  filteredTrades = computed(() => {
    const allTrades = this.trades();
    const currentFilters = this.filters();

    // If no filters are applied, return all trades
    if (!this.hasActiveFilters(currentFilters)) {
      return allTrades;
    }

    // Apply filters
    return allTrades.filter((trade: TradeCore) => {
      // Trade Type Filter
      if (currentFilters.tradeType) {
        const tradeType = this.getTradeType(trade);
        const filterType = this.mapTradeTypeToDisplay(currentFilters.tradeType);
        if (tradeType !== filterType) {
          return false;
        }
      }

      // Book Filter
      if (currentFilters.book) {
        const book = this.getBook(trade).toLowerCase();
        const filterBook = currentFilters.book.toLowerCase();
        if (!book.includes(filterBook)) {
          return false;
        }
      }

      // Counterparty Filter
      if (currentFilters.counterparty) {
        const counterparty = this.getCounterparty(trade).toLowerCase();
        const filterCounterparty = currentFilters.counterparty.toLowerCase();
        if (!counterparty.includes(filterCounterparty)) {
          return false;
        }
      }

      // Date Range Filter
      if (currentFilters.dateRange) {
        const tradeDate = this.getTradeDate(trade);
        if (tradeDate) {
          const tradeDateObj = new Date(tradeDate);
          
          if (currentFilters.dateRange.startDate) {
            const startDate = new Date(currentFilters.dateRange.startDate);
            if (tradeDateObj < startDate) {
              return false;
            }
          }
          
          if (currentFilters.dateRange.endDate) {
            const endDate = new Date(currentFilters.dateRange.endDate);
            // Set end date to end of day for inclusive comparison
            endDate.setHours(23, 59, 59, 999);
            if (tradeDateObj > endDate) {
              return false;
            }
          }
        }
      }

      // Search Text Filter (searches across multiple fields)
      if (currentFilters.searchText) {
        const searchText = currentFilters.searchText.toLowerCase();
        const tradeId = this.getTradeId(trade).toLowerCase();
        const label = this.getTradeLabel(trade).toLowerCase();
        const book = this.getBook(trade).toLowerCase();
        const counterparty = this.getCounterparty(trade).toLowerCase();
        const tradeType = this.getTradeType(trade).toLowerCase();
        
        const matchesSearch = 
          tradeId.includes(searchText) ||
          label.includes(searchText) ||
          book.includes(searchText) ||
          counterparty.includes(searchText) ||
          tradeType.includes(searchText);
        
        if (!matchesSearch) {
          return false;
        }
      }

      return true;
    });
  });

  /**
   * Sorted trades based on current sort criteria
   */
  sortedTrades = computed(() => {
    const trades = [...this.filteredTrades()];
    const field = this.sortField();
    const direction = this.sortDirection();

    if (!field || !direction) {
      return trades;
    }

    return trades.sort((a, b) => {
      const aValue = this.getNestedValue(a, field);
      const bValue = this.getNestedValue(b, field);

      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      const comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      return direction === 'asc' ? comparison : -comparison;
    });
  });

  /**
   * Paginated trades for current page
   */
  paginatedTrades = computed(() => {
    const trades = this.sortedTrades();
    const startIndex = this.pageIndex() * this.pageSize();
    const endIndex = startIndex + this.pageSize();
    return trades.slice(startIndex, endIndex);
  });

  /**
   * Total number of filtered trades
   */
  totalTrades = computed(() => this.filteredTrades().length);

  /**
   * Whether there are any trades to display
   */
  hasTrades = computed(() => this.trades().length > 0);

  // ============================================================================
  // Table Configuration
  // ============================================================================

  /**
   * Columns to display in the table
   */
  displayedColumns: string[] = [
    'tradeId',
    'label',
    'tradeType',
    'book',
    'counterparty',
    'tradeDate',
    'actions'
  ];

  /**
   * Page size options for paginator
   */
  pageSizeOptions: number[] = [5, 10, 25, 50, 100];

  // ============================================================================
  // Lifecycle Hooks
  // ============================================================================

  ngOnInit(): void {
    this.loadTrades();
  }

  // ============================================================================
  // Public Methods
  // ============================================================================

  /**
   * Load trades from the service
   * Note: The API endpoint may not be fully implemented yet
   */
  loadTrades(): void {
    // For now, we'll use mock data since the API endpoint may not be implemented
    // In production, this would call: this.tradeService.listTrades(this.filters())
    
    // Mock data for demonstration
    const mockTrades: TradeCore[] = [
      {
        general: {
          tradeId: 'TRADE-001',
          label: 'IR Swap USD 10Y'
        },
        common: {
          book: 'RATES-DESK',
          counterparty: 'Goldman Sachs',
          tradeDate: '2024-01-15'
        }
      },
      {
        general: {
          tradeId: 'TRADE-002',
          label: 'Commodity Option Gold'
        },
        common: {
          book: 'COMMODITIES',
          counterparty: 'JP Morgan',
          tradeDate: '2024-01-16'
        }
      },
      {
        general: {
          tradeId: 'TRADE-003',
          label: 'Index Swap S&P500'
        },
        common: {
          book: 'EQUITY-DESK',
          counterparty: 'Morgan Stanley',
          tradeDate: '2024-01-17'
        }
      }
    ];

    // Set mock trades
    this.tradeService.trades.set(mockTrades);

    // Uncomment when API is ready:
    // this.tradeService.listTrades(this.filters()).subscribe({
    //   next: (trades) => {
    //     // Trades are automatically set in the service
    //   },
    //   error: (error) => {
    //     console.error('Error loading trades:', error);
    //   }
    // });
  }

  /**
   * Handle row click - navigate to trade detail
   * 
   * @param trade - The trade that was clicked
   */
  onRowClick(trade: TradeCore): void {
    const tradeId = trade.general?.tradeId;
    if (tradeId) {
      this.router.navigate(['/trades', tradeId]);
    }
  }

  /**
   * Handle page change event from paginator
   * 
   * @param event - Page event containing new page index and size
   */
  onPageChange(event: PageEvent): void {
    this.pageIndex.set(event.pageIndex);
    this.pageSize.set(event.pageSize);
  }

  /**
   * Handle sort change event from table
   * 
   * @param sort - Sort event containing field and direction
   */
  onSortChange(sort: Sort): void {
    this.sortField.set(sort.active);
    this.sortDirection.set(sort.direction);
  }

  /**
   * Handle filter change from filter component
   * This will be connected in subtask 6.2
   * 
   * @param filters - New filter criteria
   */
  onFilterChange(filters: TradeFilters): void {
    this.filters.set(filters);
    this.pageIndex.set(0); // Reset to first page when filters change
  }

  /**
   * Navigate to create new trade
   */
  onCreateTrade(): void {
    this.router.navigate(['/trades/new']);
  }

  /**
   * Refresh the trade list
   */
  onRefresh(): void {
    this.loadTrades();
  }

  // ============================================================================
  // Helper Methods
  // ============================================================================

  /**
   * Get trade type from trade data
   * 
   * @param trade - The trade object
   * @returns Trade type string or 'Unknown'
   */
  getTradeType(trade: TradeCore): string {
    // For TradeCore, we don't have swap-specific data
    // This would need to be determined from a separate field or API
    // For now, return a placeholder
    return 'Trade';
  }

  /**
   * Get nested value from object using dot notation
   * 
   * @param obj - The object to extract value from
   * @param path - Dot-separated path to the value
   * @returns The value at the path or null
   */
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, prop) => current?.[prop], obj);
  }

  /**
   * Get trade ID for display
   * 
   * @param trade - The trade object
   * @returns Trade ID or empty string
   */
  getTradeId(trade: TradeCore): string {
    return trade.general?.tradeId || '';
  }

  /**
   * Get trade label for display
   * 
   * @param trade - The trade object
   * @returns Trade label or empty string
   */
  getTradeLabel(trade: TradeCore): string {
    return trade.general?.label || '';
  }

  /**
   * Get book for display
   * 
   * @param trade - The trade object
   * @returns Book or empty string
   */
  getBook(trade: TradeCore): string {
    return trade.common?.book || '';
  }

  /**
   * Get counterparty for display
   * 
   * @param trade - The trade object
   * @returns Counterparty or empty string
   */
  getCounterparty(trade: TradeCore): string {
    return trade.common?.counterparty || '';
  }

  /**
   * Get trade date for display
   * 
   * @param trade - The trade object
   * @returns Trade date or empty string
   */
  getTradeDate(trade: TradeCore): string {
    return trade.common?.tradeDate || '';
  }

  /**
   * Check if any filters are active
   * 
   * @param filters - The filter criteria
   * @returns True if any filters are applied
   */
  private hasActiveFilters(filters: TradeFilters): boolean {
    return !!(
      filters.tradeType ||
      filters.book ||
      filters.counterparty ||
      filters.dateRange ||
      filters.searchText
    );
  }

  /**
   * Map trade type enum to display string
   * 
   * @param tradeType - The trade type enum value
   * @returns Display string for trade type
   */
  private mapTradeTypeToDisplay(tradeType: TradeType): string {
    switch (tradeType) {
      case 'ir-swap':
        return 'IR Swap';
      case 'commodity-option':
        return 'Commodity Option';
      case 'index-swap':
        return 'Index Swap';
      default:
        return 'Unknown';
    }
  }
}
