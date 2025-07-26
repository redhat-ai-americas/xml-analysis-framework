#!/usr/bin/env python3
"""
Integration tests for ServiceNow XML Handler

Tests the ServiceNowHandler with real synthetic ServiceNow export files.
"""

import unittest
import sys
import os
from pathlib import Path
import defusedxml.ElementTree as ET

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.handlers.servicenow_handler import ServiceNowHandler
from src.core.analyzer import XMLDocumentAnalyzer


class TestServiceNowIntegration(unittest.TestCase):
    """Integration tests for ServiceNow handler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.handler = ServiceNowHandler()
        self.analyzer = XMLDocumentAnalyzer()
        
        # Get project root and sample data paths
        self.project_root = Path(__file__).parent.parent.parent
        self.sample_dir = self.project_root / "sample_data" / "test_files_synthetic"
        
    def test_incident_export(self):
        """Test analyzing incident export file"""
        file_path = self.sample_dir / "small" / "servicenow" / "incident_export.xml"
        
        if not file_path.exists():
            self.skipTest(f"Sample file not found: {file_path}")
        
        # Test with analyzer
        result = self.analyzer.analyze_document(str(file_path))
        
        self.assertNotIn('error', result)
        self.assertEqual(result['handler_used'], 'ServiceNowHandler')
        self.assertEqual(result['document_type'].type_name, 'ServiceNow Incident')
        
    def test_problem_export(self):
        """Test analyzing problem export file"""
        file_path = self.sample_dir / "small" / "servicenow" / "problem_export.xml"
        
        if not file_path.exists():
            self.skipTest(f"Sample file not found: {file_path}")
        
        # Parse and test with handler directly
        tree = ET.parse(str(file_path))
        root = tree.getroot()
        
        can_handle, confidence = self.handler.can_handle_xml(root, {})
        self.assertTrue(can_handle)
        self.assertGreater(confidence, 0.5)
        
        type_info = self.handler.detect_xml_type(root, {})
        self.assertEqual(type_info.type_name, 'ServiceNow Problem')
        
    def test_change_request_export(self):
        """Test analyzing change request export file"""
        file_path = self.sample_dir / "small" / "servicenow" / "change_request_export.xml"
        
        if not file_path.exists():
            self.skipTest(f"Sample file not found: {file_path}")
        
        # Test with analyzer
        result = self.analyzer.analyze_document(str(file_path))
        
        self.assertNotIn('error', result)
        self.assertEqual(result['document_type'].type_name, 'ServiceNow Change_Request')
        
    def test_full_export_analysis(self):
        """Test analyzing full ServiceNow export with multiple record types"""
        file_path = self.sample_dir / "medium" / "servicenow" / "full_export.xml"
        
        if not file_path.exists():
            self.skipTest(f"Sample file not found: {file_path}")
        
        # Parse and analyze
        tree = ET.parse(str(file_path))
        root = tree.getroot()
        
        # Test detection
        can_handle, confidence = self.handler.can_handle_xml(root, {})
        self.assertTrue(can_handle)
        self.assertGreater(confidence, 0.7)
        
        # Test type detection
        type_info = self.handler.detect_xml_type(root, {})
        self.assertIn('ServiceNow', type_info.type_name)
        
        # Test full analysis
        analysis = self.handler.analyze_xml(root, str(file_path))
        
        # Check key findings
        self.assertIn('key_findings', analysis.__dict__)
        findings = analysis.key_findings
        
        # Should detect multiple incidents
        if 'incident_count' in findings:
            self.assertGreaterEqual(findings['incident_count'], 2)
        
        # Check for recommendations
        self.assertIsInstance(analysis.recommendations, list)
        self.assertGreater(len(analysis.recommendations), 0)
        
        # Check AI use cases
        self.assertIsInstance(analysis.ai_use_cases, list)
        self.assertGreater(len(analysis.ai_use_cases), 3)
        
        # Some expected use cases
        use_case_text = ' '.join(analysis.ai_use_cases)
        self.assertIn('incident', use_case_text.lower())
        
    def test_key_data_extraction(self):
        """Test extraction of key structured data"""
        file_path = self.sample_dir / "small" / "servicenow" / "incident_export.xml"
        
        if not file_path.exists():
            self.skipTest(f"Sample file not found: {file_path}")
        
        tree = ET.parse(str(file_path))
        root = tree.getroot()
        
        # Extract key data
        data = self.handler.extract_xml_key_data(root)
        
        # Should have ticket info
        self.assertIn('ticket_info', data)
        ticket = data['ticket_info']
        self.assertEqual(ticket['number'], 'INC0012345')
        self.assertEqual(ticket['state'], '7')
        
        # Should have conversation thread
        self.assertIn('conversation_thread', data)
        thread = data['conversation_thread']
        self.assertGreaterEqual(len(thread), 3)  # 3 journal entries
        
        # Should have attachments
        self.assertIn('attachments', data)
        attachments = data['attachments']
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0]['file_name'], 'cable_damage_photo.jpg')
        
        # Should have timeline
        self.assertIn('timeline', data)
        self.assertGreater(len(data['timeline']), 0)
        
        # Should have people involved
        self.assertIn('people_involved', data)
        people = data['people_involved']
        self.assertIn('requesters', people)
        self.assertIn('assignees', people)


if __name__ == '__main__':
    unittest.main()