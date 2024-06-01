import requests
import yaml
import os

MITRE_CTI_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
PROFILES_DIR = "profiles"

def fetch_mitre_cti_data():
    response = requests.get(MITRE_CTI_URL)
    response.raise_for_status()
    return response.json()

def extract_threat_actors(data):
    threat_actors = []
    for obj in data["objects"]:
        if obj["type"] == "intrusion-set":
            threat_actors.append(obj)
    return threat_actors

def create_profile(actor):
    profile = {
        'id': actor.get('id', ''),
        'created': actor.get('created', ''),
        'modified': actor.get('modified', ''),
        'name': actor.get('name', ''),
        'aliases': actor.get('aliases', []),
        'motivations': actor.get('motivations', []),
        'target sectors': actor.get('x_mitre_targeted_platforms', []),
        'descriptions': actor.get('description', ''),
        'external references': actor.get('external_references', [])
    }
    return profile

def save_profile(profile, directory=PROFILES_DIR):
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"{profile['name']}.yaml")
    with open(file_path, 'w') as file:
        yaml.dump(profile, file, sort_keys=False)

def main():
    data = fetch_mitre_cti_data()
    threat_actors = extract_threat_actors(data)
    for actor in threat_actors:
        profile = create_profile(actor)
        save_profile(profile)

if __name__ == "__main__":
    main()
