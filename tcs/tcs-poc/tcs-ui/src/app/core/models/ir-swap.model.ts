/**
 * IR Swap Trade Models
 * 
 * Interest Rate Swap specific trade data structure.
 * Extends TradeCore with swap-specific details and legs.
 * Maps directly to the complete JSON payload structure from the API.
 */

import { TradeCore } from './trade-core.model';
import { SwapDetails, SwapLeg } from './swap.model';

// ============================================================================
// IR Swap Trade Interface
// ============================================================================

/**
 * Complete IR Swap trade structure
 * Composition: TradeCore + SwapDetails + SwapLegs
 * 
 * This interface maps directly to the flattened JSON structure:
 * {
 *   general: { ... },
 *   common: { ... },
 *   swapDetails: { ... },
 *   swapLegs: [ ... ]
 * }
 */
export interface IRSwapTrade extends TradeCore {
  swapDetails: SwapDetails;
  swapLegs: SwapLeg[];
}

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard to check if a trade is an IR Swap
 * Validates that the trade has all required IR Swap properties
 */
export function isIRSwapTrade(trade: any): trade is IRSwapTrade {
  return (
    trade &&
    typeof trade === 'object' &&
    'general' in trade &&
    'common' in trade &&
    'swapDetails' in trade &&
    'swapLegs' in trade &&
    Array.isArray(trade.swapLegs)
  );
}
