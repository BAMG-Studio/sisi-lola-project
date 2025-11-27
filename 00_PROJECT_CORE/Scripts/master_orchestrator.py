"""
Master Automation Orchestrator
Coordinates all social media automation components
"""

import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Import our custom modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    from social_media_account_db import SocialMediaAccountDB, AccountStatus
    from automated_content_scheduler import AutomatedContentScheduler, ScheduledPost, ScheduleStatus
    from unified_api_poster import UnifiedAPIPoster, PostContent
    from oauth_credential_manager import SecureCredentialManager
    from content_template_generator import ContentTemplateGenerator, ContentCategory
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    print("Make sure all required scripts are in the same directory.")


@dataclass
class OrchestrationConfig:
    """Orchestrator configuration"""
    auto_post_enabled: bool = False
    post_interval_minutes: int = 30
    max_posts_per_run: int = 5
    retry_failed_posts: bool = True
    max_retries: int = 3
    dry_run: bool = False
    enable_logging: bool = True
    log_level: str = "INFO"


class MasterAutomationOrchestrator:
    """
    Master orchestrator coordinating all automation components:
    - Content scheduling
    - Platform posting
    - Analytics tracking
    - Error handling and retries
    - Logging and monitoring
    """
    
    def __init__(self, config: OrchestrationConfig = None):
        if config is None:
            config = OrchestrationConfig()
        self.config = config
        
        # Initialize components
        self.account_db = SocialMediaAccountDB()
        self.scheduler = AutomatedContentScheduler()
        self.poster = UnifiedAPIPoster()
        self.cred_manager = SecureCredentialManager()
        self.template_generator = ContentTemplateGenerator()
        
        # Setup logging
        self._setup_logging()
        
        # Statistics
        self.stats = {
            'total_posts_attempted': 0,
            'total_posts_successful': 0,
            'total_posts_failed': 0,
            'posts_by_platform': {},
            'errors': []
        }
        
        self.logger.info("Master Automation Orchestrator initialized")
    
    def _setup_logging(self):
        """Setup logging system"""
        if not self.config.enable_logging:
            logging.disable(logging.CRITICAL)
            self.logger = logging.getLogger('orchestrator')
            return
        
        # Create logs directory
        log_dir = Path(__file__).parent.parent / "08_MLOPS_PIPELINE" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        log_file = log_dir / f"orchestrator_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('orchestrator')
        self.logger.info(f"Logging initialized - {log_file}")
    
    # ========================================================================
    # MAIN ORCHESTRATION METHODS
    # ========================================================================
    
    def run_full_cycle(self):
        """
        Execute full automation cycle:
        1. Check for due posts
        2. Post to platforms
        3. Update statuses
        4. Log results
        """
        self.logger.info("="*70)
        self.logger.info("Starting full automation cycle")
        self.logger.info("="*70)
        
        try:
            # Step 1: Get posts due now
            due_posts = self.scheduler.get_posts_due_now(window_minutes=30)
            
            if not due_posts:
                self.logger.info("No posts due at this time")
                return
            
            self.logger.info(f"Found {len(due_posts)} posts due for posting")
            
            # Limit posts per run
            posts_to_process = due_posts[:self.config.max_posts_per_run]
            
            # Step 2: Process each post
            for post_data in posts_to_process:
                self._process_post(post_data)
                
                # Rate limiting between posts
                time.sleep(5)
            
            # Step 3: Generate report
            self._generate_cycle_report()
            
        except Exception as e:
            self.logger.error(f"Error in automation cycle: {e}", exc_info=True)
            self.stats['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'phase': 'full_cycle'
            })
    
    def _process_post(self, post_data: Dict):
        """Process single scheduled post"""
        post_id = post_data['id']
        title = post_data['title']
        
        self.logger.info(f"Processing post {post_id}: {title}")
        
        try:
            # Create PostContent object
            platforms = post_data.get('platforms', [])
            
            content = PostContent(
                title=post_data['title'],
                caption=post_data['caption'],
                media_path=post_data.get('media_path'),
                media_type=post_data.get('media_type', 'video'),
                tags=post_data.get('tags', []),
                hashtags=post_data.get('hashtags', [])
            )
            
            # Dry run check
            if self.config.dry_run:
                self.logger.info(f"DRY RUN: Would post to {', '.join(platforms)}")
                self.scheduler.update_post_status(post_id, ScheduleStatus.POSTED)
                return
            
            # Post to platforms
            results = self.poster.post_to_all_platforms(content, platforms)
            
            # Update statistics
            for result in results:
                self.stats['total_posts_attempted'] += 1
                
                if result.success:
                    self.stats['total_posts_successful'] += 1
                    self.stats['posts_by_platform'][result.platform] = \
                        self.stats['posts_by_platform'].get(result.platform, 0) + 1
                    
                    # Update platform schedule
                    self.scheduler.update_platform_schedule(
                        post_id=post_id,
                        platform=result.platform,
                        posted=True,
                        post_url=result.post_url
                    )
                    
                    self.logger.info(f"✅ Posted to {result.platform}: {result.post_url}")
                else:
                    self.stats['total_posts_failed'] += 1
                    self.stats['errors'].append({
                        'post_id': post_id,
                        'platform': result.platform,
                        'error': result.error_message,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Update with error
                    self.scheduler.update_platform_schedule(
                        post_id=post_id,
                        platform=result.platform,
                        posted=False,
                        error_message=result.error_message
                    )
                    
                    self.logger.error(f"❌ Failed to post to {result.platform}: {result.error_message}")
            
            # Update post status
            all_successful = all(r.success for r in results)
            if all_successful:
                self.scheduler.update_post_status(post_id, ScheduleStatus.POSTED)
            else:
                self.scheduler.update_post_status(post_id, ScheduleStatus.FAILED)
        
        except Exception as e:
            self.logger.error(f"Error processing post {post_id}: {e}", exc_info=True)
            self.scheduler.update_post_status(post_id, ScheduleStatus.FAILED)
            self.stats['errors'].append({
                'post_id': post_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def _generate_cycle_report(self):
        """Generate and save cycle report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'config': asdict(self.config),
            'statistics': self.stats,
            'summary': {
                'total_attempted': self.stats['total_posts_attempted'],
                'total_successful': self.stats['total_posts_successful'],
                'total_failed': self.stats['total_posts_failed'],
                'success_rate': (self.stats['total_posts_successful'] / 
                               self.stats['total_posts_attempted'] * 100) 
                               if self.stats['total_posts_attempted'] > 0 else 0
            }
        }
        
        # Save report
        report_dir = Path(__file__).parent.parent / "08_MLOPS_PIPELINE" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"orchestration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Report saved: {report_file}")
        
        # Print summary
        self._print_summary(report['summary'])
    
    def _print_summary(self, summary: Dict):
        """Print execution summary"""
        print("\n" + "="*70)
        print("AUTOMATION CYCLE SUMMARY")
        print("="*70)
        print(f"Total Posts Attempted: {summary['total_attempted']}")
        print(f"✅ Successful: {summary['total_successful']}")
        print(f"❌ Failed: {summary['total_failed']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        if self.stats['posts_by_platform']:
            print("\nPosts by Platform:")
            for platform, count in self.stats['posts_by_platform'].items():
                print(f"  {platform}: {count}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5
                print(f"  - {error.get('platform', 'general')}: {error.get('error', 'Unknown')[:100]}")
        
        print("="*70)
    
    # ========================================================================
    # CONTENT GENERATION METHODS
    # ========================================================================
    
    def generate_and_schedule_content(self, count: int = 14, 
                                     category_distribution: Dict = None):
        """
        Generate content using templates and schedule automatically
        
        Args:
            count: Number of content pieces to generate
            category_distribution: Distribution of content categories
        """
        self.logger.info(f"Generating and scheduling {count} content pieces")
        
        # Generate batch
        batch = self.template_generator.generate_batch(count, category_distribution)
        
        platforms = ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Reddit']
        
        scheduled_count = 0
        
        for item in batch:
            # Get platform-optimized content
            platform_content = item['platform_content']
            
            # Use Instagram content as base (good balance)
            instagram_content = platform_content.get('Instagram', {})
            
            # Create scheduled post
            post = ScheduledPost(
                title=item['topic'],
                caption=instagram_content.get('raw_caption', item['description']),
                content_type=item['category'],
                platforms=platforms,
                tags=instagram_content.get('hashtags', [])[:10],
                hashtags=instagram_content.get('hashtags', []),
                media_type='video',
                notes=f"Auto-generated from template: {item['category']}"
            )
            
            # Add to scheduler (auto-schedule)
            post_id = self.scheduler.add_post(post, auto_schedule=True)
            scheduled_count += 1
            
            self.logger.info(f"Scheduled post {post_id}: {item['topic']}")
        
        print(f"\n✅ Successfully generated and scheduled {scheduled_count} posts!")
        
        # Print schedule summary
        self.scheduler.print_schedule_summary()
    
    # ========================================================================
    # MONITORING & MAINTENANCE METHODS
    # ========================================================================
    
    def check_system_health(self) -> Dict:
        """
        Check health of all system components
        
        Returns:
            Health status dictionary
        """
        health = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {}
        }
        
        # Check database connectivity
        try:
            accounts = self.account_db.get_all_accounts()
            health['components']['account_database'] = {
                'status': 'healthy',
                'accounts_tracked': len(accounts)
            }
        except Exception as e:
            health['components']['account_database'] = {
                'status': 'error',
                'error': str(e)
            }
            health['overall_status'] = 'degraded'
        
        # Check scheduler
        try:
            pending = self.scheduler.get_pending_posts(limit=1)
            health['components']['scheduler'] = {
                'status': 'healthy',
                'pending_posts': len(pending)
            }
        except Exception as e:
            health['components']['scheduler'] = {
                'status': 'error',
                'error': str(e)
            }
            health['overall_status'] = 'degraded'
        
        # Check credentials
        validation = self.cred_manager.validate_all()
        configured_count = sum(1 for v in validation.values() if v)
        
        health['components']['credentials'] = {
            'status': 'healthy' if configured_count > 0 else 'warning',
            'platforms_configured': f"{configured_count}/6",
            'details': validation
        }
        
        if configured_count == 0:
            health['overall_status'] = 'warning'
        
        return health
    
    def print_system_status(self):
        """Print comprehensive system status"""
        print("\n" + "="*70)
        print("SYSTEM STATUS REPORT")
        print("="*70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Account status
        print("\n📊 ACCOUNTS:")
        progress = self.account_db.get_creation_progress()
        print(f"  Total Accounts: {progress['total_accounts']}")
        print(f"  Created: {progress['created_accounts']}")
        print(f"  Live: {progress['live_accounts']}")
        print(f"  Progress: {progress['progress_percentage']:.1f}%")
        
        # Schedule status
        print("\n📅 CONTENT SCHEDULE:")
        pending = self.scheduler.get_pending_posts()
        due_now = self.scheduler.get_posts_due_now()
        print(f"  Pending Posts: {len(pending)}")
        print(f"  Due Now (30min): {len(due_now)}")
        
        # Content mix
        mix = self.scheduler.get_content_mix_current()
        if mix:
            print("\n  Content Mix:")
            for content_type, percentage in mix.items():
                print(f"    {content_type}: {percentage:.1%}")
        
        # Credentials
        print("\n🔑 API CREDENTIALS:")
        validation = self.cred_manager.validate_all()
        for platform, is_valid in validation.items():
            status = "✅ Configured" if is_valid else "❌ Not Configured"
            print(f"  {platform.capitalize():15} {status}")
        
        # Health check
        print("\n💚 SYSTEM HEALTH:")
        health = self.check_system_health()
        print(f"  Overall Status: {health['overall_status'].upper()}")
        
        for component, status in health['components'].items():
            comp_status = status['status']
            emoji = "✅" if comp_status == 'healthy' else "⚠️" if comp_status == 'warning' else "❌"
            print(f"  {emoji} {component}: {comp_status}")
        
        print("="*70)
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def run_interactive_mode(self):
        """Run interactive mode with menu"""
        while True:
            print("\n" + "="*70)
            print("SISI LOLA MASTER AUTOMATION ORCHESTRATOR")
            print("="*70)
            print("\nOptions:")
            print("1. Run Full Automation Cycle")
            print("2. Generate & Schedule Content")
            print("3. View System Status")
            print("4. Check System Health")
            print("5. View Pending Posts")
            print("6. View Schedule Summary")
            print("7. Test Posting (Dry Run)")
            print("8. Configure Settings")
            print("9. Exit")
            
            choice = input("\nEnter choice (1-9): ").strip()
            
            if choice == '1':
                self.run_full_cycle()
            elif choice == '2':
                count = input("How many posts to generate? (default: 14): ").strip()
                count = int(count) if count else 14
                self.generate_and_schedule_content(count)
            elif choice == '3':
                self.print_system_status()
            elif choice == '4':
                health = self.check_system_health()
                print(json.dumps(health, indent=2))
            elif choice == '5':
                pending = self.scheduler.get_pending_posts(limit=10)
                print(f"\nNext {len(pending)} pending posts:")
                for post in pending:
                    print(f"  - {post['title']} ({post['schedule_time']})")
            elif choice == '6':
                self.scheduler.print_schedule_summary()
            elif choice == '7':
                original_dry_run = self.config.dry_run
                self.config.dry_run = True
                self.run_full_cycle()
                self.config.dry_run = original_dry_run
            elif choice == '8':
                self._configure_settings()
            elif choice == '9':
                print("Exiting...")
                break
            else:
                print("Invalid choice!")
    
    def _configure_settings(self):
        """Interactive settings configuration"""
        print("\n" + "="*70)
        print("CONFIGURATION")
        print("="*70)
        
        print(f"\nCurrent Settings:")
        print(f"  Auto-post enabled: {self.config.auto_post_enabled}")
        print(f"  Post interval: {self.config.post_interval_minutes} minutes")
        print(f"  Max posts per run: {self.config.max_posts_per_run}")
        print(f"  Dry run mode: {self.config.dry_run}")
        
        if input("\nModify settings? (y/n): ").lower() == 'y':
            self.config.auto_post_enabled = input("Enable auto-posting? (y/n): ").lower() == 'y'
            
            interval = input(f"Post interval in minutes (current: {self.config.post_interval_minutes}): ").strip()
            if interval:
                self.config.post_interval_minutes = int(interval)
            
            max_posts = input(f"Max posts per run (current: {self.config.max_posts_per_run}): ").strip()
            if max_posts:
                self.config.max_posts_per_run = int(max_posts)
            
            self.config.dry_run = input("Enable dry run mode? (y/n): ").lower() == 'y'
            
            print("\n✅ Settings updated!")


def main():
    """Main entry point"""
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║                                                                    ║
    ║         SISI LOLA MASTER AUTOMATION ORCHESTRATOR v1.0             ║
    ║                                                                    ║
    ║     Coordinating social media automation across 9 platforms       ║
    ║                                                                    ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Create orchestrator with default config
    config = OrchestrationConfig(
        auto_post_enabled=False,  # Safety: disabled by default
        dry_run=True,  # Safety: dry run by default
        post_interval_minutes=30,
        max_posts_per_run=5,
        enable_logging=True,
        log_level="INFO"
    )
    
    orchestrator = MasterAutomationOrchestrator(config)
    
    # Run interactive mode
    orchestrator.run_interactive_mode()


if __name__ == "__main__":
    main()
