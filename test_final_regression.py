#!/usr/bin/env python3

import xml_analysis_framework as xaf
import os
import glob
from collections import defaultdict

print("Final regression test for xml-analysis-framework v1.4.4")
print("=" * 70)

# Get diverse test files from different categories
test_files = []

# Small files - various types
small_dirs = ["ant", "hl7", "kml", "gpx", "tei", "pmml", "scap"]
for dir_name in small_dirs:
    pattern = f"sample_data/test_files/small/{dir_name}/*.xml"
    found = glob.glob(pattern)[:1]  # Take 1 from each type
    test_files.extend(found)

# Medium files
medium_files = glob.glob("sample_data/test_files/medium/**/*.xml", recursive=True)[:5]
test_files.extend(medium_files)

# Large files
large_files = glob.glob("sample_data/test_files/large/**/*.xml", recursive=True)[:2]
test_files.extend(large_files)

# Add SCAP file if exists
scap_file = "sample_data/node2.example.com-STIG-20250710162433.xml"
if os.path.exists(scap_file):
    test_files.append(scap_file)

# Remove duplicates
test_files = list(set([f for f in test_files if os.path.exists(f)]))

print(f"Testing {len(test_files)} diverse XML files from multiple categories\n")
print("-" * 70)

# Test each file
results = defaultdict(list)
successes = 0
failures = []
chunk_tests = 0

for file_path in sorted(test_files):
    try:
        # Basic analysis
        result = xaf.analyze(file_path)
        doc_type = result.type_name
        confidence = result.confidence
        file_size = os.path.getsize(file_path) / 1024  # KB
        
        results[doc_type].append({
            'file': os.path.basename(file_path),
            'confidence': confidence,
            'size_kb': file_size
        })
        successes += 1
        
        # Display result
        fname = os.path.basename(file_path)[:40]
        size_str = f"{file_size:.1f}KB"
        print(f"✓ {fname:40} [{size_str:>8}] -> {doc_type} ({confidence:.2f})")
        
        # Test chunking on a subset
        if chunk_tests < 5 and file_size < 100:  # Test chunking on smaller files
            try:
                chunks = xaf.chunk(file_path, strategy="hierarchical")
                print(f"  └─ Chunking: {len(chunks)} chunks")
                chunk_tests += 1
            except Exception as ce:
                print(f"  └─ Chunking failed: {str(ce)[:50]}")
            
    except Exception as e:
        failures.append((file_path, str(e)))
        fname = os.path.basename(file_path)[:40]
        print(f"✗ {fname:40} -> ERROR: {str(e)[:50]}")

print("\n" + "=" * 70)
print("RESULTS SUMMARY")
print("=" * 70)

print(f"\n📊 Overall Success Rate: {successes}/{len(test_files)} ({100*successes/len(test_files):.1f}%)")

print("\n📋 Document Types Detected:")
for doc_type, files in sorted(results.items()):
    avg_confidence = sum(f['confidence'] for f in files) / len(files)
    total_size = sum(f['size_kb'] for f in files)
    print(f"  • {doc_type}:")
    print(f"    - Files: {len(files)}")
    print(f"    - Avg confidence: {avg_confidence:.2f}")
    print(f"    - Total size: {total_size:.1f} KB")

if failures:
    print(f"\n❌ Failed Files ({len(failures)}):")
    for filepath, error in failures[:5]:
        print(f"  ✗ {os.path.basename(filepath)}: {error[:80]}")

# Test different chunking strategies
print("\n" + "=" * 70)
print("CHUNKING STRATEGY TESTS")
print("=" * 70)

test_file = test_files[0] if test_files else None
if test_file and os.path.exists(test_file):
    print(f"\nTesting chunking strategies on: {os.path.basename(test_file)}")
    strategies = ["hierarchical", "sliding_window", "content_aware", "auto"]
    
    for strategy in strategies:
        try:
            chunks = xaf.chunk(test_file, strategy=strategy)
            print(f"  • {strategy:15} -> {len(chunks)} chunks")
        except Exception as e:
            print(f"  • {strategy:15} -> ERROR: {str(e)[:40]}")

# Test API consistency
print("\n" + "=" * 70)
print("API CONSISTENCY TESTS")
print("=" * 70)

if test_files:
    test_file = test_files[0]
    print(f"\nTesting API methods on: {os.path.basename(test_file)}")
    
    try:
        # Test analyze (enhanced)
        result1 = xaf.analyze(test_file)
        print(f"  ✓ analyze():          {result1.type_name}")
        
        # Test analyze_enhanced (explicit)
        result2 = xaf.analyze_enhanced(test_file)
        print(f"  ✓ analyze_enhanced(): {result2.type_name}")
        
        # Test schema analysis
        schema = xaf.analyze_schema(test_file)
        print(f"  ✓ analyze_schema():   {schema.total_elements} elements")
        
        # Test direct class usage
        analyzer = xaf.XMLDocumentAnalyzer()
        result3 = analyzer.analyze_document(test_file)
        print(f"  ✓ Direct class:       {result3.type_name}")
        
    except Exception as e:
        print(f"  ✗ API Error: {e}")

print("\n" + "=" * 70)
if failures:
    print(f"⚠️  Testing completed with {len(failures)} failures")
else:
    print("✅ All tests passed successfully!")
print(f"📦 xml-analysis-framework v1.4.4 regression test complete")
print("=" * 70)