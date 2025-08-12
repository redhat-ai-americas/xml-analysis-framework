#!/usr/bin/env python3
"""
Test script to verify xml-analysis-framework 1.4.2 from PyPI
Tests the package with real S1000D files and other XML documents
"""

import sys
import subprocess
import os
from pathlib import Path

def install_package():
    """Install the latest version from PyPI"""
    print("📦 Installing xml-analysis-framework 1.4.2 from PyPI...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "--upgrade", "xml-analysis-framework==1.4.2"
        ], check=True)
        print("✅ Package installed successfully\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install package: {e}")
        return False

def test_package_import():
    """Test basic package import and version"""
    print("🔍 Testing package import...")
    try:
        import xml_analysis_framework as xaf
        print(f"✅ Package imported successfully")
        print(f"   Version: {xaf.__version__}")
        
        # Check for expected functions
        assert hasattr(xaf, 'analyze'), "Missing 'analyze' function"
        assert hasattr(xaf, 'analyze_schema'), "Missing 'analyze_schema' function"
        assert hasattr(xaf, 'chunk'), "Missing 'chunk' function"
        print("✅ All expected functions are available\n")
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}\n")
        return False

def test_s1000d_files():
    """Test S1000D handler with real files"""
    print("🔧 Testing S1000D Handler with real files...")
    
    import xml_analysis_framework as xaf
    
    test_files = {
        "Procedures (251A, 520A)": [
            "test_data/s1000d/procedures/DMC-BRAKE-AAA-DA1-10-00-00AA-251A-A_003-00_EN-US.XML",
            "test_data/s1000d/procedures/DMC-S1000DBIKE-AAA-DA1-10-00-00AA-251A-A_009-00_EN-US.XML",
            "test_data/s1000d/procedures/DMC-S1000DBIKE-AAA-DA2-10-00-00AA-520A-A_010-00_EN-US.XML",
        ],
        "Descriptions (041A, 341A)": [
            "test_data/s1000d/descriptions/DMC-BRAKE-AAA-DA1-00-00-00AA-041A-A_003-00_EN-US.XML",
            "test_data/s1000d/descriptions/DMC-S1000DBIKE-AAA-DA1-00-00-00AA-341A-A_009-00_EN-US.XML",
            "test_data/s1000d/descriptions/DMC-S1000DLIGHTING-AAA-D00-00-00-00AA-341A-A_009-00_EN-US.XML",
        ],
        "Equipment Lists (056A)": [
            "test_data/s1000d/equipment_lists/DMC-S1000DLIGHTING-AAA-D00-00-00-00AA-056A-A_010-00_EN-US.XML",
        ]
    }
    
    total_tests = 0
    successful_s1000d = 0
    
    for category, files in test_files.items():
        print(f"\n📂 {category}")
        print("-" * 50)
        
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"   ⚠️  File not found: {file_path}")
                continue
            
            try:
                # Test basic analysis
                result = xaf.analyze(file_path)
                total_tests += 1
                
                filename = os.path.basename(file_path)[:40] + "..."
                print(f"   📄 {filename}")
                print(f"      Handler: {result.handler_used}")
                print(f"      Type: {result.type_name}")
                print(f"      Confidence: {result.confidence}")
                
                # Check if S1000D handler was used
                if result.handler_used == "S1000DHandler":
                    successful_s1000d += 1
                    print(f"      ✅ S1000D detected correctly")
                    
                    # Try to access metadata if available
                    if hasattr(result, 'metadata') and result.metadata:
                        if 'dmc_code' in result.metadata:
                            print(f"      DMC: {result.metadata['dmc_code']}")
                        if 'info_code' in result.metadata:
                            print(f"      Info Code: {result.metadata['info_code']}")
                else:
                    print(f"      ⚠️  Expected S1000DHandler, got {result.handler_used}")
                    
            except Exception as e:
                print(f"   ❌ Error analyzing {file_path}: {e}")
                total_tests += 1
    
    print("\n" + "=" * 50)
    print(f"S1000D Handler Test Summary:")
    print(f"   Total files tested: {total_tests}")
    print(f"   S1000D detected: {successful_s1000d}")
    print(f"   Success rate: {successful_s1000d/total_tests*100:.1f}%" if total_tests > 0 else "   No files tested")
    
    return successful_s1000d > 0

def test_other_xml_files():
    """Test with other XML file types"""
    print("\n📚 Testing other XML handlers...")
    
    import xml_analysis_framework as xaf
    
    # Sample XML documents to test
    test_cases = [
        {
            "name": "RSS Feed",
            "content": """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>http://example.com</link>
    <description>Test RSS feed</description>
    <item>
      <title>Test Item</title>
      <link>http://example.com/item1</link>
      <description>Test item description</description>
    </item>
  </channel>
</rss>""",
            "expected_handler": "RSSHandler"
        },
        {
            "name": "Maven POM",
            "content": """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>test-project</artifactId>
  <version>1.0.0</version>
  <dependencies>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.12</version>
    </dependency>
  </dependencies>
</project>""",
            "expected_handler": "MavenPOMHandler"
        },
        {
            "name": "Generic XML",
            "content": """<?xml version="1.0" encoding="UTF-8"?>
<root>
  <data>
    <item id="1">Test Item 1</item>
    <item id="2">Test Item 2</item>
  </data>
</root>""",
            "expected_handler": "GenericXMLHandler"
        }
    ]
    
    success_count = 0
    
    for test in test_cases:
        # Create temporary file
        temp_file = f"temp_test_{test['name'].replace(' ', '_').lower()}.xml"
        try:
            with open(temp_file, 'w') as f:
                f.write(test['content'])
            
            # Analyze the file
            result = xaf.analyze(temp_file)
            
            print(f"\n   📝 {test['name']}:")
            print(f"      Handler: {result.handler_used}")
            print(f"      Expected: {test['expected_handler']}")
            
            if result.handler_used == test['expected_handler']:
                print(f"      ✅ Correct handler detected")
                success_count += 1
            else:
                print(f"      ⚠️  Different handler than expected")
            
            # Test chunking
            chunks = xaf.chunk(temp_file)
            print(f"      Chunks created: {len(chunks)}")
            
            # Test schema analysis
            schema = xaf.analyze_schema(temp_file)
            print(f"      Schema elements: {schema.total_elements}")
            
        except Exception as e:
            print(f"   ❌ Error testing {test['name']}: {e}")
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    print(f"\n   Other handlers success: {success_count}/{len(test_cases)}")
    return success_count == len(test_cases)

def test_chunking_strategies():
    """Test different chunking strategies"""
    print("\n🔪 Testing chunking strategies...")
    
    import xml_analysis_framework as xaf
    
    # Test with an S1000D file if available
    test_file = "test_data/s1000d/procedures/DMC-BRAKE-AAA-DA1-10-00-00AA-251A-A_003-00_EN-US.XML"
    
    if not os.path.exists(test_file):
        # Create a simple test file
        test_file = "temp_chunking_test.xml"
        with open(test_file, 'w') as f:
            f.write("""<?xml version="1.0"?>
<document>
    <section id="1">
        <title>Section 1</title>
        <content>This is the first section with some content.</content>
    </section>
    <section id="2">
        <title>Section 2</title>
        <content>This is the second section with more content.</content>
    </section>
    <section id="3">
        <title>Section 3</title>
        <content>This is the third section with additional content.</content>
    </section>
</document>""")
        temp_created = True
    else:
        temp_created = False
    
    strategies = ["auto", "hierarchical", "sliding_window", "content_aware"]
    success_count = 0
    
    for strategy in strategies:
        try:
            chunks = xaf.chunk(test_file, strategy=strategy)
            print(f"   📊 Strategy '{strategy}': {len(chunks)} chunks created")
            
            if len(chunks) > 0:
                # Handle XMLChunk objects (they have .text attribute)
                first_chunk = chunks[0]
                if hasattr(first_chunk, 'text'):
                    print(f"      First chunk size: {len(first_chunk.text)} chars")
                else:
                    print(f"      First chunk type: {type(first_chunk)}")
                success_count += 1
            else:
                print(f"      ⚠️  No chunks created")
                
        except Exception as e:
            print(f"   ❌ Error with strategy '{strategy}': {e}")
    
    # Clean up if we created a temp file
    if temp_created and os.path.exists(test_file):
        os.remove(test_file)
    
    print(f"\n   Chunking strategies success: {success_count}/{len(strategies)}")
    return success_count > 0

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 XML Analysis Framework v1.4.2 PyPI Package Test")
    print("=" * 60)
    
    # Track test results
    results = []
    
    # Install package
    if not install_package():
        print("❌ Cannot proceed without package installation")
        sys.exit(1)
    
    # Run tests
    results.append(("Import Test", test_package_import()))
    results.append(("S1000D Files", test_s1000d_files()))
    results.append(("Other XML Types", test_other_xml_files()))
    results.append(("Chunking Strategies", test_chunking_strategies()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n   Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Package is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()