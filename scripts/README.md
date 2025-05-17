# Formateador de términos latinos y superíndices

Este script automatiza la corrección de frases latinas y la conversión de números en superíndice en archivos `.md`. Está diseñado para usarse con textos académicos, entradas de blog o libros digitales en formato Markdown.

## Funciones principales

- Convierte expresiones latinas comunes como `op. cit.`, `et al.`, `infra`, etc., al formato *cursiva* con asteriscos.
- Detecta palabras seguidas de números y las convierte al formato con superíndice (ejemplo: `nota23` → `nota<sup>23</sup>`).
- Guarda una copia de seguridad del archivo original (`.bak`).
- Genera un archivo de log `cambios.txt` con un resumen detallado de las modificaciones.
- Evita aplicar cursivas si el término ya está entre asteriscos, para prevenir errores como `**op. cit.**`.

## Ejemplos

### Frases latinas corregidas

```markdown
Se hace referencia a *infra*, *supra* y *ibid.* en las notas anteriores.
Según *op. cit.* (p. 45), el argumento ya se ha presentado.
