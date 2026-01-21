import { Pipe, PipeTransform } from '@angular/core';

/**
 * CurrencyFormatPipe
 * 
 * Formats numeric values with appropriate precision and formatting.
 * Handles currency amounts, percentages, and general numeric values.
 * 
 * Requirements:
 * - 5.4: Format numeric columns with appropriate precision
 * - 16.3: Format numeric values in grids and displays
 * 
 * Usage:
 *   {{ amount | currencyFormat }}
 *   {{ amount | currencyFormat:'USD' }}
 *   {{ rate | currencyFormat:'percent' }}
 *   {{ value | currencyFormat:'number':4 }}
 */
@Pipe({
  name: 'currencyFormat',
  standalone: true
})
export class CurrencyFormatPipe implements PipeTransform {
  transform(
    value: number | string | null | undefined,
    type: 'currency' | 'percent' | 'number' = 'number',
    currencyCode: string = 'USD',
    decimalPlaces?: number
  ): string {
    if (value === null || value === undefined || value === '') {
      return '';
    }

    const numValue = typeof value === 'string' ? parseFloat(value) : value;

    if (isNaN(numValue)) {
      return '';
    }

    switch (type) {
      case 'currency':
        return this.formatCurrency(numValue, currencyCode, decimalPlaces);
      case 'percent':
        return this.formatPercent(numValue, decimalPlaces);
      case 'number':
        return this.formatNumber(numValue, decimalPlaces);
      default:
        return this.formatNumber(numValue, decimalPlaces);
    }
  }

  private formatCurrency(value: number, currencyCode: string, decimalPlaces?: number): string {
    const decimals = decimalPlaces !== undefined ? decimalPlaces : 2;
    
    try {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currencyCode,
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      }).format(value);
    } catch (error) {
      // Fallback if currency code is invalid
      return this.formatNumber(value, decimals);
    }
  }

  private formatPercent(value: number, decimalPlaces?: number): string {
    const decimals = decimalPlaces !== undefined ? decimalPlaces : 2;
    
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value / 100);
  }

  private formatNumber(value: number, decimalPlaces?: number): string {
    // Determine appropriate decimal places if not specified
    let decimals: number;
    
    if (decimalPlaces !== undefined) {
      decimals = decimalPlaces;
    } else {
      // Auto-detect based on value magnitude
      if (Math.abs(value) >= 1000000) {
        decimals = 0; // Large numbers: no decimals
      } else if (Math.abs(value) >= 1) {
        decimals = 2; // Regular numbers: 2 decimals
      } else if (Math.abs(value) > 0) {
        decimals = 4; // Small numbers: 4 decimals
      } else {
        decimals = 0; // Zero
      }
    }

    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  }
}
