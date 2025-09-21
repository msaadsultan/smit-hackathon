# Run poetry install with administrative privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {  
    # Relaunch as admin
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Current working directory
$workingDir = "c:\Users\Saadi\Documents\campus-ai-agent"

# Navigate to project directory
Set-Location $workingDir

# Run poetry install
poetry install --no-root