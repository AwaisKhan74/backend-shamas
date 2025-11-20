"""
Views for administration app (penalties management).
"""
from finance.views import PenaltyViewSet

# Re-export PenaltyViewSet for URL routing
__all__ = ['PenaltyViewSet']
