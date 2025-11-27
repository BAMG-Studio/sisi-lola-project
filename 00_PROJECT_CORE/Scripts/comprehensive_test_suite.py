"""
Comprehensive Test Suite for Social Media Automation System
Tests all components end-to-end
"""

import sys
import unittest
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from social_media_account_db import SocialMediaAccountDB, AccountStatus
from automated_content_scheduler import AutomatedContentScheduler, ScheduledPost, ScheduleStatus, ContentType
from oauth_credential_manager import SecureCredentialManager, OAuthSetupWizard
from content_template_generator import ContentTemplateGenerator, ContentCategory
from unified_api_poster import UnifiedAPIPoster, PostContent, CredentialManager


class TestSocialMediaAccountDB(unittest.TestCase):
    """Test account database functionality"""
    
    def setUp(self):
        """Setup test database"""
        self.test_db_path = Path(__file__).parent / "test_accounts.db"
        self.db = SocialMediaAccountDB(str(self.test_db_path))
    
    def tearDown(self):
        """Cleanup test database"""
        if self.test_db_path.exists():
            self.test_db_path.unlink()
    
    def test_database_initialization(self):
        """Test database creation"""
        self.assertTrue(self.test_db_path.exists())
        
        # Verify tables exist
        conn = self.db.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.db.close()
        
        expected_tables = ['accounts', 'monetization_requirements', 'analytics', 'activity_log']
        for table in expected_tables:
            self.assertIn(table, tables)
    
    def test_seed_accounts(self):
        """Test account seeding"""
        self.db.seed_initial_accounts()
        
        accounts = self.db.get_all_accounts()
        self.assertEqual(len(accounts), 9)  # 6 global + 3 African
        
        # Verify platform types
        global_platforms = self.db.get_all_accounts(platform_type='global')
        african_platforms = self.db.get_all_accounts(platform_type='african')
        
        self.assertEqual(len(global_platforms), 6)
        self.assertEqual(len(african_platforms), 3)
    
    def test_update_account_status(self):
        """Test status updates"""
        self.db.seed_initial_accounts()
        
        # Update YouTube status
        success = self.db.update_account_status('YouTube', AccountStatus.CREATED)
        self.assertTrue(success)
        
        # Verify update
        account = self.db.get_account('YouTube')
        self.assertEqual(account['account_status'], AccountStatus.CREATED.value)
    
    def test_monetization_tracking(self):
        """Test monetization requirement tracking"""
        self.db.seed_initial_accounts()
        self.db.seed_monetization_requirements()
        
        # Update Twitch progress
        success = self.db.update_monetization_progress('Twitch', 'followers', 45)
        self.assertTrue(success)
        
        # Get status
        status = self.db.get_monetization_status('Twitch')
        self.assertEqual(status['platform'], 'Twitch')
        self.assertTrue(len(status['requirements']) > 0)


class TestAutomatedContentScheduler(unittest.TestCase):
    """Test content scheduler"""
    
    def setUp(self):
        """Setup test scheduler"""
        self.test_db_path = Path(__file__).parent / "test_schedule.db"
        self.scheduler = AutomatedContentScheduler(str(self.test_db_path))
    
    def tearDown(self):
        """Cleanup"""
        if self.test_db_path.exists():
            self.test_db_path.unlink()
    
    def test_add_post(self):
        """Test adding posts to schedule"""
        post = ScheduledPost(
            title="Test Post",
            caption="This is a test post",
            content_type=ContentType.EDUCATIONAL.value,
            platforms=['YouTube', 'Instagram'],
            priority=7
        )
        
        post_id = self.scheduler.add_post(post, auto_schedule=True)
        self.assertIsNotNone(post_id)
        self.assertGreater(post_id, 0)
    
    def test_get_pending_posts(self):
        """Test retrieving pending posts"""
        # Add multiple posts
        for i in range(5):
            post = ScheduledPost(
                title=f"Test Post {i}",
                caption=f"Content {i}",
                content_type=ContentType.EDUCATIONAL.value,
                platforms=['YouTube'],
                priority=i
            )
            self.scheduler.add_post(post, auto_schedule=True)
        
        pending = self.scheduler.get_pending_posts()
        self.assertEqual(len(pending), 5)
    
    def test_content_mix_calculation(self):
        """Test content mix compliance"""
        # Add posts with different types
        content_types = [
            ContentType.EDUCATIONAL.value,
            ContentType.EDUCATIONAL.value,
            ContentType.ENTERTAINMENT.value,
            ContentType.COMMUNITY.value
        ]
        
        for i, content_type in enumerate(content_types):
            post = ScheduledPost(
                title=f"Post {i}",
                caption="Test",
                content_type=content_type,
                platforms=['YouTube']
            )
            self.scheduler.add_post(post, auto_schedule=True)
        
        mix = self.scheduler.get_content_mix_current()
        self.assertIn(ContentType.EDUCATIONAL.value, mix)
        self.assertEqual(mix[ContentType.EDUCATIONAL.value], 0.5)  # 2/4 = 50%
    
    def test_schedule_export(self):
        """Test calendar export"""
        # Add posts
        for i in range(3):
            post = ScheduledPost(
                title=f"Export Test {i}",
                caption="Export test",
                content_type=ContentType.EDUCATIONAL.value,
                platforms=['YouTube']
            )
            self.scheduler.add_post(post, auto_schedule=True)
        
        export_path = self.scheduler.export_calendar()
        self.assertTrue(export_path.exists())
        
        # Cleanup
        export_path.unlink()


class TestOAuthCredentialManager(unittest.TestCase):
    """Test credential management"""
    
    def setUp(self):
        """Setup test credentials"""
        self.test_creds_path = Path(__file__).parent / "test_credentials.json"
        self.manager = SecureCredentialManager(str(self.test_creds_path))
    
    def tearDown(self):
        """Cleanup"""
        if self.test_creds_path.exists():
            self.test_creds_path.unlink()
    
    def test_credential_loading(self):
        """Test loading credentials from environment"""
        # Credentials should be loaded (or empty)
        creds = self.manager.get('youtube')
        self.assertIsNotNone(creds)
    
    def test_credential_setting(self):
        """Test setting credentials"""
        self.manager.set('youtube', 
                        client_id='test_client_id',
                        client_secret='test_secret')
        
        creds = self.manager.get('youtube')
        self.assertEqual(creds.client_id, 'test_client_id')
    
    def test_credential_persistence(self):
        """Test saving and loading credentials"""
        self.manager.set('instagram',
                        access_token='test_token',
                        business_account_id='123456')
        
        self.manager.save_credentials()
        
        # Create new manager and verify it loads saved data
        new_manager = SecureCredentialManager(str(self.test_creds_path))
        creds = new_manager.get('instagram')
        
        self.assertEqual(creds.access_token, 'test_token')
    
    def test_validation(self):
        """Test credential validation"""
        # Initially should fail (no creds)
        validation = self.manager.validate_all()
        
        # Set some credentials
        self.manager.set('reddit',
                        client_id='test',
                        client_secret='test')
        
        # Validation should still show status
        self.assertIsInstance(validation, dict)


class TestContentTemplateGenerator(unittest.TestCase):
    """Test content generation"""
    
    def setUp(self):
        """Setup generator"""
        self.generator = ContentTemplateGenerator()
    
    def test_template_loading(self):
        """Test templates are loaded"""
        self.assertGreater(len(self.generator.templates), 0)
        self.assertIn(ContentCategory.TECH_INNOVATION.value, self.generator.templates)
    
    def test_single_content_generation(self):
        """Test generating single content piece"""
        content = self.generator.generate(
            category=ContentCategory.TECH_INNOVATION.value,
            topic="Test Topic",
            description="Test description",
            platforms=['YouTube', 'Instagram']
        )
        
        self.assertIn('YouTube', content)
        self.assertIn('Instagram', content)
        
        # Verify structure
        youtube_content = content['YouTube']
        self.assertIn('title', youtube_content)
        self.assertIn('caption', youtube_content)
        self.assertIn('hashtags', youtube_content)
    
    def test_batch_generation(self):
        """Test batch content generation"""
        batch = self.generator.generate_batch(count=10)
        
        self.assertEqual(len(batch), 10)
        
        # Verify structure
        for item in batch:
            self.assertIn('category', item)
            self.assertIn('topic', item)
            self.assertIn('platform_content', item)
    
    def test_platform_optimization(self):
        """Test platform-specific optimization"""
        from content_template_generator import PlatformOptimizer
        
        # Test caption optimization
        long_caption = "A" * 3000
        optimized = PlatformOptimizer.optimize_caption(long_caption, 'TikTok')
        
        self.assertLessEqual(len(optimized), 150)
        
        # Test hashtag optimization
        many_hashtags = [f'tag{i}' for i in range(50)]
        optimized = PlatformOptimizer.optimize_hashtags(many_hashtags, 'TikTok')
        
        self.assertEqual(len(optimized), 5)


class TestUnifiedAPIPoster(unittest.TestCase):
    """Test API posting system"""
    
    def setUp(self):
        """Setup poster"""
        self.poster = UnifiedAPIPoster()
    
    def test_credential_manager_integration(self):
        """Test credential manager"""
        self.assertIsNotNone(self.poster.creds)
    
    def test_post_content_creation(self):
        """Test creating PostContent objects"""
        content = PostContent(
            title="Test Post",
            caption="This is a test",
            media_type="video",
            tags=['test', 'automation'],
            hashtags=['TestTag', 'AutomationTag']
        )
        
        self.assertEqual(content.title, "Test Post")
        self.assertEqual(len(content.tags), 2)
    
    def test_platform_routing(self):
        """Test platform routing (dry run)"""
        content = PostContent(
            title="Test",
            caption="Test caption",
            media_type="text"
        )
        
        # Test manual platforms (should return instructions)
        result = self.poster._post_to_vumistream(content)
        self.assertFalse(result.success)  # Manual posting required
        self.assertIn("Manual posting required", result.error_message)


class TestIntegrationWorkflow(unittest.TestCase):
    """Test complete workflow integration"""
    
    def setUp(self):
        """Setup all components"""
        test_dir = Path(__file__).parent / "test_integration"
        test_dir.mkdir(exist_ok=True)
        
        self.account_db = SocialMediaAccountDB(str(test_dir / "accounts.db"))
        self.scheduler = AutomatedContentScheduler(str(test_dir / "schedule.db"))
        self.generator = ContentTemplateGenerator()
        
        self.test_dir = test_dir
    
    def tearDown(self):
        """Cleanup"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow: generate → schedule → track"""
        # Step 1: Seed accounts
        self.account_db.seed_initial_accounts()
        accounts = self.account_db.get_all_accounts()
        self.assertEqual(len(accounts), 9)
        
        # Step 2: Generate content
        batch = self.generator.generate_batch(count=5)
        self.assertEqual(len(batch), 5)
        
        # Step 3: Schedule content
        for item in batch:
            post = ScheduledPost(
                title=item['topic'],
                caption=item['description'],
                content_type=item['category'],
                platforms=['YouTube', 'Instagram']
            )
            post_id = self.scheduler.add_post(post, auto_schedule=True)
            self.assertIsNotNone(post_id)
        
        # Step 4: Verify scheduled
        pending = self.scheduler.get_pending_posts()
        self.assertEqual(len(pending), 5)
        
        # Step 5: Check content mix
        compliance = self.scheduler.check_content_mix_compliance()
        self.assertIn('compliant', compliance)


def run_all_tests():
    """Run all test suites"""
    print("="*70)
    print("RUNNING COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSocialMediaAccountDB))
    suite.addTests(loader.loadTestsFromTestCase(TestAutomatedContentScheduler))
    suite.addTests(loader.loadTestsFromTestCase(TestOAuthCredentialManager))
    suite.addTests(loader.loadTestsFromTestCase(TestContentTemplateGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedAPIPoster))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWorkflow))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    failed = len(result.failures)
    errs = len(result.errors)
    success_pct = (passed / total * 100) if total else 0.0

    print(f"Tests run: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errs}")
    print(f"Success rate: {success_pct:.1f}%")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
