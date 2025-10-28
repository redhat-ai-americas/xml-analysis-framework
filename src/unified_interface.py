"""Unified interface compatibility layer for xml-analysis-framework.

This module provides a consistent interface wrapper that can be copied to other frameworks.
It ensures all analysis results have the same access patterns regardless of the underlying
implementation.
"""

from typing import Dict, Any, Optional, List
from analysis_framework_base import UnifiedAnalysisResult as BaseUnifiedAnalysisResult


class UnifiedAnalysisResult(BaseUnifiedAnalysisResult):
    """Wrapper to provide consistent interface for SpecializedAnalysis objects.

    This class extends the base UnifiedAnalysisResult to provide backward compatibility
    with xml-analysis-framework's SpecializedAnalysis format.

    This class provides:
    - Dictionary-style access: result['key']
    - Attribute access: result.key
    - Consistent method interface: result.to_dict()
    """

    def __init__(self, specialized_analysis):
        """Initialize with a SpecializedAnalysis object.

        Args:
            specialized_analysis: The raw analysis result from XMLDocumentAnalyzer
        """
        # Extract standard fields from SpecializedAnalysis
        document_type = getattr(specialized_analysis, 'type_name', 'unknown')
        confidence = getattr(specialized_analysis, 'confidence', 1.0)
        metadata = getattr(specialized_analysis, 'metadata', {})
        content = getattr(specialized_analysis, 'content', '')
        ai_opportunities = getattr(specialized_analysis, 'ai_opportunities', [])

        # Initialize base class
        super().__init__(
            document_type=document_type,
            confidence=confidence,
            framework='xml-analysis-framework',
            metadata=metadata,
            content=content,
            ai_opportunities=ai_opportunities,
            raw_analysis=specialized_analysis if isinstance(specialized_analysis, dict) else {}
        )

        # Store raw analysis for backward compatibility
        self._raw = specialized_analysis
        self._dict_cache = None
    
    # Override __getattr__ to proxy attributes to raw analysis for backward compatibility
    def __getattr__(self, name):
        """Proxy attribute access to the raw object for backward compatibility.

        This allows accessing any attributes from the original
        SpecializedAnalysis object that aren't in the base class.
        """
        # Avoid infinite recursion
        if name in ('_raw', '_dict_cache'):
            raise AttributeError(f"'{name}' not found")
        try:
            return getattr(object.__getattribute__(self, '_raw'), name)
        except AttributeError:
            # Fall back to base class behavior
            raise AttributeError(f"'{name}' not found in UnifiedAnalysisResult or raw analysis") 