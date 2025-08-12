#!/usr/bin/env python3

import xml_analysis_framework as xaf
import glob
import os
from collections import defaultdict

print("Testing xml-analysis-framework v1.4.4 regression with various XML types")
print("=" * 70)

# Get various test files
test_patterns = [
    "sample_data/test_files/*.xml",
    "sample_data/test_files/**/*.xml",
    "sample_data/*.xml"
]

all_files = []
for pattern in test_patterns:
    all_files.extend(glob.glob(pattern, recursive=True))

# Remove duplicates and limit to diverse set
seen = set()
test_files = []
for f in all_files:
    if f not in seen and os.path.exists(f):
        seen.add(f)
        test_files.append(f)
        if len(test_files) >= 20:  # Test up to 20 files
            break

# Group results by document type
results = defaultdict(list)
successes = 0
failures = []

print(f"Testing {len(test_files)} diverse XML files...\n")

for file_path in test_files:
    try:
        result = xaf.analyze(file_path)
        doc_type = result.type_name
        results[doc_type].append(os.path.basename(file_path))
        successes += 1
        print(f"✓ {os.path.basename(file_path)[:40]:40} -> {doc_type}")
    except Exception as e:
        failures.append((os.path.basename(file_path), str(e)))
        print(f"✗ {os.path.basename(file_path)[:40]:40} -> ERROR: {str(e)[:50]}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\nSuccess Rate: {successes}/{len(test_files)} ({100*successes/len(test_files):.1f}%)")

print("\nDocument Types Detected:")
for doc_type, files in sorted(results.items()):
    print(f"  • {doc_type}: {len(files)} file(s)")

if failures:
    print(f"\nFailed Files ({len(failures)}):")
    for filename, error in failures:
        print(f"  ✗ {filename}: {error[:100]}")

# Test specific file types that are common
print("\n" + "=" * 70)
print("SPECIFIC TYPE TESTS")
print("=" * 70)

# Test SCAP if available
scap_files = glob.glob("sample_data/*STIG*.xml")[:1]
if scap_files:
    print("\nSCAP Security Report:")
    result = xaf.analyze(scap_files[0])
    print(f"  Type: {result.type_name}")
    print(f"  Confidence: {result.confidence:.2f}")
    if hasattr(result, 'key_findings') and result.key_findings:
        print(f"  Key findings: {list(result.key_findings.keys())[:3]}")

# Test Maven POM if available  
pom_files = glob.glob("sample_data/**/pom.xml", recursive=True)[:1]
if pom_files:
    print("\nMaven POM:")
    result = xaf.analyze(pom_files[0])
    print(f"  Type: {result.type_name}")
    print(f"  Confidence: {result.confidence:.2f}")

# Test RSS if available
rss_files = glob.glob("sample_data/**/*rss*.xml", recursive=True)[:1]
if rss_files:
    print("\nRSS Feed:")
    result = xaf.analyze(rss_files[0])
    print(f"  Type: {result.type_name}")
    print(f"  Confidence: {result.confidence:.2f}")

print("\n" + "=" * 70)
print("✅ Regression test complete!")