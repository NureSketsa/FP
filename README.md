# pbkk

## [learnvidai.site](https://learnvidai.site)

FOR PBKKK

REQUIREMENT/HOW TO
1. Make Venv and activate the venv
  ```
  python -m venv venv
  .\venv\Scripts\Activate
2. install `Install Chocolatey`,`MiKTeX` and `FFmpeg`
  [ Install Chocolatey ]
  a. Open PowerShell as Administrator (Press Start, type PowerShell, right-click → Run as Administrator.)
  b. copy and run
  ```bash
  Set-ExecutionPolicy Bypass -Scope Process -Force; `
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
  iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  ````
  c. Wait until you see “Chocolatey installed successfully”.
  d. Close the admin PowerShell after it finishes.

  [`MiKTeX` and `FFmpeg`]
  a. Now open a new Administrator PowerShell and run
  b. copy and run
  ```
  choco install miktex ffmpeg -y
  ```

  [VERIFY]
  a. copy and run
  ```bash
  miktex-console --version   # Check MiKTeX
  ffmpeg -version            # Check FFmpeg
  ```
3. now copy and run  `pip install -r requirements.txt`

run the APP
```
streamlit run app.py

uvicorn MAIN.main:app --reload
```


deactivate
Remove-Item -Recurse -Force .\venv