import os
import sys
from pathlib import Path

# Add Scripts directory to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__)))

from oauth_credential_manager import SecureCredentialManager

def store_youtube_creds():
    print("Storing YouTube credentials securely...")
    
    manager = SecureCredentialManager()
    
    # YouTube credentials provided by user
    manager.set(
        'youtube',
        client_id='44388863436-3bs6dd34q2l0moqhprebikpjv91teq0i.apps.googleusercontent.com',
        client_secret='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',
        # Note: Access/Refresh tokens were not provided in the initial dump, 
        # only API Key. We'll store API Key in additional_info for now.
        api_key='AIzaSyAnZtkd0puPVFTC51BYhniRsGHLQe98cQU'
    )
    
    # Store other platform IDs as placeholders to mark them as "partially configured"
    # Facebook
    manager.set(
        'facebook',
        page_id='950684708116727'
    )
    
    # Instagram
    manager.set(
        'instagram',
        business_account_id='950684708116727' # Linked to FB Page ID
    )
    
    # Reddit
    manager.set(
        'reddit',
        username='sisilola',
        user_agent='SisiLola Bot v1.0 by u/sisilola'
    )
    
    manager.save_credentials()
    print("✅ Credentials updated in secure storage.")

if __name__ == "__main__":
    store_youtube_creds()
