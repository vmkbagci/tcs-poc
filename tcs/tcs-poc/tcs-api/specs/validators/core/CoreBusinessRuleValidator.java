// AUTO-GENERATED from specs/validators/core/business_rules.md
// To update this validator, edit the markdown specification and regenerate

package com.macquarie.tcs.validation.validators.core;

import com.macquarie.tcs.models.ReadOnlyTrade;
import com.macquarie.tcs.validation.ValidationResult;
import com.macquarie.tcs.validation.validators.Validator;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;

/**
 * Core Business Rules Validator
 *
 * Validates universal business rules that apply to ALL trade types.
 * These are fundamental business logic checks that ensure data quality and
 * consistency across the entire trading system.
 *
 * Current Scope: Minimal validation - only critical date format validation for now.
 *
 * Applies to: All trade types (ir-swap, commodity-option, index-swap, etc.)
 */
public class CoreBusinessRuleValidator extends Validator {

    /**
     * ISO 8601 date format pattern (YYYY-MM-DD)
     */
    private static final DateTimeFormatter ISO_DATE_FORMATTER = DateTimeFormatter.ISO_LOCAL_DATE;

    /**
     * Validates universal business rules for all trade types.
     *
     * Currently validates:
     * - Trade date format (YYYY-MM-DD ISO 8601 format)
     *
     * @param trade The read-only trade object to validate
     * @return ValidationResult with success=true if no errors found, false otherwise.
     *         Includes list of errors and warnings.
     */
    @Override
    public ValidationResult validate(ReadOnlyTrade trade) {
        List<String> errors = new ArrayList<>();
        List<String> warnings = new ArrayList<>();

        // Validate Trade Date Format
        // Per spec: common.tradeDate must follow ISO 8601 format (YYYY-MM-DD)
        String tradeDateValue = trade.jmesGet("common.tradeDate");

        // Per spec: Skip validation if field is null or missing
        // (structural validator handles missing fields)
        if (tradeDateValue != null) {
            // Attempt to parse using ISO 8601 date format
            try {
                LocalDate.parse(tradeDateValue, ISO_DATE_FORMATTER);
                // If parsing succeeds, validation passes (no error)
            } catch (DateTimeParseException e) {
                // If parsing fails, record error with actual invalid value
                errors.add(String.format(
                    "Invalid tradeDate format: %s. Expected YYYY-MM-DD",
                    tradeDateValue
                ));
            }
        }

        // Return validation result
        // Per spec: Success only if no errors found
        return new ValidationResult(
            errors.isEmpty(),  // success
            errors,            // errors list
            warnings           // warnings list
        );
    }
}