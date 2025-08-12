#!/usr/bin/env python3
"""
S1000D RAG Demo Script

Demonstrates how to use the XML Analysis Framework with the new S1000D handler
to prepare S1000D technical documentation for RAG (Retrieval Augmented Generation) applications.
"""

import sys
import os
import json
from pathlib import Path

# Add src to path for imports
framework_root = Path(__file__).parent
src_path = framework_root / "src"
sys.path.insert(0, str(src_path))

def analyze_s1000d_document(file_path: str):
    """Analyze a single S1000D document for RAG preparation"""
    
    try:
        import src as xaf
        
        print(f"📄 Analyzing S1000D document: {os.path.basename(file_path)}")
        print("-" * 60)
        
        # Enhanced analysis with S1000D-specific insights
        analysis = xaf.analyze_enhanced(file_path)
        
        print(f"🔍 Document Type: {analysis.type_name}")
        print(f"🎯 Handler Used: {analysis.handler_used}")
        print(f"📊 Confidence: {analysis.confidence:.2f}")
        
        if hasattr(analysis, 'metadata') and analysis.metadata:
            print(f"📋 S1000D Metadata:")
            for key, value in analysis.metadata.items():
                if key in ['dmc_code', 'technical_name', 'info_name', 'document_subtype']:
                    print(f"   {key}: {value}")
        
        if hasattr(analysis, 'key_findings') and analysis.key_findings:
            s1000d_info = analysis.key_findings.get('s1000d_info', {})
            if s1000d_info:
                print(f"🔧 S1000D Info:")
                print(f"   Document Type: {s1000d_info.get('document_type', 'Unknown')}")
                print(f"   Version: {s1000d_info.get('version', 'Unknown')}")
                
                dmc_analysis = s1000d_info.get('dmc_analysis', {})
                if dmc_analysis.get('valid'):
                    print(f"   DMC Code: {dmc_analysis.get('full_code', 'N/A')}")
        
        # Show AI use cases
        if hasattr(analysis, 'ai_use_cases') and analysis.ai_use_cases:
            print(f"🤖 AI Use Cases:")
            for use_case in analysis.ai_use_cases[:3]:  # Show first 3
                print(f"   • {use_case}")
        
        # Show data inventory
        if hasattr(analysis, 'data_inventory') and analysis.data_inventory:
            print(f"📊 Data Inventory:")
            for data_type, count in analysis.data_inventory.items():
                if count > 0:
                    print(f"   {data_type}: {count}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def chunk_s1000d_for_rag(file_path: str, strategy: str = "hierarchical"):
    """Chunk S1000D document for RAG applications"""
    
    try:
        import src as xaf
        
        print(f"\n✂️  Chunking S1000D document using '{strategy}' strategy...")
        print("-" * 60)
        
        chunks = xaf.chunk(file_path, strategy=strategy)
        
        print(f"📦 Generated {len(chunks)} chunks")
        
        # Analyze chunk characteristics
        if chunks:
            avg_size = sum(chunk.token_estimate for chunk in chunks) / len(chunks)
            max_size = max(chunk.token_estimate for chunk in chunks)
            min_size = min(chunk.token_estimate for chunk in chunks)
            
            print(f"📏 Chunk Statistics:")
            print(f"   Average size: {avg_size:.0f} tokens")
            print(f"   Max size: {max_size} tokens")
            print(f"   Min size: {min_size} tokens")
            
            # Show sample chunks
            print(f"\n📋 Sample Chunks:")
            for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                print(f"   Chunk {i+1} ({chunk.token_estimate} tokens):")
                print(f"     Path: {chunk.element_path}")
                print(f"     Content preview: {chunk.content[:100]}...")
                if chunk.elements_included:
                    print(f"     Elements: {', '.join(chunk.elements_included[:3])}{'...' if len(chunk.elements_included) > 3 else ''}")
                print()
        
        return chunks
        
    except Exception as e:
        print(f"❌ Chunking failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_rag_ready_data(analysis, chunks, output_dir: str = "s1000d_rag_output"):
    """Save analysis and chunks in RAG-ready format"""
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n💾 Saving RAG-ready data to {output_dir}/...")
        
        # Save analysis
        analysis_data = {
            "document_type": analysis.type_name,
            "handler_used": analysis.handler_used,
            "confidence": analysis.confidence,
            "metadata": analysis.metadata,
            "key_findings": analysis.key_findings,
            "ai_use_cases": analysis.ai_use_cases,
            "data_inventory": analysis.data_inventory,
            "structured_data": analysis.structured_data,
            "quality_metrics": analysis.quality_metrics,
        }
        
        with open(f"{output_dir}/analysis.json", "w") as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        # Save chunks
        chunks_data = []
        for chunk in chunks:
            chunk_data = {
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "element_path": chunk.element_path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "elements_included": chunk.elements_included,
                "metadata": chunk.metadata,
                "token_estimate": chunk.token_estimate,
            }
            chunks_data.append(chunk_data)
        
        with open(f"{output_dir}/chunks.json", "w") as f:
            json.dump(chunks_data, f, indent=2)
        
        # Create RAG-optimized metadata
        rag_metadata = {
            "document_info": {
                "type": analysis.type_name,
                "dmc_code": analysis.metadata.get("dmc_code"),
                "technical_name": analysis.metadata.get("technical_name"),
                "info_name": analysis.metadata.get("info_name"),
            },
            "chunk_summary": {
                "total_chunks": len(chunks),
                "avg_tokens": sum(c.token_estimate for c in chunks) / len(chunks) if chunks else 0,
                "content_types": list(set(c.element_path.split('/')[-1] for c in chunks if c.element_path)),
            },
            "ai_applications": analysis.ai_use_cases,
        }
        
        with open(f"{output_dir}/rag_metadata.json", "w") as f:
            json.dump(rag_metadata, f, indent=2)
        
        print(f"✅ Saved:")
        print(f"   📄 analysis.json - Complete document analysis")
        print(f"   📦 chunks.json - Document chunks for vector storage")
        print(f"   🎯 rag_metadata.json - RAG-optimized metadata")
        
        return output_dir
        
    except Exception as e:
        print(f"❌ Save failed: {e}")
        return None

def main():
    """Main demo function"""
    print("🚀 S1000D RAG Demo")
    print("=" * 60)
    
    # S1000D test file
    s1000d_file = "/Users/wjackson/Developer/AI-test-data/xml/bike_dataset/S1000D Issue 5.0/Bike Data Set for Release number 5.0/DMC-S1000DBIKE-AAA-DA1-10-00-00AA-251A-A_009-00_EN-US.XML"
    
    if not os.path.exists(s1000d_file):
        print(f"❌ S1000D test file not found: {s1000d_file}")
        print("\n📝 To run this demo:")
        print("1. Ensure the S1000D bike dataset is available")
        print("2. Update the file path in this script")
        print("3. Run the demo again")
        return False
    
    # Step 1: Analyze document
    analysis = analyze_s1000d_document(s1000d_file)
    if not analysis:
        return False
    
    # Step 2: Chunk for RAG
    chunks = chunk_s1000d_for_rag(s1000d_file, strategy="hierarchical")
    if not chunks:
        return False
    
    # Step 3: Save RAG-ready data
    output_dir = save_rag_ready_data(analysis, chunks)
    if not output_dir:
        return False
    
    print(f"\n🎉 S1000D RAG preparation complete!")
    print(f"📁 Output directory: {output_dir}")
    print(f"\n💡 Next steps for RAG implementation:")
    print(f"   1. Load chunks.json into your vector database")
    print(f"   2. Use analysis.json for context-aware retrieval")
    print(f"   3. Apply rag_metadata.json for query routing")
    print(f"   4. Implement S1000D-specific query understanding")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
