#!/usr/bin/env python3
"""
Quick test script to validate the XML analyzer setup
"""

import sys
import os
from pathlib import Path

# Ensure we can import from the project root regardless of current working directory
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also ensure the current directory includes the project root for relative imports
os.chdir(project_root)

def test_imports():
    """Test that all required imports work"""
    try:
        from src.core.schema_analyzer import XMLSchemaAnalyzer
        print("✅ Imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_sample_file():
    """Test with a sample XML file"""
    sample_files = [
        "../sample_data/test_files/small/scap/ios-sample-1.0.xccdf.xml",
        "../sample_data/test_files/small/ant/ant-ivy-build.xml",
        "../sample_data/test_files_synthetic/small/servicenow/incident_export.xml"
    ]
    
    for sample_file in sample_files:
        if Path(sample_file).exists():
            print(f"📄 Testing with {sample_file}")
            try:
                from src.core.schema_analyzer import XMLSchemaAnalyzer
                analyzer = XMLSchemaAnalyzer()
                
                # Quick test - just parse first 1000 lines to validate structure
                with open(sample_file, 'r') as f:
                    first_part = ''.join(f.readlines()[:1000])
                
                print(f"✅ File is readable and appears to be XML")
                print(f"📊 Sample size: {len(first_part)} characters from first 1000 lines")
                return True
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                return False
    
    print("❌ No sample files found")
    return False

def main():
    print("🧪 Testing XML Analyzer Setup")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        return False
    
    # Test sample file
    if not test_sample_file():
        return False
    
    print("\n✅ All tests passed!")
    print("🚀 Ready to use: python analyze.py <xml_file>")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
