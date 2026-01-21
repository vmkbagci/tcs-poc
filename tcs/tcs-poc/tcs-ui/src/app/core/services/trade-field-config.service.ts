/**
 * Trade Field Configuration Service
 * 
 * Responsible for determining field configuration based on trade type.
 * Uses compositional approach: Core fields + Trade-specific fields = Final configuration
 * 
 * Architecture:
 * - Core field configs exist for each section (general, common, swapDetails, swapLegs, schedule)
 * - Trade-specific configs add/override fields for specific trade types
 * - Final config is composed by merging core + trade-specific
 * 
 * Visibility Logic:
 * - If a field exists in config → it's visible
 * - If a field doesn't exist in config → it's not visible
 * - No need for explicit visible/readonly flags
 * 
 * Example:
 * General Section:
 *   Core: [tradeId, label, coLocatedId] (all trades)
 *   IR Swap: + [packageIdentifier, packageType]
 *   Commodity Swap: + [packageIdentifier, commodityType]
 *   Index Swap: + [indexIdentifier]
 */

import { Injectable, signal, computed } from '@angular/core';

// ============================================================================
// Field Configuration Types
// ============================================================================

/**
 * Configuration for a single field
 */
export interface FieldConfig {
  fieldName: string;
  label: string;
  required: boolean;
  placeholder?: string;
  helpText?: string;
  validationRules?: ValidationRule[];
}

/**
 * Validation rule for a field
 */
export interface ValidationRule {
  type: 'required' | 'pattern' | 'min' | 'max' | 'minLength' | 'maxLength' | 'custom';
  value?: any;
  message: string;
}

/**
 * Section configuration (e.g., General, Common, SwapDetails)
 */
export interface SectionConfig {
  sectionName: string;
  fields: Map<string, FieldConfig>;
}

/**
 * Complete trade configuration
 */
export interface TradeConfig {
  tradeType: string;
  sections: Map<string, SectionConfig>;
}

// ============================================================================
// Trade Field Configuration Service
// ============================================================================

/**
 * Instance-per-trade service
 * Each trade gets its own configuration instance to support multiple trades open simultaneously
 * 
 * Usage:
 * @Component({
 *   providers: [TradeFieldConfigService]  // ← Creates new instance per component
 * })
 */
@Injectable()
export class TradeFieldConfigService {
  
  /**
   * Current trade type
   */
  private currentTradeType = signal<string | null>(null);
  
  /**
   * Current trade configuration (composed from core + trade-specific)
   */
  private currentConfig = computed(() => {
    const tradeType = this.currentTradeType();
    if (!tradeType) {
      return null;
    }
    return this.composeConfigForTradeType(tradeType);
  });
  
  // ============================================================================
  // Public API
  // ============================================================================
  
  /**
   * Set the current trade type
   * This triggers recalculation of field configurations
   */
  setTradeType(tradeType: string): void {
    this.currentTradeType.set(tradeType);
  }
  
  /**
   * Get the complete configuration for the current trade type
   */
  getConfig(): TradeConfig | null {
    return this.currentConfig();
  }
  
  /**
   * Check if a field exists (and therefore should be visible)
   */
  hasField(sectionName: string, fieldName: string): boolean {
    const config = this.currentConfig();
    if (!config) {
      return false;
    }
    
    const section = config.sections.get(sectionName);
    if (!section) {
      return false;
    }
    
    return section.fields.has(fieldName);
  }
  
  /**
   * Check if a field is required
   */
  isFieldRequired(sectionName: string, fieldName: string): boolean {
    const field = this.getFieldConfig(sectionName, fieldName);
    return field ? field.required : false;
  }
  
  /**
   * Get field configuration for a specific field
   */
  getFieldConfig(sectionName: string, fieldName: string): FieldConfig | null {
    const config = this.currentConfig();
    if (!config) {
      return null;
    }
    
    const section = config.sections.get(sectionName);
    if (!section) {
      return null;
    }
    
    return section.fields.get(fieldName) || null;
  }
  
  /**
   * Get section configuration
   */
  getSectionConfig(sectionName: string): SectionConfig | null {
    const config = this.currentConfig();
    if (!config) {
      return null;
    }
    
    return config.sections.get(sectionName) || null;
  }
  
  /**
   * Get all field names for a section
   */
  getFieldNames(sectionName: string): string[] {
    const section = this.getSectionConfig(sectionName);
    return section ? Array.from(section.fields.keys()) : [];
  }
  
  // ============================================================================
  // Compositional Configuration Builder
  // ============================================================================
  
  /**
   * Compose configuration for a specific trade type
   * Merges core fields + trade-specific fields
   */
  private composeConfigForTradeType(tradeType: string): TradeConfig {
    const config: TradeConfig = {
      tradeType,
      sections: new Map()
    };
    
    // Build each section by composing core + trade-specific fields
    config.sections.set('general', this.composeGeneralSection(tradeType));
    config.sections.set('common', this.composeCommonSection(tradeType));
    config.sections.set('swapDetails', this.composeSwapDetailsSection(tradeType));
    config.sections.set('swapLegs', this.composeSwapLegsSection(tradeType));
    config.sections.set('schedule', this.composeScheduleSection(tradeType));
    
    return config;
  }
  
  /**
   * Compose General section configuration
   * Core fields + trade-specific fields
   */
  private composeGeneralSection(tradeType: string): SectionConfig {
    const coreFields = this.getCoreGeneralFields();
    const tradeSpecificFields = this.getTradeSpecificGeneralFields(tradeType);
    const mergedFields = new Map([...coreFields, ...tradeSpecificFields]);
    
    return {
      sectionName: 'general',
      fields: mergedFields
    };
  }
  
  /**
   * Compose Common section configuration
   */
  private composeCommonSection(tradeType: string): SectionConfig {
    const coreFields = this.getCoreCommonFields();
    const tradeSpecificFields = this.getTradeSpecificCommonFields(tradeType);
    const mergedFields = new Map([...coreFields, ...tradeSpecificFields]);
    
    return {
      sectionName: 'common',
      fields: mergedFields
    };
  }
  
  /**
   * Compose SwapDetails section configuration
   */
  private composeSwapDetailsSection(tradeType: string): SectionConfig {
    const coreFields = this.getCoreSwapDetailsFields();
    const tradeSpecificFields = this.getTradeSpecificSwapDetailsFields(tradeType);
    const mergedFields = new Map([...coreFields, ...tradeSpecificFields]);
    
    return {
      sectionName: 'swapDetails',
      fields: mergedFields
    };
  }
  
  /**
   * Compose SwapLegs section configuration
   */
  private composeSwapLegsSection(tradeType: string): SectionConfig {
    const coreFields = this.getCoreSwapLegFields();
    const tradeSpecificFields = this.getTradeSpecificSwapLegFields(tradeType);
    const mergedFields = new Map([...coreFields, ...tradeSpecificFields]);
    
    return {
      sectionName: 'swapLegs',
      fields: mergedFields
    };
  }
  
  /**
   * Compose Schedule section configuration
   */
  private composeScheduleSection(tradeType: string): SectionConfig {
    const coreFields = this.getCoreScheduleFields();
    const tradeSpecificFields = this.getTradeSpecificScheduleFields(tradeType);
    const mergedFields = new Map([...coreFields, ...tradeSpecificFields]);
    
    return {
      sectionName: 'schedule',
      fields: mergedFields
    };
  }
  
  // ============================================================================
  // Core Field Definitions (Common to ALL trades)
  // ============================================================================
  
  /**
   * Core General fields (exist in ALL trades)
   */
  private getCoreGeneralFields(): Map<string, FieldConfig> {
    return new Map([
      ['tradeId', {
        fieldName: 'tradeId',
        label: 'Trade ID',
        required: true
      }],
      ['label', {
        fieldName: 'label',
        label: 'Label',
        required: false
      }],
      ['coLocatedId', {
        fieldName: 'coLocatedId',
        label: 'Co-Located ID',
        required: false
      }],
      ['priceMaker', {
        fieldName: 'priceMaker',
        label: 'Price Maker',
        required: false
      }],
      ['marketer', {
        fieldName: 'marketer',
        label: 'Marketer',
        required: false
      }],
      ['transactionOriginator', {
        fieldName: 'transactionOriginator',
        label: 'Transaction Originator',
        required: false
      }],
      ['transactionAcceptor', {
        fieldName: 'transactionAcceptor',
        label: 'Transaction Acceptor',
        required: false
      }],
      ['executionDateTime', {
        fieldName: 'executionDateTime',
        label: 'Execution Date Time',
        required: false
      }],
      ['executionVenueType', {
        fieldName: 'executionVenueType',
        label: 'Execution Venue Type',
        required: false
      }],
      ['isOffMarketPrice', {
        fieldName: 'isOffMarketPrice',
        label: 'Is Off Market Price',
        required: false
      }]
    ]);
  }
  
  /**
   * Core Common fields (exist in ALL trades)
   */
  private getCoreCommonFields(): Map<string, FieldConfig> {
    return new Map([
      ['book', {
        fieldName: 'book',
        label: 'Book',
        required: true
      }],
      ['counterparty', {
        fieldName: 'counterparty',
        label: 'Counterparty',
        required: true
      }],
      ['tradeDate', {
        fieldName: 'tradeDate',
        label: 'Trade Date',
        required: true
      }],
      ['inputDate', {
        fieldName: 'inputDate',
        label: 'Input Date',
        required: false
      }],
      ['comment', {
        fieldName: 'comment',
        label: 'Comment',
        required: false
      }],
      ['ISDADefinition', {
        fieldName: 'ISDADefinition',
        label: 'ISDA Definition',
        required: false
      }]
    ]);
  }
  
  /**
   * Core SwapDetails fields (exist in ALL swap trades)
   */
  private getCoreSwapDetailsFields(): Map<string, FieldConfig> {
    return new Map([
      ['underlying', {
        fieldName: 'underlying',
        label: 'Underlying',
        required: false
      }],
      ['settlementType', {
        fieldName: 'settlementType',
        label: 'Settlement Type',
        required: false
      }],
      ['swapType', {
        fieldName: 'swapType',
        label: 'Swap Type',
        required: false
      }],
      ['isCleared', {
        fieldName: 'isCleared',
        label: 'Is Cleared',
        required: false
      }]
    ]);
  }
  
  /**
   * Core SwapLeg fields (exist in ALL swap legs)
   */
  private getCoreSwapLegFields(): Map<string, FieldConfig> {
    return new Map([
      ['direction', {
        fieldName: 'direction',
        label: 'Direction',
        required: true
      }],
      ['currency', {
        fieldName: 'currency',
        label: 'Currency',
        required: true
      }],
      ['rateType', {
        fieldName: 'rateType',
        label: 'Rate Type',
        required: true
      }],
      ['notional', {
        fieldName: 'notional',
        label: 'Notional',
        required: true
      }],
      ['startDate', {
        fieldName: 'startDate',
        label: 'Start Date',
        required: true
      }],
      ['endDate', {
        fieldName: 'endDate',
        label: 'End Date',
        required: true
      }]
    ]);
  }
  
  /**
   * Core Schedule fields (exist in ALL schedules)
   */
  private getCoreScheduleFields(): Map<string, FieldConfig> {
    return new Map([
      ['periodIndex', {
        fieldName: 'periodIndex',
        label: 'Period Index',
        required: true
      }],
      ['startDate', {
        fieldName: 'startDate',
        label: 'Start Date',
        required: true
      }],
      ['endDate', {
        fieldName: 'endDate',
        label: 'End Date',
        required: true
      }],
      ['paymentDate', {
        fieldName: 'paymentDate',
        label: 'Payment Date',
        required: true
      }],
      ['notional', {
        fieldName: 'notional',
        label: 'Notional',
        required: true
      }]
    ]);
  }
  
  // ============================================================================
  // Trade-Specific Field Definitions
  // ============================================================================
  
  /**
   * Trade-specific General fields
   */
  private getTradeSpecificGeneralFields(tradeType: string): Map<string, FieldConfig> {
    switch (tradeType) {
      case 'ir-swap':
        return new Map([
          ['isPackageTrade', {
            fieldName: 'isPackageTrade',
            label: 'Is Package Trade',
            required: false
          }],
          ['packageIdentifier', {
            fieldName: 'packageIdentifier',
            label: 'Package Identifier',
            required: false
          }],
          ['packageType', {
            fieldName: 'packageType',
            label: 'Package Type',
            required: false
          }]
        ]);
      
      case 'commodity-swap':
        return new Map([
          ['isPackageTrade', {
            fieldName: 'isPackageTrade',
            label: 'Is Package Trade',
            required: false
          }],
          ['packageIdentifier', {
            fieldName: 'packageIdentifier',
            label: 'Package Identifier',
            required: false
          }],
          ['commodityType', {
            fieldName: 'commodityType',
            label: 'Commodity Type',
            required: false
          }]
        ]);
      
      case 'index-swap':
        return new Map([
          ['indexIdentifier', {
            fieldName: 'indexIdentifier',
            label: 'Index Identifier',
            required: false
          }]
        ]);
      
      default:
        return new Map();
    }
  }
  
  /**
   * Trade-specific Common fields
   */
  private getTradeSpecificCommonFields(tradeType: string): Map<string, FieldConfig> {
    // Currently no trade-specific common fields
    return new Map();
  }
  
  /**
   * Trade-specific SwapDetails fields
   */
  private getTradeSpecificSwapDetailsFields(tradeType: string): Map<string, FieldConfig> {
    switch (tradeType) {
      case 'ir-swap':
        return new Map([
          ['principalExchange', {
            fieldName: 'principalExchange',
            label: 'Principal Exchange',
            required: false
          }],
          ['isIsdaFallback', {
            fieldName: 'isIsdaFallback',
            label: 'Is ISDA Fallback',
            required: false
          }]
        ]);
      
      default:
        return new Map();
    }
  }
  
  /**
   * Trade-specific SwapLeg fields
   */
  private getTradeSpecificSwapLegFields(tradeType: string): Map<string, FieldConfig> {
    // Currently no trade-specific leg fields
    return new Map();
  }
  
  /**
   * Trade-specific Schedule fields
   */
  private getTradeSpecificScheduleFields(tradeType: string): Map<string, FieldConfig> {
    switch (tradeType) {
      case 'ir-swap':
        return new Map([
          ['rate', {
            fieldName: 'rate',
            label: 'Rate',
            required: false
          }],
          ['interest', {
            fieldName: 'interest',
            label: 'Interest',
            required: false
          }],
          ['index', {
            fieldName: 'index',
            label: 'Index',
            required: false
          }]
        ]);
      
      default:
        return new Map();
    }
  }
}
