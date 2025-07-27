#!/usr/bin/env python3
"""
Test API harmonization between analyze_document and chunk_document.
Ensures both new (DocumentTypeInfo) and legacy (dict) formats work.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.analyzer import XMLDocumentAnalyzer
from src.core.chunking import ChunkingOrchestrator, ChunkingConfig
from src.base import DocumentTypeInfo, SpecializedAnalysis


def test_new_format():
    """Test with new format (DocumentTypeInfo objects)"""
    print("🧪 Testing NEW format (DocumentTypeInfo objects)")
    print("-" * 50)
    
    analyzer = XMLDocumentAnalyzer()
    orchestrator = ChunkingOrchestrator()
    
    # Analyze returns DocumentTypeInfo objects
    result = analyzer.analyze_document('sample_data/test_files/small/scap/ios-sample-1.1.xccdf.xml')
    
    print(f"Document type: {result['document_type'].type_name}")
    print(f"Confidence: {result['document_type'].confidence}")
    print(f"Type: {type(result['document_type'])}")
    
    # This should work directly without conversion
    config = ChunkingConfig(max_chunk_size=2000, min_chunk_size=300)
    chunks = orchestrator.chunk_document(
        'sample_data/test_files/small/scap/ios-sample-1.1.xccdf.xml', 
        result, 
        strategy='auto', 
        config=config
    )
    
    print(f"✅ Created {len(chunks)} chunks")
    print(f"✅ Chunk metadata includes doc type: {chunks[0].metadata.get('document_type')}")
    return True


def test_legacy_format():
    """Test with legacy format (dictionaries)"""
    print("\n🧪 Testing LEGACY format (dictionaries)")
    print("-" * 50)
    
    orchestrator = ChunkingOrchestrator()
    
    # Simulate legacy format
    legacy_result = {
        'document_type': {
            'type_name': 'SCAP/XCCDF Document',
            'confidence': 0.9
        },
        'analysis': SpecializedAnalysis(
            recommendations=['Use hierarchical chunking'],
            data_inventory={'security_rules': 100},
            ai_use_cases=['Security compliance checking'],
            structured_data={},
            quality_metrics={'completeness': 0.8}
        )
    }
    
    print(f"Document type: {legacy_result['document_type']['type_name']}")
    print(f"Confidence: {legacy_result['document_type']['confidence']}")
    print(f"Type: {type(legacy_result['document_type'])}")
    
    # This should also work
    config = ChunkingConfig(max_chunk_size=2000, min_chunk_size=300)
    chunks = orchestrator.chunk_document(
        'sample_data/test_files/small/scap/ios-sample-1.1.xccdf.xml', 
        legacy_result, 
        strategy='auto', 
        config=config
    )
    
    print(f"✅ Created {len(chunks)} chunks")
    print(f"✅ Chunk metadata includes doc type: {chunks[0].metadata.get('document_type')}")
    return True


def test_simple_api():
    """Test that the simple API works seamlessly"""
    print("\n🧪 Testing SIMPLE API (xaf.chunk)")
    print("-" * 50)
    
    import xml_analysis_framework as xaf
    from xml_analysis_framework.core.chunking import ChunkingConfig
    
    # Simple API with custom config
    config = ChunkingConfig(
        max_chunk_size=2000,
        min_chunk_size=300,
        overlap_size=150,
        preserve_hierarchy=True
    )
    
    # This handles all format conversions internally
    chunks = xaf.chunk(
        'sample_data/test_files/small/scap/ios-sample-1.1.xccdf.xml',
        strategy='auto',
        config=config
    )
    
    print(f"✅ Created {len(chunks)} chunks")
    print(f"✅ Simple API handles all conversions internally")
    return True


def main():
    """Run all harmonization tests"""
    print("🚀 XML Analysis Framework - API Harmonization Test")
    print("=" * 60)
    print("Testing that chunk_document works with both:")
    print("1. New format (DocumentTypeInfo objects from analyze_document)")
    print("2. Legacy format (dictionaries)")
    print("3. Simple API (automatic conversion)")
    print("=" * 60)
    
    tests = [
        test_new_format,
        test_legacy_format,
        test_simple_api
    ]
    
    results = []
    for test in tests:
        try:
            success = test()
            results.append(success)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 API Harmonization successful!")
        print("\n✨ Benefits of keeping confidence levels:")
        print("   🔸 Helps select the best handler when multiple match")
        print("   🔸 Provides transparency about detection certainty")
        print("   🔸 Useful for debugging and quality assurance")
        print("   🔸 Allows for confidence-based processing decisions")
    else:
        print("\n❌ Some tests failed.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())