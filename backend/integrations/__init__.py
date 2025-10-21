"""
Brazilian Climate Data API Integrations

This package contains adapters for Brazilian government climate and environmental data sources:
- INPE (Instituto Nacional de Pesquisas Espaciais) - Climate projections
- ANA (Agência Nacional de Águas) - Hydrological data
- Cemaden (Centro Nacional de Monitoramento) - Disaster monitoring
"""

from .inpe_client import INPEClient
from .ana_client import ANAClient

__all__ = ['INPEClient', 'ANAClient']
