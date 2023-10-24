#!/usr/bin/env python3

import json
import subprocess
import sys
import re
import time
from distutils.version import LooseVersion

global builds
global ignore_list
builds = ["gitlab-ce", "gitlab-ee"]
ignore_list = ["rc", "nightly", "latest"]

start_time = time.time()

def main(argv):
    if(len(argv) == 0):
        exit("hashes_dict_file file missing")

    hashes_dict_file = argv[0]
    process_missing_tags(hashes_dict_file)


def get_manifest_hash(branch, version):
    image = "gitlab/%s:%s" % (branch, version)
    print("Processing image: %s" % image)

    # pull tag
    subprocess.check_output("docker pull %s" % image, shell=True)
    css_file = subprocess.check_output("docker run --rm -t %s ls /opt/gitlab/embedded/service/gitlab-rails/public/assets|egrep '^application-.*\\.css' | grep -v \\.gz" % image, shell=True)

    # get version hash
    _hash = ""
    pattern = r'^application-(.*)\.css'
    match = re.match(pattern, css_file.decode('utf-8'))
    if match:
        _hash = match.group(1)

    # cleanup
    subprocess.check_output("docker rmi %s" % image, shell=True)

    return str(_hash)


def load_hashes_dict(hashes_dict_file):
    with open(hashes_dict_file, "r") as file:
        raw_hashes = file.read()
    hashes = json.loads(raw_hashes)

    return hashes


def write_hashes_dict(hashes, path):
    sorted_data = dict(sorted(hashes.items(), key=lambda x: LooseVersion(x[1]['versions'][0]), reverse=True))
    with open(path, "w") as output:
        json.dump(sorted_data, output, indent=4)


def load_tags(build):
    with open("%s_tags.json" % build, "r") as file:
        raw_tags = file.read()
    tags = json.loads(raw_tags)

    return tags


def load_processed_tags():
    with open("tags_processed.json", "r") as file:
        raw_processed_tags = file.read()
    processed_tags = json.loads(raw_processed_tags)

    return processed_tags


def write_processed_tags(processed):
    sorted_data = {key: sorted(value, key=LooseVersion, reverse=True) for key, value in processed.items()}

    with open("tags_processed.json", "w") as output:
        json.dump(sorted_data, output, indent=4)


def process_missing_tags(hashes_dict_file):
    hashes = load_hashes_dict(hashes_dict_file)
    processed = load_processed_tags()
    # process missing tags
    for build in builds:
        tags = load_tags(build)
        for tag in tags["results"]:
            elapsed_time = time.time() - start_time
            if elapsed_time > 5.5 * 3600:  # 5 hours = 5 * 3600秒
                write_hashes_dict(hashes, hashes_dict_file)
                write_processed_tags(processed)
            version = str(tag["name"])
            if(
                not any(version == ignore for ignore in ignore_list)
                and
                not any(version == processed for processed in processed[build]) # if processed is ""
            ):
                _hash = get_manifest_hash(build, version)
                if hashes.get(_hash):
                    hashes[_hash]["versions"].append(version)
                else:
                    hashes[_hash] = {"build": build, "versions": [version]}

                processed[build].append(version)

    write_hashes_dict(hashes, hashes_dict_file)
    write_processed_tags(processed)


if __name__ == "__main__":
    main(sys.argv[1:])
