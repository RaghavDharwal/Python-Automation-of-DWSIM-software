#!/usr/bin/env python3
"""
validate_setup.py

Quick validation script to check if the DWSIM automation environment
is properly configured before running the main screening script.
"""

import os
import sys


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        return False


def check_pythonnet():
    """Check if pythonnet is installed."""
    print("Checking pythonnet...")
    try:
        from pythonnet import load
        # Configure Mono runtime for macOS/Linux
        import platform
        if platform.system() in ["Darwin", "Linux"]:
            try:
                load("mono")
                print("  ✓ pythonnet installed and configured with Mono")
            except Exception as e:
                print(f"  ⚠ pythonnet installed but Mono configuration issue: {e}")
                print("    This may still work - will check .NET runtime separately")
        import clr
        print("  ✓ pythonnet installed")
        return True
    except ImportError:
        print("  ✗ pythonnet not installed")
        print("    Install with: pip install pythonnet==3.0.3")
        return False


def check_optional_packages():
    """Check optional packages for plotting."""
    print("Checking optional packages...")
    missing = []
    
    try:
        import matplotlib
        print("  ✓ matplotlib installed")
    except ImportError:
        print("  ⚠ matplotlib not installed (optional, needed for plots)")
        missing.append("matplotlib")
    
    try:
        import numpy
        print("  ✓ numpy installed")
    except ImportError:
        print("  ⚠ numpy not installed (optional)")
        missing.append("numpy")
    
    try:
        import pandas
        print("  ✓ pandas installed")
    except ImportError:
        print("  ⚠ pandas not installed (optional)")
        missing.append("pandas")
    
    if missing:
        print(f"    Install with: pip install {' '.join(missing)}")
    
    return True  # Optional packages don't fail validation


def check_dwsim_dir():
    """Check if DWSIM directory is configured and accessible."""
    print("Checking DWSIM installation...")
    
    dwsim_dir = os.environ.get("DWSIM_INSTALL_DIR")
    if not dwsim_dir:
        print("  ✗ DWSIM_INSTALL_DIR environment variable not set")
        print("    Set it with:")
        print("      Windows: $env:DWSIM_INSTALL_DIR = 'C:\\Program Files\\DWSIM'")
        print("      Linux/Mac: export DWSIM_INSTALL_DIR='/path/to/DWSIM'")
        return False
    
    print(f"  → DWSIM_INSTALL_DIR = {dwsim_dir}")
    
    if not os.path.exists(dwsim_dir):
        print(f"  ✗ Directory does not exist: {dwsim_dir}")
        return False
    
    print(f"  ✓ Directory exists")
    
    # Check for required DLLs
    required_dlls = [
        "DWSIM.Automation.dll",
        "DWSIM.Interfaces.dll",
        "DWSIM.Thermodynamics.dll",
        "DWSIM.UnitOperations.dll",
    ]
    
    missing_dlls = []
    for dll in required_dlls:
        dll_path = os.path.join(dwsim_dir, dll)
        if os.path.exists(dll_path):
            print(f"  ✓ Found {dll}")
        else:
            print(f"  ✗ Missing {dll}")
            missing_dlls.append(dll)
    
    if missing_dlls:
        print(f"  ✗ Missing {len(missing_dlls)} required DLL(s)")
        print("    Make sure DWSIM is properly installed")
        return False
    
    return True


def check_dotnet():
    """Check if .NET/Mono is available."""
    print("Checking .NET/Mono runtime...")
    
    # Try to load CLR
    try:
        from pythonnet import load
        import platform
        
        # Configure runtime based on platform
        if platform.system() in ["Darwin", "Linux"]:
            try:
                load("mono")
                print("  ✓ Mono runtime loaded successfully")
            except Exception as e:
                print(f"  ⚠ Mono load warning: {e}")
                
        import clr
        try:
            # Try to load a system assembly
            clr.AddReference("System")
            print("  ✓ .NET/Mono runtime is accessible")
            return True
        except Exception as e:
            print(f"  ✗ Failed to load .NET assemblies: {e}")
            return False
    except ImportError:
        print("  ✗ pythonnet not installed (required for .NET access)")
        return False


def check_workspace_files():
    """Check if required workspace files exist."""
    print("Checking workspace files...")
    
    required = ["run_screening.py", "requirements.txt", "README.md"]
    optional = ["plot_results.py", "QUICKSTART.md"]
    
    all_ok = True
    for fname in required:
        if os.path.exists(fname):
            print(f"  ✓ {fname}")
        else:
            print(f"  ✗ {fname} (required)")
            all_ok = False
    
    for fname in optional:
        if os.path.exists(fname):
            print(f"  ✓ {fname}")
        else:
            print(f"  ⚠ {fname} (optional)")
    
    return all_ok


def main():
    print("=" * 60)
    print("DWSIM Automation Setup Validation")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("pythonnet Library", check_pythonnet),
        ("Optional Packages", check_optional_packages),
        (".NET/Mono Runtime", check_dotnet),
        ("DWSIM Installation", check_dwsim_dir),
        ("Workspace Files", check_workspace_files),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Error during check: {e}")
            results.append((name, False))
        print()
    
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Result: {passed}/{total} checks passed")
    print()
    
    if passed == total:
        print("✓ All checks passed! You're ready to run:")
        print("  python run_screening.py")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("  See README.md or QUICKSTART.md for setup instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
