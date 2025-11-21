# All to Markdown

Sistema completo para crawlear sitios de documentación y convertir todas las páginas a formato Markdown usando IA y [MarkItDown](https://github.com/microsoft/markitdown).

## 🎯 ¿Qué hace este proyecto?

Este proyecto consta de **tres componentes principales** que trabajan juntos:

1. **🕷️ Crawler Inteligente** (`crawl_documentation.py`): Usa GPT-5.1 para navegar automáticamente por documentación siguiendo enlaces de "siguiente página"
2. **📄 Conversor de URLs** (`url_to_markdown.py`): Convierte cualquier URL a Markdown (páginas web, PDFs, videos de YouTube, etc.)
3. **🎬 Orquestador Principal** (`main.py`): Coordina todo el proceso de crawling y conversión

## 📋 Requisitos

- Python 3.10 o superior
- Clave de API de OpenAI (para el crawler)
- MarkItDown instalado con todas las dependencias

## 🚀 Instalación

```bash
# Crear entorno virtual con uv
uv venv --python=3.12 .venv
source .venv/bin/activate

# Clonar e instalar MarkItDown
git clone git@github.com:microsoft/markitdown.git
uv pip install -e 'markitdown/packages/markitdown[all]'

# Instalar dependencias adicionales
uv pip install langchain-openai python-dotenv requests
```

### Configuración de variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
OPENAI_API_KEY=tu_clave_api_aqui
```

## 💻 Uso

### Opción 1: Script Principal (Recomendado)

Usa `main.py` para crawlear y convertir documentación completa:

```bash
# Uso básico
python main.py "https://www.gradio.app/main/guides/quickstart"

# Con directorio de salida personalizado
python main.py "https://docs.python.org/3/tutorial/" -o python_docs

# Con archivo de URLs personalizado
python main.py "https://example.com/docs" -o docs -f urls.txt

# Ver todas las opciones
python main.py --help
```

**¿Qué hace el script principal?**

1. 🔍 Crawlea la documentación desde la URL base (usando IA)
2. 💾 Guarda la lista de URLs encontradas en un archivo
3. 📄 Lee las URLs del archivo
4. 🔄 Convierte cada página a Markdown
5. 💾 Guarda todos los archivos en un directorio organizado

### Opción 2: Crawler de Documentación

Usa `crawl_documentation.py` para solo obtener las URLs:

```bash
python crawl_documentation.py
```

**Configuración del crawler** (edita las constantes en el archivo):

```python
# Model configuration
MODEL_NAME = "gpt-5.1"  # Modelo a usar
REASONING_EFFORT = "high"  # "low", "medium", o "high"

# Crawler configuration
MAX_PAGES = 500  # Máximo de páginas a crawlear
DELAY_BETWEEN_PAGES = 2  # Segundos entre peticiones
```

El crawler:
- 🤖 Usa GPT-5.1 para identificar enlaces de "siguiente página"
- 🔗 Maneja URLs relativas y absolutas automáticamente
- 🔄 Evita loops detectando URLs ya visitadas
- 💾 Guarda todas las URLs en `documentation_urls.txt`
- ⏱️ Incluye delays para ser respetuoso con los servidores

### Opción 3: Conversor Individual

Usa `url_to_markdown.py` para convertir URLs individuales:

```bash
# Convertir una página web
python url_to_markdown.py "https://www.python.org" output.md

# Convertir un video de YouTube (con transcripción)
python url_to_markdown.py "https://www.youtube.com/watch?v=VIDEO_ID" video.md

# Convertir un PDF
python url_to_markdown.py "https://example.com/document.pdf" document.md
```

### Como módulos Python

Todos los scripts pueden importarse y usarse en tus propios programas:

```python
# Usar el crawler
from crawl_documentation import crawl_documentation

urls = crawl_documentation("https://docs.example.com/start")
print(f"Found {len(urls)} pages")

# Usar el conversor
from url_to_markdown import convert_url_to_markdown

success = convert_url_to_markdown(
    url="https://www.python.org",
    output_path="output.md"
)

# Usar el orquestador
from main import process_documentation

process_documentation(
    base_url="https://docs.example.com",
    output_dir="my_docs",
    urls_file="my_urls.txt"
)
```

## 📦 Tipos de contenido soportados

El conversor puede procesar:

- ✅ Páginas web HTML
- ✅ Videos de YouTube (título, descripción, transcripción)
- ✅ Archivos PDF
- ✅ Documentos de Office (Word, Excel, PowerPoint)
- ✅ Imágenes (con metadatos EXIF y OCR)
- ✅ Archivos de audio (con transcripción)
- ✅ Páginas de Wikipedia
- ✅ Feeds RSS
- ✅ Archivos CSV, JSON, XML
- ✅ Archivos ZIP (itera sobre el contenido)
- ✅ Y más...

## 🔧 Estructura del proyecto

```
all_to_markdown/
│
├── crawl_documentation.py       # Crawler inteligente con LLM
│   ├── download_html()          # Descarga HTML de URLs
│   ├── extract_next_link()      # Extrae siguiente enlace con IA
│   └── crawl_documentation()    # Función principal de crawling
│
├── url_to_markdown.py           # Conversor de URLs a Markdown
│   ├── convert_url_to_markdown() # Convierte una URL
│   └── main()                   # CLI para uso standalone
│
├── main.py                      # Orquestador principal
│   ├── sanitize_filename()      # Genera nombres de archivo seguros
│   ├── process_documentation()  # Proceso completo
│   └── main()                   # CLI del orquestador
│
├── .env                         # Variables de entorno (API keys)
├── pyproject.toml              # Configuración del proyecto
└── README.md                    # Esta documentación
```

## 📖 Características principales

### 🕷️ Crawler Inteligente
- 🤖 Usa GPT-5.1 con razonamiento de alta calidad
- 🎯 Identifica automáticamente enlaces de navegación
- 🔗 Normaliza URLs (maneja rutas relativas, duplicados, etc.)
- 🛡️ Protección contra loops infinitos
- ⏱️ Rate limiting configurable
- 💾 Guarda progreso automáticamente

### 📄 Conversor Versátil
- ✨ Soporta múltiples tipos de contenido
- 📁 Crea directorios automáticamente
- ✅ Validación de URLs
- 📊 Información detallada de conversión
- ⚠️ Manejo robusto de errores

### 🎬 Orquestador Completo
- 🔄 Proceso end-to-end automatizado
- 📊 Progreso detallado con estadísticas
- 🏷️ Nombres de archivo sanitizados
- 📁 Organización automática de salida
- ⌨️ Interrumpible con Ctrl+C

## 🎓 Ejemplos de uso avanzado

### Workflow completo paso a paso

```bash
# 1. Primero, crawlea la documentación
python crawl_documentation.py

# 2. (Opcional) Edita documentation_urls.txt para filtrar URLs

# 3. Convierte todas las páginas
python main.py "https://docs.example.com" --file documentation_urls.txt
```

### Procesar múltiples documentaciones

```python
from main import process_documentation

documentations = [
    ("https://docs.python.org/3/tutorial/", "python_docs"),
    ("https://docs.djangoproject.com/en/stable/", "django_docs"),
    ("https://flask.palletsprojects.com/", "flask_docs"),
]

for base_url, output_dir in documentations:
    print(f"\nProcessing {base_url}...")
    process_documentation(base_url, output_dir)
```

### Personalizar el crawler

```python
from crawl_documentation import crawl_documentation

# Crawlear con límite personalizado
urls = crawl_documentation(
    start_url="https://docs.example.com/intro",
    max_pages=100  # Solo las primeras 100 páginas
)

# Guardar en tu propio formato
with open("my_urls.json", "w") as f:
    import json
    json.dump({"urls": urls}, f, indent=2)
```

## 🔍 Archivos generados

Después de ejecutar el proceso completo, encontrarás:

```
all_to_markdown/
├── documentation_urls.txt        # Lista de URLs crawleadas
└── markdown_output/              # Directorio con archivos MD
    ├── guides_quickstart.md
    ├── guides_interface.md
    ├── guides_blocks.md
    └── ...
```

## ⚙️ Configuración avanzada

### Variables configurables en `crawl_documentation.py`

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `MODEL_NAME` | Modelo de OpenAI a usar | `"gpt-5.1"` |
| `REASONING_EFFORT` | Nivel de razonamiento | `"high"` |
| `MAX_PAGES` | Límite de páginas | `500` |
| `DELAY_BETWEEN_PAGES` | Delay entre requests (seg) | `2` |

### Cambiar la URL base en el crawler

Edita la función `main()` en `crawl_documentation.py`:

```python
def main():
    # Cambia esta URL por tu documentación
    start_url = "https://tu-documentacion.com/inicio"
    
    all_urls = crawl_documentation(start_url)
    # ...
```

## 🐛 Solución de problemas

### Error: "OPENAI_API_KEY not found"

**Solución**: Crea un archivo `.env` con tu clave de API:

```bash
echo "OPENAI_API_KEY=tu_clave_aqui" > .env
```

### El crawler no encuentra el siguiente enlace

**Posibles causas**:
- La documentación no tiene enlaces de navegación claros
- El HTML es muy complejo o dinámico
- Intenta aumentar `REASONING_EFFORT` a `"high"`

### Error al convertir URLs

**Solución**: Algunas URLs pueden requerir dependencias adicionales:

```bash
# Para videos de YouTube
uv pip install youtube-transcript-api

# Para PDFs
uv pip install pdfplumber

# Para imágenes con OCR
uv pip install pytesseract
```

## 📝 Archivos del proyecto

| Archivo | Descripción |
|---------|-------------|
| `crawl_documentation.py` | Crawler inteligente con LLM |
| `url_to_markdown.py` | Conversor de URLs a Markdown |
| `main.py` | Script principal orquestador |
| `.env` | Variables de entorno (no incluido) |
| `pyproject.toml` | Configuración del proyecto Python |
| `README.md` | Esta documentación |

## 🤝 Créditos

Este proyecto utiliza:
- [MarkItDown](https://github.com/microsoft/markitdown) de Microsoft para conversión a Markdown
- [LangChain](https://github.com/langchain-ai/langchain) para integración con LLMs
- [OpenAI API](https://platform.openai.com/) para el razonamiento del crawler

## 📄 Licencia

MIT License

