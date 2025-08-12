#!/usr/bin/env python3
"""
Test S1000D Handler with Real Test Data

This script tests the S1000D handler with the newly collected test data files
to verify proper detection and analysis across different document types.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
framework_root = Path(__file__).parent
src_path = framework_root / "src"
sys.path.insert(0, str(framework_root))
sys.path.insert(0, str(src_path))

def safe_get_attr(obj, attr, default="Unknown"):
    """Safely get attribute from object, handling both dict and object types"""
    if isinstance(obj, dict):
        return obj.get(attr, default)
    else:
        return getattr(obj, attr, default)

def test_s1000d_files():
    """Test S1000D handler with collected test data"""
    
    try:
        import src as xaf
        
        print("🧪 S1000D Handler Test with Real Data")
        print("=" * 60)
        
        test_files = {
            "🔧 PROCEDURES (DA1*251A*, DA2*520A*)": [
                "test_data/s1000d/procedures/DMC-BRAKE-AAA-DA1-10-00-00AA-251A-A_003-00_EN-US.XML",
                "test_data/s1000d/procedures/DMC-S1000DBIKE-AAA-DA1-10-00-00AA-251A-A_009-00_EN-US.XML",
                "test_data/s1000d/procedures/DMC-S1000DBIKE-AAA-DA2-10-00-00AA-520A-A_010-00_EN-US.XML",
                "test_data/s1000d/procedures/DMC-S1000DBIKE-AAA-DA2-20-00-00AA-520A-A_010-00_EN-US.XML",
                "test_data/s1000d/procedures/DMC-S1000DBIKE-AAA-DA2-30-00-00AA-520A-A_010-00_EN-US.XML"
            ],
            "📄 DESCRIPTIONS (*041A*, *341A*)": [
                "test_data/s1000d/descriptions/DMC-BRAKE-AAA-DA1-00-00-00AA-041A-A_003-00_EN-US.XML",
                "test_data/s1000d/descriptions/DMC-BRAKE-AAA-DA1-00-00-00AA-341A-A_003-00_EN-US.XML",
                "test_data/s1000d/descriptions/DMC-S1000DBIKE-AAA-D00-00-00-00AA-041A-A_011-00_EN-US.XML",
                "test_data/s1000d/descriptions/DMC-S1000DBIKE-AAA-DA1-00-00-00AA-341A-A_009-00_EN-US.XML",
                "test_data/s1000d/descriptions/DMC-S1000DLIGHTING-AAA-D00-00-00-00AA-341A-A_009-00_EN-US.XML"
            ],
            "📋 EQUIPMENT LISTS (*056A*)": [
                "test_data/s1000d/equipment_lists/DMC-S1000DLIGHTING-AAA-D00-00-00-00AA-056A-A_010-00_EN-US.XML"
            ]
        }
        
        total_files = 0
        successful_s1000d = 0
        
        for category, files in test_files.items():
            print(f"\n{category}")
            print("-" * 60)
            
            for file_path in files:
                if not os.path.exists(file_path):
                    print(f"   ❌ File not found: {file_path}")
                    continue
                    
                try:
                    result = xaf.analyze(file_path)
                    total_files += 1
                    
                    filename = os.path.basename(file_path)[:45] + "..."
                    handler = safe_get_attr(result, "handler_used")
                    doc_type = safe_get_attr(result, "type_name") 
                    confidence = safe_get_attr(result, "confidence")
                    
                    print(f"   📄 {filename}")
                    print(f"      Handler: {handler}")
                    print(f"      Type: {doc_type}")
                    print(f"      Confidence: {confidence}")
                    
                    # Check if S1000D handler was used
                    if handler == "S1000DHandler":
                        successful_s1000d += 1
                        print(f"      ✅ S1000D detected correctly")
                        
                        # Try to get DMC code if available
                        if hasattr(result, 'metadata') and isinstance(result.metadata, dict):
                            dmc_code = result.metadata.get('dmc_code')
                            if dmc_code:
                                print(f"      DMC: {dmc_code}")
                    else:
                        print(f"      ⚠️  Expected S1000DHandler, got {handler}")
                    
                    print()
                    
                except Exception as e:
                    print(f"   ❌ Error analyzing {file_path}: {e}")
                    total_files += 1
        
        # Summary
        print("=" * 60)
        print(f"📊 Test Summary:")
        print(f"   Total files tested: {total_files}")
        print(f"   S1000D handler used: {successful_s1000d}")
        print(f"   Success rate: {successful_s1000d/total_files*100:.1f}%" if total_files > 0 else "   No files tested")
        
        if successful_s1000d == total_files:
            print("🎉 All files correctly identified as S1000D!")
            return True
        else:
            print("⚠️  Some files were not identified as S1000D")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_s1000d_files()
    sys.exit(0 if success else 1)