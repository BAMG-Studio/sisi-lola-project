#!/usr/bin/env python3
"""
Launch Readiness Validator for Sisi Lola Social Media Management System

Validates all components are ready for platform launch with comprehensive checks:
- Account creation completeness
- Content queue readiness
- Profile assets availability
- Monetization setup
- Analytics configuration
- Integration readiness

Author: Sisi Lola Team
Date: November 25, 2025
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum


class ReadinessLevel(Enum):
    """Readiness status levels"""
    READY = "✅ READY"
    WARNING = "⚠️ WARNING"
    BLOCKED = "❌ BLOCKED"
    NOT_STARTED = "⏸️ NOT STARTED"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    category: str
    check_name: str
    status: ReadinessLevel
    message: str
    score: int  # 0-100
    recommendations: List[str]


class LaunchReadinessValidator:
    """Validates launch readiness across all system components"""
    
    def __init__(self, workspace_root: Path = None):
        """Initialize validator with workspace root"""
        if workspace_root is None:
            workspace_root = Path(__file__).parent.parent.parent
        
        self.workspace_root = Path(workspace_root)
        
        # Check both possible locations for databases
        possible_accounts_db = [
            self.workspace_root / "05_BRANDING_ARTIFACTS/sisi_lola_accounts.db",
            self.workspace_root / "00_PROJECT_CORE/05_BRANDING_ARTIFACTS/sisi_lola_accounts.db"
        ]
        possible_analytics_db = [
            self.workspace_root / "05_BRANDING_ARTIFACTS/sisi_lola_analytics.db",
            self.workspace_root / "00_PROJECT_CORE/05_BRANDING_ARTIFACTS/sisi_lola_analytics.db"
        ]
        
        # Use first existing path
        self.accounts_db = next((p for p in possible_accounts_db if p.exists()), possible_accounts_db[0])
        self.analytics_db = next((p for p in possible_analytics_db if p.exists()), possible_analytics_db[0])
        
        self.content_queue = self.workspace_root / "03_MEDIA_ASSETS/content_queue/content_queue.json"
        self.validation_results: List[ValidationResult] = []
    
    def validate_all(self) -> Dict:
        """Run all validation checks"""
        print("=" * 80)
        print("🚀 SISI LOLA LAUNCH READINESS VALIDATION")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Workspace: {self.workspace_root}")
        print("=" * 80)
        print()
        
        # Run all validation categories
        self._validate_accounts()
        self._validate_content()
        self._validate_assets()
        self._validate_monetization()
        self._validate_analytics()
        self._validate_integrations()
        self._validate_documentation()
        
        # Generate summary
        summary = self._generate_summary()
        self._print_results()
        
        return summary
    
    def _validate_accounts(self):
        """Validate account creation and configuration"""
        category = "Account Management"
        
        if not self.accounts_db.exists():
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Database Existence",
                status=ReadinessLevel.BLOCKED,
                message="Account database not found",
                score=0,
                recommendations=["Run: python3 social_media_account_db.py"]
            ))
            return
        
        try:
            conn = sqlite3.connect(self.accounts_db)
            cursor = conn.cursor()
            
            # Check total accounts
            cursor.execute("SELECT COUNT(*) FROM accounts")
            total_accounts = cursor.fetchone()[0]
            
            # Check created accounts
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE account_status IN ('created', 'verified', 'configured', 'live')")
            created_accounts = cursor.fetchone()[0]
            
            # Check verified accounts
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE email_verified = 1")
            verified_count = cursor.fetchone()[0]
            
            # Check 2FA enabled
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE two_fa_enabled = 1")
            twofa_count = cursor.fetchone()[0]
            
            # Check profile assets
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE profile_picture_uploaded = 1 AND banner_uploaded = 1")
            assets_complete = cursor.fetchone()[0]
            
            # Check African platforms
            cursor.execute("""
                SELECT COUNT(*) FROM accounts 
                WHERE platform_type = 'african' 
                AND account_status IN ('created', 'verified', 'configured', 'live')
            """)
            african_platforms = cursor.fetchone()[0]
            
            conn.close()
            
            # Account creation check
            if created_accounts == 0:
                status = ReadinessLevel.NOT_STARTED
                score = 0
                message = f"No accounts created yet (0/{total_accounts})"
                recs = [
                    "Follow ACCOUNT_SETUP_STEP_BY_STEP.md",
                    "Start with Vumistream and Twiva for immediate monetization",
                    "Update database after each account creation"
                ]
            elif created_accounts < total_accounts:
                status = ReadinessLevel.WARNING
                score = int((created_accounts / total_accounts) * 100)
                message = f"Partial account creation ({created_accounts}/{total_accounts} accounts)"
                recs = [f"Complete remaining {total_accounts - created_accounts} accounts"]
            else:
                status = ReadinessLevel.READY
                score = 100
                message = f"All accounts created ({created_accounts}/{total_accounts})"
                recs = []
            
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Account Creation",
                status=status,
                message=message,
                score=score,
                recommendations=recs
            ))
            
            # Verification check
            if verified_count == 0:
                status = ReadinessLevel.BLOCKED
                score = 0
                recs = ["Verify email addresses for all created accounts"]
            elif verified_count < created_accounts:
                status = ReadinessLevel.WARNING
                score = int((verified_count / max(created_accounts, 1)) * 100)
                recs = [f"Verify remaining {created_accounts - verified_count} accounts"]
            else:
                status = ReadinessLevel.READY
                score = 100
                recs = []
            
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Email Verification",
                status=status,
                message=f"{verified_count}/{max(created_accounts, 1)} accounts verified",
                score=score,
                recommendations=recs
            ))
            
            # 2FA check
            if created_accounts > 0 and twofa_count == 0:
                status = ReadinessLevel.WARNING
                score = 0
                recs = ["Enable 2FA on all accounts for security"]
            elif twofa_count < created_accounts:
                status = ReadinessLevel.WARNING
                score = int((twofa_count / max(created_accounts, 1)) * 100)
                recs = [f"Enable 2FA on remaining {created_accounts - twofa_count} accounts"]
            else:
                status = ReadinessLevel.READY if created_accounts > 0 else ReadinessLevel.NOT_STARTED
                score = 100 if created_accounts > 0 else 0
                recs = []
            
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Two-Factor Authentication",
                status=status,
                message=f"{twofa_count}/{max(created_accounts, 1)} accounts secured",
                score=score,
                recommendations=recs
            ))
            
            # African platforms priority check
            if african_platforms == 0:
                status = ReadinessLevel.WARNING
                score = 0
                recs = [
                    "PRIORITY: Create Vumistream account (immediate monetization)",
                    "PRIORITY: Create Twiva account (commission-based income)"
                ]
            elif african_platforms < 3:
                status = ReadinessLevel.WARNING
                score = int((african_platforms / 3) * 100)
                recs = [f"Complete remaining {3 - african_platforms} African platform accounts"]
            else:
                status = ReadinessLevel.READY
                score = 100
                recs = []
            
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="African Platforms Priority",
                status=status,
                message=f"{african_platforms}/3 African platforms set up",
                score=score,
                recommendations=recs
            ))
            
        except Exception as e:
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Database Access",
                status=ReadinessLevel.BLOCKED,
                message=f"Error accessing database: {str(e)}",
                score=0,
                recommendations=["Check database integrity", "Run: python3 social_media_account_db.py"]
            ))
    
    def _validate_content(self):
        """Validate content queue readiness"""
        category = "Content Management"
        
        if not self.content_queue.exists():
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Content Queue Existence",
                status=ReadinessLevel.BLOCKED,
                message="Content queue not found",
                score=0,
                recommendations=["Run: python3 content_queue_manager.py"]
            ))
            return
        
        try:
            with open(self.content_queue, 'r') as f:
                content_data = json.load(f)
            
            # Handle both list and dict formats
            if isinstance(content_data, list):
                items = content_data
            else:
                items = content_data.get('items', [])
            
            total_items = len(items)
            
            # Check minimum content
            min_required = 14  # 2 weeks
            if total_items == 0:
                status = ReadinessLevel.BLOCKED
                score = 0
                message = "No content in queue"
                recs = [
                    "Create at least 14 content items for 2-week launch",
                    "Use content_queue_manager.py to add content",
                    "Follow content mix: 40% educational, 30% entertainment, 20% community, 10% promotional"
                ]
            elif total_items < min_required:
                status = ReadinessLevel.WARNING
                score = int((total_items / min_required) * 100)
                message = f"Insufficient content ({total_items}/{min_required} items)"
                recs = [f"Create {min_required - total_items} more content items"]
            else:
                status = ReadinessLevel.READY
                score = 100
                message = f"Sufficient content ({total_items} items)"
                recs = []
            
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Content Volume",
                status=status,
                message=message,
                score=score,
                recommendations=recs
            ))
            
            # Check scheduled content
            scheduled_items = [item for item in items if item.get('scheduled_date')]
            if len(scheduled_items) == 0 and total_items > 0:
                status = ReadinessLevel.WARNING
                score = 0
                recs = ["Schedule content items with dates and times"]
            elif len(scheduled_items) < total_items:
                status = ReadinessLevel.WARNING
                score = int((len(scheduled_items) / max(total_items, 1)) * 100)
                recs = [f"Schedule remaining {total_items - len(scheduled_items)} items"]
            else:
                status = ReadinessLevel.READY if total_items > 0 else ReadinessLevel.NOT_STARTED
                score = 100 if total_items > 0 else 0
                recs = []
            
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Content Scheduling",
                status=status,
                message=f"{len(scheduled_items)}/{max(total_items, 1)} items scheduled",
                score=score,
                recommendations=recs
            ))
            
            # Check content mix
            if total_items > 0:
                types = {}
                for item in items:
                    ctype = item.get('content_type', 'unknown')
                    types[ctype] = types.get(ctype, 0) + 1
                
                educational_pct = (types.get('educational', 0) / total_items) * 100
                entertainment_pct = (types.get('entertainment', 0) / total_items) * 100
                community_pct = (types.get('community', 0) / total_items) * 100
                promotional_pct = (types.get('promotional', 0) / total_items) * 100
                
                # Check if within 10% tolerance
                issues = []
                if abs(educational_pct - 40) > 10:
                    issues.append(f"Educational: {educational_pct:.1f}% (target 40%)")
                if abs(entertainment_pct - 30) > 10:
                    issues.append(f"Entertainment: {entertainment_pct:.1f}% (target 30%)")
                if abs(community_pct - 20) > 10:
                    issues.append(f"Community: {community_pct:.1f}% (target 20%)")
                if promotional_pct < 5:
                    issues.append(f"Promotional: {promotional_pct:.1f}% (target 10%)")
                
                if issues:
                    status = ReadinessLevel.WARNING
                    score = 50
                    recs = ["Adjust content mix to match targets:"] + issues
                else:
                    status = ReadinessLevel.READY
                    score = 100
                    recs = []
                
                self.validation_results.append(ValidationResult(
                    category=category,
                    check_name="Content Mix Compliance",
                    status=status,
                    message=f"Mix: {educational_pct:.0f}% edu, {entertainment_pct:.0f}% ent, {community_pct:.0f}% com, {promotional_pct:.0f}% promo",
                    score=score,
                    recommendations=recs
                ))
            
        except Exception as e:
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Content Queue Access",
                status=ReadinessLevel.BLOCKED,
                message=f"Error accessing content queue: {str(e)}",
                score=0,
                recommendations=["Check content_queue.json integrity"]
            ))
    
    def _validate_assets(self):
        """Validate profile assets availability"""
        category = "Brand Assets"
        
        # Check profile pictures
        profile_dir = self.workspace_root / "05_BRANDING_ARTIFACTS/profile_pictures"
        banner_dir = self.workspace_root / "05_BRANDING_ARTIFACTS/banners"
        
        has_profile = profile_dir.exists() and any(profile_dir.iterdir()) if profile_dir.exists() else False
        has_banners = banner_dir.exists() and any(banner_dir.iterdir()) if banner_dir.exists() else False
        
        if not has_profile:
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Profile Pictures",
                status=ReadinessLevel.BLOCKED,
                message="No profile pictures found",
                score=0,
                recommendations=[
                    "Create 800x800px master profile picture",
                    "Use profile_image_validator.py to resize for all platforms",
                    "Save to 05_BRANDING_ARTIFACTS/profile_pictures/"
                ]
            ))
        else:
            profiles = list(profile_dir.glob("*.png")) + list(profile_dir.glob("*.jpg"))
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Profile Pictures",
                status=ReadinessLevel.READY,
                message=f"{len(profiles)} profile images available",
                score=100,
                recommendations=[]
            ))
        
        if not has_banners:
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Banner Images",
                status=ReadinessLevel.WARNING,
                message="No banner images found",
                score=0,
                recommendations=[
                    "Create platform-specific banners",
                    "YouTube: 2560x1440px",
                    "Facebook: 820x312px",
                    "Save to 05_BRANDING_ARTIFACTS/banners/"
                ]
            ))
        else:
            banners = list(banner_dir.glob("*.png")) + list(banner_dir.glob("*.jpg"))
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Banner Images",
                status=ReadinessLevel.READY,
                message=f"{len(banners)} banner images available",
                score=100,
                recommendations=[]
            ))
        
        # Check bio templates
        bio_file = self.workspace_root / "05_BRANDING_ARTIFACTS/BIO_TEMPLATES.md"
        if bio_file.exists():
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Bio Templates",
                status=ReadinessLevel.READY,
                message="Bio templates available",
                score=100,
                recommendations=[]
            ))
        else:
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Bio Templates",
                status=ReadinessLevel.WARNING,
                message="Bio templates not found",
                score=0,
                recommendations=["Create BIO_TEMPLATES.md with platform-specific bios"]
            ))
    
    def _validate_monetization(self):
        """Validate monetization readiness"""
        category = "Monetization"
        
        if not self.accounts_db.exists():
            return
        
        try:
            conn = sqlite3.connect(self.accounts_db)
            cursor = conn.cursor()
            
            # Check immediate monetization platforms
            cursor.execute("""
                SELECT platform_name, account_status, monetization_status
                FROM accounts
                WHERE platform_name IN ('Vumistream', 'Twiva')
            """)
            immediate_platforms = cursor.fetchall()
            
            ready_count = sum(1 for p in immediate_platforms if p[1] in ('created', 'verified', 'configured', 'live'))
            
            if ready_count == 0:
                status = ReadinessLevel.WARNING
                score = 0
                message = "No immediate monetization platforms set up"
                recs = [
                    "PRIORITY: Set up Vumistream (immediate tips & subscriptions)",
                    "PRIORITY: Set up Twiva (commission-based income)"
                ]
            elif ready_count < 2:
                status = ReadinessLevel.WARNING
                score = 50
                message = f"{ready_count}/2 immediate monetization platforms ready"
                recs = ["Complete both Vumistream and Twiva setup"]
            else:
                status = ReadinessLevel.READY
                score = 100
                message = "Both immediate monetization platforms ready"
                recs = []
            
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Immediate Monetization",
                status=status,
                message=message,
                score=score,
                recommendations=recs
            ))
            
            # Check Twitch progress (fastest tier monetization)
            cursor.execute("""
                SELECT current_value, requirement_met
                FROM monetization_requirements
                WHERE platform_name = 'Twitch' AND requirement_type = 'followers'
            """)
            twitch_data = cursor.fetchone()
            
            if twitch_data:
                followers = twitch_data[0] or 0
                progress = (followers / 50) * 100
                
                if progress >= 90:
                    status = ReadinessLevel.READY
                    score = 100
                    message = f"Twitch Affiliate almost achieved ({followers}/50 followers)"
                    recs = ["Continue streaming to reach Affiliate status"]
                elif progress >= 50:
                    status = ReadinessLevel.WARNING
                    score = int(progress)
                    message = f"Twitch progress: {progress:.0f}% ({followers}/50 followers)"
                    recs = ["Stream regularly to grow follower count"]
                else:
                    status = ReadinessLevel.NOT_STARTED if followers == 0 else ReadinessLevel.WARNING
                    score = int(progress)
                    message = f"Twitch early stage ({followers}/50 followers)"
                    recs = ["Start streaming 2-3x weekly", "Engage with community"]
                
                self.validation_results.append(ValidationResult(
                    category=category,
                    check_name="Twitch Affiliate Progress",
                    status=status,
                    message=message,
                    score=score,
                    recommendations=recs
                ))
            
            conn.close()
            
        except Exception as e:
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Monetization Status",
                status=ReadinessLevel.BLOCKED,
                message=f"Error checking monetization: {str(e)}",
                score=0,
                recommendations=["Check accounts database"]
            ))
    
    def _validate_analytics(self):
        """Validate analytics configuration"""
        category = "Analytics"
        
        if not self.analytics_db.exists():
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Analytics Database",
                status=ReadinessLevel.WARNING,
                message="Analytics database not initialized",
                score=0,
                recommendations=["Run: python3 analytics_dashboard.py"]
            ))
        else:
            try:
                conn = sqlite3.connect(self.analytics_db)
                cursor = conn.cursor()
                
                # Check if tables exist
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                if table_count >= 4:
                    status = ReadinessLevel.READY
                    score = 100
                    message = "Analytics system ready"
                    recs = []
                else:
                    status = ReadinessLevel.WARNING
                    score = 50
                    message = f"Incomplete analytics setup ({table_count}/4 tables)"
                    recs = ["Reinitialize analytics database"]
                
                self.validation_results.append(ValidationResult(
                    category=category,
                    check_name="Analytics Database",
                    status=status,
                    message=message,
                    score=score,
                    recommendations=recs
                ))
                
                conn.close()
                
            except Exception as e:
                self.validation_results.append(ValidationResult(
                    category=category,
                    check_name="Analytics Database",
                    status=ReadinessLevel.BLOCKED,
                    message=f"Error: {str(e)}",
                    score=0,
                    recommendations=["Check database integrity"]
                ))
    
    def _validate_integrations(self):
        """Validate third-party integrations"""
        category = "Integrations"
        
        # Check Buffer export availability
        buffer_file = self.workspace_root / "03_MEDIA_ASSETS/content_queue/buffer_import.csv"
        
        if buffer_file.exists():
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Buffer Integration",
                status=ReadinessLevel.READY,
                message="Buffer import file available",
                score=100,
                recommendations=["Import buffer_import.csv into Buffer dashboard"]
            ))
        else:
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Buffer Integration",
                status=ReadinessLevel.WARNING,
                message="Buffer import not generated",
                score=0,
                recommendations=[
                    "Run content_queue_manager.py to generate Buffer CSV",
                    "Set up Buffer account at buffer.com"
                ]
            ))
        
        # Check automation guide
        automation_guide = self.workspace_root / "05_BRANDING_ARTIFACTS/AUTOMATION_SETUP_GUIDE.md"
        
        if automation_guide.exists():
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Automation Documentation",
                status=ReadinessLevel.READY,
                message="Automation guide available",
                score=100,
                recommendations=[]
            ))
        else:
            self.validation_results.append(ValidationResult(
                category=category,
                check_name="Automation Documentation",
                status=ReadinessLevel.WARNING,
                message="Automation guide missing",
                score=0,
                recommendations=["Create AUTOMATION_SETUP_GUIDE.md"]
            ))
    
    def _validate_documentation(self):
        """Validate documentation completeness"""
        category = "Documentation"
        
        required_docs = {
            "Account Master": "05_BRANDING_ARTIFACTS/SOCIAL_MEDIA_ACCOUNTS_MASTER.md",
            "Setup Guide": "05_BRANDING_ARTIFACTS/ACCOUNT_SETUP_STEP_BY_STEP.md",
            "Bio Templates": "05_BRANDING_ARTIFACTS/BIO_TEMPLATES.md",
            "Scripts README": "00_PROJECT_CORE/Scripts/README.md"
        }
        
        found = 0
        missing = []
        
        for name, path in required_docs.items():
            full_path = self.workspace_root / path
            if full_path.exists():
                found += 1
            else:
                missing.append(name)
        
        total = len(required_docs)
        score = int((found / total) * 100)
        
        if found == total:
            status = ReadinessLevel.READY
            message = f"All documentation complete ({found}/{total})"
            recs = []
        else:
            status = ReadinessLevel.WARNING
            message = f"Incomplete documentation ({found}/{total})"
            recs = [f"Create missing: {', '.join(missing)}"]
        
        self.validation_results.append(ValidationResult(
            category=category,
            check_name="Documentation Completeness",
            status=status,
            message=message,
            score=score,
            recommendations=recs
        ))
    
    def _generate_summary(self) -> Dict:
        """Generate overall readiness summary"""
        total_score = sum(r.score for r in self.validation_results)
        max_score = len(self.validation_results) * 100
        overall_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        status_counts = {
            ReadinessLevel.READY: 0,
            ReadinessLevel.WARNING: 0,
            ReadinessLevel.BLOCKED: 0,
            ReadinessLevel.NOT_STARTED: 0
        }
        
        for result in self.validation_results:
            status_counts[result.status] += 1
        
        # Determine overall readiness
        if status_counts[ReadinessLevel.BLOCKED] > 0:
            overall_status = "BLOCKED - Critical issues must be resolved"
        elif overall_percentage >= 80:
            overall_status = "READY - Launch approved"
        elif overall_percentage >= 60:
            overall_status = "NEARLY READY - Minor improvements needed"
        elif overall_percentage >= 40:
            overall_status = "IN PROGRESS - Significant work remaining"
        else:
            overall_status = "NOT READY - Major setup required"
        
        return {
            'overall_percentage': overall_percentage,
            'overall_status': overall_status,
            'total_checks': len(self.validation_results),
            'ready': status_counts[ReadinessLevel.READY],
            'warnings': status_counts[ReadinessLevel.WARNING],
            'blocked': status_counts[ReadinessLevel.BLOCKED],
            'not_started': status_counts[ReadinessLevel.NOT_STARTED],
            'timestamp': datetime.now().isoformat()
        }
    
    def _print_results(self):
        """Print formatted validation results"""
        print("\n" + "=" * 80)
        print("📋 VALIDATION RESULTS BY CATEGORY")
        print("=" * 80)
        
        # Group by category
        categories = {}
        for result in self.validation_results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        # Print each category
        for category, results in categories.items():
            print(f"\n📂 {category}")
            print("-" * 80)
            
            for result in results:
                print(f"\n  {result.status.value} {result.check_name}")
                print(f"  └─ {result.message}")
                print(f"  └─ Score: {result.score}/100")
                
                if result.recommendations:
                    print(f"  └─ Recommendations:")
                    for rec in result.recommendations:
                        print(f"     • {rec}")
        
        # Print summary
        summary = self._generate_summary()
        
        print("\n" + "=" * 80)
        print("🎯 OVERALL READINESS SUMMARY")
        print("=" * 80)
        print(f"\nOverall Score: {summary['overall_percentage']:.1f}%")
        
        # Progress bar
        bar_length = 50
        filled = int(bar_length * summary['overall_percentage'] / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"[{bar}]")
        
        print(f"\nStatus: {summary['overall_status']}")
        print(f"\nChecks Breakdown:")
        print(f"  ✅ Ready: {summary['ready']}")
        print(f"  ⚠️  Warnings: {summary['warnings']}")
        print(f"  ❌ Blocked: {summary['blocked']}")
        print(f"  ⏸️  Not Started: {summary['not_started']}")
        print(f"\nTotal Checks: {summary['total_checks']}")
        
        # Critical path
        print("\n" + "=" * 80)
        print("🚀 CRITICAL PATH TO LAUNCH")
        print("=" * 80)
        
        blocked = [r for r in self.validation_results if r.status == ReadinessLevel.BLOCKED]
        high_priority = [r for r in self.validation_results if r.status == ReadinessLevel.WARNING and r.score < 30]
        
        if blocked:
            print("\n❌ BLOCKERS (Must resolve before launch):")
            for i, result in enumerate(blocked, 1):
                print(f"\n{i}. {result.check_name}")
                for rec in result.recommendations:
                    print(f"   • {rec}")
        
        if high_priority:
            print("\n⚠️  HIGH PRIORITY (Strongly recommended):")
            for i, result in enumerate(high_priority, 1):
                print(f"\n{i}. {result.check_name}")
                for rec in result.recommendations[:2]:  # Top 2 recommendations
                    print(f"   • {rec}")
        
        if not blocked and not high_priority:
            print("\n✅ No critical blockers! System ready for launch.")
            print("\nRecommended next steps:")
            print("  1. Begin posting content according to schedule")
            print("  2. Monitor analytics daily")
            print("  3. Engage with community actively")
            print("  4. Track monetization progress weekly")
        
        print("\n" + "=" * 80)
    
    def export_report(self, output_file: Path = None):
        """Export validation report to JSON"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.workspace_root / f"08_MLOPS_PIPELINE/reports/launch_readiness_{timestamp}.json"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        summary = self._generate_summary()
        
        report = {
            'summary': summary,
            'results': [
                {
                    'category': r.category,
                    'check_name': r.check_name,
                    'status': r.status.value,
                    'message': r.message,
                    'score': r.score,
                    'recommendations': r.recommendations
                }
                for r in self.validation_results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report exported to: {output_file}")
        
        return output_file


def main():
    """Main execution"""
    validator = LaunchReadinessValidator()
    summary = validator.validate_all()
    validator.export_report()
    
    # Return exit code based on readiness
    if summary['blocked'] > 0:
        return 2  # Blocked
    elif summary['overall_percentage'] < 60:
        return 1  # Not ready
    else:
        return 0  # Ready


if __name__ == "__main__":
    exit(main())
