import os

def load_dna_assets():
    """
    Utility to verify DNA assets exist
    """
    dna_path = "assets/dna"
    if not os.path.exists(dna_path):
        return {"status": "error", "message": "DNA folder missing"}
    
    return {
        "status": "success",
        "files": os.listdir(dna_path)
    }