# auditar_sincro.ps1 — inventario de scripts del disco + chequeo de sincronía vs _manifest.json
# Correr desde la RAÍZ del repo:
#   powershell -ExecutionPolicy Bypass -File scripts\auxiliares\auditar_sincro.ps1

$root = (Get-Location).Path

# 1. ubicar el manifest y leerlo (en minúsculas para comparar hashes case-insensitive)
$manifest = Get-ChildItem -Recurse -Filter "_manifest.json" -ErrorAction SilentlyContinue | Select-Object -First 1
$mtext = if ($manifest) { (Get-Content $manifest.FullName -Raw).ToLower() } else { "" }
Write-Host ("Manifest: " + $(if ($manifest) { $manifest.FullName } else { "NO ENCONTRADO (sync no verificable)" }))
Write-Host ""

# 2. recorrer todos los .py bajo scripts\ : versión + hash + estado de sincro + fecha
Get-ChildItem -Path scripts -Recurse -Filter *.py -ErrorAction SilentlyContinue | ForEach-Object {
    $txt  = Get-Content $_.FullName -Raw
    $ver  = if ($txt -match '__version__\s*=\s*["\x27]([^"\x27]+)["\x27]') { $Matches[1] } else { '-' }
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLower()
    $rel  = $_.FullName.Substring($root.Length + 1)
    $sync = if     ($mtext -eq "")        { 'sin-manifest' }
            elseif ($mtext.Contains($hash)) { 'OK' }
            else                            { 'FUERA-DE-SINCRO' }
    [PSCustomObject]@{
        Sync       = $sync
        Script     = $rel
        Version    = $ver
        Modificado = $_.LastWriteTime.ToString('yyyy-MM-dd HH:mm')
        Hash8      = $hash.Substring(0, 8)
    }
} | Sort-Object Sync, Script | Format-Table -AutoSize
