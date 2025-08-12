#!/usr/bin/env python3

import xml_analysis_framework as xaf
import glob
import os

print("Testing xml-analysis-framework v1.4.4 with S1000D entity handling")
print("=" * 60)

# Test S1000D files with entities
s1000d_files = (glob.glob("test_data/s1000d/procedures/*.XML") + 
                glob.glob("test_data/s1000d/descriptions/*.XML"))[:5]  # Test first 5

successes = 0
failures = 0

for file_path in s1000d_files:
    try:
        result = xaf.analyze(file_path)
        print(f"✓ {os.path.basename(file_path)}: {result.type_name}")
        successes += 1
    except Exception as e:
        print(f"✗ {os.path.basename(file_path)}: {e}")
        failures += 1

print("\n" + "=" * 60)
print(f"Results: {successes} successes, {failures} failures")
print(f"Success rate: {successes}/{len(s1000d_files)} ({100*successes/len(s1000d_files):.0f}%)")

# Test with a file that has entities
test_file = "test_data/s1000d/procedures/DA2-DA41-A2-02-0520A-341A-B.XML"
if os.path.exists(test_file):
    print(f"\nDetailed test of file with entities: {os.path.basename(test_file)}")
    result = xaf.analyze(test_file)
    
    if hasattr(result, 'metadata') and result.metadata and 'extracted_entities' in result.metadata:
        print(f"Extracted entities: {len(result.metadata['extracted_entities'])}")
        for entity in result.metadata['extracted_entities'][:3]:
            print(f"  - {entity['name']}: {entity['system_id']}")