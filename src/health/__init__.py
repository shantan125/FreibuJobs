"""
Health Module

Provides health check and monitoring capabilities
for Azure Container Apps deployment.
"""

from .health_check import HealthCheckServer

__all__ = ['HealthCheckServer']
