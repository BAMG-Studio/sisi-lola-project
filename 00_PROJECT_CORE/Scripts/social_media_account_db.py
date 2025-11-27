"""
Sisi Lola Social Media Account Management System
Database schema and models for tracking all social media accounts
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class AccountStatus(Enum):
    """Account creation status"""
    NOT_CREATED = "not_created"
    CREATED = "created"
    VERIFIED = "verified"
    CONFIGURED = "configured"
    LIVE = "live"


class MonetizationStatus(Enum):
    """Monetization eligibility status"""
    NOT_ELIGIBLE = "not_eligible"
    IN_PROGRESS = "in_progress"
    ELIGIBLE = "eligible"
    ENABLED = "enabled"


class PlatformType(Enum):
    """Platform categorization"""
    GLOBAL = "global"
    AFRICAN = "african"


@dataclass
class SocialMediaAccount:
    """Social media account data model"""
    platform_name: str
    platform_type: str  # global or african
    email: str
    username: str
    display_name: str
    profile_url: Optional[str] = None
    account_status: str = AccountStatus.NOT_CREATED.value
    email_verified: bool = False
    phone_verified: bool = False
    two_fa_enabled: bool = False
    bio: Optional[str] = None
    profile_picture_uploaded: bool = False
    banner_uploaded: bool = False
    created_date: Optional[str] = None
    last_updated: Optional[str] = None
    monetization_status: str = MonetizationStatus.NOT_ELIGIBLE.value
    followers: int = 0
    notes: Optional[str] = None


@dataclass
class MonetizationRequirement:
    """Monetization requirements for each platform"""
    platform_name: str
    requirement_type: str
    requirement_value: int
    current_value: int = 0
    requirement_met: bool = False
    estimated_timeline_days: Optional[int] = None


class SocialMediaAccountDB:
    """Database manager for social media accounts"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_path = Path(__file__).parent.parent
            db_path = base_path / "05_BRANDING_ARTIFACTS" / "sisi_lola_accounts.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.initialize_database()
    
    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def initialize_database(self):
        """Create database tables"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform_name TEXT UNIQUE NOT NULL,
                platform_type TEXT NOT NULL,
                email TEXT NOT NULL,
                username TEXT NOT NULL,
                display_name TEXT NOT NULL,
                profile_url TEXT,
                account_status TEXT DEFAULT 'not_created',
                email_verified BOOLEAN DEFAULT 0,
                phone_verified BOOLEAN DEFAULT 0,
                two_fa_enabled BOOLEAN DEFAULT 0,
                bio TEXT,
                profile_picture_uploaded BOOLEAN DEFAULT 0,
                banner_uploaded BOOLEAN DEFAULT 0,
                created_date TEXT,
                last_updated TEXT,
                monetization_status TEXT DEFAULT 'not_eligible',
                followers INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # Monetization requirements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monetization_requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform_name TEXT NOT NULL,
                requirement_type TEXT NOT NULL,
                requirement_value INTEGER NOT NULL,
                current_value INTEGER DEFAULT 0,
                requirement_met BOOLEAN DEFAULT 0,
                estimated_timeline_days INTEGER,
                last_updated TEXT,
                FOREIGN KEY (platform_name) REFERENCES accounts(platform_name)
            )
        ''')
        
        # Analytics tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform_name TEXT NOT NULL,
                date TEXT NOT NULL,
                followers INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                posts_count INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                reach INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                FOREIGN KEY (platform_name) REFERENCES accounts(platform_name)
            )
        ''')
        
        # Activity log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform_name TEXT,
                activity_type TEXT NOT NULL,
                activity_description TEXT,
                timestamp TEXT NOT NULL,
                status TEXT
            )
        ''')
        
        conn.commit()
        self.close()
    
    def seed_initial_accounts(self):
        """Populate database with initial account data"""
        accounts = [
            # Global Platforms
            SocialMediaAccount(
                platform_name="YouTube",
                platform_type=PlatformType.GLOBAL.value,
                email="youtube_sisilola+seun.beaconagilelogix@gmail.com",
                username="@sisilola",
                display_name="Sisi Lola",
                bio="AI-powered voice celebrating African culture, innovation, and community."
            ),
            SocialMediaAccount(
                platform_name="Instagram",
                platform_type=PlatformType.GLOBAL.value,
                email="instagram_sisilola+seun.beaconagilelogix@gmail.com",
                username="@sisilola",
                display_name="Sisi Lola",
                bio="🌍 AI Voice of African Culture\n✨ Celebrating heritage, innovation & community"
            ),
            SocialMediaAccount(
                platform_name="TikTok",
                platform_type=PlatformType.GLOBAL.value,
                email="tiktok_sisilola+seun.beaconagilelogix@gmail.com",
                username="@sisilola",
                display_name="Sisi Lola",
                bio="AI Voice of Africa 🌍 | Celebrating Culture & Innovation ✨"
            ),
            SocialMediaAccount(
                platform_name="Facebook",
                platform_type=PlatformType.GLOBAL.value,
                email="facebook_sisilola+seun.beaconagilelogix@gmail.com",
                username="@SisiLolaOfficial",
                display_name="Sisi Lola",
                bio="AI-Powered Voice of African Culture 🌍"
            ),
            SocialMediaAccount(
                platform_name="Twitch",
                platform_type=PlatformType.GLOBAL.value,
                email="twitch_sisilola+seun.beaconagilelogix@gmail.com",
                username="sisilola",
                display_name="Sisi Lola",
                bio="AI-powered creator celebrating African culture"
            ),
            SocialMediaAccount(
                platform_name="Reddit",
                platform_type=PlatformType.GLOBAL.value,
                email="reddit_sisilola+seun.beaconagilelogix@gmail.com",
                username="sisilola",
                display_name="Sisi Lola",
                bio="AI advocate for African culture and innovation 🌍"
            ),
            
            # African Platforms
            SocialMediaAccount(
                platform_name="Vumistream",
                platform_type=PlatformType.AFRICAN.value,
                email="vumistream_sisilola+seun.beaconagilelogix@gmail.com",
                username="sisilola",
                display_name="Sisi Lola",
                bio="AI Voice of Africa! 🌍 Live streaming culture, innovation & community",
                monetization_status=MonetizationStatus.ELIGIBLE.value
            ),
            SocialMediaAccount(
                platform_name="Twiva",
                platform_type=PlatformType.AFRICAN.value,
                email="twiva_sisilola+seun.beaconagilelogix@gmail.com",
                username="sisilola",
                display_name="Sisi Lola",
                bio="African culture meets innovation! Supporting African businesses",
                monetization_status=MonetizationStatus.ELIGIBLE.value
            ),
            SocialMediaAccount(
                platform_name="Wowzi",
                platform_type=PlatformType.AFRICAN.value,
                email="wowzi_sisilola+seun.beaconagilelogix@gmail.com",
                username="sisilola",
                display_name="Sisi Lola",
                bio="AI-powered African influencer partnering with brands"
            ),
        ]
        
        conn = self.connect()
        cursor = conn.cursor()
        
        for account in accounts:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO accounts (
                        platform_name, platform_type, email, username, display_name,
                        bio, account_status, monetization_status, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    account.platform_name,
                    account.platform_type,
                    account.email,
                    account.username,
                    account.display_name,
                    account.bio,
                    account.account_status,
                    account.monetization_status,
                    datetime.now().isoformat()
                ))
            except sqlite3.IntegrityError:
                pass  # Account already exists
        
        conn.commit()
        self.close()
    
    def seed_monetization_requirements(self):
        """Populate monetization requirements"""
        requirements = [
            # TikTok
            MonetizationRequirement("TikTok", "followers", 10000, estimated_timeline_days=90),
            MonetizationRequirement("TikTok", "views_30_days", 100000, estimated_timeline_days=90),
            
            # YouTube
            MonetizationRequirement("YouTube", "subscribers", 1000, estimated_timeline_days=120),
            MonetizationRequirement("YouTube", "watch_hours_12_months", 4000, estimated_timeline_days=120),
            
            # Instagram
            MonetizationRequirement("Instagram", "followers_for_brands", 10000, estimated_timeline_days=120),
            
            # Facebook
            MonetizationRequirement("Facebook", "page_followers", 10000, estimated_timeline_days=150),
            MonetizationRequirement("Facebook", "watch_minutes", 600000, estimated_timeline_days=150),
            
            # Twitch
            MonetizationRequirement("Twitch", "followers", 50, estimated_timeline_days=30),
            MonetizationRequirement("Twitch", "stream_hours", 8, estimated_timeline_days=14),
            MonetizationRequirement("Twitch", "stream_days", 7, estimated_timeline_days=14),
            MonetizationRequirement("Twitch", "avg_concurrent_viewers", 3, estimated_timeline_days=30),
        ]
        
        conn = self.connect()
        cursor = conn.cursor()
        
        for req in requirements:
            cursor.execute('''
                INSERT OR IGNORE INTO monetization_requirements (
                    platform_name, requirement_type, requirement_value,
                    current_value, estimated_timeline_days, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                req.platform_name,
                req.requirement_type,
                req.requirement_value,
                req.current_value,
                req.estimated_timeline_days,
                datetime.now().isoformat()
            ))
        
        conn.commit()
        self.close()
    
    def update_account_status(self, platform_name: str, status: AccountStatus) -> bool:
        """Update account creation status"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE accounts 
            SET account_status = ?, last_updated = ?
            WHERE platform_name = ?
        ''', (status.value, datetime.now().isoformat(), platform_name))
        
        success = cursor.rowcount > 0
        conn.commit()
        self.close()
        
        # Log activity
        if success:
            self.log_activity(
                platform_name,
                "status_update",
                f"Account status updated to {status.value}"
            )
        
        return success
    
    def update_verification_status(self, platform_name: str, 
                                   email_verified: bool = None,
                                   phone_verified: bool = None,
                                   two_fa_enabled: bool = None) -> bool:
        """Update verification statuses"""
        conn = self.connect()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if email_verified is not None:
            updates.append("email_verified = ?")
            params.append(email_verified)
        if phone_verified is not None:
            updates.append("phone_verified = ?")
            params.append(phone_verified)
        if two_fa_enabled is not None:
            updates.append("two_fa_enabled = ?")
            params.append(two_fa_enabled)
        
        if not updates:
            return False
        
        updates.append("last_updated = ?")
        params.append(datetime.now().isoformat())
        params.append(platform_name)
        
        query = f"UPDATE accounts SET {', '.join(updates)} WHERE platform_name = ?"
        cursor.execute(query, params)
        
        success = cursor.rowcount > 0
        conn.commit()
        self.close()
        
        return success
    
    def update_profile_assets(self, platform_name: str,
                            profile_picture: bool = None,
                            banner: bool = None) -> bool:
        """Update profile asset upload status"""
        conn = self.connect()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if profile_picture is not None:
            updates.append("profile_picture_uploaded = ?")
            params.append(profile_picture)
        if banner is not None:
            updates.append("banner_uploaded = ?")
            params.append(banner)
        
        if not updates:
            return False
        
        updates.append("last_updated = ?")
        params.append(datetime.now().isoformat())
        params.append(platform_name)
        
        query = f"UPDATE accounts SET {', '.join(updates)} WHERE platform_name = ?"
        cursor.execute(query, params)
        
        success = cursor.rowcount > 0
        conn.commit()
        self.close()
        
        return success
    
    def update_metrics(self, platform_name: str, followers: int = None, **kwargs) -> bool:
        """Update account metrics"""
        conn = self.connect()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if followers is not None:
            updates.append("followers = ?")
            params.append(followers)
        
        updates.append("last_updated = ?")
        params.append(datetime.now().isoformat())
        params.append(platform_name)
        
        query = f"UPDATE accounts SET {', '.join(updates)} WHERE platform_name = ?"
        cursor.execute(query, params)
        
        success = cursor.rowcount > 0
        conn.commit()
        self.close()
        
        return success
    
    def update_monetization_progress(self, platform_name: str, 
                                    requirement_type: str,
                                    current_value: int) -> bool:
        """Update monetization requirement progress"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get requirement value
        cursor.execute('''
            SELECT requirement_value FROM monetization_requirements
            WHERE platform_name = ? AND requirement_type = ?
        ''', (platform_name, requirement_type))
        
        row = cursor.fetchone()
        if not row:
            self.close()
            return False
        
        requirement_value = row[0]
        requirement_met = current_value >= requirement_value
        
        cursor.execute('''
            UPDATE monetization_requirements
            SET current_value = ?, requirement_met = ?, last_updated = ?
            WHERE platform_name = ? AND requirement_type = ?
        ''', (current_value, requirement_met, datetime.now().isoformat(),
              platform_name, requirement_type))
        
        success = cursor.rowcount > 0
        conn.commit()
        self.close()
        
        return success
    
    def log_activity(self, platform_name: str, activity_type: str,
                    description: str, status: str = "success"):
        """Log activity"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO activity_log (platform_name, activity_type, 
                                     activity_description, timestamp, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (platform_name, activity_type, description, 
              datetime.now().isoformat(), status))
        
        conn.commit()
        self.close()
    
    def get_account(self, platform_name: str) -> Optional[Dict]:
        """Get account details"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM accounts WHERE platform_name = ?', (platform_name,))
        row = cursor.fetchone()
        
        self.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_accounts(self, platform_type: str = None) -> List[Dict]:
        """Get all accounts, optionally filtered by type"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if platform_type:
            cursor.execute('SELECT * FROM accounts WHERE platform_type = ?', (platform_type,))
        else:
            cursor.execute('SELECT * FROM accounts')
        
        rows = cursor.fetchall()
        self.close()
        
        return [dict(row) for row in rows]
    
    def get_monetization_status(self, platform_name: str) -> Dict:
        """Get monetization status and requirements"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM monetization_requirements
            WHERE platform_name = ?
        ''', (platform_name,))
        
        requirements = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT monetization_status FROM accounts
            WHERE platform_name = ?
        ''', (platform_name,))
        
        row = cursor.fetchone()
        status = row[0] if row else "not_eligible"
        
        self.close()
        
        return {
            "platform": platform_name,
            "status": status,
            "requirements": requirements
        }
    
    def get_creation_progress(self) -> Dict:
        """Get overall account creation progress"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM accounts')
        total = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM accounts 
            WHERE account_status IN ('verified', 'configured', 'live')
        ''')
        created = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM accounts 
            WHERE account_status = 'live'
        ''')
        live = cursor.fetchone()[0]
        
        self.close()
        
        return {
            "total_accounts": total,
            "created_accounts": created,
            "live_accounts": live,
            "progress_percentage": (created / total * 100) if total > 0 else 0
        }
    
    def export_to_json(self, filepath: str):
        """Export all data to JSON"""
        data = {
            "accounts": self.get_all_accounts(),
            "export_date": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_report(self) -> str:
        """Generate text report of account status"""
        accounts = self.get_all_accounts()
        progress = self.get_creation_progress()
        
        report = []
        report.append("=" * 60)
        report.append("SISI LOLA SOCIAL MEDIA ACCOUNTS STATUS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append(f"Total Accounts: {progress['total_accounts']}")
        report.append(f"Created: {progress['created_accounts']}")
        report.append(f"Live: {progress['live_accounts']}")
        report.append(f"Progress: {progress['progress_percentage']:.1f}%")
        report.append("")
        report.append("ACCOUNT DETAILS:")
        report.append("-" * 60)
        
        for account in accounts:
            report.append(f"\n{account['platform_name']} ({account['platform_type']})")
            report.append(f"  Status: {account['account_status']}")
            report.append(f"  Email: {account['email']}")
            report.append(f"  Username: {account['username']}")
            report.append(f"  Verified: Email={account['email_verified']}, Phone={account['phone_verified']}, 2FA={account['two_fa_enabled']}")
            report.append(f"  Assets: Profile={account['profile_picture_uploaded']}, Banner={account['banner_uploaded']}")
            report.append(f"  Followers: {account['followers']}")
            report.append(f"  Monetization: {account['monetization_status']}")
            if account['profile_url']:
                report.append(f"  URL: {account['profile_url']}")
        
        return "\n".join(report)


def main():
    """Initialize and test the database"""
    db = SocialMediaAccountDB()
    
    print("Initializing Sisi Lola Social Media Accounts Database...")
    db.seed_initial_accounts()
    db.seed_monetization_requirements()
    
    print("\nGenerated Report:")
    print(db.generate_report())
    
    # Export to JSON
    export_path = Path(__file__).parent.parent / "05_BRANDING_ARTIFACTS" / "accounts_export.json"
    db.export_to_json(str(export_path))
    print(f"\nExported to: {export_path}")


if __name__ == "__main__":
    main()
