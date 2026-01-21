/**
 * Validation Service
 * 
 * Handles client-side and server-side validation with debouncing.
 * Provides field-level and form-level validation capabilities.
 */

import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject, of } from 'rxjs';
import { debounceTime, switchMap, catchError, tap } from 'rxjs/operators';
import { environment } from '@environments/environment';
import { Trade, ValidationResponse, ValidationError } from '@core/models';

/**
 * Client-side validation result
 */
export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

/**
 * Field validation rules
 */
interface FieldValidationRule {
  required?: boolean;
  pattern?: RegExp;
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  custom?: (value: any) => string | null;
}

@Injectable({
  providedIn: 'root'
})
export class ValidationService {
  private http = inject(HttpClient);
  private readonly apiUrl = environment.apiBaseUrl;

  // ============================================================================
  // Signal-based State
  // ============================================================================

  /**
   * Map of field names to their validation errors
   */
  private fieldErrorsMap = signal<Map<string, string[]>>(new Map());

  /**
   * Validation in progress flag
   */
  validating = signal<boolean>(false);

  /**
   * Last validation response
   */
  lastValidationResponse = signal<ValidationResponse | null>(null);

  // ============================================================================
  // Validation Cache
  // ============================================================================

  /**
   * Cache for validation results
   * Key: JSON stringified trade data, Value: ValidationResponse
   */
  private validationCache = new Map<string, ValidationResponse>();

  // ============================================================================
  // Debounced Validation Subject
  // ============================================================================

  /**
   * Subject for debounced async validation
   */
  private validationSubject = new Subject<Trade>();

  /**
   * Observable for debounced validation results
   */
  private debouncedValidation$ = this.validationSubject.pipe(
    debounceTime(300), // 300ms debounce
    switchMap(trade => this.validateTradeAsync(trade))
  );

  constructor() {
    // Subscribe to debounced validation
    this.debouncedValidation$.subscribe();
  }

  // ============================================================================
  // Client-Side Validation
  // ============================================================================

  /**
   * Validate a single field with client-side rules
   * 
   * @param fieldName - The name of the field to validate
   * @param value - The value to validate
   * @param rules - Optional validation rules
   * @returns ValidationResult
   */
  validateField(
    fieldName: string, 
    value: any, 
    rules?: FieldValidationRule
  ): ValidationResult {
    const errors: string[] = [];

    if (!rules) {
      return { valid: true, errors: [] };
    }

    // Required validation
    if (rules.required && this.isEmpty(value)) {
      errors.push(`${fieldName} is required`);
    }

    // Skip other validations if value is empty and not required
    if (this.isEmpty(value) && !rules.required) {
      return { valid: true, errors: [] };
    }

    // Pattern validation
    if (rules.pattern && typeof value === 'string') {
      if (!rules.pattern.test(value)) {
        errors.push(`${fieldName} format is invalid`);
      }
    }

    // Min length validation
    if (rules.minLength && typeof value === 'string') {
      if (value.length < rules.minLength) {
        errors.push(`${fieldName} must be at least ${rules.minLength} characters`);
      }
    }

    // Max length validation
    if (rules.maxLength && typeof value === 'string') {
      if (value.length > rules.maxLength) {
        errors.push(`${fieldName} must not exceed ${rules.maxLength} characters`);
      }
    }

    // Min value validation
    if (rules.min !== undefined && typeof value === 'number') {
      if (value < rules.min) {
        errors.push(`${fieldName} must be at least ${rules.min}`);
      }
    }

    // Max value validation
    if (rules.max !== undefined && typeof value === 'number') {
      if (value > rules.max) {
        errors.push(`${fieldName} must not exceed ${rules.max}`);
      }
    }

    // Custom validation
    if (rules.custom) {
      const customError = rules.custom(value);
      if (customError) {
        errors.push(customError);
      }
    }

    // Update field errors map
    this.setFieldErrors(fieldName, errors);

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Validate required fields
   * 
   * @param fieldName - The name of the field
   * @param value - The value to validate
   * @returns ValidationResult
   */
  validateRequired(fieldName: string, value: any): ValidationResult {
    return this.validateField(fieldName, value, { required: true });
  }

  /**
   * Validate email format
   * 
   * @param fieldName - The name of the field
   * @param value - The email value to validate
   * @returns ValidationResult
   */
  validateEmail(fieldName: string, value: string): ValidationResult {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return this.validateField(fieldName, value, { pattern: emailPattern });
  }

  /**
   * Validate date format (YYYY-MM-DD)
   * 
   * @param fieldName - The name of the field
   * @param value - The date value to validate
   * @returns ValidationResult
   */
  validateDate(fieldName: string, value: string): ValidationResult {
    const datePattern = /^\d{4}-\d{2}-\d{2}$/;
    return this.validateField(fieldName, value, { 
      pattern: datePattern,
      custom: (val) => {
        if (!val) return null;
        const date = new Date(val);
        return isNaN(date.getTime()) ? `${fieldName} is not a valid date` : null;
      }
    });
  }

  /**
   * Validate numeric value
   * 
   * @param fieldName - The name of the field
   * @param value - The numeric value to validate
   * @param min - Optional minimum value
   * @param max - Optional maximum value
   * @returns ValidationResult
   */
  validateNumeric(
    fieldName: string, 
    value: any, 
    min?: number, 
    max?: number
  ): ValidationResult {
    return this.validateField(fieldName, value, {
      custom: (val) => {
        if (val === null || val === undefined || val === '') return null;
        return isNaN(Number(val)) ? `${fieldName} must be a number` : null;
      },
      min,
      max
    });
  }

  // ============================================================================
  // Server-Side Validation
  // ============================================================================

  /**
   * Validate trade asynchronously with the backend API
   * Implements caching to avoid redundant API calls
   * 
   * @param trade - The trade data to validate
   * @returns Observable of ValidationResponse
   */
  validateTradeAsync(trade: Trade): Observable<ValidationResponse> {
    // Check cache first
    const cacheKey = JSON.stringify(trade);
    if (this.validationCache.has(cacheKey)) {
      return of(this.validationCache.get(cacheKey)!);
    }

    this.validating.set(true);

    return this.http.post<ValidationResponse>(`${this.apiUrl}/trades/validate`, trade)
      .pipe(
        tap(response => {
          this.validating.set(false);
          this.lastValidationResponse.set(response);
          
          // Cache the result
          this.validationCache.set(cacheKey, response);
          
          // Update field errors from server response
          if (response.errors && response.errors.length > 0) {
            this.updateFieldErrorsFromResponse(response.errors);
          } else {
            this.clearAllFieldErrors();
          }
        }),
        catchError(error => {
          this.validating.set(false);
          const errorResponse: ValidationResponse = {
            success: false,
            errors: [{
              field: 'general',
              message: 'Validation request failed',
              code: 'VALIDATION_ERROR'
            }]
          };
          this.lastValidationResponse.set(errorResponse);
          return of(errorResponse);
        })
      );
  }

  /**
   * Trigger debounced async validation
   * Use this method when you want validation to be debounced
   * 
   * @param trade - The trade data to validate
   */
  validateTradeDebounced(trade: Trade): void {
    this.validationSubject.next(trade);
  }

  // ============================================================================
  // Field Error Management
  // ============================================================================

  /**
   * Get errors for a specific field as a signal
   * 
   * @param fieldName - The name of the field
   * @returns Computed signal of error messages
   */
  getFieldErrors(fieldName: string) {
    return computed(() => {
      const errorsMap = this.fieldErrorsMap();
      return errorsMap.get(fieldName) || [];
    });
  }

  /**
   * Check if a field has errors
   * 
   * @param fieldName - The name of the field
   * @returns Computed signal indicating if field has errors
   */
  hasFieldErrors(fieldName: string) {
    return computed(() => {
      const errors = this.getFieldErrors(fieldName)();
      return errors.length > 0;
    });
  }

  /**
   * Set errors for a specific field
   * 
   * @param fieldName - The name of the field
   * @param errors - Array of error messages
   */
  setFieldErrors(fieldName: string, errors: string[]): void {
    const currentMap = new Map(this.fieldErrorsMap());
    if (errors.length > 0) {
      currentMap.set(fieldName, errors);
    } else {
      currentMap.delete(fieldName);
    }
    this.fieldErrorsMap.set(currentMap);
  }

  /**
   * Clear errors for a specific field
   * 
   * @param fieldName - The name of the field
   */
  clearFieldErrors(fieldName: string): void {
    const currentMap = new Map(this.fieldErrorsMap());
    currentMap.delete(fieldName);
    this.fieldErrorsMap.set(currentMap);
  }

  /**
   * Clear all field errors
   */
  clearAllFieldErrors(): void {
    this.fieldErrorsMap.set(new Map());
  }

  /**
   * Get all field errors as a plain object
   * 
   * @returns Object with field names as keys and error arrays as values
   */
  getAllFieldErrors(): Record<string, string[]> {
    const errorsMap = this.fieldErrorsMap();
    const result: Record<string, string[]> = {};
    errorsMap.forEach((errors, fieldName) => {
      result[fieldName] = errors;
    });
    return result;
  }

  // ============================================================================
  // Cache Management
  // ============================================================================

  /**
   * Clear validation cache
   */
  clearValidationCache(): void {
    this.validationCache.clear();
  }

  /**
   * Clear last validation response
   */
  clearLastValidationResponse(): void {
    this.lastValidationResponse.set(null);
  }

  // ============================================================================
  // Private Helper Methods
  // ============================================================================

  /**
   * Check if a value is empty
   * 
   * @param value - The value to check
   * @returns True if value is empty
   */
  private isEmpty(value: any): boolean {
    return value === null || 
           value === undefined || 
           value === '' || 
           (Array.isArray(value) && value.length === 0);
  }

  /**
   * Update field errors from server validation response
   * 
   * @param errors - Array of validation errors from server
   */
  private updateFieldErrorsFromResponse(errors: ValidationError[]): void {
    const newErrorsMap = new Map<string, string[]>();
    
    errors.forEach(error => {
      const fieldErrors = newErrorsMap.get(error.field) || [];
      fieldErrors.push(error.message);
      newErrorsMap.set(error.field, fieldErrors);
    });

    this.fieldErrorsMap.set(newErrorsMap);
  }
}
