#!/usr/bin/env python3
"""
Pytest runner script for REGON MCP Server tests.

This script provides convenient ways to run different test suites using pytest
with proper configuration and reporting.

Usage:
    python tests/run_pytest.py [options]
    
Examples:
    python tests/run_pytest.py                    # Run all tests
    python tests/run_pytest.py --unit             # Run only unit tests
    python tests/run_pytest.py --integration      # Run only integration tests
    python tests/run_pytest.py --http             # Run only HTTP server tests
    python tests/run_pytest.py --stdio            # Run only stdio server tests
    python tests/run_pytest.py --coverage         # Run with coverage report
    python tests/run_pytest.py --verbose          # Verbose output
    python tests/run_pytest.py --fast             # Skip slow tests
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Configure UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


def run_pytest(args):
    """Run pytest with the specified arguments."""
    # Change to project root if we're in tests directory
    original_dir = os.getcwd()
    project_root = Path(__file__).parent.parent
    
    if 'tests' in os.getcwd():
        os.chdir(project_root)
    
    try:
        # Build pytest command
        pytest_cmd = [sys.executable, '-m', 'pytest']
        
        # Add test selection arguments
        if args.unit:
            pytest_cmd.extend(['-m', 'unit'])
        elif args.integration:
            pytest_cmd.extend(['-m', 'integration'])
        elif args.http:
            pytest_cmd.extend(['-m', 'http'])
        elif args.stdio:
            pytest_cmd.extend(['-m', 'stdio'])
        elif args.api:
            pytest_cmd.extend(['-m', 'api'])
        
        # Add performance arguments
        if args.fast:
            pytest_cmd.extend(['-m', 'not slow'])
        
        # Add output arguments
        if args.verbose:
            pytest_cmd.append('-v')
        else:
            pytest_cmd.append('-q')
        
        # Add coverage arguments
        if args.coverage:
            pytest_cmd.extend([
                '--cov=regon_mcp_server',
                '--cov-report=term-missing',
                '--cov-report=html:htmlcov'
            ])
        
        # Add parallel execution if requested
        if args.parallel:
            pytest_cmd.extend(['-n', 'auto'])
        
        # Add specific test files if provided
        if args.test_files:
            pytest_cmd.extend(args.test_files)
        else:
            pytest_cmd.append('tests/')
        
        # Add any additional pytest arguments
        if args.pytest_args:
            pytest_cmd.extend(args.pytest_args)
        
        print("🧪 Running pytest with command:")
        print(" ".join(pytest_cmd))
        print("=" * 60)
        
        # Run pytest
        result = subprocess.run(pytest_cmd)
        return result.returncode
        
    finally:
        os.chdir(original_dir)


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description='Run REGON MCP Server tests with pytest',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Test selection arguments
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        '--unit', action='store_true',
        help='Run only unit tests'
    )
    test_group.add_argument(
        '--integration', action='store_true',
        help='Run only integration tests'
    )
    test_group.add_argument(
        '--http', action='store_true',
        help='Run only HTTP server tests'
    )
    test_group.add_argument(
        '--stdio', action='store_true',
        help='Run only stdio server tests'
    )
    test_group.add_argument(
        '--api', action='store_true',
        help='Run only API integration tests (requires network)'
    )
    
    # Performance arguments
    parser.add_argument(
        '--fast', action='store_true',
        help='Skip slow tests for faster execution'
    )
    parser.add_argument(
        '--parallel', action='store_true',
        help='Run tests in parallel using pytest-xdist'
    )
    
    # Output arguments
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--coverage', action='store_true',
        help='Generate coverage report'
    )
    
    # File selection
    parser.add_argument(
        'test_files', nargs='*',
        help='Specific test files to run'
    )
    
    # Pass-through arguments to pytest
    parser.add_argument(
        '--pytest-args', nargs=argparse.REMAINDER,
        help='Additional arguments to pass to pytest'
    )
    
    args = parser.parse_args()
    
    # Run tests
    exit_code = run_pytest(args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
