#!/usr/bin/env python3
"""
XML Specialized Handlers System

This module provides a flexible framework for detecting and handling different XML document types.
Each handler provides specialized analysis and extraction logic for its document type.

Key features:
- Automatic document type detection
- Pluggable handler architecture
- Type-specific analysis and insights
- Standardized output format
"""

import defusedxml.ElementTree as ET
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from pathlib import Path
import json

# Note: Base classes imported by handlers through registry, not used directly here

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    # For runtime, we'll use Any to avoid the import
    Element = Any


# All specialized handlers have been moved to individual files in src/handlers/
# The XMLHandler base class and core data structures remain here for imports


class XMLDocumentAnalyzer:
    """Main analyzer that uses specialized handlers"""

    def __init__(self, max_file_size_mb: Optional[float] = None):
        """
        Initialize the XML document analyzer

        Args:
            max_file_size_mb: Maximum allowed file size in megabytes.
                            If None, no size limit is enforced.
                            Recommended: 100MB for production use.
        """
        self.max_file_size_mb = max_file_size_mb

        # Use the centralized handler registry
        from ..handlers import ALL_HANDLERS

        # Instantiate all handlers from the registry
        self.handlers = [handler_class() for handler_class in ALL_HANDLERS]

    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """Analyze an XML document using the appropriate handler"""

        # Check file size limits
        if self.max_file_size_mb is not None:
            try:
                file_size_bytes = Path(file_path).stat().st_size
                file_size_mb = file_size_bytes / (1024 * 1024)

                if file_size_mb > self.max_file_size_mb:
                    return {
                        "error": (
                            f"File too large: {file_size_mb:.2f}MB exceeds "
                            f"limit of {self.max_file_size_mb}MB"
                        ),
                        "file_path": file_path,
                        "file_size_mb": file_size_mb,
                        "size_limit_exceeded": True,
                    }
            except OSError as e:
                return {
                    "error": f"Failed to check file size: {e}",
                    "file_path": file_path,
                }

        # Parse the document
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            return {"error": f"Failed to parse XML: {e}", "file_path": file_path}
        except Exception as e:
            # Catch security exceptions from defusedxml
            return {
                "error": f"XML parsing blocked for security: {type(e).__name__} - {str(e)}",
                "file_path": file_path,
                "security_issue": True,
            }

        # Extract namespaces
        namespaces = self._extract_namespaces(root)

        # Find the best handler
        best_handler = None
        best_confidence = 0.0

        for handler in self.handlers:
            can_handle, confidence = handler.can_handle(
                file_path, root=root, namespaces=namespaces
            )
            if can_handle and confidence > best_confidence:
                best_handler = handler
                best_confidence = confidence

        if not best_handler:
            best_handler = self.handlers[-1]  # Use generic handler

        # Detect document type
        doc_type = best_handler.detect_type(file_path, root=root, namespaces=namespaces)

        # Perform specialized analysis (now returns unified SpecializedAnalysis)
        analysis = best_handler.analyze(file_path, root=root, namespaces=namespaces)
        
        # Add metadata to the analysis object
        analysis.file_path = file_path
        analysis.handler_used = best_handler.__class__.__name__
        analysis.namespaces = namespaces
        analysis.file_size = Path(file_path).stat().st_size
        
        return analysis

    def _extract_namespaces(self, root: Element) -> Dict[str, str]:
        """Extract all namespaces from the document"""
        namespaces = {}

        # Get namespaces from root element
        for key, value in root.attrib.items():
            if key.startswith("xmlns"):
                prefix = key.split(":")[1] if ":" in key else "default"
                namespaces[prefix] = value

        # Also check for namespaces in element tags
        for elem in root.iter():
            if "}" in elem.tag:
                uri = elem.tag.split("}")[0][1:]
                # Try to find a prefix for this URI
                prefix = None
                for p, u in namespaces.items():
                    if u == uri:
                        prefix = p
                        break
                if not prefix:
                    prefix = f"ns{len(namespaces)}"
                    namespaces[prefix] = uri

        return namespaces

    def get_available_handlers(self) -> List[str]:
        """Get list of available handler names"""
        return [handler.__class__.__name__ for handler in self.handlers]

    def get_handler_info(self) -> Dict[str, Any]:
        """Get information about loaded handlers"""
        from ..handlers import get_handler_info

        info = get_handler_info()
        info["loaded_handlers"] = len(self.handlers)
        return info

    def get_handlers_by_category(self, category: str) -> List[str]:
        """Get handler names in a specific category"""
        from ..handlers import get_handlers_by_category

        handler_classes = get_handlers_by_category(category)
        return [handler.__name__ for handler in handler_classes]


# Example usage
if __name__ == "__main__":
    analyzer = XMLDocumentAnalyzer()

    # Example: Analyze a file
    result = analyzer.analyze_document("sample_data/example.xml")

    print(json.dumps(result, indent=2, default=str))
