/**
 * Trade Core Models
 * 
 * Core trade data structure that applies to all trade types.
 * Based on the flattened JSON structure from the API.
 */

// ============================================================================
// Trade Core Interface
// ============================================================================

export interface TradeCore {
  general: GeneralSection;
  common: CommonSection;
}

// ============================================================================
// General Section
// ============================================================================

export interface GeneralSection {
  tradeId: string;
  label?: string;
  coLocatedId?: string;
  transactionRoles?: TransactionRoles;
  executionDetails?: ExecutionDetails;
  packageTradeDetails?: PackageTradeDetails;
  blockAllocationDetails?: any;
}

export interface TransactionRoles {
  marketer?: string | null;
  transactionOriginator?: string | null;
  priceMaker?: string | null;
  transactionAcceptor?: string | null;
  parameterGrantor?: string | null;
}

export interface ExecutionDetails {
  executionDateTime?: string;
  bestExecutionApplicable?: any;
  executionVenue?: ExecutionVenue;
  clearingVenue?: any;
  reportTrackingNumber?: any;
  omsOrderID?: any;
  isOffMarketPrice?: boolean;
  clientInstructionTime?: any;
}

export interface ExecutionVenue {
  executionVenue?: any;
  venueTransactionID?: any;
  executionBroker?: any;
  executionBrokeragePayer?: string;
  executionVenueMIC?: any;
  executionVenueType?: string;
}

export interface PackageTradeDetails {
  isPackageTrade?: boolean;
  packageIdentifier?: any;
  packagePriceOrSpread?: any;
  packageType?: any;
  packagePrice?: any;
  packagePriceCcy?: any;
  priceNotation?: any;
  useTradeIdAsPackageId?: boolean;
}

// ============================================================================
// Common Section
// ============================================================================

export interface CommonSection {
  book?: string;
  accountReference?: any;
  tradeDate?: string;
  counterparty?: string;
  novatedToCounterparty?: any;
  counterpartyAccountReference?: any;
  inputDate?: string;
  orderTime?: any;
  comment?: any;
  initialMargin?: any;
  backoutBook?: any;
  tradingStrategy?: any;
  ddeEligible?: string;
  backoutTradingStrategy?: any;
  externalReference?: any;
  internalReference?: any;
  initialMarginDeliveryDate?: any;
  initialMarginDescription?: any;
  structureDetails?: any;
  backoutEntity?: any;
  salesGroup?: any;
  includeFeeEngine?: any;
  acsLinkType?: any;
  regionOrAccount?: any;
  originatingSystem?: any;
  stp?: string;
  sourceSystem?: any;
  cashflowHedgeNotification?: boolean;
  IRDAdvisory?: boolean;
  isCustomBasket?: boolean | null;
  events?: TradeEvent[];
  fees?: any[];
  cvr?: any;
  rightToBreakDetails?: any;
  capitalSharing?: any[];
  tagMap?: any[];
  tradeIdentifiers?: any[];
  ISDADefinition?: string;
}

export interface TradeEvent {
  schemaVersion?: string;
  eventDescription: string;
  eventCode: string;
  businessDateTime: number | string;
  application: string;
  correlationId?: string;
}
