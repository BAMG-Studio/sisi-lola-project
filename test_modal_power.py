import modal
import os

def test_modal_brain():
    print("🧠 TESTING SISI LOLA CLOUD BRAIN...")
    
    # Connect to the deployed app
    try:
        f = modal.Function.from_name("sisi-lola-inference", "chat_api")
        response = f.remote({"message": "Sisi, how far? You dey cloud now?"})
        print(f"✅ SISI REPLIED: {response}")
    except Exception as e:
        print(f"❌ Brain Test Failed: {e}")

def test_modal_selfie():
    print("\n📸 TESTING SISI LOLA PHOTO GENERATION...")
    
    try:
        # We use the class method
        engine = modal.Cls.from_name("sisi-lola-inference", "SisiLolaEngine")()
        image_bytes = engine.generate_selfie.remote("A beautiful Nigerian woman in a high-tech studio, neon lights, 4k")
        
        with open("sisi_cloud_selfie.png", "wb") as f:
            f.write(image_bytes)
        print("✅ SUCCESS! Selfie saved as 'sisi_cloud_selfie.png'")
    except Exception as e:
        print(f"❌ Selfie Test Failed: {e}")

if __name__ == "__main__":
    test_modal_brain()
    # Uncomment below to test image gen (requires A10G GPU to be active)
    # test_modal_selfie()
