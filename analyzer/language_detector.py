import os
from collections import Counter


extensions = {

".py":"Python",

".js":"JavaScript",

".java":"Java",

".cpp":"C++",

".c":"C",

".html":"HTML",

".css":"CSS",

".sql":"SQL"

}


def detect_languages(repo_path):

    counter = Counter()

    for root, dirs, files in os.walk(repo_path):

        for file in files:

            ext = os.path.splitext(file)[1]

            if ext in extensions:

                counter[extensions[ext]] += 1

    return dict(counter)