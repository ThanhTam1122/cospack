#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Postal Code to JIS Code Converter
---------------------------------

This script converts the Japan Post's postal code CSV data to a format suitable
for importing into the HAN99MA45POSTALJIS table. It extracts postal codes and 
matches them with JIS codes based on prefecture and city information.

Usage:
    python postal_code_converter.py [input_file] [output_file]

Example:
    python postal_code_converter.py ken_all.csv postal_jis_mapping.csv

Downloads:
    Get the latest postal data from: https://www.post.japanpost.jp/zipcode/dl/utf-zip.html
"""

import csv
import sys
import re
import os
from datetime import datetime

# JIS code mapping for prefectures
# Format: {prefecture_name: prefecture_code}
PREFECTURE_CODES = {
    '北海道': '01', '青森県': '02', '岩手県': '03', '宮城県': '04', '秋田県': '05',
    '山形県': '06', '福島県': '07', '茨城県': '08', '栃木県': '09', '群馬県': '10',
    '埼玉県': '11', '千葉県': '12', '東京都': '13', '神奈川県': '14', '新潟県': '15',
    '富山県': '16', '石川県': '17', '福井県': '18', '山梨県': '19', '長野県': '20',
    '岐阜県': '21', '静岡県': '22', '愛知県': '23', '三重県': '24', '滋賀県': '25',
    '京都府': '26', '大阪府': '27', '兵庫県': '28', '奈良県': '29', '和歌山県': '30',
    '鳥取県': '31', '島根県': '32', '岡山県': '33', '広島県': '34', '山口県': '35',
    '徳島県': '36', '香川県': '37', '愛媛県': '38', '高知県': '39', '福岡県': '40',
    '佐賀県': '41', '長崎県': '42', '熊本県': '43', '大分県': '44', '宮崎県': '45',
    '鹿児島県': '46', '沖縄県': '47'
}

# City code patterns - this is a simplified approach
# In a production system, these would be loaded from a comprehensive reference table
SPECIAL_CITY_CODES = {
    # Tokyo special wards (23区)
    '千代田区': '101', '中央区': '102', '港区': '103', '新宿区': '104', '文京区': '105',
    '台東区': '106', '墨田区': '107', '江東区': '108', '品川区': '109', '目黒区': '110',
    '大田区': '111', '世田谷区': '112', '渋谷区': '113', '中野区': '114', '杉並区': '115',
    '豊島区': '116', '北区': '117', '荒川区': '118', '板橋区': '119', '練馬区': '120',
    '足立区': '121', '葛飾区': '122', '江戸川区': '123',
    
    # Other major cities
    '横浜市': '101', '川崎市': '102', '相模原市': '103',  # Kanagawa
    '札幌市': '101', '仙台市': '101', 'さいたま市': '101', '千葉市': '101',
    '静岡市': '101', '浜松市': '102',  # Shizuoka
    '名古屋市': '101', '京都市': '101', '大阪市': '101', '神戸市': '101',
    '広島市': '101', '北九州市': '101', '福岡市': '102',  # Fukuoka
}

def get_jis_code(prefecture_name, city_name):
    """
    Create a 5-digit JIS code from prefecture and city names.
    
    The code follows the JIS X 0401/0402 standard format:
    - First 2 digits: Prefecture code (01-47)
    - Last 3 digits: City/ward code
    
    Args:
        prefecture_name: Prefecture name (e.g., '東京都')
        city_name: City/ward name (e.g., '千代田区')
    
    Returns:
        5-digit JIS code string
    """
    # Get prefecture code
    prefecture_code = PREFECTURE_CODES.get(prefecture_name, '00')
    
    # Check for special cities/wards
    city_code = None
    
    # Extract main city name from city_name (handle districts within cities)
    main_city_match = re.match(r'(.+?[市区町村])', city_name)
    main_city = main_city_match.group(1) if main_city_match else city_name
    
    # Look for exact matches in our special city code dictionary
    if main_city in SPECIAL_CITY_CODES:
        city_code = SPECIAL_CITY_CODES[main_city]
    else:
        # For other cities/towns/villages, use a pattern based on city type
        if '区' in city_name:
            # District within a designated city
            district_match = re.match(r'(.+市)(.+区)', city_name)
            if district_match:
                city = district_match.group(1)
                district = district_match.group(2)
                if city in SPECIAL_CITY_CODES:
                    # Within a major city, calculate district code
                    city_base = SPECIAL_CITY_CODES[city]
                    # This is a simplification - actual implementation would use a lookup table
                    district_num = 1  # Default district number
                    city_code = f"{city_base}{district_num:01d}"
        
        # Default handling for cities/towns/villages
        if city_code is None:
            if '市' in main_city:
                city_code = '201'  # Standard city
            elif '町' in main_city:
                city_code = '301'  # Town
            elif '村' in main_city:
                city_code = '401'  # Village
            else:
                city_code = '000'  # Unknown/other
    
    # If we still don't have a city code, use default
    if not city_code:
        city_code = '000'
    
    # Ensure city_code is 3 digits
    city_code = city_code.zfill(3)
    
    return f"{prefecture_code}{city_code}"

def convert_postal_code_data(input_file, output_file):
    """
    Convert Japan Post postal code data to JIS code mapping format.
    
    Args:
        input_file: Path to the Japan Post CSV file
        output_file: Path to the output CSV file
        
    Returns:
        Number of records processed
    """
    count = 0
    records = {}  # Use dict to avoid duplicates
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            for row in reader:
                try:
                    # Japan Post CSV format:
                    # 0: 全国地方公共団体コード, 1: 郵便番号(5桁), 2: 郵便番号(7桁)
                    # 3: 都道府県名カナ, 4: 市区町村名カナ, 5: 町域名カナ
                    # 6: 都道府県名, 7: 市区町村名, 8: 町域名
                    
                    # Extract the data we need
                    postal_code = row[2].strip()  # 7-digit postal code
                    prefecture_name = row[6].strip()
                    city_name = row[7].strip()
                    street_name = row[8].strip()
                    
                    # Skip if missing required data
                    if not postal_code or not prefecture_name or not city_name:
                        continue
                    
                    # Generate JIS code
                    jis_code = get_jis_code(prefecture_name, city_name)
                    
                    # Create a key to avoid duplicates
                    key = postal_code
                    if key not in records:
                        records[key] = [postal_code, jis_code, prefecture_name, city_name, street_name]
                        count += 1
                
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            # Write header
            writer.writerow(['PostalCode', 'JISCode', 'PrefectureName', 'CityName', 'StreetName'])
            # Write data
            for record in records.values():
                writer.writerow(record)
        
        print(f"Conversion complete. Processed {count} records.")
        return count
    
    except Exception as e:
        print(f"Error converting postal code data: {e}")
        return 0

def main():
    """Main function to handle script execution."""
    if len(sys.argv) < 3:
        print("Usage: python postal_code_converter.py [input_file] [output_file]")
        return
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    print(f"Converting postal code data from {input_file} to {output_file}...")
    start_time = datetime.now()
    count = convert_postal_code_data(input_file, output_file)
    end_time = datetime.now()
    
    print(f"Processed {count} records in {(end_time - start_time).total_seconds():.2f} seconds.")
    
    if count > 0:
        print(f"Output saved to: {output_file}")
        print("Next steps:")
        print("1. Review the output file for accuracy")
        print("2. Import the data into the HAN99MA45POSTALJIS table using SQL BULK INSERT")

if __name__ == "__main__":
    main() 