import re
import sys
from pathlib import Path
import shutil
from datetime import datetime
from collections import Counter

ARCHIVO_ULTIMA_RUTA = '.ultima_ruta.txt'
superscript_counter = Counter()
frase_counter = Counter()

SIMPLE_WORDS = ["infra", "supra", "ibid", "passim", "circa"]
PHRASE_PATTERNS = {
    "op. cit.": r"op\. cit\.",
    "et al.": r"et al\.",
    "s.v.": r"s\.v\.",
    "loc. cit.": r"loc\. cit\.",
    "i.e.": r"i\.e\.",
    "e.g.": r"e\.g\."
}

simple_pattern = re.compile(rf"(?<!\*)\b({'|'.join(SIMPLE_WORDS)})\b([.,;:]?)(?!\*)")
phrase_wrappers = {
    p: re.compile(rf"(?<!\*)\b{ptn}\b([ \t]*[.,;:])?(?!\*)")
    for p, ptn in PHRASE_PATTERNS.items()
}
phrase_spacings = {
    p: re.compile(rf"\*\s*{ptn}\s*\*") for p, ptn in PHRASE_PATTERNS.items()
}
inline_number_pattern = re.compile(r'([A-Za-zÁÉÍÓÚÜüáéíóúñÑ]+)(\d{1,4})([.,;:]?)')
after_punctuation_pattern = re.compile(r'([»”’\)\]])(\d{1,4})([.,;:]?)')

def guardar_ultima_ruta(ruta):
    with open(ARCHIVO_ULTIMA_RUTA, 'w', encoding='utf-8') as f:
        f.write(ruta)

def cargar_ultima_ruta():
    if Path(ARCHIVO_ULTIMA_RUTA).exists():
        return Path(ARCHIVO_ULTIMA_RUTA).read_text(encoding='utf-8').strip()
    return ''

def excluir_fecha(texto, pos):
    contexto = texto[max(0, pos - 100):pos].lower()
    return bool(re.search(r'\b(año|años)\s*(\d{1,4})?\b', contexto))

def ya_en_cursiva(texto, start, end):
    return texto[max(0, start - 1)] == '*' and texto[min(len(texto) - 1, end)] == '*'

def procesar_texto(texto):
    def reemplazar_simple(match):
        palabra, punct = match.groups()
        start, end = match.span(1)
        if ya_en_cursiva(texto, start, end):
            return match.group(0)
        frase_counter[palabra] += 1
        return f'*{palabra}*{punct or ""}'

    texto = simple_pattern.sub(reemplazar_simple, texto)

    for frase, fixer in phrase_spacings.items():
        if fixer.search(texto):
            frase_counter[frase] += 1
        texto = fixer.sub(f'*{frase}*', texto)

    for frase, detector in phrase_wrappers.items():
        def make_reemplazo(f):
            def reemplazar_frase(match):
                raw_punct = match.group(1) or ''
                punct = raw_punct.strip()
                start, end = match.span(0)
                palabra_fin = end - len(raw_punct)
                if ya_en_cursiva(texto, start, palabra_fin):
                    return match.group(0)
                frase_counter[f] += 1
                return f'*{f}{punct}*'
            return reemplazar_frase

        texto = detector.sub(make_reemplazo(frase), texto)

    def reemplazar_palabra_numero(match):
        palabra, numero, puntuacion = match.groups()
        pos = match.start()
        if excluir_fecha(texto, pos):
            return match.group(0)
        clave = f"{palabra}{numero}"
        superscript_counter[clave] += 1
        return f"{palabra}<sup>{numero}</sup>{puntuacion or ''}"

    texto = inline_number_pattern.sub(reemplazar_palabra_numero, texto)

    def reemplazar_signo_numero(match):
        simbolo, numero, puntuacion = match.groups()
        clave = f"{simbolo}{numero}"
        superscript_counter[clave] += 1
        return f"{simbolo}<sup>{numero}</sup>{puntuacion or ''}"

    texto = after_punctuation_pattern.sub(reemplazar_signo_numero, texto)

    texto = re.sub(r'([.,;:])(?=[^\s\n</])', r'\1 ', texto)
    texto = re.sub(r'(?<![.,;:]) {2,}', ' ', texto)
    texto = re.sub(r' +\n', '\n', texto)
    texto = texto.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")

    return texto

def contar_lineas_modificadas(original, actualizado):
    original_lines = original.splitlines()
    actualizado_lines = actualizado.splitlines()
    max_len = max(len(original_lines), len(actualizado_lines))
    cambios = 0
    for i in range(max_len):
        linea_original = original_lines[i] if i < len(original_lines) else ''
        linea_nueva = actualizado_lines[i] if i < len(actualizado_lines) else ''
        if linea_original != linea_nueva:
            cambios += 1
    return cambios

def generar_resumen_total(lineas_modificadas=0):
    total_frases = sum(frase_counter.values())
    total_super = sum(superscript_counter.values())
    total = total_frases + total_super
    return "\n".join([
        "=== Total de modificaciones ===",
        f"- Frases latinas corregidas: {total_frases}",
        f"- Palabras con superíndice: {total_super}",
        f"- Líneas modificadas: {lineas_modificadas}",
        f"- Total general: {total}"
    ])

def process_file(file_path):
    file = Path(file_path)
    if not file.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return False

    original_text = file.read_text(encoding='utf-8')
    updated_text = procesar_texto(original_text)

    if updated_text == original_text:
        print("ℹ️ No se realizaron cambios.")
        return True

    backup_path = file.with_suffix(file.suffix + ".bak")
    shutil.copyfile(file, backup_path)
    print(f"✅ Copia de respaldo creada: {backup_path.name}")

    file.write_text(updated_text, encoding='utf-8')
    print(f"✅ Archivo actualizado: {file.name}")

    lineas_modificadas = contar_lineas_modificadas(original_text, updated_text)

    log_path = file.parent / "cambios.txt"
    with open(log_path, "w", encoding='utf-8') as log:
        log.write(f"=== {datetime.now().isoformat()} ===\n")
        log.write(f"Archivo: {file.name}\n\n")
        log.write(generar_resumen_total(lineas_modificadas) + "\n\n")

        if frase_counter:
            log.write("=== Frases latinas corregidas ===\n")
            for frase, cuenta in frase_counter.most_common():
                log.write(f"- *{frase}*: {cuenta} vez/veces\n")

        if superscript_counter:
            log.write("\n=== Conversiones a superíndice ===\n")
            for entrada, cuenta in superscript_counter.most_common():
                log.write(f"- {entrada}: {cuenta} vez/veces\n")

        log.write("\n" + generar_resumen_total(lineas_modificadas) + "\n")
        log.write("\n---\n")

    print(f"📝 Log actualizado: {log_path.name}")
    return True

if __name__ == "__main__":
    print("📄 Formateador de términos latinos y superíndices")
    ultima = cargar_ultima_ruta()
    if ultima:
        print(f"(Enter para usar la última ruta: {ultima})")
    ruta = input("Ruta del archivo .md a procesar: ").strip()
    if not ruta:
        ruta = ultima
    if not ruta or not Path(ruta).exists():
        print("❌ Ruta no válida.")
        sys.exit(1)

    guardar_ultima_ruta(ruta)
    process_file(ruta)
