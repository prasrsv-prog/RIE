#define MyAppName "RCIS"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "RSV Helmets"
#define MyAppExeName "RCIS.exe"

[Setup]
AppId={{B77010D1-82F7-4C72-9E6A-E8CB579A4974}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\RCIS
DefaultGroupName=RCIS
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DisableProgramGroupPage=yes
OutputDir=..\..\dist\installer
OutputBaseFilename=RCIS-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
Uninstallable=yes

[Files]
Source: "..\..\dist\RCIS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\RCIS"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\RCIS"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch RCIS"; Flags: nowait postinstall skipifsilent
