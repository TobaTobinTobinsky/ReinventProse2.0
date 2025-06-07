# -*- coding: utf-8 -*-
"""
Nombre del Archivo: Util.py
Descripción: Este módulo proporciona funciones de utilidad esenciales para la aplicación,
             incluyendo la gestión de rutas de assets, carga de imágenes y iconos,
             y creación de bitmaps de placeholder.
Autor: AutoDoc AI
Fecha: 07/06/2025
Versión: 0.0.1
Licencia: MIT License
"""

import wx
import os
import sys
from typing import Optional

def get_base_path() -> str:
    """
    Determina la ruta base de la aplicación.

    Si la aplicación se ejecuta como un ejecutable empaquetado por PyInstaller,
    la ruta base es el directorio temporal `sys._MEIPASS`. De lo contrario,
    es el directorio del script principal que se está ejecutando.

    Returns:
        str: La ruta base absoluta de la aplicación.
    """
    base_path_str: str
    # Comprueba si la aplicación está empaquetada por PyInstaller
    if hasattr(sys, '_MEIPASS'):
        # Si está empaquetada, usa el directorio temporal de PyInstaller
        # pyright: ignore[reportGeneralTypeIssues, reportUnknownMemberType]
        base_path_str = sys._MEIPASS
        return base_path_str
    else:
        # Si se ejecuta como script normal, usa el directorio del script principal
        base_path_from_argv: str
        # Obtiene la ruta absoluta del script y luego su directorio
        base_path_from_argv = os.path.dirname(os.path.abspath(sys.argv[0]))
        return base_path_from_argv

def get_asset_path(filename: str) -> Optional[str]:
    """
    Construye la ruta completa a un archivo de asset.

    Busca el archivo especificado primero dentro de una subcarpeta 'assets'
    relativa a la ruta base de la aplicación. Si no se encuentra allí,
    busca directamente en la ruta base.

    Args:
        filename (str): El nombre del archivo del asset (ej. "app_icon.ico").

    Returns:
        Optional[str]: La ruta absoluta al archivo del asset si se encuentra.
                       Retorna None si el archivo no existe en ninguna de las ubicaciones buscadas
                       o si el nombre del archivo está vacío.
    """
    # Verifica si el nombre del archivo es válido
    if not filename:
        return None

    # Obtiene la ruta base de la aplicación
    base_path: str
    base_path = get_base_path()

    # Construye la ruta buscando en la subcarpeta 'assets'
    path_in_assets: str
    path_in_assets = os.path.join(base_path, "assets", filename)
    # Verifica si el archivo existe en la subcarpeta 'assets'
    if os.path.exists(path_in_assets) and os.path.isfile(path_in_assets):
        return path_in_assets

    # Si no se encontró en 'assets', construye la ruta buscando directamente en la base
    path_in_root: str
    path_in_root = os.path.join(base_path, filename)
    # Verifica si el archivo existe en la ruta base
    if os.path.exists(path_in_root) and os.path.isfile(path_in_root):
        return path_in_root

    # Si el archivo no se encontró en ninguna de las ubicaciones
    # print(f"Advertencia (Util.get_asset_path): Asset '{filename}' no encontrado.") # Comentado para evitar salida en producción
    return None

def load_image(filepath: str) -> Optional[wx.Bitmap]:
    """
    Carga una imagen desde una ruta de archivo y la convierte en un objeto wx.Bitmap.

    Intenta cargar la imagen desde la ruta especificada. Si la ruta no existe,
    no es un archivo, o la carga falla por cualquier motivo (ej. formato no soportado),
    la función retorna None.

    Args:
        filepath (str): La ruta absoluta o relativa al archivo de la imagen.

    Returns:
        Optional[wx.Bitmap]: El objeto wx.Bitmap creado a partir de la imagen cargada.
                             Retorna None si la carga falla o la ruta no es válida.
    """
    # Verifica si la ruta del archivo es válida
    if not filepath:
        return None

    # Verifica si la ruta existe y es un archivo
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        return None

    try:
        # Intenta crear un wx.Bitmap desde el archivo. wx.BITMAP_TYPE_ANY intenta detectar el tipo.
        image_bitmap: wx.Bitmap
        image_bitmap = wx.Bitmap(filepath, wx.BITMAP_TYPE_ANY)

        # Verifica si el bitmap se creó correctamente
        if not image_bitmap.IsOk():
            return None
        return image_bitmap
    except Exception:
        # Captura cualquier excepción durante la carga (ej. archivo corrupto)
        return None

def load_icon_bitmap(icon_name: str, size: wx.Size = wx.Size(16, 16)) -> wx.Bitmap:
    """
    Carga un icono como un objeto wx.Bitmap del tamaño especificado.

    Primero intenta cargar el icono desde un archivo utilizando `get_asset_path`
    con el nombre proporcionado. Si la carga desde archivo falla o el archivo
    no se encuentra, recurre a `wx.ArtProvider` para obtener un icono de fallback
    basado en el nombre del archivo (mapeando nombres comunes a IDs de ArtProvider).

    Args:
        icon_name (str): El nombre del archivo del icono (ej. "edit.png").
        size (wx.Size, opcional): El tamaño deseado para el bitmap del icono.
                                  Por defecto es wx.Size(16, 16).

    Returns:
        wx.Bitmap: El bitmap del icono cargado y redimensionado al tamaño especificado.
                   Si la carga desde archivo falla, retorna un bitmap de fallback
                   obtenido de wx.ArtProvider.
    """
    # Intenta obtener la ruta del archivo del icono
    icon_path: Optional[str]
    icon_path = get_asset_path(icon_name)

    loaded_bitmap: Optional[wx.Bitmap] = None
    # Si se encontró la ruta, intenta cargar la imagen
    if icon_path:
        loaded_bitmap = load_image(icon_path)

    # Si la carga desde archivo fue exitosa y el bitmap es válido
    if loaded_bitmap and loaded_bitmap.IsOk():
        # Convierte el bitmap a imagen para poder redimensionarla
        image: wx.Image
        image = loaded_bitmap.ConvertToImage()
        # Redimensiona la imagen al tamaño deseado con alta calidad
        image.Rescale(size.GetWidth(), size.GetHeight(), wx.IMAGE_QUALITY_HIGH)
        # Convierte la imagen redimensionada de vuelta a bitmap
        bitmap_result: wx.Bitmap
        bitmap_result = wx.Bitmap(image)
        return bitmap_result
    else:
        # Si la carga desde archivo falló, usa wx.ArtProvider como fallback
        art_id: str
        # Mapea nombres de archivo comunes a IDs de wx.ArtProvider
        if icon_name == "edit.png" or icon_name == "edit2.png":
            art_id = wx.ART_EDIT
        elif icon_name == "new_book.png":
            art_id = wx.ART_NEW
        elif icon_name == "save.png":
            art_id = wx.ART_FILE_SAVE
        elif icon_name == "library.png":
            art_id = wx.ART_GO_HOME
        elif icon_name == "undo.png":
            art_id = wx.ART_UNDO
        elif icon_name == "redo.png":
            art_id = wx.ART_REDO
        elif icon_name in ["bold.png", "italic.png", "underline.png"]:
            art_id = wx.ART_QUESTION # Usa un icono genérico de pregunta para formatos de texto
        else:
            art_id = wx.ART_MISSING_IMAGE # Icono por defecto para imágenes no encontradas

        # Obtiene el bitmap del ArtProvider con el ID y tamaño especificados
        art_bitmap: wx.Bitmap
        art_bitmap = wx.ArtProvider.GetBitmap(art_id, wx.ART_TOOLBAR, size)
        return art_bitmap

def create_placeholder_bitmap(width: int, height: int, text: str = "Sin Imagen") -> wx.Bitmap:
    """
    Crea un objeto wx.Bitmap de placeholder con un color de fondo, un borde y texto opcional.

    Este bitmap se puede usar para representar visualmente un área donde debería haber
    una imagen pero no se pudo cargar o no está disponible.

    Args:
        width (int): El ancho deseado para el bitmap en píxeles.
        height (int): El alto deseado para el bitmap en píxeles.
        text (str, opcional): El texto a dibujar en el centro del placeholder.
                              Por defecto es "Sin Imagen".

    Returns:
        wx.Bitmap: El bitmap de placeholder generado.
    """
    # Crea un nuevo bitmap vacío con las dimensiones especificadas
    bitmap: wx.Bitmap
    bitmap = wx.Bitmap(width, height)
    # Crea un contexto de dispositivo de memoria para dibujar en el bitmap
    dc: wx.MemoryDC
    dc = wx.MemoryDC()
    # Selecciona el bitmap en el contexto del dispositivo
    dc.SelectObject(bitmap)

    # Configura el pincel para el fondo (gris claro)
    background_brush: wx.Brush
    background_brush = wx.Brush(wx.Colour(220, 220, 220))
    # Establece el fondo del contexto y lo limpia (lo llena con el color de fondo)
    dc.SetBackground(background_brush)
    dc.Clear()

    # Configura la pluma para el borde (gris medio)
    border_pen: wx.Pen
    border_pen = wx.Pen(wx.Colour(150, 150, 150), 1)
    # Establece la pluma y dibuja un rectángulo que cubre todo el bitmap para crear el borde
    dc.SetPen(border_pen)
    dc.DrawRectangle(0, 0, width, height)

    # Si se proporcionó texto, lo dibuja en el centro
    if text:
        # Configura el color del texto (gris oscuro)
        text_color: wx.Colour
        text_color = wx.Colour(100, 100, 100)
        dc.SetTextForeground(text_color)
        # Obtiene la fuente por defecto del sistema
        font: wx.Font
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        # Ajusta el tamaño de la fuente si el bitmap es muy pequeño
        if width < 100 or height < 50:
            current_point_size: int
            current_point_size = font.GetPointSize()
            new_point_size: int
            new_point_size = max(6, current_point_size - 2) # Reduce el tamaño, mínimo 6
            font.SetPointSize(new_point_size)
        # Establece la fuente en el contexto del dispositivo
        dc.SetFont(font)

        # Obtiene las dimensiones del texto con la fuente actual
        text_width: int
        text_height: int
        text_width, text_height = dc.GetTextExtent(text)

        # Calcula la posición para centrar el texto
        x_pos: int
        x_pos = (width - text_width) // 2
        y_pos: int
        y_pos = (height - text_height) // 2
        # Dibuja el texto en la posición calculada
        dc.DrawText(text, x_pos, y_pos)

    # Deselecciona el bitmap del contexto del dispositivo para liberar recursos
    dc.SelectObject(wx.NullBitmap)
    return bitmap