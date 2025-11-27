"""
Data Quality & Coverage Evaluation for Sisi Lola MLOps

Technical Explanation:
- Analyzes ingested datasets for completeness, quality, and balance
- Checks code-switching patterns, language distribution, audio metrics
- Generates reports for decision-making (which languages need more data)

Layman Explanation:
This is like a "health check" for our training data. It tells us:
- Do we have enough examples in each language?
- Is the audio quality good enough?
- Are we missing important patterns (like Yoruba-English mixing)?

Usage:
    python dataset_coverage_report.py --manifest data/processed/asr_manifest_all.tsv --output reports/coverage.json
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict


def analyze_language_distribution(manifest_tsv: Path) -> Dict:
    """
    Analyze language balance across dataset.
    
    Technical: Counts samples, total duration, split distribution per language.
    Layman: Shows how many voice samples we have for each language.
    """
    lang_stats = defaultdict(lambda: {
        "total_samples": 0,
        "total_duration_hours": 0.0,
        "splits": Counter(),
        "speakers": set()
    })
    
    with open(manifest_tsv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            lang = row["language"]
            duration = float(row.get("duration_sec", 0))
            split = row.get("split", "unknown")
            speaker = row.get("speaker_id", "unknown")
            
            lang_stats[lang]["total_samples"] += 1
            lang_stats[lang]["total_duration_hours"] += duration / 3600
            lang_stats[lang]["splits"][split] += 1
            lang_stats[lang]["speakers"].add(speaker)
    
    # Convert to serializable format
    result = {}
    for lang, stats in lang_stats.items():
        result[lang] = {
            "total_samples": stats["total_samples"],
            "total_duration_hours": round(stats["total_duration_hours"], 2),
            "splits": dict(stats["splits"]),
            "unique_speakers": len(stats["speakers"])
        }
    
    return result


def analyze_code_switching_patterns(segments_csv: Path) -> Dict:
    """
    Analyze code-switching frequency and patterns.
    
    Technical: Counts mixed-language segments, detects switch boundaries.
    Layman: Shows how often people mix languages (like Yoruba + English).
    """
    total_segments = 0
    code_switched = 0
    language_pairs = Counter()
    
    with open(segments_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        prev_lang = None
        for row in reader:
            total_segments += 1
            lang = row["language"]
            
            # Detect code-switching within single utterance
            if "-" in lang or lang == "mixed":
                code_switched += 1
            
            # Detect boundary switches
            if prev_lang and prev_lang != lang:
                pair = tuple(sorted([prev_lang, lang]))
                language_pairs[pair] += 1
            
            prev_lang = lang
    
    return {
        "total_segments": total_segments,
        "code_switched_segments": code_switched,
        "code_switch_rate": round(code_switched / total_segments, 3) if total_segments > 0 else 0,
        "common_language_pairs": dict(language_pairs.most_common(10))
    }


def analyze_text_quality(manifest_tsv: Path) -> Dict:
    """
    Analyze text transcription quality.
    
    Technical: Checks for empty texts, diacritic usage (Yoruba), length distribution.
    Layman: Makes sure the written transcriptions are complete and correct.
    """
    total_texts = 0
    empty_texts = 0
    yoruba_with_diacritics = 0
    yoruba_total = 0
    length_stats = []
    
    with open(manifest_tsv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            total_texts += 1
            text = row.get("text", "")
            lang = row["language"]
            
            if not text or text.strip() == "":
                empty_texts += 1
                continue
            
            length_stats.append(len(text))
            
            # Check Yoruba diacritics
            if lang in ["yo", "yo_ng"]:
                yoruba_total += 1
                if any(c in text for c in "áàéèíìóòúùẹọṣ"):
                    yoruba_with_diacritics += 1
    
    return {
        "total_texts": total_texts,
        "empty_texts": empty_texts,
        "avg_text_length": round(sum(length_stats) / len(length_stats), 1) if length_stats else 0,
        "min_text_length": min(length_stats) if length_stats else 0,
        "max_text_length": max(length_stats) if length_stats else 0,
        "yoruba_diacritic_coverage": round(yoruba_with_diacritics / yoruba_total, 3) if yoruba_total > 0 else 0
    }


def generate_recommendations(report: Dict) -> List[str]:
    """
    Generate actionable recommendations based on analysis.
    
    Technical: Rule-based heuristics to suggest next steps.
    Layman: Tells you what to do next to improve the dataset.
    """
    recommendations = []
    
    lang_dist = report.get("language_distribution", {})
    
    # Check for underrepresented languages
    for lang, stats in lang_dist.items():
        if stats["total_duration_hours"] < 1.0:
            recommendations.append(
                f"⚠️  {lang}: Only {stats['total_duration_hours']:.1f} hours. "
                f"Need at least 5 hours for good ASR. Consider more recordings."
            )
        
        if stats["unique_speakers"] < 5:
            recommendations.append(
                f"⚠️  {lang}: Only {stats['unique_speakers']} speakers. "
                f"Need 10+ for accent diversity. Recruit more voice actors."
            )
    
    # Check code-switching
    cs_stats = report.get("code_switching_patterns", {})
    if cs_stats.get("code_switch_rate", 0) < 0.1:
        recommendations.append(
            "💡 Low code-switching rate (<10%). Add mixed Yoruba-English samples "
            "for better Yorunglish handling."
        )
    
    # Check Yoruba diacritics
    text_quality = report.get("text_quality", {})
    if text_quality.get("yoruba_diacritic_coverage", 1.0) < 0.5:
        recommendations.append(
            "⚠️  Less than 50% of Yoruba texts have diacritics. "
            "This will hurt tone accuracy. Review and add diacritics."
        )
    
    if not recommendations:
        recommendations.append("✅ Dataset looks good! Ready for training.")
    
    return recommendations


def generate_report(
    asr_manifest: Path,
    code_switch_segments: Path | None,
    output_json: Path
) -> None:
    """
    Generate comprehensive data quality report.
    
    Technical: Aggregates all metrics, generates JSON report + recommendations.
    Layman: Creates a full "report card" for the training data.
    """
    report = {}
    
    # Language distribution
    if asr_manifest.exists():
        print("Analyzing language distribution...")
        report["language_distribution"] = analyze_language_distribution(asr_manifest)
    
    # Code-switching patterns
    if code_switch_segments and code_switch_segments.exists():
        print("Analyzing code-switching patterns...")
        report["code_switching_patterns"] = analyze_code_switching_patterns(code_switch_segments)
    
    # Text quality
    if asr_manifest.exists():
        print("Analyzing text quality...")
        report["text_quality"] = analyze_text_quality(asr_manifest)
    
    # Generate recommendations
    report["recommendations"] = generate_recommendations(report)
    
    # Write report
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Report saved to {output_json}")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DATA QUALITY REPORT SUMMARY")
    print("="*60)
    
    if "language_distribution" in report:
        print("\n🌍 Language Coverage:")
        for lang, stats in sorted(report["language_distribution"].items()):
            print(f"  {lang:8} {stats['total_samples']:>6} samples  "
                  f"{stats['total_duration_hours']:>6.1f}h  "
                  f"{stats['unique_speakers']:>3} speakers")
    
    if "text_quality" in report:
        tq = report["text_quality"]
        print(f"\n📝 Text Quality:")
        print(f"  Avg length: {tq['avg_text_length']} chars")
        print(f"  Yoruba diacritic coverage: {tq['yoruba_diacritic_coverage']*100:.1f}%")
    
    if "code_switching_patterns" in report:
        cs = report["code_switching_patterns"]
        print(f"\n🔀 Code-Switching:")
        print(f"  Rate: {cs['code_switch_rate']*100:.1f}%")
        print(f"  Common pairs: {list(cs.get('common_language_pairs', {}).keys())[:3]}")
    
    print("\n💡 Recommendations:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate data quality report")
    parser.add_argument(
        "--asr-manifest",
        type=str,
        default="data/processed/asr_manifest_all.tsv",
        help="Path to ASR manifest TSV"
    )
    parser.add_argument(
        "--code-switch-segments",
        type=str,
        help="Path to code-switch segments CSV (optional)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/reports/coverage_report.json",
        help="Output JSON report path"
    )
    args = parser.parse_args()
    
    generate_report(
        Path(args.asr_manifest),
        Path(args.code_switch_segments) if args.code_switch_segments else None,
        Path(args.output)
    )
