#!/usr/bin/env python3
"""
MASTER BATCH PROCESSOR & ASSET TRACKER
Comprehensive automation for the entire Sisi Lola asset generation pipeline
Tracks progress, validates completeness, and provides reporting
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
MANIFEST_FILE = PROJECT_ROOT / "MASTER_ASSET_MANIFEST.csv"

# ============================================================================
# PROGRESS TRACKING
# ============================================================================

def load_manifest():
    """Load the master asset manifest"""
    assets = []
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        assets = list(reader)
    return assets

def save_manifest(assets):
    """Save updated manifest"""
    if not assets:
        return
    
    fieldnames = assets[0].keys()
    backup_file = MANIFEST_FILE.with_suffix('.csv.backup')
    
    # Create backup
    if MANIFEST_FILE.exists():
        import shutil
        shutil.copy(MANIFEST_FILE, backup_file)
    
    # Save updated manifest
    with open(MANIFEST_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(assets)

def get_progress_stats(assets):
    """Calculate progress statistics"""
    stats = {
        'total': len(assets),
        'pending': 0,
        'generated': 0,
        'approved': 0,
        'by_category': defaultdict(lambda: {'total': 0, 'pending': 0, 'generated': 0}),
        'by_type': defaultdict(lambda: {'total': 0, 'pending': 0, 'generated': 0})
    }
    
    for asset in assets:
        category = asset['Category']
        asset_type = asset['Type']
        status = asset['Status']
        
        # Overall stats
        if 'Pending' in status:
            stats['pending'] += 1
        elif 'Generated' in status or 'Complete' in status:
            stats['generated'] += 1
        
        # Category stats
        stats['by_category'][category]['total'] += 1
        if 'Pending' in status:
            stats['by_category'][category]['pending'] += 1
        elif 'Generated' in status or 'Complete' in status:
            stats['by_category'][category]['generated'] += 1
        
        # Type stats
        stats['by_type'][asset_type]['total'] += 1
        if 'Pending' in status:
            stats['by_type'][asset_type]['pending'] += 1
        elif 'Generated' in status or 'Complete' in status:
            stats['by_type'][asset_type]['generated'] += 1
    
    return stats

def print_progress_report(stats):
    """Print formatted progress report"""
    print("\n" + "=" * 80)
    print("SISI LOLA PROJECT - ASSET GENERATION PROGRESS REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Overall progress
    total = stats['total']
    generated = stats['generated']
    pending = stats['pending']
    percent = (generated / total * 100) if total > 0 else 0
    
    print(f"\nOVERALL PROGRESS: {generated}/{total} ({percent:.1f}%)")
    print(f"  ✓ Generated: {generated}")
    print(f"  ⏳ Pending:   {pending}")
    
    # Progress bar
    bar_width = 50
    filled = int(bar_width * generated / total) if total > 0 else 0
    bar = '█' * filled + '░' * (bar_width - filled)
    print(f"\n  [{bar}] {percent:.1f}%")
    
    # By category
    print("\n" + "-" * 80)
    print("PROGRESS BY CATEGORY:")
    print("-" * 80)
    print(f"{'Category':<30} {'Total':<10} {'Generated':<12} {'Pending':<10} {'%':<10}")
    print("-" * 80)
    
    for category, data in sorted(stats['by_category'].items()):
        total_cat = data['total']
        gen_cat = data['generated']
        pend_cat = data['pending']
        percent_cat = (gen_cat / total_cat * 100) if total_cat > 0 else 0
        
        print(f"{category:<30} {total_cat:<10} {gen_cat:<12} {pend_cat:<10} {percent_cat:<10.1f}%")
    
    # By type
    print("\n" + "-" * 80)
    print("PROGRESS BY TYPE:")
    print("-" * 80)
    print(f"{'Type':<20} {'Total':<10} {'Generated':<12} {'Pending':<10} {'%':<10}")
    print("-" * 80)
    
    for asset_type, data in sorted(stats['by_type'].items()):
        total_type = data['total']
        gen_type = data['generated']
        pend_type = data['pending']
        percent_type = (gen_type / total_type * 100) if total_type > 0 else 0
        
        print(f"{asset_type:<20} {total_type:<10} {gen_type:<12} {pend_type:<10} {percent_type:<10.1f}%")
    
    print("=" * 80)

# ============================================================================
# PRIORITY QUEUE GENERATOR
# ============================================================================

def generate_priority_queue(assets):
    """Generate prioritized task list based on project phases"""
    
    priority_1 = []  # Foundation assets (must do first)
    priority_2 = []  # Expansion assets
    priority_3 = []  # Nice-to-have assets
    
    for asset in assets:
        if asset['Status'] != 'Pending Generation':
            continue  # Skip already generated
        
        category = asset['Category']
        subcategory = asset['Subcategory']
        
        # Priority 1: Foundation (Core identity and main studio)
        if (category == '01_AVATAR_DNA' and 'Reference_Sheets' in subcategory) or \
           (category == '02_ENVIRONMENTS_VR' and 'Main_Studio' in subcategory) or \
           (category == '05_BRANDING_ARTIFACTS' and 'Logos_2D' in subcategory) or \
           (category == '04_AUDIO_CORE' and 'Voice_Samples' in subcategory):
            priority_1.append(asset)
        
        # Priority 2: Expansion (More variety and content)
        elif (category == '01_AVATAR_DNA' and ('Expression' in subcategory or 'Outfit' in subcategory)) or \
             (category == '02_ENVIRONMENTS_VR' and ('Tech_Review' in subcategory or 'OnLocation' in subcategory)) or \
             (category == '04_AUDIO_CORE'):
            priority_2.append(asset)
        
        # Priority 3: Content production
        else:
            priority_3.append(asset)
    
    return {
        'Phase 1 - Foundation (Do First)': priority_1,
        'Phase 2 - Expansion': priority_2,
        'Phase 3 - Content Production': priority_3
    }

def export_priority_queue(queue, output_path):
    """Export priority queue to markdown file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# SISI LOLA PROJECT - PRIORITIZED TASK QUEUE\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("---\n\n")
        
        for phase, assets in queue.items():
            f.write(f"## {phase}\n\n")
            f.write(f"**Total Assets:** {len(assets)}\n\n")
            
            if len(assets) == 0:
                f.write("✓ All assets in this phase completed!\n\n")
                continue
            
            f.write("| ID | Filename | Type | Prompt (First 100 chars) |\n")
            f.write("|----|---------|----|------------------------|\n")
            
            for asset in assets:
                asset_id = asset['ID']
                filename = asset['Filename']
                asset_type = asset['Type']
                prompt_preview = asset['Prompt'][:100] + "..." if len(asset['Prompt']) > 100 else asset['Prompt']
                
                f.write(f"| {asset_id} | {filename} | {asset_type} | {prompt_preview} |\n")
            
            f.write("\n---\n\n")
        
        f.write("\n## How to Use This Queue\n\n")
        f.write("1. Start with **Phase 1** assets - these are the foundation\n")
        f.write("2. Generate assets in order within each phase\n")
        f.write("3. Mark as 'Generated' in the manifest as you complete them\n")
        f.write("4. Re-run this script to update the queue\n")
        f.write("5. Move to next phase when current phase is complete\n\n")
        f.write("**Estimated Timeline:**\n")
        f.write("- Phase 1: 1-2 weeks (35-40 assets)\n")
        f.write("- Phase 2: 2-3 weeks (60-80 assets)\n")
        f.write("- Phase 3: 3-4 weeks (100+ assets)\n")
    
    print(f"✓ Exported priority queue to: {output_path}")

# ============================================================================
# VALIDATION & QUALITY CHECKS
# ============================================================================

def validate_file_exists(filepath):
    """Check if a file exists at the given path"""
    return Path(filepath).exists()

def validate_completeness():
    """Check which assets have been generated and exist on disk"""
    assets = load_manifest()
    validation_report = []
    
    for asset in assets:
        filename = asset['Filename']
        category = asset['Category']
        subcategory = asset['Subcategory']
        status = asset['Status']
        
        # Construct expected file path
        expected_path = PROJECT_ROOT / category / subcategory / filename
        
        file_exists = validate_file_exists(expected_path)
        
        # Determine validation status
        if file_exists and 'Pending' in status:
            validation_status = "WARNING: File exists but marked as Pending"
        elif not file_exists and ('Generated' in status or 'Complete' in status):
            validation_status = "ERROR: Marked as generated but file missing"
        elif file_exists and ('Generated' in status or 'Complete' in status):
            validation_status = "OK: File exists and marked as complete"
        elif not file_exists and 'Pending' in status:
            validation_status = "EXPECTED: Not yet generated"
        else:
            validation_status = "UNKNOWN"
        
        validation_report.append({
            'ID': asset['ID'],
            'Filename': filename,
            'Status': status,
            'File Exists': file_exists,
            'Validation': validation_status
        })
    
    return validation_report

def export_validation_report(report, output_path):
    """Export validation report to CSV"""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['ID', 'Filename', 'Status', 'File Exists', 'Validation'])
        writer.writeheader()
        writer.writerows(report)
    
    # Print summary
    errors = [r for r in report if 'ERROR' in r['Validation']]
    warnings = [r for r in report if 'WARNING' in r['Validation']]
    ok = [r for r in report if 'OK' in r['Validation']]
    
    print(f"\n✓ Validation complete:")
    print(f"  OK: {len(ok)}")
    print(f"  Warnings: {len(warnings)}")
    print(f"  Errors: {len(errors)}")
    print(f"\n✓ Full report saved to: {output_path}")

# ============================================================================
# AUTOMATION HELPER SCRIPTS
# ============================================================================

def generate_update_status_script(output_path):
    """Generate a helper script to update asset status"""
    script = '''#!/usr/bin/env python3
"""
Quick script to update asset status in manifest
Usage: python update_status.py <ASSET_ID> <NEW_STATUS>
Example: python update_status.py AVT-REF-0001 "Generated"
"""

import csv
import sys
from pathlib import Path

MANIFEST = Path(__file__).parent.parent / "MASTER_ASSET_MANIFEST.csv"

def update_status(asset_id, new_status):
    """Update status of a specific asset"""
    assets = []
    found = False
    
    # Read manifest
    with open(MANIFEST, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        assets = list(reader)
    
    # Update asset
    for asset in assets:
        if asset['ID'] == asset_id:
            asset['Status'] = new_status
            found = True
            print(f"✓ Updated {asset_id}: {asset['Filename']}")
            print(f"  Status: {new_status}")
            break
    
    if not found:
        print(f"✗ Asset ID '{asset_id}' not found in manifest")
        return False
    
    # Create backup
    backup = MANIFEST.with_suffix('.csv.backup')
    import shutil
    shutil.copy(MANIFEST, backup)
    
    # Save updated manifest
    fieldnames = assets[0].keys()
    with open(MANIFEST, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(assets)
    
    print(f"✓ Manifest updated (backup saved to {backup.name})")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_status.py <ASSET_ID> <NEW_STATUS>")
        print('\\nExample: python update_status.py AVT-REF-0001 "Generated"')
        print('\\nCommon statuses:')
        print('  - "Pending Generation"')
        print('  - "Generated"')
        print('  - "Quality Approved"')
        print('  - "Needs Revision"')
        sys.exit(1)
    
    asset_id = sys.argv[1]
    new_status = sys.argv[2]
    
    update_status(asset_id, new_status)
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"✓ Created status update script: {output_path}")

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """Interactive main menu"""
    print("\n" + "=" * 80)
    print("SISI LOLA PROJECT - MASTER BATCH PROCESSOR")
    print("=" * 80)
    print("\nSelect an option:")
    print("  1. View Progress Report")
    print("  2. Generate Priority Queue")
    print("  3. Validate File Completeness")
    print("  4. Export All Reports")
    print("  5. Create Helper Scripts")
    print("  6. Exit")
    print("\n" + "=" * 80)
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    assets = load_manifest()
    
    if choice == '1':
        stats = get_progress_stats(assets)
        print_progress_report(stats)
    
    elif choice == '2':
        queue = generate_priority_queue(assets)
        output = PROJECT_ROOT / "00_PROJECT_CORE" / "PRIORITY_QUEUE.md"
        export_priority_queue(queue, output)
    
    elif choice == '3':
        report = validate_completeness()
        output = PROJECT_ROOT / "00_PROJECT_CORE" / "VALIDATION_REPORT.csv"
        export_validation_report(report, output)
    
    elif choice == '4':
        print("\nGenerating all reports...")
        
        # Progress report
        stats = get_progress_stats(assets)
        print_progress_report(stats)
        
        # Priority queue
        queue = generate_priority_queue(assets)
        queue_output = PROJECT_ROOT / "00_PROJECT_CORE" / "PRIORITY_QUEUE.md"
        export_priority_queue(queue, queue_output)
        
        # Validation
        report = validate_completeness()
        val_output = PROJECT_ROOT / "00_PROJECT_CORE" / "VALIDATION_REPORT.csv"
        export_validation_report(report, val_output)
        
        print("\n✓ All reports generated successfully")
    
    elif choice == '5':
        print("\nCreating helper scripts...")
        script_dir = PROJECT_ROOT / "00_PROJECT_CORE" / "Scripts"
        script_dir.mkdir(exist_ok=True)
        
        update_script = script_dir / "update_status.py"
        generate_update_status_script(update_script)
        
        print("✓ Helper scripts created")
    
    elif choice == '6':
        print("\nExiting...")
        return
    
    else:
        print("\n✗ Invalid choice. Please select 1-6.")
    
    # Ask if user wants to continue
    cont = input("\nReturn to main menu? (y/n): ").strip().lower()
    if cont == 'y':
        main_menu()

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1]
        assets = load_manifest()
        
        if command == 'progress':
            stats = get_progress_stats(assets)
            print_progress_report(stats)
        
        elif command == 'queue':
            queue = generate_priority_queue(assets)
            output = PROJECT_ROOT / "00_PROJECT_CORE" / "PRIORITY_QUEUE.md"
            export_priority_queue(queue, output)
        
        elif command == 'validate':
            report = validate_completeness()
            output = PROJECT_ROOT / "00_PROJECT_CORE" / "VALIDATION_REPORT.csv"
            export_validation_report(report, output)
        
        elif command == 'all':
            stats = get_progress_stats(assets)
            print_progress_report(stats)
            
            queue = generate_priority_queue(assets)
            queue_output = PROJECT_ROOT / "00_PROJECT_CORE" / "PRIORITY_QUEUE.md"
            export_priority_queue(queue, queue_output)
            
            report = validate_completeness()
            val_output = PROJECT_ROOT / "00_PROJECT_CORE" / "VALIDATION_REPORT.csv"
            export_validation_report(report, val_output)
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: progress, queue, validate, all")
    
    else:
        # Interactive mode
        main_menu()
