$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
function Check([string]$Step) { if ($LASTEXITCODE -ne 0) { throw "$Step failed with exit code $LASTEXITCODE" } }
python -m pip install --upgrade pip
Check 'pip'
python -m pip install -r requirements.txt 'pyinstaller>=6.12,<7'
Check 'dependencies'
python -m unittest discover -s tests -v
Check 'tests'
if (!(Test-Path vendor/llama.cpp/CMakeLists.txt)) {
    New-Item -ItemType Directory -Force vendor | Out-Null
    git clone --filter=blob:none https://github.com/ggml-org/llama.cpp vendor/llama.cpp
    Check 'engine checkout'
}
git -C vendor/llama.cpp checkout --detach 2d8a32502909ca065c41c4cf5f2fb1c427c047fc
Check 'pinned engine revision'
cmake -S vendor/llama.cpp -B native-build -A x64 -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_TOOLS=ON -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DGGML_NATIVE=OFF -DBUILD_SHARED_LIBS=OFF
Check 'engine configure'
cmake --build native-build --config Release --target llama-server -j 2
Check 'engine compilation'
New-Item -ItemType Directory -Force engine | Out-Null
Copy-Item native-build/bin/Release/llama-server.exe engine/llama-server.exe -Force
Get-ChildItem native-build/bin/Release -Filter *.dll | Copy-Item -Destination engine -Force
Copy-Item vendor/llama.cpp/LICENSE engine/llama.cpp-LICENSE.txt -Force
if (Test-Path vendor/llama.cpp/licenses) { Copy-Item vendor/llama.cpp/licenses engine/upstream-licenses -Recurse -Force }
python tools/download_font.py
Check 'font and license download'
python -m PyInstaller --noconfirm --clean --onedir --windowed --name JUPITAR --collect-all faster_whisper --collect-all ctranslate2 --collect-all tokenizers --collect-all sounddevice --collect-all av --collect-all onnxruntime --collect-all huggingface_hub --collect-all PIL --collect-all psutil --add-data 'assets;assets' --add-binary 'engine/llama-server.exe;engine' --add-data 'engine;engine' main.py
Check 'application bundle'
Copy-Item LICENSE dist/JUPITAR/LICENSE.txt -Force
Copy-Item THIRD_PARTY.md dist/JUPITAR/THIRD_PARTY.md -Force
$report = Join-Path (Get-Location) 'frozen-smoke-test.json'
$p = Start-Process -FilePath 'dist/JUPITAR/JUPITAR.exe' -ArgumentList @('--self-test',"`"$report`"") -Wait -PassThru
if ($p.ExitCode -ne 0 -or !(Test-Path $report)) { throw 'Frozen application smoke test failed.' }
$smoke=Get-Content $report -Raw | ConvertFrom-Json
if (!$smoke.gui -or !$smoke.engine -or !$smoke.imports) { throw 'Frozen smoke-test report contains a failure.' }
$compiler = @("${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (!$compiler) { throw 'Inno Setup 6 compiler not found. Install it on the build machine, not the end-user laptop.' }
& $compiler packaging/JUPITAR.iss
Check 'installer'
Get-FileHash release/*.exe -Algorithm SHA256 | Format-List | Out-File release/SHA256.txt
Copy-Item docs/END_USER_INSTALL.md release/READ_ME_FIRST.md -Force
Write-Host 'Unsigned Windows installer created in release/. Clean-machine testing and signing still required.'
