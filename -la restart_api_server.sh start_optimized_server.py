[33mcommit e749d45bef5b918f0d7780f5039f3e75782d87ea[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m)[m
Author: Sisi Lola Project <sisilolalive@gmail.com>
Date:   Thu Dec 18 03:59:48 2025 -0500

    Fix: Bracket pollution, response formatting, and optimization activation
    
    - Added _remove_bracket_pollution() to strip [Word] patterns while keeping valid language tags [EN], [NP], etc.
    - Added _add_paragraph_formatting() to break long responses into readable paragraphs
    - Updated optimized_inference.py with _post_process_response() for the Nigerian models path
    - Updated frontend cleanTextForDisplay() with same fixes
    - Added environment variables for model optimization (MODEL_CACHE_ENABLED, RESPONSE_CACHE_ENABLED)
    - Created restart_api_server.sh and start_optimized_server.py deployment scripts
    
    Fixes: 70s response time (needs server restart), bracket pollution, lack of paragraphs

 .gitattributes                     |   2 [31m-[m
 .../scripts/optimized_inference.py |  69 [32m+++++[m
 restart_api_server.sh              |  68 [32m+++++[m
 .../app/services/prompt_engine.py  |  84 [32m+++++[m
 sisi_lola_api/static/index.html    |  41 [32m++[m[31m-[m
 start_optimized_server.py          | 169 [32m+++++++++++[m
 6 files changed, 424 insertions(+), 9 deletions(-)
