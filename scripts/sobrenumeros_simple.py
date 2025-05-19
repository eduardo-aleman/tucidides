import re
import os

ARCHIVO_ULTIMA_RUTA = '.ultima_ruta.txt'

def guardar_ultima_ruta(ruta):
    with open(ARCHIVO_ULTIMA_RUTA, 'w', encoding='utf-8') as f:
        f.write(ruta)

def cargar_ultima_ruta():
    if os.path.exists(ARCHIVO_ULTIMA_RUTA):
        with open(ARCHIVO_ULTIMA_RUTA, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ''

def procesar_archivo(ruta):
    with open(ruta, 'r', encoding='utf-8') as f:
        texto = f.read()

    # Evita modificar notas en fechas
    def excluir_fecha(pos):
        contexto = texto[max(0, pos - 100):pos].lower()
        palabras = re.findall(r'\b\w+\b', contexto)[-3:]
        return any(p in ['año', 'años', 'entre', 'del'] for p in palabras)

    # palabra + número
    def reemplazar(match):
        palabra, numero, puntuacion = match.groups()
        if excluir_fecha(match.start()):
            return match.group(0)
        return f'{palabra}<sup>{numero}</sup>{puntuacion}'

    texto = re.sub(r'([A-Za-zÁÉÍÓÚÜüáéíóúñÑ]+)(\d{1,3})([.,;:]?)', reemplazar, texto)
    texto = re.sub(r'([»”’\)\]])(\d{1,3})([.,;:]?)', r'\1<sup>\2</sup>\3', texto)

    # Espaciado y comillas
    texto = re.sub(r'([.,;:])(?=[^\s\n</])', r'\1 ', texto)
    texto = re.sub(r'(?<![.,;:]) {2,}', ' ', texto)
    texto = re.sub(r' +\n', '\n', texto)
    texto = texto.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")

    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(texto)

    print("✅ Sobrenúmeros aplicados sin enlaces ni notas.")

if __name__ == "__main__":
    ultima_ruta = cargar_ultima_ruta()
    if ultima_ruta:
        print(f"Última ruta usada: {ultima_ruta}")
    ruta = input("Ruta del archivo Markdown (Enter para usar la última): ").strip()
    if not ruta:
        if not ultima_ruta:
            print("⚠️ No hay ruta previa guardada.")
            exit()
        ruta = ultima_ruta

    if not os.path.exists(ruta):
        print("❌ Ruta inválida.")
        exit()

    procesar_archivo(ruta)
    guardar_ultima_ruta(ruta)
