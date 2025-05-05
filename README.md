# timologia_db
Timologia database for Demos Stylianou ltd
Install libraries in the python envinroment using:
<pre><code>
conda install -r requirements.txt
</code></pre>

Caution on Pyqt5 lib depends on OS-Mac/Windows/Linux

Includes: 
- Dates timologiou as column
- Greek
- multiple descriptions- nested
- search base on name
- Autocomplete names and description
- edit all 
- change id to arithmos timologiou
- Save .db and .csv

To package the programme into a single .exe for windows, use anaconda .env or python .env in cmd and execute:

pyinstaller --onefile --windowed timologia-gui.py

Then in dist/timologia.exe

Remember that the timologia.db should be present in the directory.

[text](vscode-local:/c%3A/Users/conno/Desktop/timologia_db-main/timologia_db-main-v2/timologia.db)