# African Language Dataset Licensing Guide for Commercial Use

## Overview

This guide helps the Sisi Lola Voice Dataset Curator identify datasets that are safe for commercial use in the Sisi Lola virtual influencer project.

---

## ✅ Most Permissive (Commercial-Friendly)

### CC0-1.0 (Public Domain)
- **Use**: Unrestricted commercial use
- **Attribution**: Not required (but appreciated)
- **Modifications**: Allowed without restrictions
- **Datasets**: 
  - Mozilla Common Voice Pidgin
- **Best for**: Commercial products without attribution requirements
- **Sisi Lola Status**: ✅ SAFE TO USE

### MIT License
- **Use**: Unrestricted commercial use
- **Attribution**: Required in source code/documentation
- **Modifications**: Allowed
- **Datasets**: 
  - Rexe/Nigerian Pidgin Speech
- **Best for**: Open-source friendly commercial products
- **Sisi Lola Status**: ✅ SAFE TO USE (include attribution)

### CC-BY 4.0 (Attribution)
- **Use**: Commercial use allowed
- **Attribution**: Required (credit original creators)
- **Modifications**: Allowed
- **Datasets**:
  - FLEURS (Google)
  - Luganda-Swahili TTS
  - YoruLect
  - IroyinSpeech
- **Best for**: Commercial products with proper attribution
- **Sisi Lola Status**: ✅ SAFE TO USE (include attribution)

### CC-BY-SA 4.0 (Attribution + ShareAlike)
- **Use**: Commercial use allowed
- **Attribution**: Required
- **Share-Alike**: Derivative works must use same license
- **Datasets**: 
  - BibleTTS (Hausa, Yoruba, Ewe, Twi, Lingala)
  - OpenSLR-32 (Xhosa, Zulu, Afrikaans)
  - OpenSLR-86 (Yoruba)
  - Yoruba-LJSpeech
  - Hausa Speech Corpus
- **Best for**: Commercial products that can share derivatives
- **Sisi Lola Status**: ✅ SAFE TO USE (models trained on this data inherit license)

---

## ⚠️ Conditionally Safe Licenses

### Apache 2.0
- **Use**: Commercial use allowed
- **Patent Grant**: Includes patent protection
- **Attribution**: Required
- **Modifications**: Must document changes
- **Datasets**: 
  - AfriSpeech-200
- **Sisi Lola Status**: ✅ SAFE TO USE (include NOTICE file)

### CC-BY-NC-SA 4.0 (Non-Commercial + ShareAlike)
- **Use**: Non-commercial only
- **Attribution**: Required
- **Share-Alike**: Required
- **Datasets**: Some research datasets
- **Sisi Lola Status**: ⚠️ CHECK CAREFULLY - May not be usable for commercial products

---

## ❌ Restrictive Licenses

### Research/Academic Only
- **Use**: Non-commercial/research only
- **Datasets**: 
  - Some NaijaVoices subsets
  - Nigerian Pidgin ASR 1.0
  - Various academic paper datasets
- **Sisi Lola Status**: ❌ DO NOT USE for commercial products

### Custom Academic Licenses
- **Use**: Varies - often research only
- **Datasets**: University research projects
- **Sisi Lola Status**: ❌ CONTACT AUTHORS before use

---

## Quick Reference Table

| License | Commercial Use | Attribution | ShareAlike | Sisi Lola Safe |
|---------|---------------|-------------|------------|----------------|
| CC0-1.0 | ✅ Yes | ❌ No | ❌ No | ✅ YES |
| MIT | ✅ Yes | ✅ Yes | ❌ No | ✅ YES |
| CC-BY 4.0 | ✅ Yes | ✅ Yes | ❌ No | ✅ YES |
| CC-BY-SA 4.0 | ✅ Yes | ✅ Yes | ✅ Yes | ✅ YES |
| Apache 2.0 | ✅ Yes | ✅ Yes | ❌ No | ✅ YES |
| CC-BY-NC 4.0 | ❌ No | ✅ Yes | ❌ No | ❌ NO |
| CC-BY-NC-SA 4.0 | ❌ No | ✅ Yes | ✅ Yes | ❌ NO |
| Research Only | ❌ No | Varies | Varies | ❌ NO |

---

## Recommendation for Sisi Lola

### Priority Order for Dataset Selection:

1. **First Choice**: CC0 and MIT licensed datasets
   - No legal complications
   - Maximum flexibility

2. **Second Choice**: CC-BY 4.0 licensed datasets
   - Just need attribution in credits/documentation

3. **Third Choice**: CC-BY-SA 4.0 licensed datasets
   - Good quality (BibleTTS is studio-quality)
   - Models trained on this data should be shared under same terms
   - Document the source datasets used

4. **Fourth Choice**: Apache 2.0 licensed datasets
   - Include NOTICE file
   - Good for code/model weights

5. **Avoid**: CC-BY-NC, Research-only, or unclear licenses
   - Risk of legal issues
   - Contact authors if dataset is essential

---

## Attribution Template

When using attributed datasets, include this in your documentation/credits:

```
Sisi Lola Voice Model Attribution

This voice model was trained using the following datasets:

- BibleTTS (CC-BY-SA 4.0): https://openslr.org/129/
  Authors: Doreen Amolor, et al.
  
- FLEURS (CC-BY 4.0): https://huggingface.co/datasets/google/fleurs
  Authors: Google Research
  
- Mozilla Common Voice Nigerian Pidgin (CC0): https://commonvoice.mozilla.org/
  Contributors: Mozilla Foundation and Community

- OpenSLR-86 Yoruba (CC-BY-SA 4.0): https://openslr.org/86/
  Authors: Google and collaborators
```

---

## License Verification Checklist

Before adding a dataset to Sisi Lola training:

- [ ] Identify the license type
- [ ] Confirm commercial use is allowed
- [ ] Note attribution requirements
- [ ] Check for ShareAlike implications
- [ ] Document the source in manifest
- [ ] Add to attribution credits if required
- [ ] Verify no additional terms in README/LICENSE files

---

## Contact for Unclear Licenses

If a dataset has unclear licensing:

1. Check the dataset README and LICENSE files
2. Look for academic papers citing the dataset
3. Contact the dataset authors directly
4. When in doubt, don't use it for commercial products

---

## Updates

This guide should be updated as new datasets are discovered or license terms change.

Last Updated: December 2025
Maintained by: Sisi Lola Voice Dataset Curator
