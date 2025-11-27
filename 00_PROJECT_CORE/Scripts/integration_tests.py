#!/usr/bin/env python3
"""
Integration test suite for Sisi Lola Social Media Management System
Tests core workflows without requiring PIL/Pillow
"""

import sys
import unittest
from pathlib import Path
import json
import sqlite3
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules
from social_media_account_db import SocialMediaAccountDB, AccountStatus
from content_queue_manager import ContentQueueManager, ContentItem
from analytics_dashboard import AnalyticsDashboard, PlatformMetrics
from launch_readiness_validator import LaunchReadinessValidator


class TestAccountManagement(unittest.TestCase):
    """Test account database functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db = Path("test_accounts.db")
        if self.test_db.exists():
            self.test_db.unlink()
        self.db = SocialMediaAccountDB(self.test_db)
    
    def tearDown(self):
        """Clean up test database"""
        if self.test_db.exists():
            self.test_db.unlink()
    
    def test_database_creation(self):
        """Test database is created with correct tables"""
        self.assertTrue(self.test_db.exists())
        
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        self.assertIn('accounts', tables)
        self.assertIn('monetization_requirements', tables)
        self.assertIn('analytics', tables)
        self.assertIn('activity_log', tables)
    
    def test_seed_accounts(self):
        """Test seeding initial accounts"""
        self.db.seed_initial_accounts()
        
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM accounts")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 9)  # Should have 9 platforms
    
    def test_update_account_status(self):
        """Test updating account status"""
        self.db.seed_initial_accounts()
        self.db.update_account_status('Instagram', AccountStatus.CREATED)
        
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT account_status FROM accounts WHERE platform_name='Instagram'")
        status = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(status, 'created')
    
    def test_verification_tracking(self):
        """Test verification status tracking"""
        self.db.seed_initial_accounts()
        self.db.update_verification_status('YouTube', email_verified=True, phone_verified=True)
        
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT email_verified, phone_verified FROM accounts WHERE platform_name='YouTube'")
        email, phone = cursor.fetchone()
        conn.close()
        
        self.assertTrue(email)
        self.assertTrue(phone)
    
    def test_progress_tracking(self):
        """Test creation progress calculation"""
        self.db.seed_initial_accounts()
        self.db.update_account_status('Instagram', AccountStatus.CREATED)
        self.db.update_account_status('TikTok', AccountStatus.LIVE)
        
        progress = self.db.get_creation_progress()
        
        self.assertEqual(progress['total_accounts'], 9)
        self.assertEqual(progress['created_accounts'], 2)
        self.assertAlmostEqual(progress['progress_percentage'], 22.2, places=1)


class TestContentManagement(unittest.TestCase):
    """Test content queue functionality"""
    
    def setUp(self):
        """Set up test content queue"""
        self.test_queue = Path("test_content_queue.json")
        if self.test_queue.exists():
            self.test_queue.unlink()
        self.manager = ContentQueueManager(self.test_queue)
    
    def tearDown(self):
        """Clean up test files"""
        if self.test_queue.exists():
            self.test_queue.unlink()
    
    def test_add_content(self):
        """Test adding content items"""
        content = ContentItem(
            content_id="TEST001",
            title="Test Content",
            content_type="educational",
            platforms=["Instagram"],
            caption="Test caption"
        )
        
        self.manager.add_content(content)
        items = self.manager.get_all_content()
        
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['content_id'], "TEST001")
    
    def test_schedule_content(self):
        """Test scheduling content"""
        content = ContentItem(
            content_id="TEST002",
            title="Test Scheduled",
            content_type="entertainment",
            platforms=["TikTok"],
            caption="Test"
        )
        
        self.manager.add_content(content)
        self.manager.schedule_content("TEST002", datetime(2025, 12, 1), "10:00")
        
        items = self.manager.get_all_content()
        self.assertIsNotNone(items[0]['scheduled_date'])
        self.assertEqual(items[0]['scheduled_time'], "10:00")
    
    def test_content_mix_compliance(self):
        """Test content mix validation"""
        # Add content with proper mix
        for i in range(10):
            if i < 4:
                content_type = "educational"
            elif i < 7:
                content_type = "entertainment"
            elif i < 9:
                content_type = "community"
            else:
                content_type = "promotional"
            
            content = ContentItem(
                content_id=f"MIX{i:03d}",
                title=f"Mix Test {i}",
                content_type=content_type,
                platforms=["Instagram"],
                caption="Test",
                scheduled_date=datetime.now() + timedelta(days=i),
                scheduled_time="12:00"
            )
            self.manager.add_content(content)
        
        compliance = self.manager.check_content_mix_compliance(days=30)
        self.assertTrue(compliance['overall_compliant'])


class TestAnalyticsDashboard(unittest.TestCase):
    """Test analytics tracking"""
    
    def setUp(self):
        """Set up test analytics database"""
        self.test_db = Path("test_analytics.db")
        if self.test_db.exists():
            self.test_db.unlink()
        self.dashboard = AnalyticsDashboard(self.test_db)
    
    def tearDown(self):
        """Clean up test database"""
        if self.test_db.exists():
            self.test_db.unlink()
    
    def test_add_metrics(self):
        """Test adding daily metrics"""
        metrics = PlatformMetrics(
            platform="Instagram",
            date="2025-11-25",
            followers=1000,
            engagement_count=50,
            engagement_rate=5.0,
            impressions=10000
        )
        
        self.dashboard.add_daily_metrics(metrics)
        
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM daily_metrics")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 1)
    
    def test_growth_trends(self):
        """Test growth trend calculation"""
        # Add sequential data
        for i in range(30):
            metrics = PlatformMetrics(
                platform="TikTok",
                date=f"2025-11-{25-i:02d}" if 25-i > 0 else f"2025-10-{31-(i-25):02d}",
                followers=100 + (i * 10),
                engagement_count=10,
                engagement_rate=5.0,
                impressions=1000
            )
            self.dashboard.add_daily_metrics(metrics)
        
        trends = self.dashboard.get_growth_trends("TikTok", days=30)
        
        self.assertGreater(trends['follower_growth'], 0)
        self.assertEqual(trends['trend'], 'growing')
    
    def test_monetization_tracking(self):
        """Test monetization progress tracking"""
        self.dashboard.update_monetization_progress("Twitch", "followers", 45, 50)
        
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT current_value, requirement_met 
            FROM monetization_tracking 
            WHERE platform='Twitch' AND requirement_type='followers'
        """)
        current, met = cursor.fetchone()
        conn.close()
        
        self.assertEqual(current, 45)
        self.assertFalse(met)


class TestLaunchReadiness(unittest.TestCase):
    """Test launch readiness validation"""
    
    def setUp(self):
        """Set up test environment"""
        self.workspace = Path("test_workspace")
        self.workspace.mkdir(exist_ok=True)
        
        # Create minimal structure
        (self.workspace / "05_BRANDING_ARTIFACTS").mkdir(parents=True, exist_ok=True)
        (self.workspace / "03_MEDIA_ASSETS/content_queue").mkdir(parents=True, exist_ok=True)
        
        self.validator = LaunchReadinessValidator(self.workspace)
    
    def tearDown(self):
        """Clean up test workspace"""
        import shutil
        if self.workspace.exists():
            shutil.rmtree(self.workspace)
    
    def test_validator_initialization(self):
        """Test validator initializes correctly"""
        self.assertIsNotNone(self.validator)
        self.assertEqual(self.validator.workspace_root, self.workspace)
    
    def test_validation_categories(self):
        """Test all validation categories are checked"""
        # Create minimal files
        bio_file = self.workspace / "05_BRANDING_ARTIFACTS/BIO_TEMPLATES.md"
        bio_file.write_text("# Bio Templates\nTest content")
        
        content_file = self.workspace / "03_MEDIA_ASSETS/content_queue/content_queue.json"
        content_file.write_text("[]")
        
        summary = self.validator.validate_all()
        
        self.assertIn('total_checks', summary)
        self.assertIn('overall_percentage', summary)
        self.assertGreater(summary['total_checks'], 0)


class TestIntegration(unittest.TestCase):
    """Test complete workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path("integration_test")
        self.test_dir.mkdir(exist_ok=True)
        
        self.account_db = self.test_dir / "accounts.db"
        self.content_queue = self.test_dir / "content.json"
        self.analytics_db = self.test_dir / "analytics.db"
    
    def tearDown(self):
        """Clean up"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_complete_workflow(self):
        """Test complete account creation to analytics workflow"""
        # 1. Create account
        db = SocialMediaAccountDB(self.account_db)
        db.seed_initial_accounts()
        db.update_account_status('Instagram', AccountStatus.CREATED)
        db.update_verification_status('Instagram', email_verified=True)
        
        # 2. Add content
        manager = ContentQueueManager(self.content_queue)
        content = ContentItem(
            content_id="INT001",
            title="Integration Test",
            content_type="educational",
            platforms=["Instagram"],
            caption="Test",
            scheduled_date=datetime.now(),
            scheduled_time="12:00",
            status="published"
        )
        manager.add_content(content)
        
        # 3. Track analytics
        dashboard = AnalyticsDashboard(self.analytics_db)
        metrics = PlatformMetrics(
            platform="Instagram",
            date=datetime.now().strftime("%Y-%m-%d"),
            followers=100,
            posts_count=1,
            engagement_count=10,
            engagement_rate=10.0,
            impressions=1000
        )
        dashboard.add_daily_metrics(metrics)
        
        # 4. Verify workflow
        progress = db.get_creation_progress()
        content_items = manager.get_all_content()
        trends = dashboard.get_growth_trends("Instagram", days=1)
        
        self.assertGreater(progress['created_accounts'], 0)
        self.assertGreater(len(content_items), 0)
        self.assertIsNotNone(trends)


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("🧪 SISI LOLA SYSTEM INTEGRATION TESTS")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestAccountManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestContentManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyticsDashboard))
    suite.addTests(loader.loadTestsFromTestCase(TestLaunchReadiness))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
