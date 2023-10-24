import json
from distutils.version import LooseVersion

MIN_VUL_VERSION = "11.3.4"
MAX_VUL_VERSION = "15.1.5"
HASHES_DICT_FILE = "automation/gitlab_hashes.json"


def main():
    get_target_hashes()

def get_target_hashes():
    min_vul_version = MIN_VUL_VERSION
    max_vul_version = MAX_VUL_VERSION 
    hashes_dict_file = HASHES_DICT_FILE

    hashes = load_hashes_dict(hashes_dict_file)
    matching_hashes = {}
    for _hash, info in hashes.items():
        for version in info.get("versions", []):
            if LooseVersion(min_vul_version) <= LooseVersion(version) < LooseVersion(max_vul_version):
                matching_hashes[_hash] = info
                break

    sorted_data = dict(sorted(matching_hashes.items(), key=lambda x: LooseVersion(x[1]['versions'][0]), reverse=True))

    for _hash in sorted_data:
        print("Matching Hash:", _hash, sorted_data[_hash])


def load_hashes_dict(hashes_dict_file):
    with open(hashes_dict_file, "r") as file:
        raw_hashes = file.read()
    hashes = json.loads(raw_hashes)

    return hashes

if __name__ == "__main__":
    main()