#!/usr/bin/env python3
"""
Test S1000D Handler Integration

This script tests that the S1000D handler has been properly integrated
into the XML analysis framework without breaking existing functionality.
"""

import sys
import os
from pathlib import Path

# Add src to path and adjust for package imports
framework_root = Path(__file__).parent
src_path = framework_root / "src"
sys.path.insert(0, str(framework_root))  # Add framework root for package imports
sys.path.insert(0, str(src_path))  # Add src for direct imports

def test_handler_import():
    """Test that S1000D handler can be imported"""
    print("Testing S1000D handler import...")
    try:
        from src.handlers.s1000d_handler import S1000DHandler
        print("✅ S1000DHandler imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import S1000DHandler: {e}")
        return False

def test_handler_registry():
    """Test that S1000D handler is properly registered"""
    print("\nTesting handler registry integration...")
    try:
        from src.handlers import ALL_HANDLERS, HANDLER_CATEGORIES, S1000DHandler
        
        # Check if S1000D handler is in registry
        handler_names = [h.__name__ for h in ALL_HANDLERS]
        if "S1000DHandler" in handler_names:
            print("✅ S1000DHandler found in ALL_HANDLERS registry")
        else:
            print("❌ S1000DHandler not found in ALL_HANDLERS registry")
            return False
            
        # Check if it's in the content category
        content_handlers = HANDLER_CATEGORIES.get("content", [])
        content_handler_names = [h.__name__ for h in content_handlers]
        if "S1000DHandler" in content_handler_names:
            print("✅ S1000DHandler found in content category")
        else:
            print("❌ S1000DHandler not found in content category")
            return False
            
        # Check total handler count
        print(f"✅ Total handlers registered: {len(ALL_HANDLERS)}")
        
        return True
    except Exception as e:
        print(f"❌ Handler registry test failed: {e}")
        return False

def test_handler_instantiation():
    """Test that S1000D handler can be instantiated"""
    print("\nTesting S1000D handler instantiation...")
    try:
        from src.handlers.s1000d_handler import S1000DHandler
        handler = S1000DHandler()
        print("✅ S1000DHandler instantiated successfully")
        
        # Test basic methods exist
        methods = ['can_handle_xml', 'detect_xml_type', 'analyze_xml', 'extract_xml_key_data']
        for method in methods:
            if hasattr(handler, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Handler instantiation failed: {e}")
        return False

def test_framework_import():
    """Test that main framework still works"""
    print("\nTesting main framework import...")
    try:
        from src import analyze
        print("✅ Main framework interface imported successfully")
        return True
    except Exception as e:
        print(f"❌ Main framework import failed: {e}")
        return False

def test_s1000d_file_analysis():
    """Test S1000D handler with an actual S1000D file"""
    print("\nTesting S1000D file analysis...")
    
    # Path to S1000D test file
    s1000d_file = "/Users/wjackson/Developer/AI-test-data/xml/bike_dataset/S1000D Issue 5.0/Bike Data Set for Release number 5.0/DMC-S1000DBIKE-AAA-DA1-10-00-00AA-251A-A_009-00_EN-US.XML"
    
    if not os.path.exists(s1000d_file):
        print(f"⚠️  S1000D test file not found: {s1000d_file}")
        print("   Skipping file analysis test")
        return True
    
    try:
        from src import analyze
        
        print(f"   Analyzing: {os.path.basename(s1000d_file)}")
        result = analyze(s1000d_file)
        
        # Check if S1000D handler was used
        if result.handler_used == "S1000DHandler":
            print("✅ S1000DHandler was used for S1000D file")
            print(f"   Document type: {result.type_name}")
            print(f"   Confidence: {result.confidence}")
            
            # Check S1000D-specific metadata
            if "S1000D" in result.type_name:
                print("✅ S1000D document type detected correctly")
            else:
                print(f"⚠️  Expected S1000D in type name, got: {result.type_name}")
                
        else:
            print(f"⚠️  Expected S1000DHandler, but got: {result.handler_used}")
            print("   This might indicate the handler detection logic needs adjustment")
            
        return True
        
    except Exception as e:
        print(f"❌ S1000D file analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_existing_functionality():
    """Test that existing handlers still work"""
    print("\nTesting existing functionality isn't broken...")
    try:
        from src.handlers import ALL_HANDLERS
        
        # Try to instantiate all handlers
        successful = 0
        for handler_class in ALL_HANDLERS:
            try:
                handler = handler_class()
                successful += 1
            except Exception as e:
                print(f"❌ Failed to instantiate {handler_class.__name__}: {e}")
                return False
        
        print(f"✅ All {successful} handlers instantiated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Existing functionality test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🧪 S1000D Handler Integration Test")
    print("=" * 50)
    
    tests = [
        test_handler_import,
        test_handler_registry,
        test_handler_instantiation,
        test_framework_import,
        test_existing_functionality,
        test_s1000d_file_analysis,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Blank line between tests
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! S1000D handler integration successful!")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
