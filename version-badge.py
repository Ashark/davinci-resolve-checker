# This script is used in https://badgen.net/https/ashark.npkn.net/f1a682 to generate version badge.
# See how it works here: https://css-tricks.com/adding-custom-github-badges-to-your-repo/

from napkin import (
    response,
)  # Note that it is available only in browser in napkin website
import re
import requests
import json

url = "https://raw.githubusercontent.com/Ashark/davinci-resolve-checker/master/davinci-resolve-checker.py"
file_content = requests.get(url).text

version = "Undetected"

for line in file_content.split("\n"):
    if "project name" in line:
        version = line
        break

# print(version)
version = re.search(r'"(\d+\.\d+\.\d+.?)"', version).group(1)
# print(version)

result = """{{
  "color": "green",
  "status": "{v}",
  "subject": "checker version"
}}""".format(
    v=version
)

# print(result)
j = json.loads(result)

response.status_code = 200
response.body = j
