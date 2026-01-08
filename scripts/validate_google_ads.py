#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Ads validator - checks text length and element counts
"""
import json
import sys
import os
import argparse
from typing import List, Dict, Tuple

class GoogleAdsValidator:
    def __init__(self):
        self.limits = {
            'headline': 30,
            'description': 90,
            'path': 15
        }
        # Google Ads requirements for element counts
        self.count_requirements = {
            'headlines': {'min': 3, 'max': 15},
            'descriptions': {'min': 2, 'max': 4},
            'paths': {'min': 2, 'max': 2}  # exactly 2
        }
    
    def validate_text(self, text: str, text_type: str) -> Dict:
        """Validates single text"""
        limit = self.limits.get(text_type, 30)
        length = len(text)
        is_valid = length <= limit
        
        result = {
            'text': text,
            'length': length,
            'limit': limit,
            'valid': is_valid,
            'status': '✅' if is_valid else '❌'
        }
        
        if not is_valid:
            result['overflow'] = length - limit
            result['suggestion'] = self.suggest_shortening(text, limit)
        
        return result
    
    def suggest_shortening(self, text: str, max_length: int) -> str:
        """Suggests shortened version of text"""
        if len(text) <= max_length:
            return text
        
        # Method 1: Remove last words
        words = text.split()
        shortened = ""
        for word in words:
            test = (shortened + " " + word).strip()
            if len(test) <= max_length:
                shortened = test
            else:
                break
        
        # If still too long, cut and add "..."
        if len(shortened) > max_length:
            shortened = text[:max_length-3] + "..."
        
        return shortened
    
    def validate_count(self, element_type: str, count: int) -> Dict:
        """Checks if element count is correct"""
        req = self.count_requirements.get(element_type, {})
        min_count = req.get('min', 0)
        max_count = req.get('max', 999)
        
        is_valid = min_count <= count <= max_count
        
        result = {
            'type': element_type,
            'count': count,
            'min': min_count,
            'max': max_count,
            'valid': is_valid,
            'status': '✅' if is_valid else '❌'
        }
        
        if not is_valid:
            if count < min_count:
                result['error'] = f"Too few elements (minimum: {min_count})"
            else:
                result['error'] = f"Too many elements (maximum: {max_count})"
        
        return result
    
    def validate_headlines(self, headlines: List[str]) -> List[Dict]:
        """Validates list of headlines"""
        return [self.validate_text(h, 'headline') for h in headlines]
    
    def validate_descriptions(self, descriptions: List[str]) -> List[Dict]:
        """Validates list of descriptions"""
        return [self.validate_text(d, 'description') for d in descriptions]
    
    def validate_paths(self, paths: List[str]) -> List[Dict]:
        """Validates URL paths"""
        return [self.validate_text(p, 'path') for p in paths]
    
    def generate_report(self, ad_data: Dict) -> str:
        """Generates validation report"""
        report = []
        report.append("=" * 60)
        report.append("📊 GOOGLE ADS VALIDATION REPORT")
        report.append("=" * 60)
        
        # Check element counts
        count_errors = []
        
        if 'headlines' in ad_data:
            headlines_count = self.validate_count('headlines', len(ad_data['headlines']))
            if not headlines_count['valid']:
                count_errors.append(f"❌ Headlines: {headlines_count['count']} (required: {headlines_count['min']}-{headlines_count['max']})")
                report.append(f"\n❌ ERROR: {headlines_count['error']}")
        
        if 'descriptions' in ad_data:
            descriptions_count = self.validate_count('descriptions', len(ad_data['descriptions']))
            if not descriptions_count['valid']:
                count_errors.append(f"❌ Descriptions: {descriptions_count['count']} (required: {descriptions_count['min']}-{descriptions_count['max']})")
                report.append(f"\n❌ ERROR: {descriptions_count['error']}")
        
        if 'paths' in ad_data:
            paths_count = self.validate_count('paths', len(ad_data['paths']))
            if not paths_count['valid']:
                count_errors.append(f"❌ URL Paths: {paths_count['count']} (required: exactly {paths_count['min']})")
                report.append(f"\n❌ ERROR: {paths_count['error']}")
        
        # Headlines validation
        if 'headlines' in ad_data:
            report.append(f"\n📝 HEADLINES ({len(ad_data['headlines'])} items, max 30 characters):")
            report.append("-" * 40)
            for i, result in enumerate(self.validate_headlines(ad_data['headlines']), 1):
                report.append(f"{i:2}. {result['status']} [{result['length']:2}/{result['limit']}] \"{result['text']}\"")
                if not result['valid']:
                    report.append(f"    💡 Suggestion: \"{result['suggestion']}\"")
        
        # Descriptions validation
        if 'descriptions' in ad_data:
            report.append(f"\n📄 DESCRIPTIONS ({len(ad_data['descriptions'])} items, max 90 characters):")
            report.append("-" * 40)
            for i, result in enumerate(self.validate_descriptions(ad_data['descriptions']), 1):
                report.append(f"{i}. {result['status']} [{result['length']:2}/{result['limit']}] \"{result['text']}\"")
                if not result['valid']:
                    report.append(f"   💡 Suggestion: \"{result['suggestion']}\"")
        
        # Paths validation
        if 'paths' in ad_data:
            report.append(f"\n🔗 URL PATHS ({len(ad_data['paths'])} items, max 15 characters):")
            report.append("-" * 40)
            for i, result in enumerate(self.validate_paths(ad_data['paths']), 1):
                report.append(f"Path {i}: {result['status']} [{result['length']:2}/{result['limit']}] \"{result['text']}\"")
                if not result['valid']:
                    report.append(f"        💡 Suggestion: \"{result['suggestion']}\"")
        
        # Summary
        report.append("\n" + "=" * 60)
        report.append("📈 SUMMARY:")
        
        # Element counts
        if 'headlines' in ad_data:
            h_count = self.validate_count('headlines', len(ad_data.get('headlines', [])))
            report.append(f"{h_count['status']} Number of headlines: {h_count['count']} (required: {h_count['min']}-{h_count['max']})")
        
        if 'descriptions' in ad_data:
            d_count = self.validate_count('descriptions', len(ad_data.get('descriptions', [])))
            report.append(f"{d_count['status']} Number of descriptions: {d_count['count']} (required: {d_count['min']}-{d_count['max']})")
        
        if 'paths' in ad_data:
            p_count = self.validate_count('paths', len(ad_data.get('paths', [])))
            report.append(f"{p_count['status']} Number of paths: {p_count['count']} (required: exactly {p_count['min']})")
        
        # Text lengths
        total_headlines = len(ad_data.get('headlines', []))
        valid_headlines = sum(1 for r in self.validate_headlines(ad_data.get('headlines', [])) if r['valid'])
        report.append(f"✅ Valid headlines (length): {valid_headlines}/{total_headlines}")
        
        total_descriptions = len(ad_data.get('descriptions', []))
        valid_descriptions = sum(1 for r in self.validate_descriptions(ad_data.get('descriptions', [])) if r['valid'])
        report.append(f"✅ Valid descriptions (length): {valid_descriptions}/{total_descriptions}")
        
        total_paths = len(ad_data.get('paths', []))
        valid_paths = sum(1 for r in self.validate_paths(ad_data.get('paths', [])) if r['valid'])
        report.append(f"✅ Valid paths (length): {valid_paths}/{total_paths}")
        
        return "\n".join(report)

def main():
    """Main function - reads data from JSON file and validates"""
    parser = argparse.ArgumentParser(description="Validates JSON file with Google Ads.")
    parser.add_argument('input_file', type=str, nargs='?', default=os.path.join('tmp', 'ads.json'),
                        help='Path to input JSON file (default: tmp/ads.json)')
    args = parser.parse_args()

    ads_file = args.input_file
    
    if not os.path.exists(ads_file):
        print(f"❌ ERROR: Input file '{ads_file}' does not exist.")
        sys.exit(1)
    
    TMP_DIR = os.path.dirname(ads_file)
    if not TMP_DIR:
        TMP_DIR = '.'
    
    # Load data from file
    try:
        with open(ads_file, 'r', encoding='utf-8') as f:
            ad_data = json.load(f)
    except json.JSONDecodeError:
        print(f"❌ ERROR: Invalid file format {ads_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR while reading file {ads_file}: {e}")
        sys.exit(1)
    
    # Check for required fields
    required_fields = ['headlines', 'descriptions', 'paths']
    missing_fields = [field for field in required_fields if field not in ad_data]
    
    if missing_fields:
        print(f"❌ ERROR: Missing required fields in ads.json: {missing_fields}")
        sys.exit(1)
    
    # Validation
    validator = GoogleAdsValidator()
    
    # Generate report
    print(validator.generate_report(ad_data))
    
    # Check if all elements are correct
    all_valid = True
    error_count = 0
    count_errors = []
    
    # Check element counts
    headlines_count = validator.validate_count('headlines', len(ad_data.get('headlines', [])))
    if not headlines_count['valid']:
        all_valid = False
        count_errors.append(f"Headlines: {headlines_count['error']}")
    
    descriptions_count = validator.validate_count('descriptions', len(ad_data.get('descriptions', [])))
    if not descriptions_count['valid']:
        all_valid = False
        count_errors.append(f"Descriptions: {descriptions_count['error']}")
    
    paths_count = validator.validate_count('paths', len(ad_data.get('paths', [])))
    if not paths_count['valid']:
        all_valid = False
        count_errors.append(f"Paths: {paths_count['error']}")
    
    # Check text lengths
    headlines_validation = validator.validate_headlines(ad_data.get('headlines', []))
    invalid_headlines = [h for h in headlines_validation if not h['valid']]
    if invalid_headlines:
        all_valid = False
        error_count += len(invalid_headlines)
    
    descriptions_validation = validator.validate_descriptions(ad_data.get('descriptions', []))
    invalid_descriptions = [d for d in descriptions_validation if not d['valid']]
    if invalid_descriptions:
        all_valid = False
        error_count += len(invalid_descriptions)
    
    paths_validation = validator.validate_paths(ad_data.get('paths', []))
    invalid_paths = [p for p in paths_validation if not p['valid']]
    if invalid_paths:
        all_valid = False
        error_count += len(invalid_paths)
    
    # Determine output file paths in same directory as input file
    base_name = os.path.basename(ads_file).replace('.json', '')
    validated_file = os.path.join(TMP_DIR, f"{base_name}_validated.json")
    corrected_file = os.path.join(TMP_DIR, f"{base_name}_corrected.json")
    
    # Save detailed validation results
    validated_data = {
        'campaign_name': ad_data.get('campaign_name', ''),
        'product': ad_data.get('product', ''),
        'url': ad_data.get('url', ''),
        'headlines_validation': headlines_validation,
        'descriptions_validation': descriptions_validation,
        'paths_validation': paths_validation,
        'headlines_count': headlines_count,
        'descriptions_count': descriptions_count,
        'paths_count': paths_count,
        'all_valid': all_valid,
        'error_count': error_count,
        'count_errors': count_errors
    }
    
    with open(validated_file, 'w', encoding='utf-8') as f:
        json.dump(validated_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 Detailed results saved in: {validated_file}")
    
    # If there are errors, save corrected suggestions
    if not all_valid:
        if count_errors:
            print(f"\n⚠️ ELEMENT COUNT ERRORS:")
            for error in count_errors:
                print(f"  - {error}")
        
        if error_count > 0:
            print(f"\n⚠️ LENGTH ERRORS: Found {error_count} texts exceeding limits!")
        
        # Prepare corrected data
        corrected_ad = {
            'campaign_name': ad_data.get('campaign_name', ''),
            'product': ad_data.get('product', ''),
            'url': ad_data.get('url', ''),
            'headlines': [],
            'descriptions': [],
            'paths': []
        }
        
        # Correct headlines
        for h in headlines_validation:
            if h['valid']:
                corrected_ad['headlines'].append(h['text'])
            else:
                corrected_ad['headlines'].append(h['suggestion'])
        
        # Correct descriptions
        for d in descriptions_validation:
            if d['valid']:
                corrected_ad['descriptions'].append(d['text'])
            else:
                corrected_ad['descriptions'].append(d['suggestion'])
        
        # Correct paths
        for p in paths_validation:
            if p['valid']:
                corrected_ad['paths'].append(p['text'])
            else:
                corrected_ad['paths'].append(p['suggestion'])
        
        # Save corrected data only if there were length errors
        if error_count > 0:
            with open(corrected_file, 'w', encoding='utf-8') as f:
                json.dump(corrected_ad, f, ensure_ascii=False, indent=2)
            print(f"💡 Length correction suggestions saved in: {corrected_file}")
        
        print("\n❌ VALIDATION FAILED - correct errors before generating report")
        sys.exit(1)
    else:
        print("\n✅ VALIDATION SUCCESSFUL - all elements meet Google Ads requirements!")
        sys.exit(0)

if __name__ == "__main__":
    main()
