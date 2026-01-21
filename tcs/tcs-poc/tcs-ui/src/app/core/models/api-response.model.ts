/**
 * API Response Models
 * 
 * These interfaces define the structure of responses from the Trade API.
 */

import { Trade } from './trade.model';

// ============================================================================
// Trade API Response
// ============================================================================

export interface TradeResponse {
  success: boolean;
  trade_data?: Trade;
  errors?: string[];
  warnings?: string[];
  metadata?: Record<string, any>;
}

// ============================================================================
// Validation Response
// ============================================================================

export interface ValidationResponse {
  success: boolean;
  errors: ValidationError[];
  warnings?: string[];
}

export interface ValidationError {
  field: string;
  message: string;
  code?: string;
  severity?: 'error' | 'warning';
}

// ============================================================================
// Generic API Response
// ============================================================================

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  errors?: string[];
  warnings?: string[];
  message?: string;
}

// ============================================================================
// Error Response
// ============================================================================

export interface ApiError {
  status: number;
  statusText: string;
  message: string;
  errors?: string[];
  timestamp?: string;
}
