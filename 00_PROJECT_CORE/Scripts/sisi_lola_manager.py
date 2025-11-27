"""
Sisi Lola Social Media Management System - Master Control
Launch, manage, and monitor all social media operations
"""

import sys
from pathlib import Path
from datetime import datetime
import argparse

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from social_media_account_db import SocialMediaAccountDB, AccountStatus
from profile_image_validator import ProfileImageValidator
from content_queue_manager import ContentQueueManager
from analytics_dashboard import AnalyticsDashboard


class SisiLolaManager:
    """Master control for all social media operations"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.account_db = SocialMediaAccountDB()
        self.validator = ProfileImageValidator()
        self.content_manager = ContentQueueManager()
        self.analytics = AnalyticsDashboard()
    
    def initialize_system(self):
        """Initialize all systems"""
        print("=" * 70)
        print("INITIALIZING SISI LOLA SOCIAL MEDIA MANAGEMENT SYSTEM")
        print("=" * 70)
        print()
        
        # Initialize account database
        print("1. Initializing Account Database...")
        self.account_db.seed_initial_accounts()
        self.account_db.seed_monetization_requirements()
        print("   ✓ Account database ready")
        
        # Generate image templates
        print("\n2. Generating Image Templates...")
        output_dir = self.base_dir / "05_BRANDING_ARTIFACTS" / "image_templates"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        spec_doc = output_dir / "IMAGE_SPECIFICATIONS.md"
        self.validator.generate_specification_document(spec_doc)
        print(f"   ✓ Image specifications: {spec_doc}")
        
        # Create sample templates
        templates = [
            ("profile_800x800_master", 800, 800, True, None),
            ("profile_320x320", 320, 320, True, None),
            ("banner_youtube", 2560, 1440, False, (507, 508, 1546, 423)),
        ]
        
        for name, width, height, circular, safe_area in templates:
            output_path = output_dir / f"template_{name}.png"
            try:
                self.validator.create_template_with_guides(
                    width, height, output_path, circular, safe_area
                )
                print(f"   ✓ Created: template_{name}.png")
            except Exception as e:
                print(f"   ⚠ Warning: Could not create template {name}: {e}")
        
        # Initialize content queue
        print("\n3. Initializing Content Queue...")
        self.content_manager.generate_calendar_csv()
        print(f"   ✓ Content calendar: {self.content_manager.calendar_file}")
        
        # Initialize analytics
        print("\n4. Initializing Analytics Dashboard...")
        print("   ✓ Analytics database ready")
        
        print("\n" + "=" * 70)
        print("✓ SYSTEM INITIALIZATION COMPLETE")
        print("=" * 70)
    
    def show_dashboard(self):
        """Display comprehensive dashboard"""
        print("\n" + "=" * 70)
        print("SISI LOLA SOCIAL MEDIA DASHBOARD")
        print("=" * 70)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Account status
        print("ACCOUNT STATUS:")
        print("-" * 70)
        progress = self.account_db.get_creation_progress()
        print(f"Total Accounts: {progress['total_accounts']}")
        print(f"Created: {progress['created_accounts']}")
        print(f"Live: {progress['live_accounts']}")
        print(f"Progress: {progress['progress_percentage']:.1f}%")
        
        # Progress bar
        bar_length = 50
        filled = int(bar_length * progress['progress_percentage'] / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"[{bar}] {progress['progress_percentage']:.1f}%")
        
        # Platform breakdown
        print("\nBY PLATFORM:")
        accounts = self.account_db.get_all_accounts()
        for account in accounts:
            status_icon = {
                'not_created': '○',
                'created': '◐',
                'verified': '◑',
                'configured': '◕',
                'live': '●'
            }.get(account['account_status'], '?')
            
            print(f"  {status_icon} {account['platform_name']:15} - {account['account_status']}")
        
        # Content queue
        print("\n" + "=" * 70)
        print("CONTENT QUEUE:")
        print("-" * 70)
        stats = self.content_manager.get_content_mix_stats(14)
        print(f"Scheduled (Next 14 Days): {stats['total_scheduled']}")
        print("\nBy Type:")
        for content_type, count in stats['by_type'].items():
            pct = stats['type_percentages'][content_type]
            print(f"  {content_type:15}: {count:3} ({pct:5.1f}%)")
        
        # Monetization status
        print("\n" + "=" * 70)
        print("MONETIZATION PROGRESS:")
        print("-" * 70)
        
        priority_platforms = {
            'Vumistream': '⚡ IMMEDIATE',
            'Twiva': '⚡ IMMEDIATE',
            'Twitch': '🎯 1-2 months',
            'TikTok': '📊 2-4 months',
            'YouTube': '📊 3-6 months'
        }
        
        for platform, timeline in priority_platforms.items():
            status = self.account_db.get_monetization_status(platform)
            print(f"\n{platform} ({timeline}):")
            
            if status['requirements']:
                for req in status['requirements']:
                    current = req['current_value']
                    target = req['requirement_value']
                    pct = (current / target * 100) if target > 0 else 0
                    
                    print(f"  {req['requirement_type']:20}: {current:6,} / {target:6,} ({pct:5.1f}%)")
                    
                    # Mini progress bar
                    bar_len = 20
                    filled = int(bar_len * pct / 100)
                    bar = '█' * filled + '░' * (bar_len - filled)
                    print(f"    [{bar}]")
            else:
                print("  ✓ READY TO MONETIZE")
        
        print("\n" + "=" * 70)
    
    def show_next_steps(self):
        """Show recommended next steps"""
        print("\n" + "=" * 70)
        print("RECOMMENDED NEXT STEPS")
        print("=" * 70)
        print()
        
        accounts = self.account_db.get_all_accounts()
        
        # Count statuses
        not_created = sum(1 for a in accounts if a['account_status'] == 'not_created')
        
        if not_created > 0:
            print("🎯 PRIORITY: Create Social Media Accounts")
            print("-" * 70)
            print("Follow the step-by-step guide:")
            print(f"  File: 05_BRANDING_ARTIFACTS/ACCOUNT_SETUP_STEP_BY_STEP.md")
            print()
            print("Accounts to create:")
            for account in accounts:
                if account['account_status'] == 'not_created':
                    print(f"  ○ {account['platform_name']:15} - {account['email']}")
            print()
        
        # Check if images needed
        print("\n📸 BRANDING ASSETS")
        print("-" * 70)
        print("1. Create profile picture (800x800px master)")
        print(f"   Template: 05_BRANDING_ARTIFACTS/image_templates/template_profile_800x800_master.png")
        print()
        print("2. Create banners for:")
        print("   • YouTube (2560x1440px)")
        print("   • Facebook (820x312px)")
        print("   • Universal/African platforms (1920x1080px)")
        print()
        
        # Content suggestions
        print("\n📝 CONTENT CREATION")
        print("-" * 70)
        suggestions = self.content_manager.suggest_next_content(14)
        for suggestion in suggestions:
            print(f"  • {suggestion}")
        print()
        
        # Immediate monetization
        print("\n💰 MONETIZATION QUICK WINS")
        print("-" * 70)
        print("1. ⚡ Vumistream - Set up mobile money integration")
        print("2. ⚡ Twiva - Apply for product campaigns")
        print("3. 🎯 Twitch - Stream to hit Affiliate requirements (easiest!)")
        print()
        
        print("=" * 70)
    
    def export_all_data(self):
        """Export all data for backup/review"""
        print("\n" + "=" * 70)
        print("EXPORTING ALL DATA")
        print("=" * 70)
        print()
        
        export_dir = self.base_dir / "05_BRANDING_ARTIFACTS" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export accounts
        accounts_file = export_dir / f"accounts_{timestamp}.json"
        self.account_db.export_to_json(str(accounts_file))
        print(f"✓ Accounts exported: {accounts_file}")
        
        # Export content queue
        content_file = self.content_manager.calendar_file
        print(f"✓ Content calendar: {content_file}")
        
        # Export analytics
        analytics_dir = self.analytics.export_to_csv()
        print(f"✓ Analytics exported: {analytics_dir}")
        
        # Generate reports
        reports_dir = self.base_dir / "08_MLOPS_PIPELINE" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Account report
        account_report = reports_dir / f"account_status_{timestamp}.txt"
        with open(account_report, 'w') as f:
            f.write(self.account_db.generate_report())
        print(f"✓ Account report: {account_report}")
        
        # Content report
        content_report = reports_dir / f"content_queue_{timestamp}.txt"
        with open(content_report, 'w') as f:
            f.write(self.content_manager.generate_report())
        print(f"✓ Content report: {content_report}")
        
        # Analytics report
        analytics_report = reports_dir / f"analytics_{timestamp}.txt"
        with open(analytics_report, 'w') as f:
            f.write(self.analytics.generate_dashboard_report())
        print(f"✓ Analytics report: {analytics_report}")
        
        print("\n" + "=" * 70)
        print("✓ ALL DATA EXPORTED SUCCESSFULLY")
        print("=" * 70)
    
    def generate_launch_checklist(self):
        """Generate comprehensive launch readiness checklist"""
        print("\n" + "=" * 70)
        print("LAUNCH READINESS CHECKLIST")
        print("=" * 70)
        print()
        
        checklist = []
        accounts = self.account_db.get_all_accounts()
        
        # Account creation
        all_created = all(a['account_status'] != 'not_created' for a in accounts)
        checklist.append(('Accounts Created', all_created))
        
        all_verified = all(a['email_verified'] for a in accounts)
        checklist.append(('Emails Verified', all_verified))
        
        all_2fa = all(a['two_fa_enabled'] for a in accounts if a['account_status'] != 'not_created')
        checklist.append(('2FA Enabled', all_2fa))
        
        # Branding assets
        image_dir = self.base_dir / "05_BRANDING_ARTIFACTS" / "profile_images"
        has_profile = (image_dir / "sisilola_profile_master.png").exists()
        checklist.append(('Profile Picture Created', has_profile))
        
        # Content ready
        ready_content = len(self.content_manager.get_by_status(
            self.content_manager.queue[0].status.__class__.READY
        )) if self.content_manager.queue else 0
        has_content = ready_content >= 10
        checklist.append(('10+ Content Pieces Ready', has_content))
        
        # Monetization setup
        vumistream = self.account_db.get_account('Vumistream')
        vumi_configured = vumistream and vumistream['account_status'] in ['configured', 'live']
        checklist.append(('Vumistream Monetization Set Up', vumi_configured))
        
        print("SYSTEM READINESS:")
        print("-" * 70)
        
        for item, status in checklist:
            icon = '✓' if status else '○'
            print(f"{icon} {item}")
        
        ready_count = sum(1 for _, status in checklist if status)
        total = len(checklist)
        percentage = (ready_count / total * 100) if total > 0 else 0
        
        print()
        print(f"Overall Readiness: {ready_count}/{total} ({percentage:.1f}%)")
        
        bar_length = 50
        filled = int(bar_length * percentage / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"[{bar}] {percentage:.1f}%")
        
        print()
        if percentage >= 80:
            print("🚀 SYSTEM IS READY FOR LAUNCH!")
        elif percentage >= 50:
            print("⚠ SYSTEM PARTIALLY READY - Complete remaining items")
        else:
            print("⚠ SYSTEM NOT READY - More setup required")
        
        print()
        print("=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Sisi Lola Social Media Management System'
    )
    parser.add_argument(
        'command',
        choices=['init', 'dashboard', 'next-steps', 'export', 'launch-check', 'full'],
        help='Command to execute'
    )
    
    args = parser.parse_args()
    
    manager = SisiLolaManager()
    
    if args.command == 'init':
        manager.initialize_system()
    
    elif args.command == 'dashboard':
        manager.show_dashboard()
    
    elif args.command == 'next-steps':
        manager.show_next_steps()
    
    elif args.command == 'export':
        manager.export_all_data()
    
    elif args.command == 'launch-check':
        manager.generate_launch_checklist()
    
    elif args.command == 'full':
        manager.initialize_system()
        manager.show_dashboard()
        manager.show_next_steps()
        manager.export_all_data()
        manager.generate_launch_checklist()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, run full initialization and dashboard
        manager = SisiLolaManager()
        manager.initialize_system()
        manager.show_dashboard()
        manager.show_next_steps()
    else:
        main()
