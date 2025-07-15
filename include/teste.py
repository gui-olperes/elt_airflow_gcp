import json

with open(r"C:\Users\guipe\Documents\jornal\projeto\include\gcp_key.json") as f:
    keyfile_dict = json.load(f)

# Escapar as quebras de linha na private_key
keyfile_dict["private_key"] = keyfile_dict["private_key"].replace("\n", "\\n")

extra_json = {
    "keyfile_dict": keyfile_dict,
    "scope": "https://www.googleapis.com/auth/cloud-platform"
}

# Este é o conteúdo que você deve colar na UI do Airflow
print(json.dumps(extra_json, indent=2))
