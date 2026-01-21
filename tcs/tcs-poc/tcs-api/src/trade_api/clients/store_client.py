"""HTTP client for TCS Store API."""

import httpx
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class StoreResponse:
    """Response from store API."""
    success: bool
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class StoreClient:
    """Client for interacting with TCS Store API.
    
    This client handles communication with the tcs-store service,
    transforming data between tcs-api and tcs-store formats.
    """
    
    def __init__(self, base_url: str = "http://localhost:5500"):
        """Initialize the store client.
        
        Args:
            base_url: Base URL for the store API (default: http://localhost:5500)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = 30.0  # 30 second timeout
    
    def save_new_trade(
        self,
        trade_id: str,
        trade_data: Dict[str, Any],
        context: Dict[str, str]
    ) -> StoreResponse:
        """Save a new trade to the store.
        
        Args:
            trade_id: Trade ID (from general.tradeId)
            trade_data: Full trade data dictionary
            context: Context metadata (user, agent, action, intent)
            
        Returns:
            StoreResponse with success status and data/error
        """
        # Transform to store format
        store_request = {
            "context": context,
            "trade": {
                "id": trade_id,
                "data": trade_data
            }
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/save/new",
                    json=store_request
                )
                
                if response.status_code == 201:
                    # Success
                    return StoreResponse(
                        success=True,
                        status_code=201,
                        data=response.json()
                    )
                elif response.status_code == 409:
                    # Trade already exists
                    error_data = response.json()
                    return StoreResponse(
                        success=False,
                        status_code=409,
                        error=error_data.get("detail", "Trade already exists")
                    )
                elif response.status_code == 422:
                    # Validation error (invalid context)
                    error_data = response.json()
                    return StoreResponse(
                        success=False,
                        status_code=422,
                        error=error_data.get("detail", "Validation error")
                    )
                else:
                    # Other error
                    return StoreResponse(
                        success=False,
                        status_code=response.status_code,
                        error=f"Store API returned status {response.status_code}"
                    )
                    
        except httpx.ConnectError:
            return StoreResponse(
                success=False,
                status_code=503,
                error="Unable to connect to store API. Is it running on port 5500?"
            )
        except httpx.TimeoutException:
            return StoreResponse(
                success=False,
                status_code=504,
                error="Store API request timed out"
            )
        except Exception as e:
            return StoreResponse(
                success=False,
                status_code=500,
                error=f"Error calling store API: {str(e)}"
            )
    
    def list_trades(self, filter_dict: Optional[Dict[str, Any]] = None) -> StoreResponse:
        """List trades from the store.
        
        Args:
            filter_dict: Optional filter criteria (empty for all trades)
            
        Returns:
            StoreResponse with success status and list of trades
        """
        request_data = {
            "filter": filter_dict or {}
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/list",
                    json=request_data
                )
                
                if response.status_code == 200:
                    # Success - response is array of trades
                    trades = response.json()
                    return StoreResponse(
                        success=True,
                        status_code=200,
                        data={"trades": trades}
                    )
                else:
                    return StoreResponse(
                        success=False,
                        status_code=response.status_code,
                        error=f"Store API returned status {response.status_code}"
                    )
                    
        except httpx.ConnectError:
            return StoreResponse(
                success=False,
                status_code=503,
                error="Unable to connect to store API"
            )
        except httpx.TimeoutException:
            return StoreResponse(
                success=False,
                status_code=504,
                error="Store API request timed out"
            )
        except Exception as e:
            return StoreResponse(
                success=False,
                status_code=500,
                error=f"Error calling store API: {str(e)}"
            )
