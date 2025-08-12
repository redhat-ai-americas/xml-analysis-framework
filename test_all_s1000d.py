#!/usr/bin/env python3
"""
Test ALL S1000D files with the deployed package to identify API compatibility issues
"""

import os
import glob
from pathlib import Path

def test_all_s1000d_files():
    """Test every S1000D file we have"""
    print("=" * 70)
    print("🧪 COMPREHENSIVE S1000D FILE TEST")
    print("=" * 70)
    
    # Import the package
    try:
        import xml_analysis_framework as xaf
        print(f"✅ Using xml-analysis-framework version {xaf.__version__}\n")
    except ImportError:
        print("❌ Package not installed")
        return
    
    # Find all S1000D files
    s1000d_patterns = [
        "test_data/s1000d/procedures/*.XML",
        "test_data/s1000d/descriptions/*.XML",
        "test_data/s1000d/equipment_lists/*.XML"
    ]
    
    all_files = []
    for pattern in s1000d_patterns:
        all_files.extend(glob.glob(pattern))
    
    print(f"📁 Found {len(all_files)} S1000D files to test\n")
    
    # Track results
    success_count = 0
    failure_count = 0
    results_by_info_code = {}
    
    # Test each file
    for file_path in sorted(all_files):
        filename = os.path.basename(file_path)
        
        # Extract info code from filename (e.g., 251A, 041A, etc.)
        info_code = None
        for part in filename.split('-'):
            if 'A' in part and len(part) == 4 and part[0].isdigit():
                info_code = part
                break
        
        print(f"Testing: {filename}")
        print(f"   Info Code: {info_code}")
        
        try:
            result = xaf.analyze(file_path)
            
            # Check what type of object we got
            if hasattr(result, '__dict__'):
                print(f"   Result type: Object with attributes")
                attrs = [attr for attr in dir(result) if not attr.startswith('_')]
                print(f"   Available attributes: {', '.join(attrs[:10])}")
            elif isinstance(result, dict):
                print(f"   Result type: Dictionary")
                print(f"   Keys: {', '.join(list(result.keys())[:10])}")
            else:
                print(f"   Result type: {type(result)}")
            
            # Try to access the expected attributes
            has_handler_used = False
            has_type_name = False
            has_confidence = False
            
            # Try object attributes first
            if hasattr(result, 'handler_used'):
                handler = result.handler_used
                has_handler_used = True
                print(f"   ✅ handler_used: {handler}")
            elif isinstance(result, dict) and 'handler_used' in result:
                handler = result['handler_used']
                has_handler_used = True
                print(f"   ✅ handler_used (dict): {handler}")
            else:
                print(f"   ❌ No handler_used attribute/key")
            
            if hasattr(result, 'type_name'):
                type_name = result.type_name
                has_type_name = True
                print(f"   ✅ type_name: {type_name}")
            elif isinstance(result, dict) and 'type_name' in result:
                type_name = result['type_name']
                has_type_name = True
                print(f"   ✅ type_name (dict): {type_name}")
            else:
                print(f"   ❌ No type_name attribute/key")
            
            if hasattr(result, 'confidence'):
                confidence = result.confidence
                has_confidence = True
                print(f"   ✅ confidence: {confidence}")
            elif isinstance(result, dict) and 'confidence' in result:
                confidence = result['confidence']
                has_confidence = True
                print(f"   ✅ confidence (dict): {confidence}")
            else:
                print(f"   ❌ No confidence attribute/key")
            
            # Check if S1000D handler was used
            if has_handler_used and handler == "S1000DHandler":
                print(f"   ✅ S1000D Handler detected correctly")
                
            # Overall success for this file
            if has_handler_used and has_type_name and has_confidence:
                print(f"   ✅ FILE PASSED - All attributes accessible")
                success_count += 1
                
                # Track by info code
                if info_code not in results_by_info_code:
                    results_by_info_code[info_code] = {'success': 0, 'failure': 0}
                results_by_info_code[info_code]['success'] += 1
            else:
                print(f"   ❌ FILE FAILED - Missing required attributes")
                failure_count += 1
                
                # Track by info code
                if info_code not in results_by_info_code:
                    results_by_info_code[info_code] = {'success': 0, 'failure': 0}
                results_by_info_code[info_code]['failure'] += 1
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            failure_count += 1
            
            # Track by info code
            if info_code not in results_by_info_code:
                results_by_info_code[info_code] = {'success': 0, 'failure': 0}
            results_by_info_code[info_code]['failure'] += 1
        
        print("-" * 70)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Total files tested: {len(all_files)}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failure_count}")
    print(f"Success rate: {success_count/len(all_files)*100:.1f}%\n")
    
    print("Results by Information Code:")
    print("-" * 40)
    for code, counts in sorted(results_by_info_code.items()):
        total = counts['success'] + counts['failure']
        success_rate = counts['success'] / total * 100 if total > 0 else 0
        status = "✅" if success_rate == 100 else "❌" if success_rate == 0 else "⚠️"
        print(f"{status} {code}: {counts['success']}/{total} passed ({success_rate:.0f}%)")
    
    # Conclusion
    print("\n" + "=" * 70)
    if failure_count == 0:
        print("🎉 All S1000D files work correctly!")
    elif failure_count > len(all_files) / 2:
        print("🚨 CRITICAL: Majority of S1000D files are failing!")
        print("   The handler needs to be fixed to return consistent object types.")
    else:
        print("⚠️  Some S1000D files have compatibility issues.")
        print("   The handler may need adjustments for certain document types.")

if __name__ == "__main__":
    test_all_s1000d_files()