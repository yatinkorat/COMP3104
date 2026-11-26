# Runs each command for one lab step and saves a "terminal transcript" (prompt + output)
# to outputs\<name>.txt, which is later rendered into a screenshot.
param(
    [Parameter(Mandatory)] [string] $Name,
    [Parameter(Mandatory)] [string[]] $Commands
)
$ErrorActionPreference = 'Continue'
$root = $PSScriptRoot
Set-Location (Join-Path $root 'k8s')
$out = New-Object System.Collections.Generic.List[string]
foreach ($cmd in $Commands) {
    $out.Add("PS C:\_GBC\5th sem\comp3104\lab-10-services\k8s> $cmd")
    $result = Invoke-Expression "$cmd 2>&1" | ForEach-Object {
        if ($_ -is [System.Management.Automation.ErrorRecord]) {
            $m = $_.Exception.Message
            if ($m -eq 'System.Management.Automation.RemoteException') { '' } else { $m }
        } else { "$_" }
    }
    foreach ($line in $result) { $out.Add($line) }
    $out.Add('')
}
$out | Set-Content -Encoding utf8 (Join-Path $root "outputs\$Name.txt")
$out
