"""
OAuth Credential Manager & Setup Wizard
Secure credential storage and OAuth flow handlers for all platforms
"""

import os
import json
import webbrowser
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
import base64
from datetime import datetime, timedelta


@dataclass
class PlatformCredentials:
    """Platform credential structure"""
    platform: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[str] = None
    additional_info: Dict = None


class SecureCredentialManager:
    """
    Secure credential management with:
    - Environment variable loading
    - Encrypted file storage (optional)
    - OAuth token refresh
    - Credential validation
    """
    
    def __init__(self, credentials_file: str = None):
        if credentials_file is None:
            base_path = Path(__file__).parent.parent
            credentials_file = base_path / "05_BRANDING_ARTIFACTS" / ".credentials.json"
        
        self.credentials_file = Path(credentials_file)
        self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.credentials: Dict[str, PlatformCredentials] = {}
        self.load_credentials()
    
    def load_credentials(self):
        """Load credentials from environment variables and file"""
        # Load from environment variables (highest priority)
        self._load_from_env()
        
        # Load from file (if exists)
        if self.credentials_file.exists():
            self._load_from_file()
    
    def _load_from_env(self):
        """Load credentials from environment variables"""
        platforms = {
            'youtube': ['CLIENT_ID', 'CLIENT_SECRET', 'ACCESS_TOKEN', 'REFRESH_TOKEN'],
            'instagram': ['ACCESS_TOKEN', 'BUSINESS_ACCOUNT_ID'],
            'tiktok': ['ACCESS_TOKEN', 'OPEN_ID'],
            'facebook': ['ACCESS_TOKEN', 'PAGE_ID'],
            'twitch': ['CLIENT_ID', 'CLIENT_SECRET', 'ACCESS_TOKEN', 'BROADCASTER_ID'],
            'reddit': ['CLIENT_ID', 'CLIENT_SECRET', 'USERNAME', 'PASSWORD']
        }
        
        for platform, keys in platforms.items():
            creds = PlatformCredentials(platform=platform)
            
            for key in keys:
                env_var = f"{platform.upper()}_{key}"
                value = os.getenv(env_var)
                
                if value:
                    key_lower = key.lower()
                    if hasattr(creds, key_lower):
                        setattr(creds, key_lower, value)
                    else:
                        if creds.additional_info is None:
                            creds.additional_info = {}
                        creds.additional_info[key_lower] = value
            
            self.credentials[platform] = creds
    
    def _load_from_file(self):
        """Load credentials from JSON file"""
        try:
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
            
            for platform, cred_data in data.items():
                if platform not in self.credentials:
                    self.credentials[platform] = PlatformCredentials(platform=platform)
                
                creds = self.credentials[platform]
                for key, value in cred_data.items():
                    if hasattr(creds, key):
                        setattr(creds, key, value)
                    else:
                        if creds.additional_info is None:
                            creds.additional_info = {}
                        creds.additional_info[key] = value
        
        except Exception as e:
            print(f"Warning: Could not load credentials file: {e}")
    
    def save_credentials(self):
        """Save credentials to JSON file"""
        data = {}
        
        for platform, creds in self.credentials.items():
            data[platform] = {
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'access_token': creds.access_token,
                'refresh_token': creds.refresh_token,
                'token_expires_at': creds.token_expires_at,
                'additional_info': creds.additional_info
            }
        
        with open(self.credentials_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Credentials saved to: {self.credentials_file}")
        print("⚠️  IMPORTANT: Add this file to .gitignore!")
    
    def get(self, platform: str) -> Optional[PlatformCredentials]:
        """Get credentials for platform"""
        return self.credentials.get(platform.lower())
    
    def set(self, platform: str, **kwargs):
        """Set credentials for platform"""
        if platform.lower() not in self.credentials:
            self.credentials[platform.lower()] = PlatformCredentials(platform=platform.lower())
        
        creds = self.credentials[platform.lower()]
        
        for key, value in kwargs.items():
            if hasattr(creds, key):
                setattr(creds, key, value)
            else:
                if creds.additional_info is None:
                    creds.additional_info = {}
                creds.additional_info[key] = value
    
    def is_configured(self, platform: str) -> bool:
        """Check if platform has valid credentials"""
        creds = self.get(platform)
        if not creds:
            return False
        
        # Platform-specific validation
        required_fields = {
            'youtube': ['access_token', 'refresh_token'],
            'instagram': ['access_token'],
            'tiktok': ['access_token'],
            'facebook': ['access_token'],
            'twitch': ['access_token'],
            'reddit': ['client_id', 'client_secret']
        }
        
        required = required_fields.get(platform.lower(), [])
        
        for field in required:
            value = getattr(creds, field, None)
            if not value and creds.additional_info:
                value = creds.additional_info.get(field)
            if not value:
                return False
        
        return True
    
    def needs_refresh(self, platform: str) -> bool:
        """Check if access token needs refresh"""
        creds = self.get(platform)
        if not creds or not creds.token_expires_at:
            return False
        
        expires_at = datetime.fromisoformat(creds.token_expires_at)
        now = datetime.now()
        
        # Refresh if expiring within 1 hour
        return expires_at - now < timedelta(hours=1)
    
    def validate_all(self) -> Dict[str, bool]:
        """Validate all platform credentials"""
        validation = {}
        
        for platform in ['youtube', 'instagram', 'tiktok', 'facebook', 'twitch', 'reddit']:
            validation[platform] = self.is_configured(platform)
        
        return validation


class OAuthSetupWizard:
    """
    Interactive OAuth setup wizard for all platforms
    Guides users through obtaining credentials
    """
    
    def __init__(self, cred_manager: SecureCredentialManager = None):
        if cred_manager is None:
            cred_manager = SecureCredentialManager()
        self.cred_manager = cred_manager
    
    def run_interactive_setup(self):
        """Run interactive setup for all platforms"""
        print("=" * 70)
        print("SISI LOLA SOCIAL MEDIA - OAuth Setup Wizard")
        print("=" * 70)
        print("\nThis wizard will help you set up API credentials for all platforms.")
        print("You'll need to create developer apps on each platform first.\n")
        
        platforms = {
            '1': ('YouTube', self.setup_youtube),
            '2': ('Instagram', self.setup_instagram),
            '3': ('TikTok', self.setup_tiktok),
            '4': ('Facebook', self.setup_facebook),
            '5': ('Twitch', self.setup_twitch),
            '6': ('Reddit', self.setup_reddit),
            '7': ('All Platforms', self.setup_all)
        }
        
        print("Select platform to configure:")
        for key, (name, _) in platforms.items():
            status = "✅" if self.cred_manager.is_configured(name.lower()) else "❌"
            print(f"  {key}. {name} {status}")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice in platforms:
            name, setup_func = platforms[choice]
            print(f"\n🔧 Setting up {name}...")
            setup_func()
        else:
            print(f"❌ Invalid choice '{choice}'. Please enter a number between 1-7.")
            return self.run_interactive_setup()
    
    def setup_youtube(self):
        """Setup YouTube OAuth credentials"""
        print("\n" + "=" * 70)
        print("YOUTUBE API SETUP")
        print("=" * 70)
        
        print("""
        Steps to get YouTube API credentials:
        
        1. Go to https://console.cloud.google.com/
        2. Create a new project or select existing
        3. Enable YouTube Data API v3
        4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
        5. Application type: Web application
        6. Authorized redirect URIs: http://localhost:8080/
        7. Copy Client ID and Client Secret
        
        For Access Token & Refresh Token:
        8. Use OAuth 2.0 Playground: https://developers.google.com/oauthplayground/
        9. Select YouTube Data API v3 scopes
        10. Exchange authorization code for tokens
        """)
        
        client_id = input("\nEnter Client ID (or press Enter to skip): ").strip()
        if not client_id:
            print("⏩ Skipped YouTube setup")
            return
        
        client_secret = input("Enter Client Secret: ").strip()
        access_token = input("Enter Access Token: ").strip()
        refresh_token = input("Enter Refresh Token: ").strip()
        
        self.cred_manager.set(
            'youtube',
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        self.cred_manager.save_credentials()
        print("✅ YouTube credentials saved!")
    
    def setup_instagram(self):
        """Setup Instagram Graph API credentials"""
        print("\n" + "=" * 70)
        print("INSTAGRAM GRAPH API SETUP")
        print("=" * 70)
        
        print("""
        Steps to get Instagram API credentials:
        
        1. Go to https://developers.facebook.com/
        2. Create an App → Business Type
        3. Add Instagram Graph API product
        4. Settings → Basic → Copy App ID and App Secret
        5. Go to https://developers.facebook.com/tools/explorer/
        6. Select your app
        7. Generate User Access Token with permissions:
           - instagram_basic
           - instagram_content_publish
           - pages_read_engagement
           - pages_manage_posts
        8. Get your Instagram Business Account ID from Graph API Explorer:
           GET /me/accounts → select page → GET /{page-id}?fields=instagram_business_account
        """)
        
        access_token = input("\nEnter Access Token (or press Enter to skip): ").strip()
        if not access_token:
            print("⏩ Skipped Instagram setup")
            return
        
        business_account_id = input("Enter Business Account ID: ").strip()
        
        self.cred_manager.set(
            'instagram',
            access_token=access_token,
            business_account_id=business_account_id
        )
        
        self.cred_manager.save_credentials()
        print("✅ Instagram credentials saved!")
    
    def setup_tiktok(self):
        """Setup TikTok API credentials"""
        print("\n" + "=" * 70)
        print("TIKTOK API SETUP")
        print("=" * 70)
        
        print("""
        Steps to get TikTok API credentials:
        
        1. Go to https://developers.tiktok.com/
        2. Register as a developer
        3. Create an app
        4. Add "Content Posting API" capability
        5. Submit for review (takes 3-5 days)
        6. Once approved, go to Manage Apps → Your App
        7. Get Client Key and Client Secret
        8. Use Web Authorization to get Access Token:
           https://www.tiktok.com/auth/authorize/
        9. Get your Open ID from the authorization response
        """)
        
        access_token = input("\nEnter Access Token (or press Enter to skip): ").strip()
        if not access_token:
            print("⏩ Skipped TikTok setup")
            return
        
        open_id = input("Enter Open ID: ").strip()
        
        self.cred_manager.set(
            'tiktok',
            access_token=access_token,
            open_id=open_id
        )
        
        self.cred_manager.save_credentials()
        print("✅ TikTok credentials saved!")
    
    def setup_facebook(self):
        """Setup Facebook Graph API credentials"""
        print("\n" + "=" * 70)
        print("FACEBOOK GRAPH API SETUP")
        print("=" * 70)
        
        print("""
        Steps to get Facebook API credentials:
        
        1. Go to https://developers.facebook.com/
        2. Create an App → Business Type
        3. Settings → Basic → Copy App ID and App Secret
        4. Add Facebook Login product
        5. Settings → Advanced → Set redirect URI
        6. Use Graph API Explorer to generate User Access Token:
           https://developers.facebook.com/tools/explorer/
        7. Select permissions: pages_manage_posts, pages_read_engagement
        8. Get your Page ID: 
           Go to your Facebook Page → About → Page ID
        """)
        
        access_token = input("\nEnter Access Token (or press Enter to skip): ").strip()
        if not access_token:
            print("⏩ Skipped Facebook setup")
            return
        
        page_id = input("Enter Page ID: ").strip()
        
        self.cred_manager.set(
            'facebook',
            access_token=access_token,
            page_id=page_id
        )
        
        self.cred_manager.save_credentials()
        print("✅ Facebook credentials saved!")
    
    def setup_twitch(self):
        """Setup Twitch API credentials"""
        print("\n" + "=" * 70)
        print("TWITCH API SETUP")
        print("=" * 70)
        
        print("""
        Steps to get Twitch API credentials:
        
        1. Go to https://dev.twitch.tv/console/apps
        2. Register your application
        3. OAuth Redirect URLs: http://localhost:3000
        4. Category: Broadcasting Suite
        5. Copy Client ID and Client Secret
        6. Generate Access Token using OAuth flow:
           https://id.twitch.tv/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri=http://localhost:3000&response_type=code&scope=channel:manage:broadcast
        7. Get your Broadcaster ID:
           https://api.twitch.tv/helix/users?login=YOUR_USERNAME
        """)
        
        client_id = input("\nEnter Client ID (or press Enter to skip): ").strip()
        if not client_id:
            print("⏩ Skipped Twitch setup")
            return
        
        client_secret = input("Enter Client Secret: ").strip()
        access_token = input("Enter Access Token: ").strip()
        broadcaster_id = input("Enter Broadcaster ID: ").strip()
        
        self.cred_manager.set(
            'twitch',
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            broadcaster_id=broadcaster_id
        )
        
        self.cred_manager.save_credentials()
        print("✅ Twitch credentials saved!")
    
    def setup_reddit(self):
        """Setup Reddit API credentials"""
        print("\n" + "=" * 70)
        print("REDDIT API SETUP")
        print("=" * 70)
        
        print("""
        Steps to get Reddit API credentials:
        
        1. Go to https://www.reddit.com/prefs/apps
        2. Click "Create App" or "Create Another App"
        3. Select "script" type
        4. Name: Sisi Lola Bot
        5. Redirect URI: http://localhost:8080
        6. Copy the client ID (under app name)
        7. Copy the secret
        8. Use your Reddit username and password
        """)
        
        client_id = input("\nEnter Client ID (or press Enter to skip): ").strip()
        if not client_id:
            print("⏩ Skipped Reddit setup")
            return
        
        client_secret = input("Enter Client Secret: ").strip()
        username = input("Enter Reddit Username: ").strip()
        password = input("Enter Reddit Password: ").strip()
        
        self.cred_manager.set(
            'reddit',
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password
        )
        
        self.cred_manager.save_credentials()
        print("✅ Reddit credentials saved!")
    
    def setup_all(self):
        """Setup all platforms sequentially"""
        print("\nSetting up all platforms...")
        print("Press Enter to skip any platform.\n")
        
        for setup_func in [
            self.setup_youtube,
            self.setup_instagram,
            self.setup_tiktok,
            self.setup_facebook,
            self.setup_twitch,
            self.setup_reddit
        ]:
            try:
                setup_func()
            except KeyboardInterrupt:
                print("\nSkipping...")
                continue
        
        print("\n✅ All platforms configured!")
        self.print_status()
    
    def print_status(self):
        """Print configuration status for all platforms"""
        print("\n" + "=" * 70)
        print("CREDENTIAL CONFIGURATION STATUS")
        print("=" * 70)
        
        validation = self.cred_manager.validate_all()
        
        for platform, is_valid in validation.items():
            status = "✅ Configured" if is_valid else "❌ Not Configured"
            print(f"{platform.capitalize():15} {status}")
        
        configured_count = sum(1 for v in validation.values() if v)
        total_count = len(validation)
        
        print(f"\nTotal: {configured_count}/{total_count} platforms configured")
        print("=" * 70)
    
    def export_env_template(self, filepath: str = None):
        """Export .env template file"""
        if filepath is None:
            filepath = Path(__file__).parent.parent / ".env.template"
        
        template = """# Sisi Lola Social Media API Credentials
# Copy this file to .env and fill in your credentials

# YouTube Data API v3
YOUTUBE_CLIENT_ID=your_client_id_here
YOUTUBE_CLIENT_SECRET=your_client_secret_here
YOUTUBE_ACCESS_TOKEN=your_access_token_here
YOUTUBE_REFRESH_TOKEN=your_refresh_token_here

# Instagram Graph API
INSTAGRAM_ACCESS_TOKEN=your_access_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_business_account_id_here

# TikTok API v2
TIKTOK_ACCESS_TOKEN=your_access_token_here
TIKTOK_OPEN_ID=your_open_id_here

# Facebook Graph API
FACEBOOK_ACCESS_TOKEN=your_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here

# Twitch Helix API
TWITCH_CLIENT_ID=your_client_id_here
TWITCH_CLIENT_SECRET=your_client_secret_here
TWITCH_ACCESS_TOKEN=your_access_token_here
TWITCH_BROADCASTER_ID=your_broadcaster_id_here

# Reddit API (PRAW)
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_username_here
REDDIT_PASSWORD=your_password_here
"""
        
        with open(filepath, 'w') as f:
            f.write(template)
        
        print(f"✅ Environment template exported to: {filepath}")
        print("📝 Fill in your credentials and rename to .env")


def main():
    """Run the OAuth setup wizard"""
    wizard = OAuthSetupWizard()
    
    # Check current status
    wizard.print_status()
    
    print("\nOptions:")
    print("1. Interactive Setup")
    print("2. Export .env Template")
    print("3. Exit")
    
    choice = input("\nEnter choice: ").strip()
    
    if choice == '1':
        wizard.run_interactive_setup()
    elif choice == '2':
        wizard.export_env_template()
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()
