"""
OpenRouter Yoruba Model Tester
Tests multiple models to find best Yoruba content generator
"""
import os
import openai
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

YORUBA_PROMPT = """Generate a 2-minute video script for Sisi Lola about "AI in African Tech".

CRITICAL: Use Yoruba/Yorunglish mix:
- 60% Yoruba words and grammar
- 30% Nigerian Pidgin
- 10% English (technical terms only)

Example style: "Ẹ káàbọ̀! I dey very happy say you come here today! Make I tell you about AI..."

Generate authentic Lagos auntie vibe."""

def test_model(model_name):
    """Test a model for Yoruba generation"""
    
    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    
    print(f"\n[TESTING] {model_name}")
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": YORUBA_PROMPT}],
            max_tokens=500
        )
        
        script = response.choices[0].message.content
        
        # Count Yoruba markers
        yoruba_markers = ['ẹ', 'ọ', 'ṣ', 'káàbọ̀', 'dey', 'wetin', 'make', 'say', 'wey']
        yoruba_count = sum(script.lower().count(m) for m in yoruba_markers)
        words = len(script.split())
        yoruba_ratio = (yoruba_count / words * 100) if words > 0 else 0
        
        print(f"[RESULT] Yoruba markers: {yoruba_count}, Ratio: {yoruba_ratio:.1f}%")
        print(f"[PREVIEW] {script[:200]}...")
        
        return {
            "model": model_name,
            "script": script,
            "yoruba_ratio": yoruba_ratio,
            "success": True
        }
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return {
            "model": model_name,
            "error": str(e),
            "success": False
        }

def main():
    print("="*70)
    print("OPENROUTER YORUBA MODEL TESTER")
    print("="*70)
    
    models = [
        "anthropic/claude-3-opus",
        "google/gemini-pro-1.5",
        "meta-llama/llama-3-70b-instruct",
        "cohere/command-r-plus",
        "mistralai/mixtral-8x7b-instruct"
    ]
    
    results = []
    
    for model in models:
        result = test_model(model)
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    successful = [r for r in results if r['success']]
    successful.sort(key=lambda x: x['yoruba_ratio'], reverse=True)
    
    for i, r in enumerate(successful, 1):
        print(f"{i}. {r['model']}: {r['yoruba_ratio']:.1f}% Yoruba")
    
    if successful:
        best = successful[0]
        print(f"\n[WINNER] {best['model']} with {best['yoruba_ratio']:.1f}% Yoruba ratio")
        print(f"\n[BEST SCRIPT]")
        print(best['script'][:400])
        
        # Save
        output_dir = Path(__file__).parent.parent.parent / "03_MEDIA_ASSETS" / "yoruba_scripts"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "openrouter_best_model.txt", 'w', encoding='utf-8') as f:
            f.write(f"BEST MODEL: {best['model']}\n")
            f.write(f"YORUBA RATIO: {best['yoruba_ratio']:.1f}%\n\n")
            f.write(best['script'])
        
        print(f"\n[SAVED] Best result to yoruba_scripts/openrouter_best_model.txt")
        print(f"\n[NEXT] Use {best['model']} for production Yoruba content")

if __name__ == "__main__":
    main()
