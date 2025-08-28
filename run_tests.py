#!/usr/bin/env python3
"""Test runner for Temporal Order Lifecycle System"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests based on specified type"""

    # Add the app directory to Python path
    app_dir = Path(__file__).parent / "app"
    sys.path.insert(0, str(app_dir))

    # Base pytest command
    cmd = ["python3", "-m", "pytest"]

    # Add verbose flag if requested
    if verbose:
        cmd.append("-v")

    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])

    # Add test directory
    tests_dir = Path(__file__).parent / "tests"
    cmd.append(str(tests_dir))

    # Filter tests based on type
    if test_type == "unit":
        cmd.extend(["-k", "not integration"])
    elif test_type == "integration":
        cmd.extend(["-k", "integration"])
    elif test_type == "activities":
        cmd.extend(
            [
                "-k",
                "TestReceiveOrderActivity or TestValidateOrderActivity or TestChargePaymentActivity or TestStartShippingActivity",
            ]
        )
    elif test_type == "workflows":
        cmd.extend(["-k", "TestOrderWorkflow or TestShippingWorkflow"])
    elif test_type == "database":
        cmd.extend(
            [
                "-k",
                "TestDatabaseModels or TestOrderRepository or TestPaymentRepository or TestEventRepository",
            ]
        )
    elif test_type == "api":
        print("⚠️  API tests removed - file deleted")
        return 0
    elif test_type == "shipping":
        print("⚠️  Shipping tests removed - file deleted")
        return 0

    print(f"🚀 Running {test_type} tests...")
    print(f"📋 Command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        # Run the tests
        result = subprocess.run(cmd, cwd=Path(__file__).parent, check=False)

        print("=" * 60)
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Some tests failed (exit code: {result.returncode})")

        return result.returncode

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def main():
    """Main function to parse arguments and run tests"""
    parser = argparse.ArgumentParser(
        description="Run tests for Temporal Order Lifecycle System"
    )

    parser.add_argument(
        "--type",
        "-t",
        choices=[
            "all",
            "unit",
            "integration",
            "activities",
            "workflows",
            "database",
            "api",
            "shipping",
        ],
        default="all",
        help="Type of tests to run (default: all)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Run tests in verbose mode"
    )

    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Generate coverage report"
    )

    parser.add_argument(
        "--list", "-l", action="store_true", help="List available test categories"
    )

    args = parser.parse_args()

    if args.list:
        print("📚 Available test categories:")
        print("  all        - Run all tests")
        print("  unit       - Run unit tests only")
        print("  integration - Run integration tests only")
        print("  activities - Run activity tests only")
        print("  workflows  - Run workflow tests only")
        print("  database   - Run database tests only")
        print("  api        - API tests removed")
        print("  shipping   - Shipping tests removed")
        return 0

    # Check if tests directory exists
    tests_dir = Path(__file__).parent / "tests"
    if not tests_dir.exists():
        print("❌ Tests directory not found!")
        print("   Make sure you're running this from the project root directory.")
        return 1

    # Check if required packages are installed
    try:
        import pytest
        import temporalio
        import fastapi
        import sqlalchemy
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("   Install test dependencies with: pip install pytest pytest-asyncio")
        return 1

    # Run the tests
    return run_tests(args.type, args.verbose, args.coverage)


if __name__ == "__main__":
    sys.exit(main())
