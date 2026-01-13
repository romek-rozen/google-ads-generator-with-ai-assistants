#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text file generator for Performance Max (PMAX) ads
"""
import json
import sys
import os
import argparse
from datetime import datetime

MOBILE_HEADLINE_LIMIT = 15

def generate_pmax_txt(validated_data: dict) -> str:
    """Generates formatted PMAX ad text for .txt file"""

    lines = []
    lines.append("=" * 70)
    lines.append("🎯 PERFORMANCE MAX (PMAX) - READY TEXTS TO COPY")
    lines.append("=" * 70)
    lines.append(f"Generation date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Campaign information
    if validated_data.get('campaign_name'):
        lines.append(f"📌 Campaign: {validated_data['campaign_name']}")
    if validated_data.get('product'):
        lines.append(f"📦 Product/Service: {validated_data['product']}")
    if validated_data.get('url'):
        lines.append(f"🔗 Target URL: {validated_data['url']}")

    lines.append("")
    lines.append("-" * 70)

    # Headlines
    lines.append("")
    lines.append("📝 HEADLINES (max 30 chars)")
    lines.append("-" * 40)

    headlines = []
    if 'headlines_validation' in validated_data:
        for item in validated_data['headlines_validation']:
            headlines.append(item['text'])
    elif 'headlines' in validated_data:
        headlines = validated_data['headlines']

    # Number headlines with mobile indicator
    mobile_count = 0
    for i, headline in enumerate(headlines, 1):
        mobile_tag = ""
        if len(headline) <= MOBILE_HEADLINE_LIMIT:
            mobile_tag = " 📱"
            mobile_count += 1
        lines.append(f"{i:2}. {headline}{mobile_tag}")

    lines.append("")
    lines.append(f"Total headlines: {len(headlines)}")
    lines.append(f"Mobile-friendly (≤{MOBILE_HEADLINE_LIMIT} chars): {mobile_count}")

    # Long Headlines
    lines.append("")
    lines.append("-" * 70)
    lines.append("")
    lines.append("📝 LONG HEADLINES (max 90 chars)")
    lines.append("-" * 40)

    long_headlines = []
    if 'long_headlines_validation' in validated_data:
        for item in validated_data['long_headlines_validation']:
            long_headlines.append(item['text'])
    elif 'long_headlines' in validated_data:
        long_headlines = validated_data['long_headlines']

    # Number long headlines
    for i, headline in enumerate(long_headlines, 1):
        lines.append(f"{i}. {headline}")

    lines.append("")
    lines.append(f"Total long headlines: {len(long_headlines)}")

    # Descriptions
    lines.append("")
    lines.append("-" * 70)
    lines.append("")
    lines.append("📄 DESCRIPTIONS (max 90 chars)")
    lines.append("-" * 40)

    descriptions = []
    if 'descriptions_validation' in validated_data:
        for item in validated_data['descriptions_validation']:
            descriptions.append(item['text'])
    elif 'descriptions' in validated_data:
        descriptions = validated_data['descriptions']

    # Number descriptions
    for i, description in enumerate(descriptions, 1):
        lines.append(f"{i}. {description}")

    lines.append("")
    lines.append(f"Total descriptions: {len(descriptions)}")

    # URL Paths
    lines.append("")
    lines.append("-" * 70)
    lines.append("")
    lines.append("🔗 URL PATHS (Display Paths, max 15 chars)")
    lines.append("-" * 40)

    paths = []
    if 'paths_validation' in validated_data:
        for item in validated_data['paths_validation']:
            paths.append(item['text'])
    elif 'paths' in validated_data:
        paths = validated_data['paths']

    # Display paths
    for i, path in enumerate(paths, 1):
        lines.append(f"Path {i}: {path}")

    # CTA
    if validated_data.get('cta'):
        lines.append("")
        lines.append("-" * 70)
        lines.append("")
        lines.append("🔘 CALL TO ACTION (CTA)")
        lines.append("-" * 40)
        lines.append(validated_data['cta'])

    # Format for copying
    lines.append("")
    lines.append("=" * 70)
    lines.append("📋 QUICK COPY FORMAT")
    lines.append("=" * 70)
    lines.append("")
    lines.append("HEADLINES:")
    for headline in headlines:
        lines.append(headline)

    lines.append("")
    lines.append("LONG HEADLINES:")
    for headline in long_headlines:
        lines.append(headline)

    lines.append("")
    lines.append("DESCRIPTIONS:")
    for description in descriptions:
        lines.append(description)

    lines.append("")
    lines.append("PATHS:")
    for path in paths:
        lines.append(path)

    if validated_data.get('cta'):
        lines.append("")
        lines.append("CTA:")
        lines.append(validated_data['cta'])

    # Statistics
    lines.append("")
    lines.append("=" * 70)
    lines.append("📊 STATISTICS")
    lines.append("=" * 70)

    # Calculate average lengths
    avg_headline_len = sum(len(h) for h in headlines) / len(headlines) if headlines else 0
    avg_long_headline_len = sum(len(h) for h in long_headlines) / len(long_headlines) if long_headlines else 0
    avg_description_len = sum(len(d) for d in descriptions) / len(descriptions) if descriptions else 0

    lines.append(f"• Number of headlines: {len(headlines)} (required: 3-15)")
    lines.append(f"• Number of long headlines: {len(long_headlines)} (required: 1-5)")
    lines.append(f"• Number of descriptions: {len(descriptions)} (required: 3-5)")
    lines.append(f"• Number of paths: {len(paths)} (required: 2)")
    lines.append(f"• Mobile headlines (≤15 chars): {mobile_count} (required: min 1)")
    lines.append(f"• Average headline length: {avg_headline_len:.1f} chars (max 30)")
    lines.append(f"• Average long headline length: {avg_long_headline_len:.1f} chars (max 90)")
    lines.append(f"• Average description length: {avg_description_len:.1f} chars (max 90)")

    # Validation status
    lines.append("")
    if validated_data.get('all_valid'):
        lines.append("✅ STATUS: All elements passed PMAX validation successfully!")
    else:
        lines.append("⚠️ STATUS: Some elements require corrections")
        if validated_data.get('count_errors'):
            lines.append("Errors:")
            for error in validated_data['count_errors']:
                lines.append(f"  - {error}")

    lines.append("")
    lines.append("=" * 70)
    lines.append("End of PMAX report")
    lines.append("=" * 70)

    return "\n".join(lines)

def main():
    """Main function - reads validated PMAX JSON and generates txt file"""

    parser = argparse.ArgumentParser(description="Generates PMAX txt file from validated data.")
    parser.add_argument('-o', '--output', type=str, default='pmax.txt',
                        help='Output file name (default: pmax.txt)')
    parser.add_argument('-d', '--dir', type=str, default='ads',
                        help='Target directory for output file (default: ads)')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='Automatically confirm file generation in case of validation warnings')
    parser.add_argument('input_file', type=str, nargs='?', default=os.path.join('tmp', 'pmax_validated.json'),
                        help='Path to input *_validated.json file (default: tmp/pmax_validated.json)')
    args = parser.parse_args()

    validated_file = args.input_file

    if not os.path.exists(validated_file):
        print(f"❌ ERROR: Input file '{validated_file}' does not exist.")
        print("First run validation: python3 scripts/validate_pmax.py")
        sys.exit(1)

    # Load data
    try:
        with open(validated_file, 'r', encoding='utf-8') as f:
            validated_data = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ ERROR: Invalid file format {validated_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR while reading file {validated_file}: {e}")
        sys.exit(1)

    # Check validation status
    if not validated_data.get('all_valid') and not args.yes:
        print("⚠️ WARNING: PMAX ad did not pass full validation!")
        print("Some elements may require corrections.")
        response = input(f"Do you still want to generate file {args.output}? (y/n): ")
        if response.lower() != 'y':
            print("File generation cancelled.")
            sys.exit(1)

    # Generate text
    pmax_text = generate_pmax_txt(validated_data)

    # Determine output file path
    output_dir = args.dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created target directory: {output_dir}")

    output_file = os.path.join(output_dir, args.output)

    # Save to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pmax_text)

        print("=" * 60)
        print(f"✅ SUCCESS: File '{output_file}' has been generated!")
        print("=" * 60)
        print(f"📁 Location: {output_file}")
        print("")

        # Get counts from validated data
        headlines_count = len(validated_data.get('headlines_validation', validated_data.get('headlines', [])))
        long_headlines_count = len(validated_data.get('long_headlines_validation', validated_data.get('long_headlines', [])))
        descriptions_count = len(validated_data.get('descriptions_validation', validated_data.get('descriptions', [])))
        paths_count = len(validated_data.get('paths_validation', validated_data.get('paths', [])))

        print("📋 File contains:")
        print(f"  • {headlines_count} headlines")
        print(f"  • {long_headlines_count} long headlines")
        print(f"  • {descriptions_count} descriptions")
        print(f"  • {paths_count} URL paths")
        print("")
        print(f"💡 Tip: You can now copy content from file {os.path.basename(output_file)}")
        print("   directly to Google Ads Performance Max interface.")

        # Optionally display content
        print("\n" + "=" * 60)
        print("CONTENT PREVIEW:")
        print("=" * 60)
        # Display first 30 lines
        preview_lines = pmax_text.split('\n')[:30]
        for line in preview_lines:
            print(line)
        if len(pmax_text.split('\n')) > 30:
            print("...")
            print(f"(Full content in file {args.output})")

        sys.exit(0)

    except Exception as e:
        print(f"❌ ERROR while saving file {output_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
