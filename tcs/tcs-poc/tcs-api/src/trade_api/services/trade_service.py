"""Service layer for trade operations."""

from datetime import datetime
from typing import Dict, Any, Optional
import uuid

from trade_api.models import TradeTemplateFactory, Trade
from trade_api.validation import ValidationFactory
from trade_api.clients import StoreClient
from trade_api.services.results import (
    TradeCreationResult,
    TradeValidationResult,
    TradeSaveResult
)


class TradeService:
    """Service for coordinating trade operations.

    This service encapsulates the business logic and orchestration for:
    - Creating new trades from templates
    - Validating trade data
    - Saving trades

    It separates business concerns from HTTP/API concerns.
    """

    def __init__(
        self,
        template_factory: TradeTemplateFactory,
        validation_factory: ValidationFactory,
        store_client: Optional[StoreClient] = None
    ):
        """Initialize the service with required factories.

        Args:
            template_factory: Factory for creating trade templates
            validation_factory: Factory for creating validation pipelines
            store_client: Optional client for store API (creates default if not provided)
        """
        self.template_factory = template_factory
        self.validation_factory = validation_factory
        self.store_client = store_client or StoreClient()

    def _generate_document_id(self) -> str:
        """Generate a UUID v4 document ID.

        Returns:
            UUID v4 string in standard format (36 characters with hyphens)
        """
        return str(uuid.uuid4())

    def _generate_correlation_id(self) -> str:
        """Generate a UUID v4 correlation ID.

        Returns:
            UUID v4 string in standard format (36 characters with hyphens)
        """
        return str(uuid.uuid4())

    def create_new_trade(self, trade_type: str) -> TradeCreationResult:
        """Create a new trade from a template.

        This method orchestrates the following steps:
        1. Create a template assembler for the trade type
        2. Assemble the template into a trade dictionary
        3. Generate a unique trade ID
        4. Populate date/time fields
        5. Create a Trade object
        6. Return result with trade data and metadata

        Args:
            trade_type: The type of trade (e.g., 'ir-swap', 'commodity-option')

        Returns:
            TradeCreationResult containing the trade data, metadata, and any errors

        Raises:
            ValueError: If the trade type is invalid or template configuration is bad
        """
        try:
            # Step 1-2: Create assembler and assemble template
            assembler = self.template_factory.create_assembler(trade_type=trade_type)
            trade_dict = assembler.assemble()

            # Step 3: Generate unique trade ID
            date_str = datetime.now().strftime("%Y%m%d")
            type_code = trade_type.upper().replace("-", "")
            sequence = str(uuid.uuid4().int)[:4]
            trade_id = f"NEW-{date_str}-{type_code}-{sequence}"

            # Populate trade ID in the trade dictionary
            if "general" in trade_dict:
                trade_dict["general"]["tradeId"] = trade_id

            # Step 4: Populate date/time fields
            today = datetime.now().strftime("%Y-%m-%d")
            execution_datetime = datetime.now().isoformat() + "Z"

            if "common" in trade_dict:
                trade_dict["common"]["tradeDate"] = today
                trade_dict["common"]["inputDate"] = today

            if "general" in trade_dict and "executionDetails" in trade_dict["general"]:
                trade_dict["general"]["executionDetails"]["executionDateTime"] = execution_datetime

            # Step 5: Create Trade object
            trade = Trade(trade_dict)

            # Step 6: Generate UUIDs
            document_id = self._generate_document_id()
            correlation_id = self._generate_correlation_id()

            # Step 7: Build metadata
            metadata = {
                "documentId": document_id,
                "correlationId": correlation_id,
                "trade_id": trade_id,
                "trade_type": trade_type,
                "template_schema_version": "v1"
            }

            return TradeCreationResult(
                success=True,
                trade_data=trade.data,
                metadata=metadata,
                errors=[]
            )

        except ValueError as e:
            return TradeCreationResult(
                success=False,
                trade_data=None,
                metadata={},
                errors=[f"Invalid configuration: {str(e)}"]
            )
        except Exception as e:
            return TradeCreationResult(
                success=False,
                trade_data=None,
                metadata={},
                errors=[f"Error creating template: {str(e)}"]
            )

    def validate_trade(
        self,
        trade_data: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> TradeValidationResult:
        """Validate trade data using the validation pipeline.

        This method orchestrates the following steps:
        1. Extract and handle incoming metadata (documentId, correlationId)
        2. Create Trade instance from the trade data
        3. Convert to read-only Trade for validation (immutability + performance)
        4. Create validation pipeline for the trade type
        5. Execute validation pipeline
        6. Return validation results with metadata

        Args:
            trade_data: Dictionary containing the trade data to validate
            metadata: Optional metadata containing documentId and correlationId

        Returns:
            TradeValidationResult containing success status, errors, warnings, and metadata
        """
        try:
            # Step 1: Extract incoming metadata
            document_id = None
            correlation_id = None

            if metadata:
                document_id = metadata.get("documentId")
                correlation_id = metadata.get("correlationId")

            # Generate documentId if not provided
            if not document_id:
                document_id = self._generate_document_id()

            # Correlation ID should always be provided by caller,
            # but generate if missing (for backward compatibility)
            if not correlation_id:
                correlation_id = self._generate_correlation_id()

            # Step 2: Create Trade instance from request
            trade = Trade(trade_data)

            # Step 3: Convert to read-only for validation (immutability + performance)
            readonly_trade = trade.to_readonly()

            # Step 4: Create pipeline (validators instantiated from registry)
            pipeline = self.validation_factory.create_pipeline(readonly_trade)

            # Step 5: Execute validation (collects all errors)
            result = pipeline.validate(readonly_trade)

            # Step 6: Build result metadata
            result_metadata = {
                "documentId": document_id,
                "correlationId": correlation_id,
                "trade_type": result.trade_type,
                "validation_timestamp": datetime.now().isoformat()
            }

            return TradeValidationResult(
                success=result.success,
                errors=result.errors,
                warnings=result.warnings,
                metadata=result_metadata
            )

        except ValueError as e:
            # Trade type detection or validator registration failed
            return TradeValidationResult(
                success=False,
                errors=[str(e)],
                warnings=[],
                metadata={}
            )
        except Exception as e:
            # Unexpected error
            return TradeValidationResult(
                success=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                metadata={}
            )

    def save_trade(self, trade_data: Dict[str, Any], context: Dict[str, str]) -> TradeSaveResult:
        """Save a trade to the store.

        Flow:
        1. Check if trade is new (tradeId starts with 'NEW')
        2. Validate the trade data
        3. If validation fails, return errors/warnings
        4. If validation passes, call tcs-store /save/new endpoint with context
        5. Return success with trade data and metadata

        Args:
            trade_data: Dictionary containing the trade data to save
            context: Context metadata with user, agent, action, intent

        Returns:
            TradeSaveResult containing success status, trade data, and any warnings/errors
        """
        try:
            # Step 1: Extract trade ID and check if it's new
            trade_id = trade_data.get("general", {}).get("tradeId", "")
            
            if not trade_id:
                return TradeSaveResult(
                    success=False,
                    trade_data=None,
                    warnings=[],
                    errors=["Trade ID is missing"]
                )
            
            is_new_trade = trade_id.startswith("NEW")
            
            if not is_new_trade:
                # TODO: Handle existing trade updates later
                return TradeSaveResult(
                    success=False,
                    trade_data=None,
                    warnings=[],
                    errors=["Updating existing trades not yet implemented"]
                )
            
            # Step 2: Validate the trade data
            validation_result = self.validate_trade(trade_data=trade_data)
            
            # Step 3: If validation fails, return errors/warnings
            if not validation_result.success:
                return TradeSaveResult(
                    success=False,
                    trade_data=None,
                    warnings=validation_result.warnings,
                    errors=validation_result.errors
                )
            
            # Step 4: Call tcs-store /save/new endpoint with context
            store_response = self.store_client.save_new_trade(
                trade_id=trade_id,
                trade_data=trade_data,
                context=context
            )
            
            # Step 5: Handle store response
            if not store_response.success:
                return TradeSaveResult(
                    success=False,
                    trade_data=None,
                    warnings=validation_result.warnings,
                    errors=[store_response.error or "Failed to save to store"],
                    metadata=validation_result.metadata
                )
            
            # Step 6: Return success with trade data and metadata
            return TradeSaveResult(
                success=True,
                trade_data=trade_data,
                warnings=validation_result.warnings,
                errors=[],
                metadata=validation_result.metadata
            )
            
        except Exception as e:
            return TradeSaveResult(
                success=False,
                trade_data=None,
                warnings=[],
                errors=[f"Error saving trade: {str(e)}"]
            )