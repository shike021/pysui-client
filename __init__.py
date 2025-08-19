"""
Pysui Client - A Sui blockchain client using JSON-RPC interface

This package provides a comprehensive client for interacting with Sui blockchain
using JSON-RPC interface instead of GraphQL.

Main components:
- SuiContractClient: Core client class for all Sui operations
- Smart contract deployment and function calling
- Account balance and object querying
- Transaction information retrieval

Usage:
    from sui_client import SuiContractClient
    
    client = SuiContractClient()
    balance = client.get_account_balance()
    print(f"Balance: {balance['total_balance_sui']:.6f} SUI")
"""

__version__ = "1.0.0"
__author__ = "Sui Client Developer"
__description__ = "A Sui blockchain client using JSON-RPC interface"

# Import main classes for easier access
try:
    from .sui_client import SuiContractClient
    __all__ = ['SuiContractClient']
except ImportError:
    # For development mode when running scripts directly
    __all__ = []
