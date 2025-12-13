# quantmetrics_rebrand.ps1
# Automated rebranding script - EdgeLab → QuantMetrics

$ErrorActionPreference = "Stop"

Write-Host "=== QuantMetrics Rebranding Script ===" -ForegroundColor Cyan
Write-Host "Converting EdgeLab references to QuantMetrics..." -ForegroundColor White

# Phase 1: Rename schema file
Write-Host "`n[1/6] Renaming core schema file..." -ForegroundColor Yellow
if (Test-Path "core/edgelab_schema.py") {
    Move-Item "core/edgelab_schema.py" "core/quantmetrics_schema.py" -Force
    Write-Host "  Renamed: edgelab_schema.py -> quantmetrics_schema.py" -ForegroundColor Green
} else {
    Write-Host "  Skip: edgelab_schema.py not found (already renamed?)" -ForegroundColor Gray
}

# Phase 2: Update Python files
Write-Host "`n[2/6] Updating Python imports and class names..." -ForegroundColor Yellow
$pyFiles = Get-ChildItem -Recurse -Include *.py -Exclude __pycache__,venv

$pyCount = 0
foreach ($file in $pyFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $original = $content
    
    # Import statements
    $content = $content -replace 'from core\.edgelab_schema', 'from core.quantmetrics_schema'
    $content = $content -replace 'import edgelab_schema', 'import quantmetrics_schema'
    
    # Class names
    $content = $content -replace '\bEdgeLabTrade\b', 'QuantMetricsTrade'
    $content = $content -replace '\bEdgeLabFormat\b', 'QuantMetricsFormat'
    
    # Documentation
    $content = $content -replace 'EdgeLab Development Team', 'QuantMetrics Development Team'
    $content = $content -replace 'EdgeLab platform', 'QuantMetrics platform'
    $content = $content -replace 'EdgeLab format', 'QuantMetrics format'
    $content = $content -replace 'EdgeLab CSV', 'QuantMetrics CSV'
    $content = $content -replace 'EdgeLab-style', 'QuantMetrics-style'
    
    if ($content -ne $original) {
        Set-Content $file.FullName $content -NoNewline -Encoding UTF8
        Write-Host "  Updated: $($file.Name)" -ForegroundColor Gray
        $pyCount++
    }
}
Write-Host "  Total Python files updated: $pyCount" -ForegroundColor Green

# Phase 3: Update HTML templates
Write-Host "`n[3/6] Updating HTML templates..." -ForegroundColor Yellow
$htmlFiles = Get-ChildItem -Path templates -Recurse -Include *.html -ErrorAction SilentlyContinue

$htmlCount = 0
foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    $original = $content
    
    # Brand names
    $content = $content -replace '\bEdgeLab\b', 'QuantMetrics'
    $content = $content -replace 'EDGELABFX', 'QuantMetrics.io'
    $content = $content -replace 'edgelab', 'quantmetrics'
    
    if ($content -ne $original) {
        Set-Content $file.FullName $content -NoNewline -Encoding UTF8
        Write-Host "  Updated: $($file.Name)" -ForegroundColor Gray
        $htmlCount++
    }
}
Write-Host "  Total HTML files updated: $htmlCount" -ForegroundColor Green

# Phase 4: Rename report template
Write-Host "`n[4/6] Renaming report template..." -ForegroundColor Yellow
if (Test-Path "templates/reports/report_edgelab.html") {
    Move-Item "templates/reports/report_edgelab.html" "templates/reports/report_quantmetrics.html" -Force
    Write-Host "  Renamed: report_edgelab.html -> report_quantmetrics.html" -ForegroundColor Green
} else {
    Write-Host "  Skip: report_edgelab.html not found" -ForegroundColor Gray
}

# Phase 5: Update app.py template reference
Write-Host "`n[5/6] Updating app.py template references..." -ForegroundColor Yellow
if (Test-Path "app.py") {
    $content = Get-Content "app.py" -Raw -Encoding UTF8
    $original = $content
    $content = $content -replace 'report_edgelab\.html', 'report_quantmetrics.html'
    
    if ($content -ne $original) {
        Set-Content "app.py" $content -NoNewline -Encoding UTF8
        Write-Host "  Updated: app.py" -ForegroundColor Green
    }
}

# Phase 6: Verification
Write-Host "`n[6/6] Running verification..." -ForegroundColor Yellow

try {
    $importTest = python -c "from core.quantmetrics_schema import QuantMetricsTrade; print('OK')" 2>&1
    if ($importTest -match "OK") {
        Write-Host "  Schema imports: OK" -ForegroundColor Green
    } else {
        Write-Host "  Schema imports: FAILED - $importTest" -ForegroundColor Red
    }
} catch {
    Write-Host "  Schema imports: FAILED - $_" -ForegroundColor Red
}

Write-Host "`n=== Rebranding Complete ===" -ForegroundColor Cyan
Write-Host "`nSummary:" -ForegroundColor White
Write-Host "  Python files updated: $pyCount" -ForegroundColor Gray
Write-Host "  HTML files updated: $htmlCount" -ForegroundColor Gray

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Review changes: git diff" -ForegroundColor White
Write-Host "  2. Test imports manually" -ForegroundColor White
Write-Host "  3. Run tests: pytest tests/" -ForegroundColor White
Write-Host "  4. Start Flask: python app.py" -ForegroundColor White
Write-Host "  5. Commit changes with git" -ForegroundColor White