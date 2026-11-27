param(
    [Parameter(Mandatory)] [string] $ProjectPython,
    [Parameter(Mandatory)] [string] $Models
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '../..'))
$pipeline = 'demo/TestPilot-Demo-Lab/scripts/product_acceptance.py'

function Invoke-DemoSample {
    param([string] $Stage, [string] $Module, [string] $Receipt)
    $output = Join-Path $PSScriptRoot $Receipt
    if (Test-Path -LiteralPath $output) { throw "Receipt already exists: $output" }
    $console = & $ProjectPython -X utf8 $pipeline $Stage --module $Module --output $output
    $sampleExit = $LASTEXITCODE
    $console | Write-Host
    if ($sampleExit -ne 0) { throw "$Stage/$Module exited $sampleExit" }
    Get-Content -Raw -Encoding utf8 -LiteralPath $output | ConvertFrom-Json
}

$summaryPath = Join-Path $PSScriptRoot 'demo-controls.json'
if (Test-Path -LiteralPath $summaryPath) { throw 'Demo controls receipt already exists' }
$owned = '.runtime/course-demo-' + [Guid]::NewGuid().ToString('N')
New-Item -ItemType Directory -Path $owned | Out-Null
$env:TESTPILOT_MODEL_RUNTIME = (Resolve-Path $owned).Path
$port = & $ProjectPython -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()'
$resources = & $ProjectPython -c 'import json; from backend.model_resources import Resources,headroom; r=Resources().sample(); print(json.dumps(dict(headroom=headroom(r), **r)))'
if ($LASTEXITCODE -ne 0) { throw 'Could not measure local resource headroom' }
$summary = [ordered]@{ commit=(git rev-parse HEAD); at=(Get-Date -Format o); preflight=($resources | ConvertFrom-Json); port=[int]$port; context=4096 }

$offline = Invoke-DemoSample blind calculator 'demo-model-offline.json'
$summary.offline_status = $offline.model_health.http
$summary.offline_error = $offline.samples[0].error
if ($summary.offline_status -ne 503 -or -not $summary.offline_error) {
    throw 'Offline model gate did not reject the AI request'
}

try {
    if ($summary.preflight.headroom) {
        $process = Start-Process -FilePath $ProjectPython -WindowStyle Hidden -PassThru -WorkingDirectory (Get-Location).Path `
            -ArgumentList '-X', 'utf8', '-m', 'eval.phase06.serve', '--models', ('"' + $Models + '"'),
                          '--data', $owned, '--port', $port, '--context', '4096' `
            -RedirectStandardOutput (Join-Path $owned 'supervisor.stdout') `
            -RedirectStandardError (Join-Path $owned 'supervisor.stderr')
        try {
            $statePath = Join-Path $owned 'attestation.json'
            $deadline = (Get-Date).AddSeconds(100)
            do {
                Start-Sleep -Milliseconds 500
                try { $state = Get-Content -Raw -LiteralPath $statePath -ErrorAction Stop | ConvertFrom-Json }
                catch { $state = $null }
                if ($state.vulkan -or $process.HasExited) { break }
            } while ((Get-Date) -lt $deadline)
            $summary.supervisor_ready = $state
            if ($state.status -eq 'serving' -and $state.vulkan) {
                $live = Invoke-DemoSample blind calculator 'demo-model-live.json'
                $summary.live_health = $live.model_health.http
                $summary.live_run_status = $live.samples[0].run.status
                $summary.live_error = $live.samples[0].error
            }
        } finally {
            New-Item -ItemType File -Path (Join-Path $owned 'STOP') -Force | Out-Null
            $summary.supervisor_exited = $process.WaitForExit(40000)
            $summary.supervisor_exit = if ($summary.supervisor_exited) { $process.ExitCode }
            $summary.supervisor_stderr = Get-Content -Raw -Encoding utf8 -LiteralPath (Join-Path $owned 'supervisor.stderr')
            if (Test-Path -LiteralPath $statePath) {
                $summary.supervisor_final = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
            }
            if (-not $summary.supervisor_exited) { throw 'Owned supervisor did not exit after STOP' }
        }
    }
    $regression = Invoke-DemoSample regression unit_scaling 'demo-template-regression.json'
    $summary.template_regression = $regression.samples[0].workflow.updated_bug.status
    $mutation = Invoke-DemoSample mutation calculator 'demo-template-mutation.json'
    $summary.template_mutation = $mutation.samples[0].report.status
    if ($summary.template_regression -ne 'resolved' -or -not $mutation.samples[0].report) {
        throw 'Template fallback did not complete the regression and mutation checks'
    }
} finally {
    $summary | ConvertTo-Json -Depth 12 | Set-Content -Encoding utf8 -LiteralPath $summaryPath
}

if ($summary.live_health -ne 200 -or $summary.live_run_status -ne 'passed') {
    exit 1
}
