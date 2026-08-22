[Setup]
AppName=MikaRoll Universal Converter
AppVersion=2.0
AppPublisher=InnocentLu
DefaultDirName={autopf}\MikaRoll
DefaultGroupName=MikaRoll
OutputDir=dist
OutputBaseFilename=MikaRoll_v2.0_Setup
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=image\icon.ico
UninstallDisplayIcon={app}\MikaRoll.exe
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\MikaRoll\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\MikaRoll"; Filename: "{app}\MikaRoll.exe"
Name: "{group}\Uninstall MikaRoll"; Filename: "{uninstallexe}"
Name: "{autodesktop}\MikaRoll"; Filename: "{app}\MikaRoll.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MikaRoll.exe"; Description: "Launch MikaRoll"; Flags: nowait postinstall skipifsilent
