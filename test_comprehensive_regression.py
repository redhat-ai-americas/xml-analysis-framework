#!/usr/bin/env python3

import xml_analysis_framework as xaf
import os
from collections import defaultdict

print("Comprehensive regression test for xml-analysis-framework v1.4.4")
print("=" * 70)

# Specific test files we know exist
test_files = [
    # SCAP file
    "sample_data/node2.example.com-STIG-20250710162433.xml",
    # Various types from test_files
    "sample_data/test_files/small/apache-ant-build.xml",
    "sample_data/test_files/small/ccda-care-plan.xml",
    "sample_data/test_files/small/maven-resolver-ant-build.xml",
    "sample_data/test_files/small/tei-simple-spec.xml",
    "sample_data/test_files/medium/ios-sample-1.0.xccdf.xml",
    "sample_data/test_files/medium/sample-wadl.xml",
]

# Add more files if they exist
additional_patterns = [
    "sample_data/test_files/**/*.xml",
    "sample_data/test_files_synthetic/*.xml"
]

import glob
for pattern in additional_patterns:
    found = glob.glob(pattern, recursive=True)[:3]  # Take up to 3 from each pattern
    test_files.extend(found)

# Remove duplicates and non-existent files
test_files = list(set([f for f in test_files if os.path.exists(f)]))[:30]

# Test each file
results = defaultdict(list)
successes = 0
failures = []

print(f"Testing {len(test_files)} XML files...\n")

for file_path in sorted(test_files):
    try:
        result = xaf.analyze(file_path)
        doc_type = result.type_name
        confidence = result.confidence
        results[doc_type].append((os.path.basename(file_path), confidence))
        successes += 1
        
        # Show file and type
        fname = os.path.basename(file_path)[:35]
        print(f"✓ {fname:35} -> {doc_type} ({confidence:.2f})")
        
        # Test chunking on a few files
        if successes <= 3:
            chunks = xaf.chunk(file_path, strategy="hierarchical")
            print(f"  └─ Chunking: {len(chunks)} chunks created")
            
    except Exception as e:
        failures.append((file_path, str(e)))
        fname = os.path.basename(file_path)[:35]
        print(f"✗ {fname:35} -> ERROR: {str(e)[:50]}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\nSuccess Rate: {successes}/{len(test_files)} ({100*successes/len(test_files):.1f}%)")

print("\nDocument Types Detected:")
for doc_type, files in sorted(results.items()):
    avg_confidence = sum(f[1] for f in files) / len(files)
    print(f"  • {doc_type}: {len(files)} file(s), avg confidence: {avg_confidence:.2f}")

if failures:
    print(f"\n❌ Failed Files ({len(failures)}):")
    for filepath, error in failures[:5]:  # Show first 5 failures
        print(f"  ✗ {os.path.basename(filepath)}: {error[:80]}")

# Test specific functionality
print("\n" + "=" * 70)
print("FUNCTIONALITY TESTS")
print("=" * 70)

# Test SCAP file specifically
scap_file = "sample_data/node2.example.com-STIG-20250710162433.xml"
if os.path.exists(scap_file):
    print("\n1. SCAP Analysis:")
    try:
        result = xaf.analyze(scap_file)
        print(f"   Type: {result.type_name}")
        print(f"   Confidence: {result.confidence:.2f}")
        if result.ai_use_cases:
            print(f"   AI Use Cases: {result.ai_use_cases[:2]}")
        chunks = xaf.chunk(scap_file, strategy="content_aware")
        print(f"   Content-aware chunks: {len(chunks)}")
    except Exception as e:
        print(f"   ERROR: {e}")

# Test schema analysis
print("\n2. Schema Analysis:")
try:
    schema_result = xaf.analyze_schema("sample_data/test_files/small/apache-ant-build.xml")
    print(f"   Elements found: {schema_result.total_elements}")
    print(f"   Max depth: {schema_result.max_depth}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 70)
if failures:
    print(f"⚠️  Regression test completed with {len(failures)} failures")
else:
    print("✅ All regression tests passed successfully!")
print("=" * 70)