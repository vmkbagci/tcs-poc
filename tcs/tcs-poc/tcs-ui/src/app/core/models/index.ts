/**
 * Core Models Index
 * 
 * Central export point for all model interfaces.
 */

// New compositional models (preferred for new code)
export * from './trade-core.model';
export * from './swap.model';
export * from './ir-swap.model';

// API and utility models
export * from './api-response.model';
export * from './filter.model';
export * from './preferences.model';

// Legacy trade model - export only non-overlapping types
export type { Trade, TradeType, TradeIdentifier, CommodityOptionLeg, IndexSwapLeg } from './trade.model';
