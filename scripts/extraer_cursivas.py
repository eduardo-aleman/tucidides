import re
from pathlib import Path
from collections import defaultdict

ARCHIVO_ULTIMA_RUTA = ".ultima_ruta.txt"
ARCHIVO_ULTIMA_LISTA = "ultima_lista_cursivas.txt"

def cargar_ultima_ruta():
    if Path(ARCHIVO_ULTIMA_RUTA).exists():
        return Path(ARCHIVO_ULTIMA_RUTA).read_text(encoding="utf-8").strip()
    return ""

def guardar_ultima_ruta(ruta):
    Path(ARCHIVO_ULTIMA_RUTA).write_text(str(ruta), encoding="utf-8")

def extraer_cursivas_con_frecuencia_y_lineas(archivo_md, guardar_txt=True):
    ruta = Path(archivo_md)
    if not ruta.exists():
        print(f"❌ Archivo no encontrado: {ruta}")
        return

    guardar_ultima_ruta(ruta)

    patron = re.compile(r'(?<!\*)\*(.+?)\*(?!\*)|(?<!_)_(.+?)_(?!_)', re.DOTALL)
    frecuencia = defaultdict(int)
    lineas = defaultdict(list)

    with ruta.open(encoding="utf-8") as f:
        for numero_linea, linea in enumerate(f, start=1):
            for a, b in patron.findall(linea):
                texto = a or b
                frecuencia[texto] += 1
                lineas[texto].append(numero_linea)

    if not frecuencia:
        print("ℹ️ No se encontraron palabras o frases en cursiva.")
        return

    print(f"\n✅ Se encontraron {len(frecuencia)} elementos únicos en cursiva.\n")
    for i, clave in enumerate(sorted(frecuencia, key=str.lower), 1):
        print(f"{i}. {clave} — {frecuencia[clave]} vez/veces — líneas {lineas[clave]}")

    if guardar_txt:
        with open(ARCHIVO_ULTIMA_LISTA, "w", encoding="utf-8") as f:
            f.write("# Lista de cursivas con frecuencia y localización\n\n")
            for clave in sorted(frecuencia, key=str.lower):
                ocurrencias = frecuencia[clave]
                ubicacion = ", ".join(map(str, lineas[clave]))
                f.write(f"- **{clave}** — {ocurrencias} vez/veces — líneas: {ubicacion}\n")
        print(f"\n💾 Lista guardada en: {ARCHIVO_ULTIMA_LISTA}")

def mostrar_lista_anterior():
    ruta = Path(ARCHIVO_ULTIMA_LISTA)
    if ruta.exists():
        print(f"📄 Última lista disponible: {ARCHIVO_ULTIMA_LISTA}")
        opcion = input("¿Deseas verla? (s/n): ").strip().lower()
        if opcion == "s":
            print("\n📋 Última lista de cursivas:\n")
            print(ruta.read_text(encoding="utf-8"))
    else:
        print("ℹ️ Aún no se ha generado ninguna lista de cursivas.")

if __name__ == "__main__":
    print("📄 Extractor de cursivas Markdown con frecuencia y localización")
    mostrar_lista_anterior()

    ruta_anterior = cargar_ultima_ruta()
    if ruta_anterior:
        print(f"(Enter para usar la última ruta: {ruta_anterior})")
    ruta_input = input("Ruta del archivo .md a procesar: ").strip()
    ruta_final = ruta_input if ruta_input else ruta_anterior

    if not ruta_final:
        print("❌ No se proporcionó ninguna ruta.")
    else:
        extraer_cursivas_con_frecuencia_y_lineas(ruta_final, guardar_txt=True)
