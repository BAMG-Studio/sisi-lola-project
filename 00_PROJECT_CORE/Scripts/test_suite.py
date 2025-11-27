"""
Comprehensive Test Suite for Sisi Lola Social Media Management System
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from social_media_account_db import (
    SocialMediaAccountDB, AccountStatus, MonetizationStatus, 
    SocialMediaAccount, PlatformType
)
from profile_image_validator import ProfileImageValidator, ImageSpec
from content_queue_manager import (
    ContentQueueManager, ContentItem, ContentType, ContentStatus
)
from analytics_dashboard import AnalyticsDashboard, PlatformMetrics


class TestSocialMediaAccountDB(unittest.TestCase):
    """Test account database functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.db_path = self.test_dir / "test_accounts.db"
        self.db = SocialMediaAccountDB(str(self.db_path))
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_database_initialization(self):
        """Test database is created with correct tables"""
        self.assertTrue(self.db_path.exists())
        
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn('accounts', tables)
        self.assertIn('monetization_requirements', tables)
        self.assertIn('analytics', tables)
        self.assertIn('activity_log', tables)
        
        self.db.close()
    
    def test_seed_initial_accounts(self):
        """Test seeding initial account data"""
        self.db.seed_initial_accounts()
        
        accounts = self.db.get_all_accounts()
        self.assertEqual(len(accounts), 9)  # 9 platforms
        
        # Check specific platforms exist
        youtube = self.db.get_account('YouTube')
        self.assertIsNotNone(youtube)
        self.assertEqual(youtube['username'], '@sisilola')
        
        vumistream = self.db.get_account('Vumistream')
        self.assertIsNotNone(vumistream)
        self.assertEqual(vumistream['platform_type'], PlatformType.AFRICAN.value)
    
    def test_update_account_status(self):
        """Test updating account status"""
        self.db.seed_initial_accounts()
        
        success = self.db.update_account_status('YouTube', AccountStatus.CREATED)
        self.assertTrue(success)
        
        account = self.db.get_account('YouTube')
        self.assertEqual(account['account_status'], AccountStatus.CREATED.value)
    
    def test_update_verification_status(self):
        """Test updating verification statuses"""
        self.db.seed_initial_accounts()
        
        success = self.db.update_verification_status(
            'Instagram',
            email_verified=True,
            two_fa_enabled=True
        )
        self.assertTrue(success)
        
        account = self.db.get_account('Instagram')
        self.assertTrue(account['email_verified'])
        self.assertTrue(account['two_fa_enabled'])
    
    def test_get_creation_progress(self):
        """Test getting overall creation progress"""
        self.db.seed_initial_accounts()
        
        # Mark some as created
        self.db.update_account_status('YouTube', AccountStatus.VERIFIED)
        self.db.update_account_status('Instagram', AccountStatus.VERIFIED)
        
        progress = self.db.get_creation_progress()
        
        self.assertEqual(progress['total_accounts'], 9)
        self.assertEqual(progress['created_accounts'], 2)
        self.assertGreater(progress['progress_percentage'], 0)
    
    def test_monetization_requirements(self):
        """Test monetization requirements tracking"""
        self.db.seed_initial_accounts()
        self.db.seed_monetization_requirements()
        
        status = self.db.get_monetization_status('TikTok')
        
        self.assertEqual(status['platform'], 'TikTok')
        self.assertGreater(len(status['requirements']), 0)
        
        # Update progress
        success = self.db.update_monetization_progress('TikTok', 'followers', 5000)
        self.assertTrue(success)


class TestProfileImageValidator(unittest.TestCase):
    """Test image validation and processing"""
    
    def setUp(self):
        """Set up validator"""
        self.validator = ProfileImageValidator()
    
    def test_specs_loaded(self):
        """Test specifications are loaded"""
        self.assertGreater(len(self.validator.SPECS), 0)
        
        # Check specific spec exists
        self.assertIn('YouTube_profile', self.validator.specs_dict)
        self.assertIn('YouTube_banner', self.validator.specs_dict)
    
    def test_image_spec_structure(self):
        """Test ImageSpec data structure"""
        spec = self.validator.specs_dict['YouTube_profile']
        
        self.assertEqual(spec.platform, 'YouTube')
        self.assertEqual(spec.image_type, 'profile')
        self.assertEqual(spec.width, 800)
        self.assertEqual(spec.height, 800)
        self.assertTrue(spec.circular_crop)
    
    def test_banner_specs(self):
        """Test banner specifications"""
        youtube_banner = self.validator.specs_dict['YouTube_banner']
        
        self.assertEqual(youtube_banner.width, 2560)
        self.assertEqual(youtube_banner.height, 1440)
        self.assertIsNotNone(youtube_banner.safe_area)


class TestContentQueueManager(unittest.TestCase):
    """Test content queue management"""
    
    def setUp(self):
        """Set up content manager"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.manager = ContentQueueManager(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_add_content(self):
        """Test adding content to queue"""
        content = ContentItem(
            content_id="TEST001",
            title="Test Content",
            content_type=ContentType.EDUCATIONAL.value,
            platforms=["Instagram", "TikTok"],
            caption="Test caption"
        )
        
        success = self.manager.add_content(content)
        self.assertTrue(success)
        
        # Try adding duplicate
        success = self.manager.add_content(content)
        self.assertFalse(success)
    
    def test_update_content(self):
        """Test updating content"""
        content = ContentItem(
            content_id="TEST002",
            title="Original Title",
            content_type=ContentType.EDUCATIONAL.value,
            platforms=["Instagram"]
        )
        
        self.manager.add_content(content)
        
        success = self.manager.update_content(
            "TEST002",
            title="Updated Title",
            status=ContentStatus.READY.value
        )
        self.assertTrue(success)
        
        updated = self.manager.get_content("TEST002")
        self.assertEqual(updated.title, "Updated Title")
        self.assertEqual(updated.status, ContentStatus.READY.value)
    
    def test_get_by_status(self):
        """Test filtering by status"""
        self.manager.add_content(ContentItem(
            content_id="READY001",
            title="Ready Content",
            content_type=ContentType.EDUCATIONAL.value,
            platforms=["Instagram"],
            status=ContentStatus.READY.value
        ))
        
        self.manager.add_content(ContentItem(
            content_id="PLANNED001",
            title="Planned Content",
            content_type=ContentType.EDUCATIONAL.value,
            platforms=["Instagram"],
            status=ContentStatus.PLANNED.value
        ))
        
        ready = self.manager.get_by_status(ContentStatus.READY)
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0].content_id, "READY001")
    
    def test_schedule_content(self):
        """Test scheduling content"""
        content = ContentItem(
            content_id="SCHEDULE001",
            title="To Schedule",
            content_type=ContentType.EDUCATIONAL.value,
            platforms=["Instagram"]
        )
        
        self.manager.add_content(content)
        
        schedule_date = datetime.now() + timedelta(days=1)
        success = self.manager.schedule_content("SCHEDULE001", schedule_date, "14:00")
        self.assertTrue(success)
        
        scheduled = self.manager.get_content("SCHEDULE001")
        self.assertEqual(scheduled.status, ContentStatus.SCHEDULED.value)
        self.assertIsNotNone(scheduled.scheduled_date)
    
    def test_content_mix_stats(self):
        """Test content mix statistics"""
        # Add varied content
        for i in range(4):
            self.manager.add_content(ContentItem(
                content_id=f"EDU{i}",
                title=f"Educational {i}",
                content_type=ContentType.EDUCATIONAL.value,
                platforms=["Instagram"],
                scheduled_date=(datetime.now() + timedelta(days=i)).isoformat(),
                status=ContentStatus.SCHEDULED.value
            ))
        
        for i in range(3):
            self.manager.add_content(ContentItem(
                content_id=f"ENT{i}",
                title=f"Entertainment {i}",
                content_type=ContentType.ENTERTAINMENT.value,
                platforms=["TikTok"],
                scheduled_date=(datetime.now() + timedelta(days=i)).isoformat(),
                status=ContentStatus.SCHEDULED.value
            ))
        
        stats = self.manager.get_content_mix_stats(7)
        
        self.assertEqual(stats['total_scheduled'], 7)
        self.assertEqual(stats['by_type'][ContentType.EDUCATIONAL.value], 4)
        self.assertEqual(stats['by_type'][ContentType.ENTERTAINMENT.value], 3)
    
    def test_content_mix_compliance(self):
        """Test content mix compliance checking"""
        compliance = self.manager.check_content_mix_compliance(7)
        
        self.assertIn('overall_compliant', compliance)
        self.assertIn('by_type', compliance)


class TestAnalyticsDashboard(unittest.TestCase):
    """Test analytics dashboard"""
    
    def setUp(self):
        """Set up analytics dashboard"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.db_path = self.test_dir / "test_analytics.db"
        self.dashboard = AnalyticsDashboard(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_add_daily_metrics(self):
        """Test adding daily metrics"""
        metrics = PlatformMetrics(
            platform="Instagram",
            date="2025-11-25",
            followers=1000,
            engagement_count=50,
            engagement_rate=5.0
        )
        
        success = self.dashboard.add_daily_metrics(metrics)
        self.assertTrue(success)
        
        # Retrieve and verify
        retrieved = self.dashboard.get_platform_metrics("Instagram", 1)
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0]['followers'], 1000)
    
    def test_growth_trends(self):
        """Test growth trend calculation"""
        # Add metrics for 5 days
        for i in range(5):
            date = (datetime.now() - timedelta(days=4-i)).strftime('%Y-%m-%d')
            metrics = PlatformMetrics(
                platform="TikTok",
                date=date,
                followers=100 + (i * 10)  # Growing by 10 each day
            )
            self.dashboard.add_daily_metrics(metrics)
        
        trends = self.dashboard.get_growth_trends("TikTok", 5)
        
        self.assertEqual(trends['follower_growth'], 40)
        self.assertEqual(trends['trend'], 'growing')
        self.assertAlmostEqual(trends['avg_daily_growth'], 8.0)
    
    def test_monetization_progress(self):
        """Test monetization progress tracking"""
        self.dashboard.update_monetization_progress(
            "YouTube",
            "subscribers",
            500,
            1000
        )
        
        status = self.dashboard.get_monetization_status()
        
        self.assertIn('YouTube', status)
        youtube_metrics = status['YouTube']
        
        subscriber_metric = next(
            (m for m in youtube_metrics if m['metric'] == 'subscribers'),
            None
        )
        
        self.assertIsNotNone(subscriber_metric)
        self.assertEqual(subscriber_metric['current'], 500)
        self.assertEqual(subscriber_metric['percentage'], 50.0)
    
    def test_all_platforms_summary(self):
        """Test getting summary for all platforms"""
        date = "2025-11-25"
        
        for platform in ['Instagram', 'TikTok', 'YouTube']:
            metrics = PlatformMetrics(
                platform=platform,
                date=date,
                followers=1000,
                engagement_count=50
            )
            self.dashboard.add_daily_metrics(metrics)
        
        summary = self.dashboard.get_all_platforms_summary(date)
        
        self.assertEqual(summary['total_followers'], 3000)
        self.assertEqual(summary['total_engagement'], 150)
        self.assertEqual(len(summary['by_platform']), 3)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up all components"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.account_db = SocialMediaAccountDB(self.test_dir / "accounts.db")
        self.content_manager = ContentQueueManager(self.test_dir / "content")
        self.analytics = AnalyticsDashboard(self.test_dir / "analytics.db")
        self.validator = ProfileImageValidator()
    
    def tearDown(self):
        """Clean up"""
        self.account_db.close()
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_full_workflow(self):
        """Test complete workflow from account creation to analytics"""
        # 1. Set up accounts
        self.account_db.seed_initial_accounts()
        accounts = self.account_db.get_all_accounts()
        self.assertGreater(len(accounts), 0)
        
        # 2. Create account
        self.account_db.update_account_status('Instagram', AccountStatus.CREATED)
        self.account_db.update_verification_status('Instagram', email_verified=True)
        
        # 3. Add content
        content = ContentItem(
            content_id="INT001",
            title="Integration Test Post",
            content_type=ContentType.EDUCATIONAL.value,
            platforms=["Instagram"],
            status=ContentStatus.READY.value
        )
        self.content_manager.add_content(content)
        
        # 4. Schedule content
        schedule_date = datetime.now() + timedelta(days=1)
        self.content_manager.schedule_content("INT001", schedule_date)
        
        # 5. Add analytics
        metrics = PlatformMetrics(
            platform="Instagram",
            date=datetime.now().strftime('%Y-%m-%d'),
            followers=500,
            posts_count=1
        )
        self.analytics.add_daily_metrics(metrics)
        
        # 6. Verify everything works together
        account = self.account_db.get_account('Instagram')
        self.assertEqual(account['account_status'], AccountStatus.CREATED.value)
        
        scheduled = self.content_manager.get_by_status(ContentStatus.SCHEDULED)
        self.assertEqual(len(scheduled), 1)
        
        analytics_data = self.analytics.get_platform_metrics("Instagram", 1)
        self.assertEqual(len(analytics_data), 1)


def run_all_tests():
    """Run all test suites"""
    print("=" * 70)
    print("SISI LOLA SOCIAL MEDIA MANAGEMENT SYSTEM - TEST SUITE")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSocialMediaAccountDB))
    suite.addTests(loader.loadTestsFromTestCase(TestProfileImageValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestContentQueueManager))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyticsDashboard))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED!")
    else:
        print("✗ SOME TESTS FAILED")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
