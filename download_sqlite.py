import urllib.request
import re
import zipfile
import io

print("Fetching SQLite download page...")
html = urllib.request.urlopen('https://www.sqlite.org/download.html').read().decode('utf-8')
match = re.search(r'(202[456]/sqlite-dll-win-x64-\d+\.zip)', html)
if match:
    url = 'https://www.sqlite.org/' + match.group(1)
    print('Downloading', url)
    response = urllib.request.urlopen(url).read()
    z = zipfile.ZipFile(io.BytesIO(response))
    z.extract('sqlite3.dll')
    print('Extracted sqlite3.dll successfully!')
else:
    print('Could not find download URL in HTML.')
