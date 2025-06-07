# ReinventProse 2.0

**Versión:** 0.0.1 (Según archivos al 07/06/2025)
**Autor Principal:** Mauricio José Tobares (Conceptualización y Dirección)
**Desarrollo:** PJ (Programador Jefe IA) y Equipo de Asistentes IA:
*   Gestor de Proyectos (GP)
*   UX/UI (DUXUI)
*   Programador Jefe (PJ)
*   Ingeniedo de pruebas (IP)

## Descripción General

ReinventProse 2.0 es una aplicación de escritorio diseñada para la gestión integral de proyectos de escritura creativa. Su objetivo es proporcionar a los escritores una herramienta robusta y organizada para llevar sus ideas desde la concepción inicial hasta un manuscrito estructurado, listo para ser revisado o exportado.

La aplicación permite a los usuarios:
*   Crear y gestionar una biblioteca de múltiples libros o proyectos de escritura.
*   Definir y editar metadatos detallados para cada libro, incluyendo título, autor, sinopsis, prólogo, texto de contraportada e imagen de portada.
*   Estructurar los libros en capítulos, con la capacidad de añadir, eliminar y reordenar (funcionalidad de reordenar no implementada explícitamente en el código analizado, pero es una expectativa común).
*   Escribir y formatear el contenido de los capítulos utilizando un editor de texto enriquecido que soporta estilos básicos como negrita, cursiva, subrayado, y selección de fuentes, tamaños y colores.
*   Desarrollar ideas asociadas a cada capítulo, diferenciando entre una "idea abstracta" principal y una lista de "ideas concretas" más detalladas.
*   Exportar los manuscritos completos a diversos formatos, incluyendo texto plano (.txt), Microsoft Word (.docx) y PDF (.pdf), facilitando la compartición y revisión.

ReinventProse 2.0 está construido con Python y la librería wxPython para la interfaz gráfica de usuario, utilizando SQLite para la persistencia de datos local.

## Estado Actual del Proyecto

Este proyecto se encuentra en una fase de desarrollo activo. La versión actual (basada en el análisis del código proporcionado y que en realidad NO ES la primera versión pero sí que es la primera versión funcional) implementa las funcionalidades centrales descritas anteriormente.

**Puntos Destacados de la Arquitectura:**
*   **Interfaz de Usuario Flexible:** Utiliza `wx.aui.AuiManager` para permitir un layout de paneles personalizable por el usuario, cuyo estado se persiste entre sesiones.
*   **Separación de Responsabilidades:** Módulos bien definidos para la interfaz de usuario (Vistas), lógica de negocio (`AppHandler`), y acceso a datos (`DBManager`).
*   **Gestión de Datos Local:** Toda la información se almacena en una base de datos SQLite local (`reinventprose_v2_data.db`), ubicada en el mismo directorio que la aplicación o en un directorio de configuración del usuario.
*   **Manejo de Cambios:** Implementa un sistema de "dirty flag" para alertar sobre cambios no guardados y prevenir la pérdida accidental de datos.

## Requisitos y Dependencias

*   **Python:** Versión 3.x (desarrollado y probado presumiblemente con una versión reciente de Python 3).
*   **wxPython:** Para la interfaz gráfica de usuario. Se recomienda la última versión estable (Phoenix).
    *   Instalación: `pip install wxpython`
*   **python-docx (Opcional, para exportación a .docx):**
    *   Instalación: `pip install python-docx`
    *   Si no está instalada, la funcionalidad de exportar a DOCX estará deshabilitada.
*   **reportlab (Opcional, para exportación a .pdf):**
    *   Instalación: `pip install reportlab`
    *   Si no está instalada, la funcionalidad de exportar a PDF estará deshabilitada.

## Cómo Ejecutar

1.  Asegurarse de tener Python 3.x instalado.
2.  Clonar este repositorio:
    ```bash
    git clone <URL-del-repositorio>
    cd <nombre-del-directorio-del-repositorio>
    ```
3.  (Recomendado) Crear y activar un entorno virtual:
    ```bash
    python -m venv .venv
    # En Windows
    .\.venv\Scripts\activate
    # En macOS/Linux
    source .venv/bin/activate
    ```
4.  Instalar las dependencias:
    ```bash
    pip install wxpython
    # Para funcionalidades de exportación completas:
    pip install python-docx reportlab
    ```
5.  Ejecutar la aplicación:
    ```bash
    python main.py
    ```

## Estructura del Proyecto (Módulos Principales)

*   `main.py`: Punto de entrada de la aplicación.
*   `AppHandler.py`: Lógica de negocio y coordinación.
*   `DBManager.py`: Gestión de la base de datos SQLite.
*   `MainWindow.py`: Ventana principal y gestión del layout AUI.
*   `LibraryView.py`: Vista de la biblioteca de libros.
*   `BookDetailsView.py`: Vista para los detalles de un libro.
*   `ChapterListView.py`: Vista de la lista de capítulos.
*   `ChapterContentView.py`: Editor de contenido enriquecido para capítulos.
*   `AbstractIdeaView.py`: Vista para la idea abstracta del capítulo.
*   `ConcreteIdeaView.py`: Vista para las ideas concretas del capítulo.
*   `NewBookDialog.py`: Diálogo para crear nuevos libros.
*   `CustomAboutDialog.py`: Ventana "Acerca de".
*   `Exporter.py`: Lógica para exportar a TXT, DOCX, PDF.
*   `Util.py`: Funciones de utilidad (carga de assets, etc.).
## FUTURO:
En próximas versiones se implementará un sistema de directorios tanto para módulos como para imágenes quedando los siguientes:
*   `RPImages/`: (Directorio futuro) Contiene imágenes e iconos utilizados por la aplicación (ej. `app_icon.ico`, iconos de la barra de herramientas).
*   `RPModules/` (Directorio futuro) Aquí se moverán todos los archivos de módulos del programa, quedando solamente main.py en la raíz del sistema.
*   `RPDB/` (Directorio futuro) para mejorar la organización del programa, cuando se ejecute la creación de la base de datos, se creará en este directorio específico.

## Contribuciones

Actualmente, el desarrollo está centralizado. Para futuras contribuciones, por favor contactar al Autor Principal.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo `LICENSE` (a ser creado, o referenciar el texto de licencia en `CustomAboutDialog.py`) para más detalles.

---
*Este README fue generado por PJ, Programador Jefe, bajo la atenta dirección del Jefe (Mauricio José Tobares).*
