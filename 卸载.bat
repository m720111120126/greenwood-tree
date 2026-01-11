@echo off
:: ========== 第一步：自动提权 ==========
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo 正在请求管理员权限...
    powershell -Command "Start-Process cmd -ArgumentList '/c', '%~f0' -Verb RunAs"
    exit /b
)

:: ========== 修复点1：防止无限循环且修复语法 ==========
:: 如果没有参数，则调用自身并传递参数，然后退出旧实例
:: 注意：这里去掉了可能导致语法错误的单引号包裹方式
if "%1"=="noPause" goto Main
cmd /c "%~f0" noPause & exit /b

:: ========== 第二步：主程序逻辑 ==========
:Main
cls
echo ==========================================
echo     绿杉树系统清理工具 (管理员模式)
echo ==========================================
echo.

:: --- 其余逻辑保持不变 ---
echo [1/5] 正在删除任务计划...
schtasks /delete /tn "绿杉树启动" /f >nul 2>&1
if %errorlevel% EQU 0 (
    echo [成功] 任务计划 "绿杉树启动" 已移除。
) else (
    echo [信息] 任务计划不存在或已删除。
)
echo.

echo [2/5] 正在清理桌面快捷方式...
for /f "skip=2 tokens=3*" %%a in ('reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v "Desktop" 2^>nul') do set "RealDesktop=%%a%%b"
set "shortcut1=%RealDesktop%\绿杉树.lnk"
set "shortcut2=%PUBLIC%\Desktop\绿杉树.lnk"

if exist "%shortcut1%" (
    del /f /q "%shortcut1%" >nul 2>&1
    echo [完成] 已删除当前用户桌面快捷方式。
) else if exist "%shortcut2%" (
    del /f /q "%shortcut2%" >nul 2>&1
    echo [完成] 已删除公共桌面快捷方式。
) else (
    echo [信息] 桌面未找到 "绿杉树" 快捷方式。
)
echo.

echo [3/5] 正在清理开始菜单...
for /f "skip=2 tokens=3*" %%a in ('reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v "Programs" 2^>nul') do set "startMenuDir=%%a %%b"
set "startMenuDir=%startMenuDir%\绿杉树"

if exist "%startMenuDir%" (
    rd /s /q "%startMenuDir%" >nul 2>&1
    echo [完成] 开始菜单 "绿杉树" 文件夹已删除。
) else (
    echo [信息] 开始菜单未找到相关条目。
)
echo.

echo [4/5] 正在清理本地源文件...
:: --- 修复点2：修正了这里的全角波浪线 ---
set "targetFolder2=%~dp0_internal"
for /f "usebackq delims=" %%d in (`dir /ad /b /s "%targetFolder2%" ^| sort /R`) do rd "%%d" >nul 2>&1
del /f /q /s "%targetFolder2%\*" >nul 2>&1
set "targetFolder=%~dp0"
for /f "usebackq delims=" %%d in (`dir /ad /b /s "%targetFolder%" ^| sort /R`) do rd "%%d" >nul 2>&1
del /f /q /s "%targetFolder%\*" >nul 2>&1
echo [完成] 本地源文件已清空。
echo.

echo ==========================================
echo     所有清理任务执行完毕。
echo     脚本将在 5 秒后自动关闭。
echo ==========================================
timeout /t 5 >nul
exit /b