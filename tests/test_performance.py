#!/usr/bin/env python3
"""
Performance test to verify the framework actually processes real files
and measure realistic processing times.
"""

import sys
import time
from pathlib import Path
import defusedxml.ElementTree as ET

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.analyzer import XMLDocumentAnalyzer
from src.handlers.servicenow_handler import ServiceNowHandler
from src.handlers.scap_handler import SCAPHandler


def time_analysis(file_path: str, description: str):
    """Time how long it takes to analyze a real file"""
    print(f"\n📊 Testing: {description}")
    print(f"📁 File: {file_path}")
    
    # Check file exists and get size
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return None
        
    file_size = path.stat().st_size
    print(f"📐 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    # Time the parsing
    start_time = time.time()
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        parse_time = time.time() - start_time
        print(f"⏱️  XML parsing: {parse_time:.3f}s")
        
        # Count elements
        element_count = len(list(root.iter()))
        print(f"🔢 Elements found: {element_count:,}")
        
        # Time the analysis
        analyzer = XMLDocumentAnalyzer()
        start_time = time.time()
        result = analyzer.analyze_document(file_path)
        analysis_time = time.time() - start_time
        
        print(f"⏱️  Analysis time: {analysis_time:.3f}s")
        print(f"🎯 Handler used: {result.get('handler_used', 'Unknown')}")
        print(f"📋 Document type: {result.get('document_type', {}).type_name}")
        
        total_time = parse_time + analysis_time
        print(f"⏱️  Total time: {total_time:.3f}s")
        
        # Calculate throughput
        elements_per_sec = element_count / total_time if total_time > 0 else 0
        print(f"🚀 Throughput: {elements_per_sec:,.0f} elements/sec")
        
        return {
            'file_size': file_size,
            'element_count': element_count,
            'parse_time': parse_time,
            'analysis_time': analysis_time,
            'total_time': total_time,
            'throughput': elements_per_sec
        }
        
    except Exception as e:
        error_time = time.time() - start_time
        print(f"❌ Error after {error_time:.3f}s: {e}")
        return None


def main():
    """Run performance tests on real files"""
    print("🚀 XML ANALYSIS FRAMEWORK - PERFORMANCE TEST")
    print("=" * 60)
    
    # Test files to analyze
    test_files = [
        ("sample_data/test_files_synthetic/small/servicenow/incident_export.xml", 
         "ServiceNow Incident (Small)"),
        ("sample_data/test_files_synthetic/medium/servicenow/full_export.xml", 
         "ServiceNow Full Export (Medium)"),
        ("sample_data/test_files/small/scap/ios-sample-1.0.xccdf.xml", 
         "SCAP/XCCDF Security Document"),
        ("sample_data/test_files/small/ant/ant-ivy-build.xml", 
         "Apache Ant Build Script"),
        ("sample_data/test_files_synthetic/small/pom/spring-boot-example-pom.xml",
         "Maven POM Spring Boot"),
    ]
    
    results = []
    project_root = Path(__file__).parent.parent
    
    for file_path, description in test_files:
        full_path = project_root / file_path
        result = time_analysis(str(full_path), description)
        if result:
            results.append((description, result))
    
    # Summary
    print(f"\n{'='*60}")
    print("📈 PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    
    if results:
        total_elements = sum(r[1]['element_count'] for r in results)
        total_time = sum(r[1]['total_time'] for r in results)
        avg_throughput = total_elements / total_time if total_time > 0 else 0
        
        print(f"🔢 Total elements processed: {total_elements:,}")
        print(f"⏱️  Total processing time: {total_time:.3f}s")
        print(f"🚀 Average throughput: {avg_throughput:,.0f} elements/sec")
        
        print(f"\n📊 Individual Results:")
        for description, result in results:
            print(f"  {description}:")
            print(f"    Elements: {result['element_count']:,}")
            print(f"    Time: {result['total_time']:.3f}s")
            print(f"    Speed: {result['throughput']:,.0f} elem/sec")
    
    print(f"\n✅ Performance test completed!")


if __name__ == "__main__":
    main()