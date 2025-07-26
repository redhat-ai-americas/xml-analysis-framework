#!/usr/bin/env python3
"""
Comprehensive test runner for all XML handler tests

Runs tests using pytest from the organized test directory structure:
- tests/unit/: Individual handler unit tests
- tests/integration/: Handler integration tests  
- tests/comprehensive/: Full system tests
- tests/: Framework tests
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Tuple

def run_pytest_command(test_path: str, category_name: str) -> Tuple[bool, str, float]:
    """Run pytest on a test directory and return success status, output, and execution time"""
    start_time = time.time()
    
    try:
        # Run pytest with verbose output and short traceback
        cmd = [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for test suites
            cwd=Path(__file__).parent
        )
        
        execution_time = time.time() - start_time
        
        # Check if pytest succeeded (return code 0)
        success = result.returncode == 0
        
        # Combine stdout and stderr for full output
        output = result.stdout
        if result.stderr:
            output += f"\n--- STDERR ---\n{result.stderr}"
            
        return success, output, execution_time
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return False, f"Test suite timed out after 300 seconds", execution_time
    except Exception as e:
        execution_time = time.time() - start_time
        return False, f"Error running pytest: {e}", execution_time

def run_individual_test(test_file: Path) -> Tuple[bool, str, float]:
    """Run an individual test file as a Python script"""
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout for individual tests
            cwd=test_file.parent
        )
        
        execution_time = time.time() - start_time
        success = result.returncode == 0
        
        output = result.stdout
        if result.stderr:
            output += f"\n--- STDERR ---\n{result.stderr}"
            
        return success, output, execution_time
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return False, "Test timed out after 60 seconds", execution_time
    except Exception as e:
        execution_time = time.time() - start_time
        return False, f"Error running test: {e}", execution_time

def run_pytest_category(category_name: str, test_path: str) -> Dict:
    """Run pytest on a test directory"""
    print(f"\n🧪 Running {category_name} Tests")
    print("=" * 60)
    
    test_dir = Path(test_path)
    if not test_dir.exists():
        print(f"  ⏭️  Directory {test_path} not found")
        return {
            'category': category_name,
            'success': False,
            'message': f"Directory {test_path} not found",
            'execution_time': 0.0
        }
    
    # Count test files
    test_files = list(test_dir.glob("test_*.py"))
    if not test_files:
        print(f"  ⏭️  No test files found in {test_path}")
        return {
            'category': category_name,
            'success': True,
            'message': f"No test files found in {test_path}",
            'execution_time': 0.0,
            'tests_found': 0
        }
    
    print(f"  📁 Found {len(test_files)} test files")
    
    # Run pytest
    success, output, exec_time = run_pytest_command(test_path, category_name)
    
    # Parse pytest output for summary
    lines = output.split('\n')
    summary_line = None
    for line in lines:
        if 'passed' in line and ('failed' in line or 'error' in line or '=' in line):
            summary_line = line.strip()
            break
    
    if success:
        print(f"  ✅ PASSED ({exec_time:.2f}s)")
        if summary_line:
            print(f"     {summary_line}")
    else:
        print(f"  ❌ FAILED ({exec_time:.2f}s)")
        if summary_line:
            print(f"     {summary_line}")
        
        # Show first few lines of error output
        error_lines = [line for line in lines if line.strip() and ('FAILED' in line or 'ERROR' in line or 'AssertionError' in line)]
        for line in error_lines[:3]:  # Show first 3 error lines
            print(f"     {line.strip()}")
    
    return {
        'category': category_name,
        'success': success,
        'message': summary_line or "No summary available",
        'execution_time': exec_time,
        'tests_found': len(test_files),
        'full_output': output
    }

def run_framework_test(test_file: Path) -> Dict:
    """Run an individual framework test file"""
    print(f"\n🔍 Running {test_file.name}")
    
    success, output, exec_time = run_individual_test(test_file)
    
    if success:
        print(f"  ✅ PASSED ({exec_time:.2f}s)")
        # Show key success messages
        success_lines = [line for line in output.split('\n') if '✅' in line]
        for line in success_lines[-3:]:  # Show last 3 success messages
            if line.strip():
                print(f"     {line.strip()}")
    else:
        print(f"  ❌ FAILED ({exec_time:.2f}s)")
        # Show error summary
        error_lines = [line for line in output.split('\n') if '❌' in line or 'Error' in line or 'Failed' in line]
        for line in error_lines[:3]:  # Show first 3 error lines
            if line.strip():
                print(f"     {line.strip()}")
    
    return {
        'test_file': test_file.name,
        'success': success,
        'execution_time': exec_time,
        'output': output
    }

def main():
    """Run all test categories"""
    print("🧪 XML HANDLERS COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("Testing all handlers from organized test directory structure")
    
    start_time = time.time()
    all_results = []
    
    # Test categories using pytest
    pytest_categories = [
        ("Unit Tests", "unit/"),
        ("Integration Tests", "integration/"),
        ("Comprehensive Tests", "comprehensive/")
    ]
    
    for category_name, test_path in pytest_categories:
        result = run_pytest_category(category_name, test_path)
        all_results.append(result)
    
    # Framework tests (run as individual scripts)
    print(f"\n🧪 Running Framework Tests")
    print("=" * 60)
    
    framework_tests = [
        Path("test_framework.py"),
        Path("test_setup.py"),
        Path("test_existing_handlers.py")
    ]
    
    framework_results = []
    for test_file in framework_tests:
        if test_file.exists():
            result = run_framework_test(test_file)
            framework_results.append(result)
        else:
            print(f"\n🔍 Running {test_file.name}")
            print(f"  ⏭️  File not found: {test_file}")
    
    # Overall summary
    total_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("📊 OVERALL TEST RESULTS SUMMARY")
    print("=" * 80)
    
    # Pytest results summary
    pytest_success = sum(1 for r in all_results if r.get('success', False))
    pytest_total = len([r for r in all_results if 'tests_found' in r])
    
    print(f"Pytest Categories: {pytest_success}/{pytest_total} passed")
    for result in all_results:
        status = "✅" if result.get('success', False) else "❌"
        exec_time = result.get('execution_time', 0)
        tests_found = result.get('tests_found', 'N/A')
        print(f"  {status} {result['category']:<20} ({tests_found} tests, {exec_time:.2f}s)")
    
    # Framework test summary
    framework_success = sum(1 for r in framework_results if r.get('success', False))
    framework_total = len(framework_results)
    
    print(f"\nFramework Tests: {framework_success}/{framework_total} passed")
    for result in framework_results:
        status = "✅" if result.get('success', False) else "❌"
        exec_time = result.get('execution_time', 0)
        print(f"  {status} {result['test_file']:<25} ({exec_time:.2f}s)")
    
    # Overall status
    total_success = pytest_success + framework_success
    total_tests = pytest_total + framework_total
    success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nOverall Success Rate: {total_success}/{total_tests} ({success_rate:.1f}%)")
    print(f"Total Execution Time: {total_time:.2f}s")
    
    if success_rate >= 80:
        print("\n✅ TEST SUITE PASSED - Most tests are working!")
        return 0
    elif success_rate >= 50:
        print("\n⚠️  TEST SUITE PARTIALLY PASSED - Some issues need attention")
        return 1
    else:
        print("\n❌ TEST SUITE FAILED - Significant issues need fixing")
        return 1

if __name__ == "__main__":
    sys.exit(main())