Set Shell = CreateObject("WScript.Shell")
' 获取当前脚本所在的文件夹路径
scriptPath = CreateObject("Scripting.FileSystemObject").GetFile(Wscript.ScriptFullName).ParentFolder.Path
' 拼接路径
exePath = scriptPath & "\main.exe"
Shell.Run """" & exePath & """", 0, False