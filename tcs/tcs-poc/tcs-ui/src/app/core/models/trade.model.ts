/**
 * Core Trade Models
 * 
 * These interfaces define the structure of trade data used throughout the application.
 * They are based on the Trade API response format and support multiple trade types:
 * - ir-swap (Interest Rate Swap)
 * - commodity-option (Commodity Option)
 * - index-swap (Index Swap)
 */

// ============================================================================
// Main Trade Interface
// ============================================================================

export interface Trade {
  general: GeneralSection;
  common: CommonSection;
  swapDetails?: SwapDetails;
  swapLegs?: SwapLeg[];
  leg?: CommodityOptionLeg | IndexSwapLeg;
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
  marketer?: any;
  transactionOriginator?: string;
  priceMaker?: string;
  transactionAcceptor?: string;
  parameterGrantor?: any;
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

export interface DateValue {
  date: string;
  expr?: any;
}

export interface TradeEvent {
  schemaVersion?: string;
  eventDescription: string;
  eventCode: string;
  businessDateTime: number | string;
  application: string;
  correlationId?: string;
}

// ============================================================================
// Swap Details (IR Swap)
// ============================================================================

export interface SwapDetails {
  underlying?: string;
  settlementType?: string;
  swapType?: string;
  isCleared?: boolean;
  markitSingleSided?: boolean;
  principalExchange?: string;
  isIsdaFallback?: boolean;
}

export interface SwapLeg {
  legIndex: number;
  direction: string;
  currency: string;
  rateType: string;
  notional?: number | null;
  scheduleType?: string;
  interestRate?: number | null;
  ratesetRef?: string | null;
  referenceTenor?: string | null;
  margin?: number | string;
  ratesetOffset?: number | null;
  paymentOffset?: number | null;
  ratesetCalendars?: string[];
  formula?: string;
  dayCountBasis?: string;
  observationMethod?: string;
  averagingMethod?: string;
  startDate?: string;
  endDate?: string;
  isAdjusted?: boolean;
  stubDate?: any;
  stubDayCountBasis?: any;
  stubType?: string;
  alignAtEom?: string;
  style?: string;
  rollConvention?: any;
  rolloverDay?: number;
  paymentFrequency?: string;
  settlementCurrency?: string;
  settlementOffset?: number;
  fxSettlement?: any;
  paymentCalendars?: string[];
  rollDateConvention?: string;
  nonStandard?: any;
  schedule?: SchedulePeriod[];
}

export interface SchedulePeriod {
  periodIndex: number;
  startDate: string;
  endDate: string;
  paymentDate: string;
  ratesetDate?: string;
  rate?: number;
  notional: number;
  interest?: number;
  margin?: number;
  index?: string;
  tenor?: string;
  interpolation?: string;
  reval?: boolean;
  [key: string]: any; // Allow dynamic properties
}

// ============================================================================
// Commodity Option Leg
// ============================================================================

export interface CommodityOptionLeg {
  commodityOptionType?: {
    commodityFinancialOptionModel?: CommodityFinancialOptionModel;
  };
  optionPremium?: OptionPremium;
  assetTypeTrade?: any;
  tagMap?: any[];
}

export interface CommodityFinancialOptionModel {
  optionExercise?: OptionExercise;
  notionalQuantity?: NotionalQuantity;
  strikeCurrency?: string;
  commodityStrikePrice?: any;
  commodityPayoff?: CommodityPayoff;
  commodityOptionPeriods?: CommodityOptionPeriods;
  commodityOptionFeatures?: CommodityOptionFeatures;
  commodityOptionExercisePayment?: CommodityOptionExercisePayment;
  pricingSchedulePeriodCountModified?: boolean;
  pricingSchedule?: PricingSchedulePeriod[];
  physicalMetalLocation?: any;
}

export interface OptionExercise {
  optionExerciseType?: any;
  settlementMethod?: any;
  swapExpiryDate?: any;
  accumulation?: any;
  automaticExercise?: boolean;
  writtenConfirmation?: boolean;
  settlementFxConversionFxType?: boolean;
}

export interface NotionalQuantity {
  notionalVolume?: {
    volumeUnit?: string;
    volumeFrequency?: any;
    volumeFuturesContracts?: number;
  };
  cashNotional?: any;
}

export interface CommodityPayoff {
  priceCalculation?: PriceCalculation;
  commodityPeriods?: any;
}

export interface PriceCalculation {
  spread?: number;
  finalPriceRounding?: Rounding;
  intermediatePriceRounding?: Rounding;
  multiAssetParams?: any;
  pricingModel?: any[];
  pricingStyle?: any;
}

export interface Rounding {
  method?: any;
  precision?: any;
}

export interface CommodityOptionPeriods {
  periodShortCode?: any;
  singleOrMultiPeriod?: any;
  effectiveDate?: AdjustedDate;
  terminationDate?: AdjustedDate;
  periodAlignOn?: any;
  periodAlignment?: any;
  rollDirectionEnum?: any;
  rollDirection?: string;
  calculationPeriods?: any;
  finalRatesetDate?: any;
  futuresObservationDate?: any;
  modified?: boolean;
}

export interface AdjustedDate {
  dateAdjustments?: {
    businessCenters?: string[];
  };
  adjustedDate?: {
    unadjustedDate?: string;
    adjustedDate?: string;
  };
}

export interface CommodityOptionFeatures {
  exerciseCutoff?: string;
  barrier?: any;
}

export interface CommodityOptionExercisePayment {
  paymentCurrency?: string;
  paymentFxFixingRefCode?: any;
  paymentFxRatesetDate?: any;
  paymentDatesModel?: any;
  fxConversionFactor?: any;
  fxTerms?: any;
  fxRatesetExprCode?: any;
}

export interface PricingSchedulePeriod {
  scheduleIndex?: number;
  deliveryDateYearMonth?: any;
  periodStartDate?: string;
  periodEndDate?: string;
  swapExpiryDate?: string;
  barrierLeg?: any;
  notionalQuantity?: any;
  perFrequencyQuantity?: any;
  strikeLeg?: any;
  assetPriceLeg?: any;
  payment?: any;
  observations?: any;
  strikeManagementPair?: any;
}

export interface OptionPremium {
  dealtPrice?: any;
  priceCurrency?: string;
  priceUnits?: string;
  deferredFlag?: boolean;
  paymentStyle?: any;
  premiumSchedule?: any;
  premiumFxFixingRefCode?: any;
  premiumFxRatesetDate?: string;
}

// ============================================================================
// Index Swap Leg
// ============================================================================

export interface IndexSwapLeg {
  underlyingAsset?: UnderlyingAsset;
  volume?: Volume;
  fixedFeeLeg?: FixedFeeLeg;
  floatingIndexLeg?: FloatingIndexLeg;
  payment?: Payment;
  assetSchedule?: any[];
  isCustomSchedule?: boolean;
  tagMap?: any[];
}

export interface UnderlyingAsset {
  indexCode?: string;
  ISIN?: any;
}

export interface Volume {
  volumeType?: any;
  rounding?: any;
}

export interface FixedFeeLeg {
  dayCountBasis?: string;
  combineFeesTbills?: any;
  feeStartDate?: string;
  settlement?: any;
}

export interface FloatingIndexLeg {
  periods?: FloatingIndexPeriods;
  price?: FloatingIndexPrice;
  indexTradeDetails?: IndexTradeDetails;
}

export interface FloatingIndexPeriods {
  singleOrMultiRatesets?: any;
  ratesetOn?: any;
  startDate?: string;
  endDate?: string;
  rollDateConvention?: any;
}

export interface FloatingIndexPrice {
  priceType?: any;
  rounding?: any;
}

export interface IndexTradeDetails {
  hedgeDisruption?: any;
  ateTrigger?: any;
  reinvesting?: any;
  stopLoss?: any;
  indexFloatingPerformance?: any;
  linkedTradeableId?: any;
  exitCost?: any;
  unilateralUnwindRights?: any;
  standardIcoh?: any;
  isBreakable?: boolean;
}

export interface Payment {
  paymentCcy?: string;
  fxConversion?: FxConversion;
  terms?: PaymentTerms;
  rounding?: any;
}

export interface FxConversion {
  fxFixingRefCode?: any;
  ratesetExprCode?: any;
  assetCcy?: string;
}

export interface PaymentTerms {
  paymentDate?: any;
  paymentDaysOffset?: number;
  dayType?: any;
  calendar?: string[];
}

// ============================================================================
// Helper Types
// ============================================================================

export type TradeType = 'ir-swap' | 'commodity-option' | 'index-swap';

export interface TradeIdentifier {
  tradeId: string;
  label: string;
  tradeType?: TradeType;
}
