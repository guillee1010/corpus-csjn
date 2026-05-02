"""
test_gemini_un_fallo.py

Script de prueba para validar la API de Gemini end-to-end:
  1. Carga la API key desde .env
  2. Carga el prompt de clasificación desde prompt_gemini_v2_lotes.md
  3. Le pasa UN solo fallo del Tomo 349 (Colegio de Martilleros, p. 1) como input
  4. Ejecuta la llamada con structured output (JSON Mode)
  5. Imprime el JSON resultante en pantalla

Estrategia de modelos (cadena de fallback):
  - Intenta primero gemini-3.1-pro-preview (flagship)
  - Si tira cupo (limit:0), hace fallback a gemini-3-flash-preview
  - Si Flash también falla, hace fallback a gemini-2.5-flash

Uso:
    python scripts/diagnosticos/test_gemini_un_fallo.py
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError

# ============================================================
# Configuración
# ============================================================

PROJ_ROOT = Path(r"C:\Users\guill\Proyectos\corpus-csjn")
ENV_FILE = PROJ_ROOT / ".env"
PROMPT_FILE = PROJ_ROOT / "prompt_gemini_v2_lotes.md"
MD_FILE = PROJ_ROOT / "markdowns_v2" / "LibroVol349-1.md"

# Cadena de modelos a intentar, en orden de preferencia.
MODELOS = [
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
]

# Rango del PRIMER fallo del 349: Colegio de Martilleros (p. 1)
LINEA_INICIO = 51
LINEA_FIN = 394

# ============================================================
# 1. Cargar API key
# ============================================================

print("=== Cargando configuración ===")
load_dotenv(ENV_FILE)
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(f"No se encontró GOOGLE_API_KEY en {ENV_FILE}")

print(f"API key cargada (...{api_key[-4:]})")

# ============================================================
# 2. Cargar prompt y fallo de prueba
# ============================================================

print(f"\n=== Cargando prompt desde {PROMPT_FILE.name} ===")
with open(PROMPT_FILE, encoding="utf-8") as f:
    prompt_sistema = f.read()
print(f"Prompt cargado: {len(prompt_sistema)} caracteres")

print(f"\n=== Extrayendo fallo de prueba ({MD_FILE.name}, lineas {LINEA_INICIO}-{LINEA_FIN}) ===")
with open(MD_FILE, encoding="utf-8") as f:
    md_lines = f.readlines()
fragmento_md = "".join(md_lines[LINEA_INICIO - 1: LINEA_FIN])
print(f"Fragmento extraido: {len(fragmento_md)} caracteres, {LINEA_FIN - LINEA_INICIO + 1} lineas")

# ============================================================
# 3. Llamar a Gemini con cadena de fallback
# ============================================================

client = genai.Client(api_key=api_key)
config = types.GenerateContentConfig(
    system_instruction=prompt_sistema,
    response_mime_type="application/json",
    temperature=0.1,
)

response = None
modelo_exitoso = None

for modelo in MODELOS:
    print(f"\n=== Intentando con {modelo} ===")
    try:
        response = client.models.generate_content(
            model=modelo,
            contents=fragmento_md,
            config=config,
        )
        modelo_exitoso = modelo
        print(f"OK - {modelo} respondio")
        break
    except ClientError as e:
        msg = str(e)
        if "RESOURCE_EXHAUSTED" in msg or "limit: 0" in msg or "429" in msg:
            print(f"  -> Cupo cero/agotado en {modelo}. Probando siguiente.")
            continue
        if "404" in msg or "NOT_FOUND" in msg or "not found" in msg.lower():
            print(f"  -> {modelo} no disponible. Probando siguiente.")
            continue
        print(f"  -> Error inesperado con {modelo}: {e}")
        raise

if response is None:
    print("\nERROR: ningun modelo de la cadena respondio.")
    print("Soluciones posibles:")
    print("  1. Habilitar billing en el proyecto Google Cloud asociado a la API key.")
    print("  2. Esperar a que se renueve el cupo (puede ser por minuto, hora o dia).")
    print("  3. Probar con otros nombres de modelo en la lista MODELOS.")
    exit(1)

# ============================================================
# 4. Mostrar resultado
# ============================================================

print(f"\n=== RESPUESTA DE {modelo_exitoso.upper()} ===\n")
print(response.text)

# Validar JSON
print("\n=== VALIDACION JSON ===")
try:
    parsed = json.loads(response.text)
    if isinstance(parsed, list):
        print(f"OK - Array JSON valido con {len(parsed)} elemento(s)")
        if len(parsed) > 0:
            print(f"\nPrimer elemento - claves: {list(parsed[0].keys())}")
            print(f"Caratula detectada: {parsed[0].get('caratula', 'N/A')}")
    elif isinstance(parsed, dict):
        print("WARNING - Es un dict, no un array. El prompt pide array.")
    else:
        print(f"WARNING - Es de tipo {type(parsed).__name__}")
except json.JSONDecodeError as e:
    print(f"ERROR - JSON invalido: {e}")

# Metadata de tokens
if hasattr(response, "usage_metadata") and response.usage_metadata:
    um = response.usage_metadata
    print(f"\n=== USO DE TOKENS ===")
    print(f"  Input:  {getattr(um, 'prompt_token_count', '?')}")
    print(f"  Output: {getattr(um, 'candidates_token_count', '?')}")
    print(f"  Total:  {getattr(um, 'total_token_count', '?')}")

print(f"\n=== Listo (modelo: {modelo_exitoso}) ===")
