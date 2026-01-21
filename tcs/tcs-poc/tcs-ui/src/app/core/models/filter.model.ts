/**
 * Filter Models
 * 
 * These interfaces define the structure of filter criteria used in the application.
 */

import { TradeType } from './trade.model';

// ============================================================================
// Trade Filters
// ============================================================================

export interface TradeFilters {
  tradeType?: TradeType | null;
  dateRange?: DateRange | null;
  counterparty?: string | null;
  book?: string | null;
  searchText?: string | null;
}

export interface DateRange {
  startDate: Date | string | null;
  endDate: Date | string | null;
}

// ============================================================================
// Pagination
// ============================================================================

export interface PaginationParams {
  page: number;
  pageSize: number;
  totalItems?: number;
  totalPages?: number;
}

// ============================================================================
// Sort Options
// ============================================================================

export interface SortOptions {
  field: string;
  direction: 'asc' | 'desc';
}

// ============================================================================
// Filter State
// ============================================================================

export interface FilterState {
  filters: TradeFilters;
  pagination: PaginationParams;
  sort?: SortOptions;
}
