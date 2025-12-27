import modal
import os
import sys

def test_sisi_query(query: str):
    print(f"🧠 SENDING QUERY TO SISI: '{query}'")
    
    try:
        f = modal.Function.from_name("sisi-lola-inference", "chat_api")
        response = f.remote({"message": query})
        print(f"\n✨ SISI LOLA REPLIED:\n{response}")
    except Exception as e:
        print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    test_query = "Find me the cheapest flight from Lagos to London for next month"
    if len(sys.argv) > 1:
        test_query = " ".join(sys.argv[1:])
    
    test_sisi_query(test_query)
