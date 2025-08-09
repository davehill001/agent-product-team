#!/usr/bin/env python3
"""
Test runner for the Multi-Agent Team system.
Runs all tests and provides a comprehensive report.
"""

import os
import sys
import unittest
import time
from datetime import datetime

# Set testing environment
os.environ["TESTING"] = "1"

def run_all_tests():
    """Run all tests and return results."""
    print("🧪 Running Multi-Agent Team System Tests")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    if not os.path.exists(start_dir):
        print("❌ Tests directory not found. Creating basic test structure...")
        os.makedirs(start_dir, exist_ok=True)
        print("✅ Tests directory created")
    
    # Discover tests
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Duration: {end_time - start_time:.2f} seconds")
    
    # Print failures and errors
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n❌ ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Overall result
    if result.wasSuccessful():
        print(f"\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n❌ SOME TESTS FAILED!")
        return False

def run_specific_test(test_name):
    """Run a specific test."""
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_quick_tests():
    """Run quick tests without full integration."""
    print("🧪 Running Quick Tests")
    print("=" * 50)
    
    # Test basic imports
    tests = [
        ("config", "import config"),
        ("memory", "import memory"),
        ("utils", "import utils"),
        ("conversation_state", "import conversation_state"),
        ("consensus", "import consensus"),
        ("agents", "import agents"),
        ("main", "import main")
    ]
    
    results = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  ✅ {name} - OK")
            results.append(True)
        except Exception as e:
            print(f"  ❌ {name} - FAILED: {e}")
            results.append(False)
    
    print(f"\nQuick tests: {sum(results)}/{len(results)} passed")
    return all(results)

def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Test runner for Multi-Agent Team system")
    parser.add_argument("--quick", "-q", action="store_true", help="Run quick tests only")
    parser.add_argument("--specific", "-s", type=str, help="Run specific test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    if args.quick:
        success = run_quick_tests()
    elif args.specific:
        success = run_specific_test(args.specific)
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    import argparse
    import logging
    main() 