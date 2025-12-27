import os

# PASTE YOUR NEW DROPBOX ACCESS TOKEN HERE
# Get it from: https://www.dropbox.com/developers/apps
NEW_DROPBOX_TOKEN = "sl.u.AGNTYamYlE3ThUcFQmEOay0Fv3XcHF3mXtSoKicgPVp_CCnoJW3ZUJq_FvBy7r4omLxNPjU92cs-D3H8sgFkFp8A4Oxj5qmMswuK2x3qVVqcQEflKIzIGQbdYgFldB7qz3oBGtsHDW-_n2X9q9baeqW-ffSU4N2VEjMT5y7GEGNyOUH4TNAN8j7IoOG2ROJN07s3NpbRtHJXoJmaHcYxzHf2ejxjFetEWSKe4lIOVCH1MwtDQnprjQyMsHmAqDOTSSIdq-HfucF6YAToGPQrs6cDqacmQRp4tnIjA-6SFlaTo3bavLiyL8Ywi73yXIV_mwU7FTu4CkssI8ojB1ajPL4kwwq6ubE16O9xhvH3VOSBwx-EWfYb-PKAEnEVNyScKyaaiUu8eiPBnA5piDZ8ri7QhTisnZPpjGNVrLI6OtQFV11unnK23NgoJID3UuRke1o-kezS4-9wbRXA1_8PvEMqPcdyiAXLjGB5Z6nMvYcpfjU_vXr3AJtsaR7yPj2IMcAjRJd_DaOdiE2gLpFA_ggSPuzH8feS-yHjFjg5pjPukajRw9QyG0zJnPphcJ8Ye0O5mqQWP-o7ZPTUadWaEDt7JdcLZuO86q8qDKboBxkKDh3GyEBF6RwS5r82BulI_Mrs8oxKtBpgCM-GM3DrF-rtQQetbX-CpPix3dvq1r2J0A3XFCuqR9fyVWDOCcRcN0VqrwD-CJGdZxai80aXgkJnZGeZJ5w9zJM0WEHX6UtH1Bm_lbwxfclZ-0SQinTN97CKXbqHKylTPRNAQ1GtVGYP0Heq2SUiMATQbTafWhRwiZFAY6EHwUCL6l7FKldA_LVJS6Ma-utdVDmF_c6Bb2nLe_oojJdumSwkTWd8lVC-jrBMoWh4MjRNzcam9yCaenua_PxFDwlOLDWEJ1tgjXEJ0HEUGWoDuOWlD8WtD0D_FwdC4CnYCk8wyek14wW4hYwv9MLUF3Go0JUJM0bH6sR9FBUmdX99hjE-DMfnLHsp1yhvyK5iYwRwZHALZKy-uRPfSR4h-idaj0IkWPggdTWNa1b2iQfvDnFMFS1cnsfjqq5DiqFd0yLQ9HXF5iow1_dpA2V6IHTfeQwbHjNXLGbGIJKSFKS7De7YFSibPDLozE2R3NE62PVOxdEDaDiQYeFnbLh60RzXySJ5ZbqmuFS5il9bPtyIr1wF-ERObSKyXNEla-CDJQcT9J86jZmFZno0h0sqA9P7REQZQm-qMmzGqZy1yNIwswt9DJeGQxok3uxZYR-dmP03AuC6rCshRPlCkDXCGrd57GMuXEDrWa8lqQUYm9FGAfgDayZBHVEnel9uExwv7aWJBszNRtWbOxph1b-dzMIsrmiwM0u128Jw0h9LEUZxcVxdmeQ0n5ZO87C_tVrcrmsF3NrYQo7aRZDl8TvDPlQvrKd-R6_PaQwW8WKyHcZ_1YB0zknfhhK5iw"

env_path = os.path.join("sisi_lola_api", ".env")

if os.path.exists(env_path):
    with open(env_path, "r") as f:
        content = f.read()
    
    import re
    if "DROPBOX_ACCESS_TOKEN=" in content:
        content = re.sub(r"DROPBOX_ACCESS_TOKEN=.*", f"DROPBOX_ACCESS_TOKEN={NEW_DROPBOX_TOKEN}", content)
    else:
        content += f"\nDROPBOX_ACCESS_TOKEN={NEW_DROPBOX_TOKEN}"
        
    with open(env_path, "w") as f:
        f.write(content)
        
    print(f"✅ Dropbox Token updated in .env")
else:
    print("❌ .env not found")
