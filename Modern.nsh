;Change this file to customize zip2exe generated installers with a modern interface

!include "MUI.nsh"

!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Quick Launch icon" SecQuick
    SetOutPath $INSTDIR
    CreateShortCut "$QUICKLAUNCH\Altitude Time.lnk" "$INSTDIR\at.exe" \
  "some command line parameters" "" "" SW_SHOWMAXIMIZED \
  ALT|CONTROL|SHIFT|F8 "This program shows altitudes of objects vs UTC"
SectionEnd