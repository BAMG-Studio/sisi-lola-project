#!/usr/bin/env python3
"""
SISI LOLA DATA VALIDATOR
Scans all files and databases for placeholder values
"""

import os
import json
import sqlite3
import re
from pathlib import Path
from typing import List, Dict, Tuple

class DataValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues = []
        self.placeholder_patterns = [
            r'placeholder',
            r'PLACEHOLDER',
            r'example\.com',
            r'test@test',
            r'xxx+',
            r'CHANGEME',
            r'UPDATEME',
            r'TODO',
        ]
    
    def scan_database(self, db_path: Path) -> List[Dict]:
        """Scan SQLite database for placeholders"""
        if not db_path.exists():
            return [{"file": str(db_path), "issue": "Database not found"}]
        
        issues = []
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    if value and isinstance(value, str):
                        for pattern in self.placeholder_patterns:
                            if re.search(pattern, value, re.IGNORECASE):
                                issues.append({
                                    "file": str(db_path),
                                    "location": f"Table: {table_name}, Row: {row_idx+1}, Col: {col_idx+1}",
                                    "value": value,
                                    "pattern": pattern
                                })
        
        conn.close()
        return issues
    
    def scan_json_file(self, json_path: Path) -> List[Dict]:
        """Scan JSON file for placeholders"""
        if not json_path.exists():
            return []
        
        issues = []
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            data_str = json.dumps(data)
            for pattern in self.placeholder_patterns:
                matches = re.finditer(pattern, data_str, re.IGNORECASE)
                for match in matches:
                    issues.append({
                        "file": str(json_path),
                        "pattern": pattern,
                        "context": data_str[max(0, match.start()-50):match.end()+50]
                    })
        except Exception as e:
            issues.append({
                "file": str(json_path),
                "issue": f"Error reading file: {str(e)}"
            })
        
        return issues
    
    def scan_python_file(self, py_path: Path) -> List[Dict]:
        """Scan Python file for hardcoded placeholders"""
        if not py_path.exists():
            return []
        
        issues = []
        try:
            with open(py_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                for pattern in self.placeholder_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Skip comments
                        if not line.strip().startswith('#'):
                            issues.append({
                                "file": str(py_path),
                                "line": line_num,
                                "code": line.strip(),
                                "pattern": pattern
                            })
        except Exception as e:
            issues.append({
                "file": str(py_path),
                "issue": f"Error reading file: {str(e)}"
            })
        
        return issues
    
    def validate_required_values(self) -> List[Dict]:
        """Check if required values are present"""
        required_checks = []
        
        # Check master DB exists and has data
        master_db = self.project_root / "sisi_lola_production.db"
        if not master_db.exists():
            required_checks.append({
                "check": "Master Database",
                "status": "MISSING",
                "action": "Run fix_placeholder_values.py"
            })
        else:
            conn = sqlite3.connect(master_db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM accounts")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                required_checks.append({
                    "check": "Account Data",
                    "status": "EMPTY",
                    "action": "Run fix_placeholder_values.py"
                })
        
        # Check .env has real values
        env_path = self.project_root / ".env"
        if env_path.exists():
            with open(env_path, 'r') as f:
                env_content = f.read()
            
            if "PLACEHOLDER" in env_content or "placeholder" in env_content:
                required_checks.append({
                    "check": "Environment Variables",
                    "status": "HAS PLACEHOLDERS",
                    "action": "Update .env with real API keys"
                })
        
        return required_checks
    
    def run_full_validation(self):
        """Execute complete validation"""
        print("\n" + "="*70)
        print("🔍 SISI LOLA - COMPREHENSIVE DATA VALIDATION")
        print("="*70)
        
        # Scan databases
        print("\n📊 Scanning Databases...")
        db_files = list(self.project_root.rglob("*.db")) + list(self.project_root.rglob("*.sqlite"))
        for db_file in db_files:
            issues = self.scan_database(db_file)
            if issues:
                self.issues.extend(issues)
                print(f"  ⚠️  Issues found in: {db_file.name}")
            else:
                print(f"  ✅ Clean: {db_file.name}")
        
        # Scan JSON files
        print("\n📄 Scanning JSON Files...")
        json_files = [
            self.project_root / "Scripts" / "platforms_config.json",
            self.project_root / "Scripts" / "content_queue.json"
        ]
        for json_file in json_files:
            if json_file.exists():
                issues = self.scan_json_file(json_file)
                if issues:
                    self.issues.extend(issues)
                    print(f"  ⚠️  Issues found in: {json_file.name}")
                else:
                    print(f"  ✅ Clean: {json_file.name}")
        
        # Scan Python scripts
        print("\n🐍 Scanning Python Scripts...")
        critical_scripts = [
            "batch_platform_ingestion.py",
            "seed_content_batch.py",
            "master_orchestrator.py",
            "unified_api_poster.py"
        ]
        scripts_dir = self.project_root / "Scripts"
        for script_name in critical_scripts:
            script_path = scripts_dir / script_name
            if script_path.exists():
                issues = self.scan_python_file(script_path)
                if issues:
                    self.issues.extend(issues)
                    print(f"  ⚠️  Issues found in: {script_name}")
                else:
                    print(f"  ✅ Clean: {script_name}")
        
        # Check required values
        print("\n✓ Checking Required Values...")
        required_issues = self.validate_required_values()
        
        # Generate Report
        print("\n" + "="*70)
        print("📋 VALIDATION REPORT")
        print("="*70)
        
        if not self.issues and not required_issues:
            print("\n✅ NO ISSUES FOUND!")
            print("All databases, configs, and scripts are clean.")
            print("System is ready for production use.")
        else:
            if self.issues:
                print(f"\n⚠️  PLACEHOLDER ISSUES FOUND: {len(self.issues)}")
                print("\nTop 10 Issues:")
                for i, issue in enumerate(self.issues[:10], 1):
                    print(f"\n{i}. File: {issue.get('file', 'Unknown')}")
                    if 'location' in issue:
                        print(f"   Location: {issue['location']}")
                    if 'pattern' in issue:
                        print(f"   Pattern: {issue['pattern']}")
                    if 'value' in issue:
                        print(f"   Value: {issue['value'][:100]}")
            
            if required_issues:
                print(f"\n⚠️  REQUIRED VALUE ISSUES: {len(required_issues)}")
                for issue in required_issues:
                    print(f"\n   Check: {issue['check']}")
                    print(f"   Status: {issue['status']}")
                    print(f"   Action: {issue['action']}")
        
        print("\n" + "="*70)
        
        # Save detailed report
        report_path = self.project_root / "VALIDATION_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump({
                "timestamp": str(Path(__file__).stat().st_mtime),
                "total_issues": len(self.issues),
                "placeholder_issues": self.issues,
                "required_value_issues": required_issues
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_path}")
        
        return len(self.issues) == 0 and len(required_issues) == 0

if __name__ == "__main__":
    validator = DataValidator()
    is_clean = validator.run_full_validation()
    
    if not is_clean:
        print("\n💡 RECOMMENDED ACTIONS:")
        print("1. Run: python fix_placeholder_values.py")
        print("2. Update .env with real API tokens")
        print("3. Run this validator again")
        print("4. Proceed with: python master_orchestrator.py")
