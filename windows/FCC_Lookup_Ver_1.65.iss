; FCC Lookup Ver 1.65 - Inno Setup Installer Script
; Fast-launch test: installs PyInstaller onedir folder.

[Setup]
AppName=FCC Lookup
AppVersion=1.65
AppVerName=FCC Lookup Ver 1.65
AppPublisher=FCC Lookup
DefaultDirName={autopf}\FCC_Lookup
DefaultGroupName=FCC Lookup
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=FCC_Lookup_Ver_1.65_Setup
SetupIconFile=FC_launcher_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSmallImageFile=fcc_icon.png
PrivilegesRequired=admin
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\FCC_Lookup_Ver_1.65.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; \
    GroupDescription: "Additional icons:"
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut"; \
    GroupDescription: "Additional icons:"

[Files]
Source: "dist\FCC_Lookup_Ver_1.65\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "FC_launcher_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "fcc_icon.png"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Create C:\FCC_DB automatically so the app can write to it on first launch.
Name: "C:\FCC_DB"; Permissions: everyone-full

[Icons]
Name: "{group}\FCC Lookup Ver 1.65"; \
    Filename: "{app}\FCC_Lookup_Ver_1.65.exe"; \
    IconFilename: "{app}\FC_launcher_icon.ico"; \
    Tasks: startmenuicon
Name: "{autodesktop}\FCC Lookup"; \
    Filename: "{app}\FCC_Lookup_Ver_1.65.exe"; \
    IconFilename: "{app}\FC_launcher_icon.ico"; \
    Tasks: desktopicon
Name: "{group}\Uninstall FCC Lookup"; \
    Filename: "{uninstallexe}"; \
    Tasks: startmenuicon

[Run]
Filename: "{app}\FCC_Lookup_Ver_1.65.exe"; \
    Description: "Launch FCC Lookup Ver 1.65 now"; \
    Flags: nowait postinstall skipifsilent

[Messages]
WelcomeLabel1=Welcome to FCC Lookup Ver 1.65 Setup
WelcomeLabel2=This will install FCC Lookup Ver 1.65 on your computer.%n%nFCC Lookup is an offline ham radio callsign lookup tool covering USA and Canada.%n%nThis fast-launch test version uses an installed app folder instead of a self-extracting one-file EXE.%n%nClick Next to continue.
FinishedHeadingLabel=FCC Lookup Ver 1.65 Installation Complete
FinishedLabel=FCC Lookup Ver 1.65 has been installed successfully!%n%nOn first launch:%n%n  1. Click [Update FCC DB] to download US license data%n  2. Click [Update Canadian DB] to download Canadian data%n  3. Use Database > Download / Update ZIP Centers for zip-to-zip distance/bearing%n  4. Use [Browse Records] to inspect ham.db%n%nBoth downloads require an internet connection and take a few minutes.
