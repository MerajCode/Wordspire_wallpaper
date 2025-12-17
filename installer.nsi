; installer.nsi
!define PRODUCT_NAME "Wordspire Wallpaper"
!define PRODUCT_VERSION "1.0.0"
!define EXE_NAME "Wordspire By (Merajcode YT).exe"  # <-- .exe का सही नाम यहाँ डालें

; --- Installation properties ---
VIProductVersion "${PRODUCT_VERSION}.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "FileDescription" "${PRODUCT_NAME} Wallpaper Manager"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "LegalCopyright" "Merajcode"

; --- Output ---
Outfile "${PRODUCT_NAME} v${PRODUCT_VERSION} Setup.exe"
InstallDir "$APPDATA\Wordspire_by_merajcode"
RequestExecutionLevel user

Icon "icon.ico"
UninstallIcon "icon.ico"

Page directory
Page instfiles

Section "Install"
    SetOutPath $INSTDIR
    File /r "dist\*.*"

    ; Optional: Create desktop shortcut
    ; --- यहाँ बदलाव किया गया है ---
    CreateShortCut "$DESKTOP\Wordspire.lnk" "$INSTDIR\${EXE_NAME}"
SectionEnd