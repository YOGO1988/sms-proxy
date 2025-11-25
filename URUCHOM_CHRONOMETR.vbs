Set WshShell = CreateObject("WScript.Shell")
' Pobierz katalog gdzie znajduje się ten skrypt VBS
ScriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
' Uruchom plik .bat w tym samym katalogu
WshShell.CurrentDirectory = ScriptDir
WshShell.Run """" & ScriptDir & "\uruchom_chronometr.bat""", 1, False
