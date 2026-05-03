# =============================================================================
# Script de path replacements - Etapa 11 de la migracion estructural
# Generado: 2026-05-02
# Version: 4 (patrones cortos, sin caracteres con tilde)
# =============================================================================
#
# Estrategia v4:
#   En lugar de buscar lineas enteras que pueden contener caracteres con tilde,
#   se buscan fragmentos cortos y unicos. Cada patron fue verificado para
#   aparecer exactamente 1 vez en el archivo correspondiente.
#
#   Beneficios:
#   - Sin riesgo de problemas de encoding (no hay tildes en los patrones).
#   - Patrones mas cortos = menos errores de transcripcion.
#   - El reemplazo solo cambia el fragmento, dejando el resto de la linea
#     (incluyendo palabras con tildes) absolutamente intacto.
#
# Objetivo:
#   Actualizar paths hardcodeados en scripts/pipeline/*.py tras la
#   reorganizacion estructural del proyecto corpus-csjn.
#
# Decisiones:
#   - Paths relativos al script invocado (paths con ../../).
#     Asume invocacion desde scripts/pipeline/ como CWD.
#   - Defaults canonicos sin sufijo de version.
#   - Solo se modifican docstrings y defaults de argparse.
#     No se toca logica de runtime.
#
# Uso:
#   .\migracion_paths_2026-05-02.ps1 -DryRun    (verifica, no aplica)
#   .\migracion_paths_2026-05-02.ps1            (aplica los cambios)
#
# Logging:
#   Genera log con timestamp en logs/migracion_paths_YYYY-MM-DD_HHMMSS.log
#   Toda la salida queda capturada en pantalla Y en el archivo de log.
#
# Atomicidad:
#   Por archivo: lee contenido completo, aplica todos los reemplazos en
#   memoria, valida, escribe a .tmp, mueve .tmp al original.
#
# Reversibilidad:
#   El estado pre-Etapa-11 esta en el commit cf836cc.
#   Para revertir: git checkout scripts/pipeline/
# =============================================================================

[CmdletBinding()]
param(
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------
$projRoot = "C:\Users\guill\Proyectos\corpus-csjn"
Set-Location $projRoot

if (-not (Test-Path "scripts\pipeline")) {
  Write-Host "ERROR: scripts\pipeline no existe en $projRoot" -ForegroundColor Red
  exit 1
}

$logsDir = Join-Path $projRoot "logs"
if (-not (Test-Path $logsDir)) {
  New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$modeTag = if ($DryRun) { "dryrun" } else { "apply" }
$logFile = Join-Path $logsDir "migracion_paths_${timestamp}_${modeTag}.log"

function Write-Log {
  param(
    [string]$Message,
    [string]$Color = "White"
  )
  if ($Color -eq "White") {
    Write-Host $Message
  } else {
    Write-Host $Message -ForegroundColor $Color
  }
  Add-Content -Path $logFile -Value $Message
}

$header = @(
  "=============================================================",
  "Migracion de paths - Etapa 11 (script v4)",
  "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
  "Modo: $(if ($DryRun) { 'DRY RUN (no se modifica nada)' } else { 'APLICAR (modificara archivos)' })",
  "Proyecto: $projRoot",
  "Log file: $logFile",
  "=============================================================",
  ""
)
foreach ($line in $header) { Write-Log $line }

# -----------------------------------------------------------------------------
# Definicion de reemplazos (patrones cortos sin tildes)
# -----------------------------------------------------------------------------
$replacements = @(
  # ---- construir_catalogo.py: docstring (linea 80) ----
  @(
    "scripts\pipeline\construir_catalogo.py",
    "  python3 construir_catalogo.py --input-dir markdowns_v2/",
    "  python3 construir_catalogo.py --input-dir ../../corpus/",
    "docstring: linea de comando de ejemplo"
  ),
  # ---- construir_catalogo.py: docstring (linea 83) ----
  @(
    "scripts\pipeline\construir_catalogo.py",
    "      --input-dir markdowns_v2/ \",
    "      --input-dir ../../corpus/ \",
    "docstring: bloque de ejemplo (--input-dir)"
  ),
  # ---- construir_catalogo.py: docstring (linea 84) ----
  @(
    "scripts\pipeline\construir_catalogo.py",
    "      --output-catalogo catalogo_v14.csv \",
    "      --output-catalogo ../../output/catalogo/catalogo.csv \",
    "docstring: bloque de ejemplo (--output-catalogo)"
  ),
  # ---- construir_catalogo.py: docstring (linea 85) ----
  @(
    "scripts\pipeline\construir_catalogo.py",
    "      --output-secciones secciones_indices_v14.csv \",
    "      --output-secciones ../../output/catalogo/secciones_indices.csv \",
    "docstring: bloque de ejemplo (--output-secciones)"
  ),
  # ---- construir_catalogo.py: argparse default --input-dir (linea 578) ----
  @(
    "scripts\pipeline\construir_catalogo.py",
    "default=Path('markdowns_v2'),",
    "default=Path('../../corpus'),",
    "argparse: default --input-dir"
  ),
  # ---- construir_catalogo.py: argparse help --input-dir (linea 579) ----
  @(
    "scripts\pipeline\construir_catalogo.py",
    "(default: markdowns_v2)",
    "(default: ../../corpus)",
    "argparse: help --input-dir"
  ),
  # ---- construir_catalogo.py: argparse default --output-catalogo (linea 582) ----
  @(
    "scripts\pipeline\construir_catalogo.py",
    "default=Path('catalogo_v14.csv'),",
    "default=Path('../../output/catalogo/catalogo.csv'),",
    "argparse: default --output-catalogo"
  ),
  # ---- construir_catalogo.py: argparse help --output-catalogo (linea 583) ----
  # Patron corto que no incluye la palabra "catalogo" con tilde
  @(
    "scripts\pipeline\construir_catalogo.py",
    "(default: catalogo_v14.csv)",
    "(default: ../../output/catalogo/catalogo.csv)",
    "argparse: help --output-catalogo"
  ),
  # ---- construir_catalogo.py: argparse default --output-secciones (linea 586) ----
  @(
    "scripts\pipeline\construir_catalogo.py",
    "default=Path('secciones_indices_v14.csv'),",
    "default=Path('../../output/catalogo/secciones_indices.csv'),",
    "argparse: default --output-secciones"
  ),
  # ---- construir_catalogo.py: argparse help --output-secciones (linea 587) ----
  @(
    "scripts\pipeline\construir_catalogo.py",
    "(default: secciones_indices_v14.csv)",
    "(default: ../../output/catalogo/secciones_indices.csv)",
    "argparse: help --output-secciones"
  ),

  # ---- cruzar_catalogo_y_mapa.py: docstring (linea 15) ----
  @(
    "scripts\pipeline\cruzar_catalogo_y_mapa.py",
    "    python cruzar_catalogo_y_mapa.py catalogo_v14.csv mapa_paginas.csv ..\\markdowns_v2 fallos_localizados.csv ..\\secciones_indices_v14.csv",
    "    python cruzar_catalogo_y_mapa.py ../../output/catalogo/catalogo.csv ../../output/mapa/mapa_paginas.csv ../../corpus ../../output/localizacion/fallos_localizados.csv ../../output/catalogo/secciones_indices.csv",
    "docstring: linea de comando de ejemplo"
  ),

  # ---- detectar_paginas.py: default ruta_catalogo (linea 546) ----
  @(
    "scripts\pipeline\detectar_paginas.py",
    "argv[3] if len(argv) >= 4 else 'catalogo_v14.csv'",
    "argv[3] if len(argv) >= 4 else '../../output/catalogo/catalogo.csv'",
    "default ruta_catalogo en main()"
  ),

  # ---- parser.py: docstring --corpus (linea 39) ----
  @(
    "scripts\pipeline\parser.py",
    "                          --corpus ../markdowns_v2 \",
    "                          --corpus ../../corpus \",
    "docstring: --corpus path"
  ),
  # ---- parser.py: docstring --output (linea 40) ----
  @(
    "scripts\pipeline\parser.py",
    "                          --output csjn_casos_v17_beta.csv",
    "                          --output ../../output/parser/csjn_casos.csv",
    "docstring: --output path"
  ),
  # ---- parser.py: argparse default --output (linea 1714) ----
  @(
    "scripts\pipeline\parser.py",
    'default="csjn_casos_v16.csv",',
    'default="../../output/parser/csjn_casos.csv",',
    "argparse: default --output"
  )
)

Write-Log "Total de reemplazos definidos: $($replacements.Count)"
Write-Log ""

# -----------------------------------------------------------------------------
# PRE-CHECK
# -----------------------------------------------------------------------------
Write-Log "--- PRE-CHECK ---"
$problems = 0
foreach ($r in $replacements) {
  $file = $r[0]; $old = $r[1]; $desc = $r[3]
  if (-not (Test-Path $file)) {
    Write-Log ("  [FAIL] {0} - archivo no existe" -f $file) "Red"
    $problems++
    continue
  }
  $content = Get-Content $file -Raw
  $count = ([regex]::Matches($content, [regex]::Escape($old))).Count
  if ($count -eq 1) {
    Write-Log ("  [OK]   {0} - {1}" -f (Split-Path $file -Leaf), $desc)
  } else {
    Write-Log ("  [FAIL] {0} - {1} (encontrado {2} veces, esperado 1)" -f (Split-Path $file -Leaf), $desc, $count) "Red"
    $problems++
  }
}

if ($problems -gt 0) {
  Write-Log ""
  Write-Log "ABORTAR: $problems patrones no aparecen exactamente 1 vez." "Red"
  Write-Log "Log guardado en: $logFile"
  exit 1
}

Write-Log ""
Write-Log "Pre-check OK. Todos los patrones aparecen exactamente 1 vez."

if ($DryRun) {
  Write-Log ""
  Write-Log "DRY RUN: no se modifico ningun archivo." "Yellow"
  Write-Log "Para aplicar: .\migracion_paths_2026-05-02.ps1"
  Write-Log ""
  Write-Log "Log guardado en: $logFile"
  exit 0
}

# -----------------------------------------------------------------------------
# APLICAR (atomico por archivo)
# -----------------------------------------------------------------------------
Write-Log ""
Write-Log "--- APLICANDO ---"

$byFile = @{}
foreach ($r in $replacements) {
  $file = $r[0]
  if (-not $byFile.ContainsKey($file)) { $byFile[$file] = @() }
  $byFile[$file] += ,@($r[1], $r[2], $r[3])
}

$totalApplied = 0
$errors = 0
$filesModified = @()

foreach ($file in $byFile.Keys) {
  Write-Log ""
  Write-Log "Archivo: $file"
  $original = Get-Content $file -Raw
  $content = $original
  $originalLength = $original.Length
  $appliedHere = 0
  $errorHere = $false

  foreach ($pair in $byFile[$file]) {
    $old = $pair[0]; $new = $pair[1]; $desc = $pair[2]
    $countBefore = ([regex]::Matches($content, [regex]::Escape($old))).Count
    if ($countBefore -ne 1) {
      Write-Log ("  [FAIL] {0}: el patron ya no aparece exactamente 1 vez (count={1})" -f $desc, $countBefore) "Red"
      $errors++
      $errorHere = $true
      break
    }
    $content = $content.Replace($old, $new)
    Write-Log ("  [OK]   {0}" -f $desc)
    $appliedHere++
  }

  if ($errorHere) {
    Write-Log ("  Archivo NO modificado por errores.") "Red"
    continue
  }

  $tmp = "$file.tmp"
  Set-Content -Path $tmp -Value $content -NoNewline -Encoding UTF8
  $newLength = (Get-Item $tmp).Length
  Move-Item -Path $tmp -Destination $file -Force

  Write-Log ("  Aplicados {0} reemplazos. Tamano: {1} -> {2} bytes (delta: {3})" -f $appliedHere, $originalLength, $newLength, ($newLength - $originalLength))
  $totalApplied += $appliedHere
  $filesModified += $file
}

# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
Write-Log ""
Write-Log "============================================================"
Write-Log "RESUMEN"
Write-Log "  Reemplazos aplicados: $totalApplied de $($replacements.Count)"
Write-Log "  Errores: $errors"
Write-Log "  Archivos modificados: $($filesModified.Count)"
foreach ($f in $filesModified) {
  Write-Log "    - $f"
}
if ($errors -eq 0 -and $totalApplied -eq $replacements.Count) {
  Write-Log "  Estado: OK" "Green"
  Write-Log ""
  Write-Log "Para verificar los cambios:"
  Write-Log "  git diff scripts/pipeline/"
  Write-Log ""
  Write-Log "Para revertir si algo se ve mal:"
  Write-Log "  git checkout scripts/pipeline/"
} else {
  Write-Log "  Estado: HAY ERRORES" "Red"
}
Write-Log ""
Write-Log "Log guardado en: $logFile"
Write-Log "============================================================"
