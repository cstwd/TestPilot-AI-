param([string]$Pack = (Split-Path $PSScriptRoot))
$ErrorActionPreference = 'Stop'
$folder = Join-Path (Resolve-Path $Pack) '06_PRESENTATION'
$qa = Join-Path (Resolve-Path $Pack) '07_FINAL_REPORT/previews'
New-Item -ItemType Directory -Path $qa -Force | Out-Null
$deckPath = Join-Path $folder 'TestPilot_AI_正式汇报.pptx'
$pdfPath = Join-Path $folder 'TestPilot_AI_正式汇报.pdf'
$app = New-Object -ComObject PowerPoint.Application
$doc = $null
try {
    $doc = $app.Presentations.Open($deckPath, -1, 0, 0)
    $doc.SaveAs($pdfPath, 32)
    $geometry = @()
    foreach ($slide in $doc.Slides) {
        $name = 'P{0:d2}.png' -f $slide.SlideIndex
        $slide.Export((Join-Path $qa $name), 'PNG', 1280, 720)
        foreach ($shape in $slide.Shapes) {
            if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
                $range = $shape.TextFrame2.TextRange
                if (($range.BoundWidth -gt $shape.Width + 3) -or ($range.BoundHeight -gt $shape.Height + 3)) {
                    $geometry += [pscustomobject]@{page=$slide.SlideIndex;name=$shape.Name;text=$range.Text;boxWidth=$shape.Width;textWidth=$range.BoundWidth;boxHeight=$shape.Height;textHeight=$range.BoundHeight}
                }
            }
        }
    }
    [pscustomobject]@{slides=$doc.Slides.Count; version=$app.Version; renderer='Microsoft PowerPoint'; overflow_candidates=@($geometry)} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $Pack '07_FINAL_REPORT/powerpoint-qa.json') -Encoding utf8
} finally {
    if ($doc) {$doc.Close() }
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($app)
}
