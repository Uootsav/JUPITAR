#define MyAppName "JUPITAR"
#define MyAppVersion "0.4.0"
[Setup]
AppId={{89109C2A-38F1-43D2-BB56-A3A0B9F4A251}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Uootsav
DefaultDirName={localappdata}\Programs\JUPITAR
DefaultGroupName=JUPITAR
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible and not arm64
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\release
OutputBaseFilename=JUPITAR-Setup-0.4.0-preview
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=..\LICENSE
UninstallDisplayIcon={app}\JUPITAR.exe
[Files]
Source: "..\dist\JUPITAR\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\JUPITAR"; Filename: "{app}\JUPITAR.exe"
[Run]
Filename: "{app}\JUPITAR.exe"; Description: "Launch JUPITAR"; Flags: nowait postinstall skipifsilent
