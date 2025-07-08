Set shell = CreateObject("WScript.Shell")
desktopPath = shell.SpecialFolders("Desktop")
shortcutPath = desktopPath & "\NyrvanaPlayer.lnk"

' Modifier ce chemin si main.py est ailleurs :
targetPython = "python"
scriptPath = shell.CurrentDirectory & "\main.py"

Set shortcut = shell.CreateShortcut(shortcutPath)
shortcut.TargetPath = targetPython
shortcut.Arguments = """" & scriptPath & """"
shortcut.WorkingDirectory = shell.CurrentDirectory
shortcut.WindowStyle = 1
shortcut.IconLocation = "python.exe, 0"
shortcut.Save
