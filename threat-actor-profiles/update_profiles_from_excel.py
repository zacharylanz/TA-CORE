import os
import pandas as pd
import yaml

EXCEL_FILE = "threat-actor-profiles/additional_enrichment/APT Groups and Operations.xlsx"
PROFILES_DIR = "profiles"

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def save_yaml(data, file_path):
    with open(file_path, 'w') as file:
        yaml.dump(data, file, sort_keys=False)

def read_excel(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        raise FileNotFoundError(f"No such file or directory: '{file_path}'")
    df = pd.read_excel(file_path, sheet_name=None)
    return df

def update_profiles_from_excel(profiles, excel_data):
    updated_profiles = {}
    for sheet_name, df in excel_data.items():
        for index, row in df.iterrows():
            profile_name = row.get('Group Name') or row.get('Operation Name')
            if profile_name and profile_name in profiles:
                profile = profiles[profile_name]
                updated = False
                updates = []
                if 'aliases' in row and not pd.isna(row['aliases']):
                    aliases = row['aliases'].split(',')
                    for alias in aliases:
                        if alias not in profile.get('aliases', []):
                            profile.setdefault('aliases', []).append(alias)
                            updates.append(f"Added alias: {alias}")
                            updated = True
                if 'motivations' in row and not pd.isna(row['motivations']):
                    motivations = row['motivations'].split(',')
                    for motivation in motivations:
                        if motivation not in profile.get('motivations', []):
                            profile.setdefault('motivations', []).append(motivation)
                            updates.append(f"Added motivation: {motivation}")
                            updated = True
                if 'target sectors' in row and not pd.isna(row['target sectors']):
                    sectors = row['target sectors'].split(',')
                    for sector in sectors:
                        if sector not in profile.get('target sectors', []):
                            profile.setdefault('target sectors', []).append(sector)
                            updates.append(f"Added target sector: {sector}")
                            updated = True
                if 'description' in row and not pd.isna(row['description']):
                    profile['descriptions'] = row['description']
                    updates.append(f"Updated description")
                    updated = True
                
                if updated:
                    updated_profiles[profile_name] = profile
                    print(f"Profile '{profile_name}' updated with changes: {', '.join(updates)}")
    return updated_profiles

def main():
    # Debugging information
    print(f"Current working directory: {os.getcwd()}")
    print(f"Excel file path: {EXCEL_FILE}")
    print(f"Profiles directory: {PROFILES_DIR}")
    
    # Load all profiles
    profiles = {}
    for profile_file in os.listdir(PROFILES_DIR):
        profile_path = os.path.join(PROFILES_DIR, profile_file)
        profile_name = os.path.splitext(profile_file)[0]
        profiles[profile_name] = load_yaml(profile_path)
    
    # Read Excel data
    print(f"Reading Excel file: {EXCEL_FILE}")
    excel_data = read_excel(EXCEL_FILE)
    
    # Update profiles with Excel data
    updated_profiles = update_profiles_from_excel(profiles, excel_data)
    
    # Save updated profiles
    for profile_name, profile in updated_profiles.items():
        profile_path = os.path.join(PROFILES_DIR, f"{profile_name}.yaml")
        save_yaml(profile, profile_path)
        print(f"Saved updated profile: {profile_name}")

if __name__ == "__main__":
    main()
