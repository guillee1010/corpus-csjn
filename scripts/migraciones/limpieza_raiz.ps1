<#
limpieza_raiz.ps1 — limpieza de la raíz y de no-canónicos (corpus-csjn)
=======================================================================
Generado en la sesión de gates/MAPA. CORRER DESDE LA RAÍZ DEL REPO.

LEÉ ANTES DE CORRER. Lo NO destructivo (mover, stagear) está activo.
Lo DESTRUCTIVO (borrar) y lo dudoso está COMENTADO: descomentá vos,
línea por línea, después de revisar.

  Categorías:
   1) Mover artefactos de ESTA sesión a su carpeta Hxx.
   2) Stagear la baja del cruft ya borrado.
   3) Preservar gold de H163 (NO borrar).
   4) [GATEADO] Mover no-canónico de pipeline, previo chequeo de imports.
   5) [COMENTADO] Uploads sueltos + dirs gitignoreados: tu decisión.
   6) Re-verificar allowlist.

NÚMERO DE SESIÓN: la BITACORA llega a H163 pero derivar_partes ya menciona
H165 → está atrasada. El número real es >=H166. Reemplazá $H por el real.
#>

# ── Número de sesión (REEMPLAZAR por el real, ver nota de arriba) ──────────
$H = "H16x"   # <-- placeholder. Confirmá el número y cambialo.

$dstAud = "scripts\auditoria\$H"
New-Item -ItemType Directory -Force -Path $dstAud | Out-Null
Write-Host "Destino auditoría de sesión: $dstAud`n" -ForegroundColor Cyan

# ── 1) Artefactos de ESTA sesión -> su Hxx (no destructivo) ───────────────
# El diagnóstico de los 478 EXTRA y su salida.
if (Test-Path "caracterizar_extra_indice.py") {
    Move-Item "caracterizar_extra_indice.py" $dstAud
    Write-Host "movido: caracterizar_extra_indice.py -> $dstAud"
}
if (Test-Path "output\visor\extra_indice_caracterizacion.txt") {
    Move-Item "output\visor\extra_indice_caracterizacion.txt" $dstAud
    Write-Host "movido: extra_indice_caracterizacion.txt -> $dstAud"
}

# ── 2) Stagear la baja del cruft ya borrado (tracked) ─────────────────────
# extraer_lote_M20.py ya está borrado en el working tree (estado ' D').
if ((git status --porcelain "extraer_lote_M20.py") -match '^ D') {
    git rm "extraer_lote_M20.py" | Out-Null
    Write-Host "git rm: extraer_lote_M20.py (baja stageada)"
}

# ── 3) Preservar gold de H163 — NO BORRAR ─────────────────────────────────
# partes_adjudicacion_manual.csv = 30 overrides manuales (gold, H163-02).
# Se preserva con su sesión. OJO: confirmá si ya existe el gold congelado
# en otro lado (H163-03 dice "fuera del pipeline") -> esto puede ser el
# original o un duplicado. NO lo borres hasta saberlo.
$h163 = "scripts\diagnostico\H163"
if (Test-Path "output\parser\partes_adjudicacion_manual.csv") {
    New-Item -ItemType Directory -Force -Path $h163 | Out-Null
    Move-Item "output\parser\partes_adjudicacion_manual.csv" $h163
    Write-Host "preservado (gold): partes_adjudicacion_manual.csv -> $h163"
}

# ── 4) [GATEADO] no-canónico en pipeline: extraer_recuperados_H109.py ──────
# Es one-shot de H109, no está en la cadena. Su familia vive en
# scripts\diagnostico\H109\. PERO: confirmá primero que NADIE lo importa.
Write-Host "`n[CHEQUEO] ¿alguien importa extraer_recuperados_H109?" -ForegroundColor Yellow
Select-String -Path scripts\pipeline\*.py -Pattern 'import extraer_recuperados|from extraer_recuperados'
Write-Host "  (si la línea de arriba NO devolvió nada, descomentá el git mv siguiente)`n"
# git mv "scripts\pipeline\extraer_recuperados_H109.py" "scripts\diagnostico\H109\"

# ── 5) [COMENTADO] Uploads sueltos + dirs gitignoreados: TU DECISIÓN ───────
# test_spacy.py — spaCy rechazado (mismatch ontológico). Archivar o borrar:
# Move-Item "test_spacy.py" "archivo\"
# Remove-Item "test_spacy.py"

# muestra_zona_epilogo.csv (532 KB) — muestra para configurar derivar_epilogo.
# Si ya cumplió, a exploratorio o borrar:
# Move-Item "muestra_zona_epilogo.csv" "scripts\diagnostico\$H\"
# Remove-Item "muestra_zona_epilogo.csv"

# Dirs top-level GITIGNOREADOS (no están en git -> sin red de recuperación).
# Revisá su contenido ANTES. docs/ lo marcaste deprecado; diagnostico/ y
# epilogo_muestra/ son extracciones sueltas. Mover a archivo\ es más seguro
# que borrar:
# Move-Item "docs" "archivo\docs_deprecado"
# Move-Item "diagnostico" "archivo\diagnostico_suelto"
# Move-Item "epilogo_muestra" "archivo\epilogo_muestra"

# ── 6) Re-verificar allowlist ─────────────────────────────────────────────
# Antes: agregá  "MAPA.md",  a ROOT_FILES_OK en
# scripts\tests\check_allowlist_paths.py (es archivo nuevo en raíz).
Write-Host "`n[VERIFICACIÓN] corré después de editar el allowlist:" -ForegroundColor Cyan
Write-Host "  python scripts\tests\check_allowlist_paths.py --all"
