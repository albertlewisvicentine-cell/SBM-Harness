#!/usr/bin/env python3
"""
Digital Assets Inventory and Conflict Verification Tool for SBM-Harness

This script checks all digital assets in the repository and verifies for any conflicts:
- Naming conflicts (duplicate filenames)
- Content conflicts (duplicate content with different names)
- License conflicts
- Configuration conflicts
- Dependency conflicts
"""

import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent

# Directories to exclude
EXCLUDE_DIRS = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}

# File extensions categorization
ASSET_CATEGORIES = {
    'source_code': {'.py', '.c', '.h', '.js', '.sh'},
    'configuration': {'.yaml', '.yml', '.json', '.toml', '.cfg', '.ini', '.rc'},
    'documentation': {'.md', '.txt', '.rst'},
    'data': {'.csv', '.ndjson', '.bin', '.log'},
    'build': {'Makefile', '.coveragerc'},
    'package': {'package.json', 'requirements.txt', 'pyproject.toml'},
    'license': {'LICENSE', 'LICENSE.APACHE2'},
}


def compute_file_hash(filepath: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"


def categorize_file(filepath: Path) -> str:
    """Categorize a file based on extension or name."""
    filename = filepath.name
    ext = filepath.suffix.lower()
    
    # Check by filename first
    for category, patterns in ASSET_CATEGORIES.items():
        if filename in patterns:
            return category
    
    # Check by extension
    for category, extensions in ASSET_CATEGORIES.items():
        if ext in extensions:
            return category
    
    return 'other'


def get_all_files() -> List[Path]:
    """Get all files in the repository, excluding certain directories."""
    files = []
    for root, dirs, filenames in os.walk(REPO_ROOT):
        # Remove excluded directories from the walk
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for filename in filenames:
            filepath = Path(root) / filename
            files.append(filepath)
    
    return files


def check_naming_conflicts(files: List[Path]) -> Dict[str, List[Path]]:
    """Check for files with the same name in different directories."""
    filename_map = defaultdict(list)
    
    for filepath in files:
        filename_map[filepath.name].append(filepath)
    
    # Filter to only conflicts (more than one file with the same name)
    conflicts = {name: paths for name, paths in filename_map.items() if len(paths) > 1}
    return conflicts


def check_content_conflicts(files: List[Path]) -> Dict[str, List[Path]]:
    """Check for files with identical content but different names."""
    hash_map = defaultdict(list)
    
    for filepath in files:
        file_hash = compute_file_hash(filepath)
        if not file_hash.startswith("ERROR:"):
            hash_map[file_hash].append(filepath)
    
    # Filter to only conflicts (same content, different paths)
    conflicts = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    return conflicts


def check_license_conflicts(files: List[Path]) -> Dict[str, any]:
    """Check for multiple license files and potential conflicts."""
    license_files = [f for f in files if 'LICENSE' in f.name.upper()]
    
    # Check if this is intentional dual-licensing (common pattern)
    is_dual_license = False
    if len(license_files) == 2:
        license_names = {f.name.upper() for f in license_files}
        # Common dual-licensing patterns
        dual_patterns = [
            {'LICENSE', 'LICENSE.APACHE2'},
            {'LICENSE', 'LICENSE-APACHE'},
            {'LICENSE', 'LICENSE.MIT'},
            {'LICENSE-MIT', 'LICENSE-APACHE'},
            {'LICENSE.MIT', 'LICENSE.APACHE2'},
        ]
        for pattern in dual_patterns:
            if license_names == pattern or license_names.issubset(pattern):
                is_dual_license = True
                break
    
    result = {
        'license_files': license_files,
        'count': len(license_files),
        'conflict': len(license_files) > 1 and not is_dual_license,
        'is_dual_license': is_dual_license
    }
    
    return result


def check_dependency_conflicts(files: List[Path]) -> Dict[str, any]:
    """Check for dependency file conflicts and inconsistencies."""
    conflicts = {}
    
    # Find all dependency files
    requirements_files = [f for f in files if f.name == 'requirements.txt']
    package_json_files = [f for f in files if f.name == 'package.json']
    pyproject_files = [f for f in files if f.name == 'pyproject.toml']
    
    conflicts['requirements.txt'] = {
        'count': len(requirements_files),
        'files': requirements_files,
        'conflict': len(requirements_files) > 1
    }
    
    conflicts['package.json'] = {
        'count': len(package_json_files),
        'files': package_json_files,
        'conflict': len(package_json_files) > 1
    }
    
    conflicts['pyproject.toml'] = {
        'count': len(pyproject_files),
        'files': pyproject_files,
        'conflict': len(pyproject_files) > 1
    }
    
    return conflicts


def check_config_conflicts(files: List[Path]) -> Dict[str, List[Path]]:
    """Check for configuration file conflicts."""
    config_files = defaultdict(list)
    
    for filepath in files:
        if categorize_file(filepath) == 'configuration':
            config_files[filepath.name].append(filepath)
    
    # Filter to only conflicts
    conflicts = {name: paths for name, paths in config_files.items() if len(paths) > 1}
    return conflicts


def generate_inventory(files: List[Path]) -> Dict[str, any]:
    """Generate a comprehensive inventory of all digital assets."""
    inventory = {
        'total_files': len(files),
        'by_category': defaultdict(list),
        'by_extension': defaultdict(int),
        'file_sizes': {},
        'total_size': 0
    }
    
    for filepath in files:
        category = categorize_file(filepath)
        rel_path = filepath.relative_to(REPO_ROOT)
        
        inventory['by_category'][category].append(str(rel_path))
        
        ext = filepath.suffix.lower() or 'no_extension'
        inventory['by_extension'][ext] += 1
        
        try:
            size = filepath.stat().st_size
            inventory['file_sizes'][str(rel_path)] = size
            inventory['total_size'] += size
        except Exception:
            pass
    
    # Convert defaultdict to regular dict for JSON serialization
    inventory['by_category'] = dict(inventory['by_category'])
    inventory['by_extension'] = dict(inventory['by_extension'])
    
    return inventory


def main():
    """Main function to run all checks and generate report."""
    print("=" * 80)
    print("SBM-HARNESS Digital Assets Inventory and Conflict Verification")
    print("=" * 80)
    print()
    
    # Get all files
    print("📁 Scanning repository...")
    all_files = get_all_files()
    print(f"   Found {len(all_files)} files\n")
    
    # Generate inventory
    print("📊 Generating inventory...")
    inventory = generate_inventory(all_files)
    print(f"   Total size: {inventory['total_size']:,} bytes\n")
    
    # Check for naming conflicts
    print("🔍 Checking for naming conflicts...")
    naming_conflicts = check_naming_conflicts(all_files)
    if naming_conflicts:
        print(f"   ⚠️  Found {len(naming_conflicts)} naming conflict(s)")
    else:
        print("   ✅ No naming conflicts found")
    print()
    
    # Check for content conflicts
    print("🔍 Checking for content conflicts...")
    content_conflicts = check_content_conflicts(all_files)
    if content_conflicts:
        print(f"   ⚠️  Found {len(content_conflicts)} content conflict(s)")
    else:
        print("   ✅ No content conflicts found")
    print()
    
    # Check license conflicts
    print("📜 Checking license files...")
    license_info = check_license_conflicts(all_files)
    if license_info['conflict']:
        print(f"   ⚠️  Multiple license files found: {license_info['count']}")
    elif license_info['is_dual_license']:
        print(f"   ℹ️  Dual-licensing detected: {license_info['count']} licenses (intentional)")
    else:
        print(f"   ✅ License files: {license_info['count']}")
    print()
    
    # Check dependency conflicts
    print("📦 Checking dependency files...")
    dependency_conflicts = check_dependency_conflicts(all_files)
    has_dep_conflict = any(info['conflict'] for info in dependency_conflicts.values())
    if has_dep_conflict:
        print("   ⚠️  Dependency conflicts found")
    else:
        print("   ✅ No dependency conflicts")
    print()
    
    # Check configuration conflicts
    print("⚙️  Checking configuration files...")
    config_conflicts = check_config_conflicts(all_files)
    if config_conflicts:
        print(f"   ⚠️  Found {len(config_conflicts)} configuration conflict(s)")
    else:
        print("   ✅ No configuration conflicts found")
    print()
    
    # Generate detailed report
    print("=" * 80)
    print("DETAILED REPORT")
    print("=" * 80)
    print()
    
    # Inventory summary
    print("📊 INVENTORY SUMMARY")
    print("-" * 80)
    for category, files_list in sorted(inventory['by_category'].items()):
        print(f"\n{category.upper()}: {len(files_list)} files")
        for f in sorted(files_list)[:5]:  # Show first 5
            print(f"  - {f}")
        if len(files_list) > 5:
            print(f"  ... and {len(files_list) - 5} more")
    print()
    
    # Naming conflicts
    if naming_conflicts:
        print("\n⚠️  NAMING CONFLICTS")
        print("-" * 80)
        for filename, paths in sorted(naming_conflicts.items()):
            print(f"\nFilename: {filename}")
            for path in paths:
                print(f"  - {path.relative_to(REPO_ROOT)}")
    
    # Content conflicts
    if content_conflicts:
        print("\n⚠️  CONTENT CONFLICTS (Duplicate Content)")
        print("-" * 80)
        for file_hash, paths in content_conflicts.items():
            print(f"\nHash: {file_hash[:16]}...")
            for path in paths:
                print(f"  - {path.relative_to(REPO_ROOT)}")
    
    # License details
    print("\n📜 LICENSE FILES")
    print("-" * 80)
    for license_file in license_info['license_files']:
        print(f"  - {license_file.relative_to(REPO_ROOT)}")
    if license_info['is_dual_license']:
        print("    ℹ️  Dual-licensing is intentional - users can choose either license")
    elif license_info['conflict']:
        print("    ⚠️  Multiple licenses may indicate licensing complexity")
    
    # Dependency details
    print("\n📦 DEPENDENCY FILES")
    print("-" * 80)
    for dep_type, info in dependency_conflicts.items():
        if info['count'] > 0:
            print(f"\n{dep_type}: {info['count']} file(s)")
            for dep_file in info['files']:
                print(f"  - {dep_file.relative_to(REPO_ROOT)}")
            if info['conflict']:
                print("    ⚠️  Multiple dependency files of same type")
    
    # Configuration conflicts
    if config_conflicts:
        print("\n⚙️  CONFIGURATION CONFLICTS")
        print("-" * 80)
        for config_name, paths in sorted(config_conflicts.items()):
            print(f"\nConfig: {config_name}")
            for path in paths:
                print(f"  - {path.relative_to(REPO_ROOT)}")
    
    # Save detailed report to JSON
    report_file = REPO_ROOT / 'DIGITAL_ASSETS_REPORT.json'
    print(f"\n💾 Saving detailed report to: {report_file}")
    
    report_data = {
        'inventory': inventory,
        'conflicts': {
            'naming': {name: [str(p.relative_to(REPO_ROOT)) for p in paths] 
                      for name, paths in naming_conflicts.items()},
            'content': {h: [str(p.relative_to(REPO_ROOT)) for p in paths] 
                       for h, paths in content_conflicts.items()},
            'license': {
                'files': [str(f.relative_to(REPO_ROOT)) for f in license_info['license_files']],
                'count': license_info['count'],
                'has_conflict': license_info['conflict'],
                'is_dual_license': license_info['is_dual_license']
            },
            'dependencies': {
                dep_type: {
                    'count': info['count'],
                    'files': [str(f.relative_to(REPO_ROOT)) for f in info['files']],
                    'has_conflict': info['conflict']
                }
                for dep_type, info in dependency_conflicts.items()
            },
            'configuration': {name: [str(p.relative_to(REPO_ROOT)) for p in paths] 
                            for name, paths in config_conflicts.items()}
        }
    }
    
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print("\n" + "=" * 80)
    print("✅ Asset inventory and conflict verification complete!")
    print("=" * 80)
    
    # Return exit code based on conflicts
    has_conflicts = (
        bool(naming_conflicts) or 
        bool(content_conflicts) or 
        license_info['conflict'] or 
        has_dep_conflict or 
        bool(config_conflicts)
    )
    
    if has_conflicts:
        print("\n⚠️  WARNING: Some conflicts were detected. Please review the report.")
        return 1
    else:
        print("\n✅ SUCCESS: No conflicts detected!")
        return 0


if __name__ == '__main__':
    exit(main())
