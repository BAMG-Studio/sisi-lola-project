#!/bin/bash
# Download African Language Datasets for Sisi Lola Voice Engine
# Run in WSL: bash download_datasets.sh

set -e  # Exit on error

echo "🌍 Downloading African Language Datasets for Sisi Lola"
echo "======================================================="
echo ""

# Create datasets directory
DATASET_DIR="../../datasets/african_languages"
mkdir -p "$DATASET_DIR"
cd "$DATASET_DIR"

echo "📂 Working directory: $(pwd)"
echo ""

# -------------------------------------------------------------------
# 1. MENYO-20k (Yoruba-English Parallel Corpus)
# -------------------------------------------------------------------
echo "📥 [1/6] Downloading MENYO-20k (Yoruba-English)..."
if [ ! -d "menyo20k" ]; then
    git clone https://github.com/dadelani/menyo-20k_MT.git menyo20k
    echo "✅ MENYO-20k downloaded"
else
    echo "⏭️  MENYO-20k already exists, skipping"
fi
echo ""

# -------------------------------------------------------------------
# 2. Lagos-NWU (Nigerian English Conversational Speech)
# -------------------------------------------------------------------
echo "📥 [2/6] Downloading Lagos-NWU (Nigerian English ASR)..."
if [ ! -d "lagos_nwu" ]; then
    # Note: This dataset requires manual download from the original source
    # GitHub repo only contains metadata
    echo "⚠️  Lagos-NWU requires manual download"
    echo "   1. Visit: https://github.com/Speech-Lab-IITM/Lagos-NWU-conversational-speech-corpus"
    echo "   2. Follow instructions to request dataset access"
    echo "   3. Download and extract to: $(pwd)/lagos_nwu"
    mkdir -p lagos_nwu
    echo "📝 Created placeholder directory"
else
    echo "⏭️  Lagos-NWU directory already exists, skipping"
fi
echo ""

# -------------------------------------------------------------------
# 3. Fleurs (Yoruba subset)
# -------------------------------------------------------------------
echo "📥 [3/6] Downloading Fleurs (Yoruba)..."
if [ ! -d "fleurs_yoruba" ]; then
    python3 - <<'EOF'
print("Loading Fleurs dataset...")
try:
    from datasets import load_dataset
    
    # Download Yoruba subset
    print("Downloading Yoruba subset (yo_ng)...")
    ds = load_dataset('google/fleurs', 'yo_ng', trust_remote_code=True)
    
    # Save to disk
    print("Saving to disk...")
    ds.save_to_disk('fleurs_yoruba')
    
    print("✅ Fleurs Yoruba downloaded successfully")
except ImportError:
    print("❌ Error: 'datasets' library not installed")
    print("   Install with: pip install datasets")
    exit(1)
except Exception as e:
    print(f"❌ Error downloading Fleurs: {e}")
    exit(1)
EOF
else
    echo "⏭️  Fleurs Yoruba already exists, skipping"
fi
echo ""

# -------------------------------------------------------------------
# 4. NaijaNLP (Nigerian Pidgin)
# -------------------------------------------------------------------
echo "📥 [4/6] Downloading NaijaNLP (Nigerian Pidgin)..."
if [ ! -d "naija_nlp" ]; then
    # Note: Repository might not exist or be accessible
    # Using fallback approach
    echo "⚠️  NaijaNLP dataset - attempting download..."
    
    # Try hausanlp organization
    if git clone https://github.com/hausanlp/NaijaNLP.git naija_nlp 2>/dev/null; then
        echo "✅ NaijaNLP downloaded"
    else
        echo "⚠️  Could not clone from hausanlp"
        echo "   Creating placeholder - collect Nigerian Pidgin data manually"
        mkdir -p naija_nlp
        cat > naija_nlp/README.md <<'HEREDOC'
# Nigerian Pidgin Dataset

Collect Nigerian Pidgin data from:
1. Social media (Twitter/X, Nigerian forums)
2. Nigerian movies (Nollywood subtitles)
3. Nigerian news websites
4. Nigerian music lyrics

Format: CSV with columns [text, sentiment, source]
HEREDOC
        echo "📝 Created placeholder with instructions"
    fi
else
    echo "⏭️  NaijaNLP already exists, skipping"
fi
echo ""

# -------------------------------------------------------------------
# 5. MasakhaNER (African Language NER)
# -------------------------------------------------------------------
echo "📥 [5/6] Downloading MasakhaNER (Hausa, Igbo, Yoruba)..."
if [ ! -d "masakhaner" ]; then
    python3 - <<'EOF'
print("Loading MasakhaNER dataset...")
try:
    from datasets import load_dataset
    
    # Download Yoruba, Hausa, Igbo
    languages = ['yor', 'hau', 'ibo']  # ISO 639-3 codes
    
    for lang in languages:
        print(f"Downloading {lang}...")
        ds = load_dataset('masakhane/masakhaner', lang, trust_remote_code=True)
        ds.save_to_disk(f'masakhaner/{lang}')
    
    print("✅ MasakhaNER downloaded successfully")
except ImportError:
    print("❌ Error: 'datasets' library not installed")
    print("   Install with: pip install datasets")
    exit(1)
except Exception as e:
    print(f"❌ Error downloading MasakhaNER: {e}")
    exit(1)
EOF
else
    echo "⏭️  MasakhaNER already exists, skipping"
fi
echo ""

# -------------------------------------------------------------------
# 6. ALFFA (Swahili ASR)
# -------------------------------------------------------------------
echo "📥 [6/6] Downloading ALFFA (Swahili)..."
if [ ! -d "alffa_swahili" ]; then
    echo "⚠️  ALFFA Swahili requires manual download"
    echo "   1. Visit: https://github.com/getalp/ALFFA_PUBLIC"
    echo "   2. Download Swahili subset"
    echo "   3. Extract to: $(pwd)/alffa_swahili"
    mkdir -p alffa_swahili
    echo "📝 Created placeholder directory"
else
    echo "⏭️  ALFFA Swahili already exists, skipping"
fi
echo ""

# -------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------
echo "======================================================="
echo "✅ Dataset Download Complete!"
echo ""
echo "📊 Downloaded Datasets:"
echo "   ✓ MENYO-20k (Yoruba-English parallel)"
echo "   ⚠️ Lagos-NWU (requires manual download)"
echo "   ✓ Fleurs (Yoruba ASR)"
echo "   ~ NaijaNLP (may require manual collection)"
echo "   ✓ MasakhaNER (Yoruba, Hausa, Igbo NER)"
echo "   ⚠️ ALFFA (Swahili - requires manual download)"
echo ""
echo "📂 Location: $(pwd)"
echo ""
echo "🚀 Next Steps:"
echo "   1. Complete manual downloads for Lagos-NWU and ALFFA"
echo "   2. Review dataset quality"
echo "   3. Run: python prepare_training_data.py"
echo ""
