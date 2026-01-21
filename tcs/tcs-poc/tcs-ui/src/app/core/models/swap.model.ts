/**
 * Swap Models
 * 
 * Reusable swap data structures applicable to all swap trade types.
 * These models map directly to the JSON payload structure from the API.
 * Based on the flattened JSON structure.
 */

// ============================================================================
// Swap Details
// ============================================================================

/**
 * Swap-level details applicable to all swap types
 * Maps directly to 'swapDetails' section in JSON payload
 */
export interface SwapDetails {
  underlying?: string;
  settlementType?: string;
  swapType?: string;
  isCleared?: boolean;
  markitSingleSided?: boolean;
  principalExchange?: string;
  isIsdaFallback?: boolean;
}

// ============================================================================
// Swap Leg
// ============================================================================

/**
 * Individual swap leg with schedule
 * Maps directly to items in 'swapLegs' array in JSON payload
 */
export interface SwapLeg {
  legIndex: number;
  direction: string;
  currency: string;
  rateType: string;
  notional: number;
  scheduleType?: string;
  
  // Fixed leg specific
  interestRate?: number;
  
  // Floating leg specific
  ratesetRef?: string | null;
  referenceTenor?: string | null;
  margin?: number | string;
  ratesetOffset?: number | null;
  
  // Common leg fields
  paymentOffset?: number;
  formula?: string;
  dayCountBasis?: string;
  observationMethod?: string;
  averagingMethod?: string;
  startDate: string;
  endDate: string;
  isAdjusted?: boolean;
  stubType?: string;
  alignAtEom?: string;
  style?: string;
  rolloverDay?: number;
  paymentFrequency?: string;
  settlementCurrency?: string;
  settlementOffset?: number;
  paymentCalendars?: string[];
  rollDateConvention?: string;
  
  // Schedule array - each leg has its own schedule
  schedule: SchedulePeriod[];
}

// ============================================================================
// Schedule Period
// ============================================================================

/**
 * Individual schedule period within a swap leg
 * Maps directly to items in 'schedule' array within each leg
 */
export interface SchedulePeriod {
  periodIndex: number;
  startDate: string;
  endDate: string;
  paymentDate: string;
  notional: number;
  
  // Fixed leg schedule fields
  rate?: number;
  interest?: number;
  
  // Floating leg schedule fields
  ratesetDate?: string;
  margin?: number;
  index?: string;
  tenor?: string;
  interpolation?: string;
  
  // Common fields
  reval?: boolean;
  
  // Allow for additional dynamic fields from API
  [key: string]: any;
}

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Check if a leg is a fixed rate leg
 */
export function isFixedLeg(leg: SwapLeg): boolean {
  return leg.rateType === 'fixed';
}

/**
 * Check if a leg is a floating rate leg
 */
export function isFloatingLeg(leg: SwapLeg): boolean {
  return leg.rateType === 'floating';
}

/**
 * Get the pay leg from an array of swap legs
 */
export function getPayLeg(legs: SwapLeg[]): SwapLeg | undefined {
  return legs.find(leg => leg.direction === 'pay');
}

/**
 * Get the receive leg from an array of swap legs
 */
export function getReceiveLeg(legs: SwapLeg[]): SwapLeg | undefined {
  return legs.find(leg => leg.direction === 'receive');
}
