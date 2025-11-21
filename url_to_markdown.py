"""
URL to Markdown Converter

Este script convierte contenido desde URLs a formato Markdown usando MarkItDown.
Puede ser usado como módulo o como script de línea de comandos.

Uso como script:
    python url_to_markdown.py <URL> <output_path>

Ejemplo:
    python url_to_markdown.py "https://www.python.org" output.md
"""

import sys
import argparse
from pathlib import Path
from markitdown import MarkItDown


def convert_url_to_markdown(url: str, output_path: str) -> bool:
    """
    Convert content from a URL to Markdown and save it to a file.
    
    Args:
        url (str): The URL to convert (can be a webpage, PDF, YouTube video, etc.)
        output_path (str): The path where the Markdown file will be saved
        
    Returns:
        bool: True if conversion was successful, False otherwise
        
    Raises:
        Exception: If there's an error during conversion or file writing
    """
    try:
        # Create MarkItDown instance
        md = MarkItDown()
        
        print(f"🔄 Convirtiendo: {url}")
        
        # Convert the URL to Markdown
        result = md.convert(url)
        
        # Create output directory if it doesn't exist
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the Markdown content to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.text_content)
        
        # Print success message with details
        print(f"✅ Conversión exitosa!")
        if result.title:
            print(f"📄 Título: {result.title}")
        print(f"💾 Guardado en: {output_file.absolute()}")
        print(f"📊 Tamaño: {len(result.text_content)} caracteres")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la conversión: {e}", file=sys.stderr)
        return False


def main():
    """
    Main function for command-line execution.
    Parses arguments and calls convert_url_to_markdown.
    """
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Convierte contenido desde URLs a formato Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python url_to_markdown.py "https://www.python.org" output.md
  python url_to_markdown.py "https://www.youtube.com/watch?v=VIDEO_ID" video.md
  python url_to_markdown.py "https://example.com/document.pdf" document.md
  
Tipos de contenido soportados:
  - Páginas web HTML
  - Videos de YouTube (con transcripción)
  - Archivos PDF
  - Documentos de Office (Word, Excel, PowerPoint)
  - Imágenes
  - Y más...
        """
    )
    
    # Add positional arguments
    parser.add_argument(
        "url",
        type=str,
        help="URL del contenido a convertir"
    )
    
    parser.add_argument(
        "output_path",
        type=str,
        help="Ruta donde guardar el archivo Markdown"
    )
    
    # Add optional arguments
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate URL format
    if not (args.url.startswith("http://") or args.url.startswith("https://")):
        print("⚠️  Advertencia: La URL debería empezar con 'http://' o 'https://'", file=sys.stderr)
        print(f"    URL recibida: {args.url}")
        response = input("¿Deseas continuar de todas formas? (s/n): ")
        if response.lower() != 's':
            print("❌ Operación cancelada.")
            sys.exit(1)
    
    # Convert URL to Markdown
    success = convert_url_to_markdown(args.url, args.output_path)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

