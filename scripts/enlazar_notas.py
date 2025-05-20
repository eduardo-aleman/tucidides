import re
from pathlib import Path

ARCHIVO_ULTIMA_RUTA = Path(".ultima_ruta.txt")

def obtener_ruta():
    if ARCHIVO_ULTIMA_RUTA.exists():
        ultima = ARCHIVO_ULTIMA_RUTA.read_text(encoding="utf-8").strip()
        print(f"📄 Último archivo usado: {ultima}")
        usar = input("¿Usar este archivo? (Enter = sí, n = no): ").strip().lower()
        if usar != "n":
            return Path(ultima)
    ruta = input("Ruta del archivo .md a procesar: ").strip()
    ARCHIVO_ULTIMA_RUTA.write_text(ruta, encoding="utf-8")
    return Path(ruta)

def procesar_md_con_notas_multilinea_markdown(ruta_md):
    contenido = ruta_md.read_text(encoding="utf-8")

    # Enlazar referencias <sup>n</sup> → <a href="#nota-n"><sup id="ref-n-x">n</sup></a>
    ref_counter = {}
    def enlazar(match):
        n = match.group(1)
        ref_counter[n] = ref_counter.get(n, 0) + 1
        return f'<a href="#nota-{n}"><sup id="ref-{n}-{ref_counter[n]}">{n}</sup></a>'

    contenido = re.sub(r'<sup>(\d+)</sup>', enlazar, contenido)

    # Dividir antes y después de ## Notas
    partes = re.split(r'(##\s+Notas\s*\n)', contenido, maxsplit=1)
    if len(partes) < 3:
        print("❌ No se encontró encabezado '## Notas'.")
        return

    antes_de_notas, encabezado, cuerpo_notas = partes

    # Extraer bloques de notas multilínea usando separación por números
    secciones = re.split(r'(?m)^(\d+)\.\s+', cuerpo_notas)
    notas_dict = {}
    for i in range(1, len(secciones) - 1, 2):
        numero = secciones[i]
        bloque = secciones[i + 1]
        siguiente = re.search(r'(?m)^(\d+)\.\s+', bloque)
        if siguiente:
            texto = bloque[:siguiente.start()].rstrip()
        else:
            texto = bloque.rstrip()
        notas_dict[numero] = texto

    # Reescribir sección de notas en Markdown con IDs y [↩︎]
    bloque_markdown = encabezado
    for n in sorted(notas_dict, key=lambda x: int(x)):
        ref_id = f"ref-{n}-1"
        texto = notas_dict[n]
        # Insertar ancla id con comentario invisible para Hugo
        bloque_markdown += f'{n}. <!-- id="nota-{n}" -->\n{textwrap_indent(texto)}\n\n[↩︎](#{ref_id})\n\n'

    # Unir todo
    contenido_final = antes_de_notas + bloque_markdown

    salida = ruta_md.with_name(ruta_md.stem + "_notas_markdown.md")
    salida.write_text(contenido_final, encoding="utf-8")
    print(f"✅ Archivo generado con notas multilínea en Markdown: {salida}")

def textwrap_indent(texto, prefix="    "):
    # Indenta cada línea del bloque para formar una lista multilínea válida en Markdown
    return "\n".join(prefix + linea if linea.strip() else "" for linea in texto.splitlines())

# Ejecutar
if __name__ == "__main__":
    ruta = obtener_ruta()
    if ruta.exists():
        procesar_md_con_notas_multilinea_markdown(ruta)
    else:
        print("❌ Ruta no válida.")
