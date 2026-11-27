param(
    [Parameter(Mandatory)] [Guid] $Session,
    [Parameter(Mandatory)] [ValidateSet(1, 2)] [int] $Round
)

$ErrorActionPreference = 'Stop'
$promptPath = Join-Path $PSScriptRoot "loop-prompt-$Round.txt"
$receiptPath = Join-Path $PSScriptRoot "loop-response-$Round.json"
if (Test-Path -LiteralPath $receiptPath) {
    throw "The original receipt already exists: $receiptPath"
}

$claudeArgs = @('-p', '--model', 'haiku', '--output-format', 'json',
    '--strict-mcp-config', '--setting-sources', '', '--tools', '',
    '--max-budget-usd', '0.15')
if ($Round -eq 1) {
    $claudeArgs += @('--session-id', $Session.ToString())
} else {
    $claudeArgs += @('--resume', $Session.ToString())
}
$prompt = Get-Content -Raw -LiteralPath $promptPath -Encoding utf8
$result = & claude.ps1 @claudeArgs $prompt
$cliExit = $LASTEXITCODE
if ($result) {
    $result | Set-Content -LiteralPath $receiptPath -Encoding utf8NoBOM
}
if ($cliExit -ne 0) {
    exit $cliExit
}
$receipt = Get-Content -Raw -LiteralPath $receiptPath -Encoding utf8 | ConvertFrom-Json
if ($receipt.is_error -or $receipt.session_id -ne $Session.ToString()) {
    throw 'The CLI did not return a successful response for the requested session'
}
$receipt.result
