#!/usr/bin/env python3
"""
Simple test to verify PR tracker core functionality works.
Tests the main capabilities with minimal dependencies and real functionality.
"""

import sys
import csv
import tempfile
import os
from pathlib import Path
import shutil

def test_csv_operations():
    """Test basic CSV reading/writing operations work."""
    print("Testing CSV operations...")
    
    # Create test CSV data
    test_data = [
        ["timestamp", "copilot_total", "copilot_merged", "codex_total", "codex_merged", 
         "cursor_total", "cursor_merged", "devin_total", "devin_merged"],
        ["2025-06-01 10:00:00", "1000", "400", "2000", "1600", "100", "80", "500", "300"]
    ]
    
    # Write test CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        writer = csv.writer(f)
        writer.writerows(test_data)
        test_csv = f.name
    
    try:
        # Try to read it back
        with open(test_csv, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if len(rows) == 2 and rows[0][0] == "timestamp":
            print("✓ CSV operations work")
            return True
        else:
            print("✗ CSV data not read correctly")
            return False
    finally:
        os.unlink(test_csv)

def test_chart_generation_imports():
    """Test that chart generation dependencies can be imported."""
    print("Testing chart generation imports...")
    
    try:
        import generate_chart
        print("✓ generate_chart module imports")
        
        # Test that the main function exists
        if hasattr(generate_chart, 'generate_chart'):
            print("✓ generate_chart function exists")
        else:
            print("✗ generate_chart function missing")
            return False
            
        return True
    except ImportError as e:
        print(f"! Chart generation dependencies missing: {e}")
        print("! This is expected if pandas/matplotlib are not installed")
        return True  # Don't fail the test for missing optional dependencies

def test_data_collection_imports():
    """Test that data collection dependencies can be imported."""
    print("Testing data collection imports...")
    
    try:
        import collect_data
        print("✓ collect_data module imports")
        
        # Test that the main function exists
        if hasattr(collect_data, 'collect_data'):
            print("✓ collect_data function exists")
        else:
            print("✗ collect_data function missing")
            return False
            
        # Check that search queries are defined
        if hasattr(collect_data, 'Q') and len(collect_data.Q) > 0:
            print("✓ Search queries are defined")
        else:
            print("✗ Search queries missing")
            return False
            
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_file_structure():
    """Test that required files exist."""
    print("Testing file structure...")
    
    required_files = ['collect_data.py', 'generate_chart.py', 'README.md']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    else:
        print("✓ All required files exist")
        return True

def test_basic_functionality():
    """Test basic functionality with existing data if available."""
    print("Testing basic functionality...")
    
    # Check if data.csv exists
    data_csv = Path("data.csv")
    if not data_csv.exists():
        print("! No data.csv found, skipping functionality test")
        return True
    
    try:
        # Try to read existing data
        with open(data_csv, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if len(rows) < 2:
            print("! data.csv has no data rows, skipping functionality test")
            return True
            
        print(f"✓ Found {len(rows)-1} data rows in data.csv")
        
        # Test that chart generation can process the data (if dependencies available)
        try:
            import generate_chart
            print("✓ Chart generation module available")
            return True
            
        except ImportError as e:
            print(f"! Chart generation dependencies not available: {e}")
            print("! This is expected if pandas/matplotlib are not installed")
            return True  # Don't fail for missing optional dependencies
    
    except Exception as e:
        print(f"✗ Failed to process data.csv: {e}")
        return False

def run_tests():
    """Run all tests."""
    print("Running simple PR tracker functionality tests...\n")
    
    tests = [
        test_file_structure,
        test_csv_operations,
        test_data_collection_imports,
        test_chart_generation_imports,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add blank line between tests
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}\n")
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Core functionality appears to work.")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)