import re
import sys
from pathlib import Path
import shutil
from datetime import datetime

LAST_FILE_PATH = Path(".last_path")

# Palabras latinas simples que deben ir en cursiva
SIMPLE_WORDS = ["infra", "supra", "ibid", "passim", "circa"]

# Frases latinas que pueden incluir puntos o espacios
PHRASE_PATTERNS = {
    "op. cit.": r"op\. cit\.",
    "et al.": r"et al\.",
    "s.v.": r"s\.v\.",
    "loc. cit.": r"loc\. cit\.",
    "i.e.": r"i\.e\.",
    "e.g.": r"e\.g\."
}

# Compilar patrones
simple_pattern = re.compile(rf"(?<!_)\\b({'|'.join(SIMPLE_WORDS)})\\b(?!_)")
phrase_wrappers = {phrase: re.compile(rf"(?<!_)\\b{pattern}\\b(?!_)")
                   for phrase, pattern in PHRASE_PATTERNS.items()}
phrase_spacings = {phrase: re.compile(rf"_\s*{pattern}\s*_")
                   for phrase, pattern in PHRASE_PATTERNS.items()}

def wrap_italics(text):
    text = simple_pattern.sub(r'_\1_', text)
    for phrase, fixer in phrase_spacings.items():
        text = fixer.sub(f'_{phrase}_', text)
    for phrase, detector in phrase_wrappers.items():
        text = detector.sub(f'_{phrase}_', text)
    return text

def process_file(file_path):
    file = Path(file_path)

    if not file.exists():
        print(f"❌ Archivo no encontrado: {file_path}")
        return False

    original_lines = file.read_text(encoding='utf-8').splitlines()
    updated_lines = []
    changes = []

    for i, line in enumerate(original_lines):
        updated_line = wrap_italics(line)
        updated_lines.append(updated_line)
        if updated_line != line:
            changes.append(f"Línea {i+1}:\n- {line}\n+ {updated_line}\n")

    backup_path = file.with_suffix(file.suffix + ".bak")
    shutil.copyfile(file, backup_path)
    print(f"✅ Copia de respaldo creada: {backup_path.name}")

    file.write_text("\n".join(updated_lines), encoding='utf-8')
    print(f"✅ Archivo actualizado: {file.name}")

    if changes:
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_path = file.parent / f"format_changes_{date_str}.log"
        with open(log_path, "a", encoding='utf-8') as log:
            log.write(f"=== {datetime.now().isoformat()} ===\n")
            log.write(f"Archivo: {file.name}\n")
            log.write("\n".join(changes))
            log.write("\n\n")
        print(f"📝 {len(changes)} cambio(s) escrito(s) en {log_path.name}")
    else:
        print("ℹ️ No se realizaron cambios.")
    return True

if __name__ == "__main__":
    print("📄 Formateador de términos latinos (Markdown con guiones bajos)")
    if LAST_FILE_PATH.exists():
        last_file = LAST_FILE_PATH.read_text().strip()
        print(f"(Presiona Enter para usar el último archivo: {last_file})")
    else:
        last_file = ""

    file_path = input("Introduce el path del archivo .md a procesar: ").strip()
    if not file_path and last_file:
        file_path = last_file

    if not file_path:
        print("⚠️ No se proporcionó ningún archivo.")
        sys.exit(1)

    # Guardar el path actual como último usado
    LAST_FILE_PATH.write_text(file_path)

    process_file(file_path)
