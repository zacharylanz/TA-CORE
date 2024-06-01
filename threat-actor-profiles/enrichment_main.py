# enrichment_main.py

import os
import yaml
from PyPDF2 import PdfFileReader
import docx
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from enrichment_dictionary import CRITICAL_INFRASTRUCTURE_SECTORS, MOTIVATIONS

# Ensure nltk data is downloaded
nltk.download('punkt')
nltk.download('stopwords')

THREAT_REPORTS_DIR = "threat_reports"
PROFILES_DIR = "profiles"

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def save_yaml(data, file_path):
    with open(file_path, 'w') as file:
        yaml.dump(data, file, sort_keys=False)

def merge_additional_info(profile, additional_info):
    updated = False
    for key, value in additional_info.items():
        if key in profile:
            if isinstance(profile[key], list) and isinstance(value, list):
                initial_length = len(profile[key])
                profile[key].extend(x for x in value if x not in profile[key])
                if len(profile[key]) > initial_length:
                    updated = True
            elif isinstance(profile[key], dict) and isinstance(value, dict):
                initial_keys = set(profile[key].keys())
                profile[key].update(value)
                if set(profile[key].keys()) > initial_keys:
                    updated = True
            else:
                if profile[key] != value:
                    profile[key] = value
                    updated = True
        else:
            profile[key] = value
            updated = True
    return updated

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PdfFileReader(file)
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
    return text

def extract_text_from_word(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_text(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def parse_additional_source(file_path):
    print(f"Parsing file: {file_path}")
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_word(file_path)
    elif file_path.endswith(".txt"):
        text = extract_text_from_text(file_path)
    else:
        raise ValueError("Unsupported file type")
    
    print(f"Extracted text: {text[:500]}...")  # Print first 500 characters of extracted text for debugging
    
    motivations = [motivation for motivation in MOTIVATIONS if motivation.lower() in text.lower()]
    target_sectors = [sector for sector in CRITICAL_INFRASTRUCTURE_SECTORS if sector.lower() in text.lower()]
    
    return {
        "motivations": motivations,
        "target sectors": target_sectors,
        "descriptions": text[:500]  # Keep a short snippet for description
    }

def find_matching_profile(profiles, text):
    for profile_name, profile in profiles.items():
        if profile_name.lower() in text.lower():
            print(f"Match found for profile name: {profile_name}")
            return profile_name, profile
        if any(alias.lower() in text.lower() for alias in profile.get("aliases", [])):
            print(f"Match found for alias in profile: {profile_name}")
            return profile_name, profile
    return None, None

def main():
    # Load all profiles
    profiles = {}
    for profile_file in os.listdir(PROFILES_DIR):
        profile_path = os.path.join(PROFILES_DIR, profile_file)
        profile_name = os.path.splitext(profile_file)[0]
        profiles[profile_name] = load_yaml(profile_path)
    
    print("Loaded profiles:")
    for name, profile in profiles.items():
        print(f"{name}: {profile.get('aliases', [])}")
    
    for file_name in os.listdir(THREAT_REPORTS_DIR):
        file_path = os.path.join(THREAT_REPORTS_DIR, file_name)
        
        try:
            additional_info = parse_additional_source(file_path)
            report_text = additional_info["descriptions"]
            
            matching_profile_name, matching_profile = find_matching_profile(profiles, report_text)
            
            if matching_profile_name:
                print(f"Updating profile: {matching_profile_name}")
                updated = merge_additional_info(matching_profile, additional_info)
                if updated:
                    profile_path = os.path.join(PROFILES_DIR, f"{matching_profile_name}.yaml")
                    save_yaml(matching_profile, profile_path)
                    print(f"Profile {matching_profile_name} updated with new information from {file_name}.")
                else:
                    print(f"No new information to update for profile {matching_profile_name}.")
            else:
                print(f"No matching profile found for the report {file_name}.")
        
        except ValueError as e:
            print(e)

if __name__ == "__main__":
    main()
