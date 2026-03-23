; nssm.exe must be placed in the same directory as installer.iss before compiling
; download from: https://nssm.cc/download

#define AppName "Face Recognition API"
#define AppVersion "1.0"
#define AppPublisher "Derby1537"
#define ServiceName "FaceRecognitionAPI"
#define InstallDir "{autopf}\FaceRecognitionAPI"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={#InstallDir}
DefaultGroupName={#AppName}
OutputBaseFilename=FaceRecognitionAPI-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; compiled app from PyInstaller (build with build_windows.ps1 first)
Source: "dist\face_recognition\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
; nssm to register the exe as a Windows service
Source: "nssm.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"

[Code]

var
  ConfigPage: TInputQueryWizardPage;
  ImagesDirPage: TInputDirWizardPage;

// ── wizard pages ──────────────────────────────────────────────────────────────

procedure InitializeWizard;
begin
  ConfigPage := CreateInputQueryPage(
    wpSelectDir,
    'Database configuration',
    'Enter the MySQL connection details',
    ''
  );
  ConfigPage.Add('Host:', False);
  ConfigPage.Add('Port:', False);
  ConfigPage.Add('User:', False);
  ConfigPage.Add('Password:', True);
  ConfigPage.Add('Database name:', False);

  ConfigPage.Values[0] := 'localhost';
  ConfigPage.Values[1] := '3306';
  ConfigPage.Values[2] := 'root';
  ConfigPage.Values[3] := '';
  ConfigPage.Values[4] := 'face_recognition';

  ImagesDirPage := CreateInputDirPage(
    ConfigPage.ID,
    'Images directory',
    'Select the folder where uploaded images will be stored',
    '',
    False,
    ''
  );
  ImagesDirPage.Add('Images folder:');
  ImagesDirPage.Values[0] := ExpandConstant('{app}\public\image');
end;

// ── validation ────────────────────────────────────────────────────────────────

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = ConfigPage.ID then
  begin
    if (ConfigPage.Values[0] = '') or (ConfigPage.Values[2] = '') or (ConfigPage.Values[4] = '') then
    begin
      MsgBox('Host, user and database name are required.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

// ── write .env ────────────────────────────────────────────────────────────────

procedure WriteEnvFile;
var
  Lines: TArrayOfString;
begin
  SetArrayLength(Lines, 7);
  Lines[0] := 'DATABASE_HOST=' + ConfigPage.Values[0];
  Lines[1] := 'DATABASE_PORT=' + ConfigPage.Values[1];
  Lines[2] := 'DATABASE_USER=' + ConfigPage.Values[2];
  Lines[3] := 'DATABASE_PASS=' + ConfigPage.Values[3];
  Lines[4] := 'DATABASE_NAME=' + ConfigPage.Values[4];
  Lines[5] := 'ENV=production';
  Lines[6] := 'IMAGES_DIR=' + ImagesDirPage.Values[0];

  SaveStringsToFile(ExpandConstant('{app}\.env'), Lines, False);
end;

// ── service helpers ───────────────────────────────────────────────────────────

function NssmPath: String;
begin
  Result := ExpandConstant('{app}\nssm.exe');
end;

procedure ServiceExec(Args: String);
var
  ResultCode: Integer;
begin
  Exec(NssmPath, Args, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

// ── post-install ──────────────────────────────────────────────────────────────

procedure CurStepChanged(CurStep: TSetupStep);
var
  ExePath: String;
begin
  if CurStep = ssPostInstall then
  begin
    WriteEnvFile;

    ExePath := ExpandConstant('{app}\face_recognition.exe');

    // register and configure the service
    ServiceExec('install ' + ExpandConstant('{#ServiceName}') + ' "' + ExePath + '"');
    ServiceExec('set ' + ExpandConstant('{#ServiceName}') + ' AppDirectory "' + ExpandConstant('{app}') + '"');
    ServiceExec('set ' + ExpandConstant('{#ServiceName}') + ' DisplayName "Face Recognition API"');
    ServiceExec('set ' + ExpandConstant('{#ServiceName}') + ' Description "Face Recognition REST API server"');
    ServiceExec('set ' + ExpandConstant('{#ServiceName}') + ' Start SERVICE_AUTO_START');

    // start the service immediately
    ServiceExec('start ' + ExpandConstant('{#ServiceName}'));

    MsgBox(
      'Installation complete.' + #13#10 +
      'The API is now running at http://localhost:8000' + #13#10 +
      'The service will start automatically at every Windows boot.',
      mbInformation, MB_OK
    );
  end;
end;

// ── uninstall: stop and remove the service ────────────────────────────────────

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    ServiceExec('stop ' + ExpandConstant('{#ServiceName}'));
    ServiceExec('remove ' + ExpandConstant('{#ServiceName}') + ' confirm');
  end;
end;
