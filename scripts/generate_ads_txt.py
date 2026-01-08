#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text file generator ads.txt from validated Google Ads
"""
import json
import sys
import os
import argparse
from datetime import datetime

def generate_ads_txt(validated_data: dict) -> str:
    """Generates formatted ad text for .txt file"""
    
    lines = []
    lines.append("=" * 70)
    lines.append("🎯 GOOGLE ADS - READY TEXTS TO COPY")
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
    lines.append("📝 HEADLINES")
    lines.append("-" * 40)
    
    headlines = []
    if 'headlines_validation' in validated_data:
        for item in validated_data['headlines_validation']:
            headlines.append(item['text'])
    
    # Number headlines
    for i, headline in enumerate(headlines, 1):
        lines.append(f"{i:2}. {headline}")
    
    lines.append("")
    lines.append(f"Total headlines: {len(headlines)}")
    
    # Descriptions
    lines.append("")
    lines.append("-" * 70)
    lines.append("")
    lines.append("📄 DESCRIPTIONS")
    lines.append("-" * 40)
    
    descriptions = []
    if 'descriptions_validation' in validated_data:
        for item in validated_data['descriptions_validation']:
            descriptions.append(item['text'])
    
    # Number descriptions
    for i, description in enumerate(descriptions, 1):
        lines.append(f"{i}. {description}")
    
    lines.append("")
    lines.append(f"Total descriptions: {len(descriptions)}")
    
    # URL Paths
    lines.append("")
    lines.append("-" * 70)
    lines.append("")
    lines.append("🔗 URL PATHS (Display Paths)")
    lines.append("-" * 40)
    
    paths = []
    if 'paths_validation' in validated_data:
        for item in validated_data['paths_validation']:
            paths.append(item['text'])
    
    # Display paths
    for i, path in enumerate(paths, 1):
        lines.append(f"Path {i}: {path}")
    
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
    lines.append("DESCRIPTIONS:")
    for description in descriptions:
        lines.append(description)
    
    lines.append("")
    lines.append("PATHS:")
    for path in paths:
        lines.append(path)
    
    # Statistics
    lines.append("")
    lines.append("=" * 70)
    lines.append("📊 STATISTICS")
    lines.append("=" * 70)
    
    # Calculate average lengths
    avg_headline_len = sum(len(h) for h in headlines) / len(headlines) if headlines else 0
    avg_description_len = sum(len(d) for d in descriptions) / len(descriptions) if descriptions else 0
    
    lines.append(f"• Number of headlines: {len(headlines)} (required: 3-15)")
    lines.append(f"• Number of descriptions: {len(descriptions)} (required: 2-4)")
    lines.append(f"• Number of paths: {len(paths)} (required: 2)")
    lines.append(f"• Average headline length: {avg_headline_len:.1f} characters (max 30)")
    lines.append(f"• Average description length: {avg_description_len:.1f} characters (max 90)")
    
    # Validation status
    lines.append("")
    if validated_data.get('all_valid'):
        lines.append("✅ STATUS: All elements passed validation successfully!")
    else:
        lines.append("⚠️ STATUS: Some elements require corrections")
        if validated_data.get('count_errors'):
            lines.append("Errors:")
            for error in validated_data['count_errors']:
                lines.append(f"  - {error}")
    
    lines.append("")
    lines.append("=" * 70)
    lines.append("End of report")
    lines.append("=" * 70)
    
    return "\n".join(lines)

def main():
    """Main function - reads validated_ad.json and generates ads.txt"""
    
    parser = argparse.ArgumentParser(description="Generates ads.txt file from validated Google Ads.")
    parser.add_argument('-o', '--output', type=str, default='ads.txt',
                        help='Output file name (default: ads.txt)')
    parser.add_argument('-d', '--dir', type=str, default='ads',
                        help='Target directory for output file (default: ads)')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='Automatically confirm file generation in case of validation warnings')
    parser.add_argument('input_file', type=str, nargs='?', default=os.path.join('tmp', 'ads_validated.json'),
                        help='Path to input *_validated.json file (default: tmp/ads_validated.json)')
    args = parser.parse_args()

    validated_file = args.input_file
    
    if not os.path.exists(validated_file):
        print(f"❌ ERROR: Input file '{validated_file}' does not exist.")
        print("First run validation: python3 scripts/validate_google_ads.py")
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
        print("⚠️ WARNING: Ad did not pass full validation!")
        print("Some elements may require corrections.")
        response = input(f"Do you still want to generate file {args.output}? (y/n): ")
        if response.lower() != 'y':
            print("File generation cancelled.")
            sys.exit(1)
    
    # Generate text
    ads_text = generate_ads_txt(validated_data)
    
    # Determine output file path
    output_dir = args.dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created target directory: {output_dir}")

    ads_txt_file = os.path.join(output_dir, args.output)
    
    # Save to file
    try:
        with open(ads_txt_file, 'w', encoding='utf-8') as f:
            f.write(ads_text)
        
        print("=" * 60)
        print(f"✅ SUCCESS: File '{ads_txt_file}' has been generated!")
        print("=" * 60)
        print(f"📁 Location: {ads_txt_file}")
        print("")
        print("📋 File contains:")
        print(f"  • {len(validated_data.get('headlines_validation', []))} headlines")
        print(f"  • {len(validated_data.get('descriptions_validation', []))} descriptions")
        print(f"  • {len(validated_data.get('paths_validation', []))} URL paths")
        print("")
        print(f"💡 Tip: You can now copy content from file {os.path.basename(ads_txt_file)}")
        print("   directly to Google Ads interface.")
        
        # Optionally display content
        print("\n" + "=" * 60)
        print("CONTENT PREVIEW:")
        print("=" * 60)
        # Display first 20 lines
        preview_lines = ads_text.split('\n')[:25]
        for line in preview_lines:
            print(line)
        if len(ads_text.split('\n')) > 25:
            print("...")
            print(f"(Full content in file {args.output})")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ ERROR while saving file {ads_txt_file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
