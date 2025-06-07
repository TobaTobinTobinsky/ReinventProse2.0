# -*- coding: utf-8 -*-
"""
Archivo: ChapterContentView.py
Descripción: Panel para visualizar y editar el contenido enriquecido de un capítulo en la aplicación ReinventProse 2.0.
Autor: AutoDoc AI
Fecha: 07/06/2025
Versión: 0.0.1
Licencia: MIT License
"""
import wx
import wx.adv
from typing import Optional, List, Tuple as TypingTuple, Dict, Any, Callable
import os
import sys
import re
import html

import Util

# IDs para los controles de la barra de herramientas de formato
ID_FORMAT_BOLD: wx.WindowIDRef = wx.NewIdRef()
ID_FORMAT_ITALIC: wx.WindowIDRef = wx.NewIdRef()
ID_FORMAT_UNDERLINE: wx.WindowIDRef = wx.NewIdRef()
ID_FONT_SIZE_CHOICE: wx.WindowIDRef = wx.NewIdRef()
ID_FONT_COLOUR_PICKER: wx.WindowIDRef = wx.NewIdRef()
ID_FONT_FACENAME_COMBO: wx.WindowIDRef = wx.NewIdRef()
ID_TEXT_STYLE_CHOICE: wx.WindowIDRef = wx.NewIdRef()


class ChapterContentView(wx.Panel):
    """
    Panel que muestra y permite editar el contenido de un capítulo con formato
    de texto enriquecido.

    Este panel incluye una barra de herramientas para aplicar formato (negrita,
    cursiva, subrayado, fuente, tamaño, color) y estilos predefinidos.
    Inicia en modo lectura y requiere que el usuario active explícitamente
    el modo edición.
    """
    # --- Declaraciones de Atributos de Clase ---
    font_sizes: List[str]
    text_styles_map: Dict[str, Dict[str, Any]]
    default_font: wx.Font
    edit_tool_icon: Optional[wx.Bitmap]

    # --- Declaraciones de Atributos de Instancia (Type Hinting) ---
    app_handler: Any
    chapter_id: Optional[int]
    _is_dirty_view: bool
    _loading_data: bool
    _is_in_edit_mode: bool

    content_label: Optional[wx.StaticText]
    content_ctrl: Optional[wx.TextCtrl]
    edit_mode_toolbar: Optional[wx.ToolBar]
    edit_tool: Optional[wx.ToolBarToolBase]
    format_toolbar: Optional[wx.ToolBar]
    font_facename_combo: Optional[wx.ComboBox]
    font_size_choice: Optional[wx.Choice]
    bold_tool: Optional[wx.ToolBarToolBase]
    italic_tool: Optional[wx.ToolBarToolBase]
    underline_tool: Optional[wx.ToolBarToolBase]
    font_colour_picker: Optional[wx.ColourPickerCtrl]
    text_style_choice: Optional[wx.Choice]


    def __init__(self, parent: wx.Window, app_handler: Any):
        """
        Inicializa una nueva instancia de ChapterContentView.

        Configura el panel, crea los controles de UI, define los tamaños de
        fuente y estilos de texto predefinidos, y establece la fuente por defecto.

        Args:
            parent (wx.Window): La ventana padre para este panel.
            app_handler (Any): Una referencia al manejador principal de la aplicación
                               (AppHandler) para interactuar con la lógica de negocio.
        """
        super().__init__(parent)
        self.app_handler = app_handler
        self.chapter_id = None
        self._is_dirty_view = False # Indica si el contenido actual tiene cambios sin guardar
        self._loading_data = False # Bandera para evitar marcar como sucio durante la carga inicial
        self._is_in_edit_mode = False # Indica si el panel está en modo edición

        # Define los tamaños de fuente disponibles en la barra de herramientas
        font_size_values: List[int]
        font_size_values = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 28, 32, 36, 48, 72]
        self.font_sizes = [str(s) for s in font_size_values]

        # Define los estilos de texto predefinidos y sus propiedades
        self.text_styles_map = {
            "Normal": {"size_delta": 0, "bold": False, "point_size": None},
            "Título 1": {"size_delta": None, "bold": True, "point_size": 18},
            "Título 2": {"size_delta": None, "bold": True, "point_size": 16},
            "Título 3": {"size_delta": None, "bold": True, "point_size": 14},
        }

        # Obtiene o define la fuente por defecto del sistema
        sys_default_font: wx.Font
        sys_default_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        if not sys_default_font.IsOk():
            # Si la fuente del sistema no es válida, usa una fuente genérica
            self.default_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        else:
            self.default_font = sys_default_font
            # Ajusta el tamaño de la fuente por defecto si está fuera de un rango razonable
            current_ps: int
            current_ps = self.default_font.GetPointSize()
            if not (9 <= current_ps <= 14):
                self.default_font.SetPointSize(11)

        self.edit_tool_icon = None

        # Crea y organiza los controles de la UI
        self._create_controls()
        self._layout_controls()
        # Carga el contenido inicial (ninguno al inicio)
        self.load_content(None)

    def get_system_font_facenames(self) -> List[str]:
        """
        Obtiene una lista de nombres de familias de fuentes disponibles en el sistema.

        Utiliza `wx.FontEnumerator` para listar las fuentes. Si no se encuentran
        fuentes, devuelve una lista predeterminada.

        Returns:
            List[str]: Una lista ordenada y única de nombres de fuentes disponibles.
        """
        font_enum: wx.FontEnumerator
        font_enum = wx.FontEnumerator()

        # Enumera los nombres de fuentes disponibles
        font_enum.EnumerateFacenames(encoding=wx.FONTENCODING_SYSTEM, fixedWidthOnly=False)

        facenames: Optional[List[str]]
        facenames = font_enum.GetFacenames()

        if not facenames:
            # Si no se encontraron fuentes, proporciona una lista básica
            default_list: List[str]
            default_list = ["Arial", "Courier New", "Times New Roman", "Verdana", "Tahoma", "Helvetica", "Sans"]
            unique_sorted_default: List[str]
            unique_sorted_default = sorted(list(set(default_list)))
            return unique_sorted_default

        # Filtra nombres de fuentes que empiezan con '@' (a menudo fuentes especiales o verticales)
        cleaned_facenames: List[str]
        cleaned_facenames = [fn for fn in facenames if not fn.startswith('@')]

        # Elimina duplicados y ordena la lista
        unique_sorted_cleaned: List[str]
        unique_sorted_cleaned = sorted(list(set(cleaned_facenames)))
        return unique_sorted_cleaned

    def _load_tool_icon(self, icon_name: str, size: wx.Size = wx.Size(16,16)) -> wx.Bitmap:
        """
        Carga un icono para la barra de herramientas utilizando la utilidad de carga.

        Args:
            icon_name (str): El nombre del archivo del icono (ej. "edit.png").
            size (wx.Size): El tamaño deseado para el icono.

        Returns:
            wx.Bitmap: El bitmap del icono cargado.
        """
        loaded_bitmap: wx.Bitmap
        loaded_bitmap = Util.load_icon_bitmap(icon_name, size)
        return loaded_bitmap

    def _text_attr_to_html_font_tag(self, attr: wx.TextAttr) -> TypingTuple[str, str]:
        """
        Convierte los atributos de fuente y color de un `wx.TextAttr` a etiquetas
        HTML `<font>`.

        Nota: Este método solo maneja atributos de fuente y color. Otros estilos
        (negrita, cursiva, subrayado) se manejan con sus propias etiquetas HTML
        (<b>, <i>, <u>).

        Args:
            attr (wx.TextAttr): El objeto de atributos de texto de wxWidgets.

        Returns:
            TypingTuple[str, str]: Una tupla que contiene la etiqueta de apertura
                                   `<font ...>` y la etiqueta de cierre `</font>`.
                                   Devuelve `("", "")` si no hay atributos de
                                   fuente o color que requieran una etiqueta `<font>`.
        """
        open_tag_parts: List[str]; open_tag_parts = ["<font"]
        font: wx.Font = attr.GetFont(); color: wx.Colour = attr.GetTextColour()
        has_font_attrs: bool = False
        # Verifica y añade el atributo 'face' si la fuente es diferente a la por defecto
        if font.IsOk():
            face_name: str = font.GetFaceName(); point_size: int = font.GetPointSize()
            default_sys_font_face: str = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT).GetFaceName()
            is_custom_face: bool = face_name and face_name.lower() != default_sys_font_face.lower() and face_name.lower() != self.default_font.GetFaceName().lower()
            if is_custom_face: open_tag_parts.append(f' face="{face_name}"'); has_font_attrs = True
            # Añade el tamaño como atributo 'data-point-size' para parseo posterior
            is_custom_size: bool = point_size != self.default_font.GetPointSize()
            if is_custom_size: open_tag_parts.append(f' data-point-size="{point_size}"'); has_font_attrs = True
        # Verifica y añade el atributo 'color' si el color es diferente al negro
        is_custom_color: bool = color.IsOk() and color != wx.BLACK
        if is_custom_color: open_tag_parts.append(f' color="{color.GetAsString(wx.C2S_HTML_SYNTAX)}"'); has_font_attrs = True
        open_tag: str
        # Construye la etiqueta de apertura si hay atributos relevantes
        if has_font_attrs: open_tag = "".join(open_tag_parts) + ">"
        else: open_tag = ""
        close_tag: str
        # Define la etiqueta de cierre si se creó una de apertura
        if open_tag: close_tag = "</font>"
        else: close_tag = ""
        return open_tag, close_tag

    def _serialize_content_to_html(self) -> str:
        """
        Serializa el contenido del `wx.TextCtrl` (incluyendo estilos) a una cadena
        HTML simple.

        Itera sobre cada carácter del TextCtrl, detectando cambios de estilo
        para crear segmentos de texto con el mismo formato. Aplica etiquetas
        HTML (<b>, <i>, <u>, <font>) según los atributos de cada segmento.

        Returns:
            str: El contenido del TextCtrl formateado como una cadena HTML.
        """
        html_output: List[str] = []
        if self.content_ctrl is None: return ""
        text_length: int = self.content_ctrl.GetLastPosition()
        if text_length == 0: return ""

        # Define el estilo inicial por defecto para el primer segmento
        initial_default_style: wx.TextAttr = wx.TextAttr()
        initial_default_style.SetFont(self.default_font); initial_default_style.SetTextColour(wx.BLACK)
        last_attr_obj_for_segment: wx.TextAttr = wx.TextAttr(initial_default_style)
        current_segment: str = ""

        i: int
        # Itera sobre cada posición en el TextCtrl
        for i in range(text_length):
            pos_attr: wx.TextAttr = wx.TextAttr()
            # Obtiene el estilo en la posición actual
            self.content_ctrl.GetStyle(i, pos_attr)
            char_text: str = self.content_ctrl.GetRange(i, i + 1)

            # Maneja saltos de línea de Windows (\r\n) para evitar duplicar \n
            if char_text == '\r':
                if i + 1 < text_length:
                    next_char: str = self.content_ctrl.GetRange(i + 1, i + 2)
                    if next_char == '\n': continue # Ignora el \r si el siguiente es \n

            # Determina si el estilo ha cambiado, indicando un nuevo segmento
            is_new_segment: bool = False
            if not current_segment: is_new_segment = True # Siempre es un nuevo segmento si el actual está vacío
            else:
                # Compara los atributos de fuente y color con los del segmento anterior
                font_changed: bool = not pos_attr.GetFont().IsSameAs(last_attr_obj_for_segment.GetFont())
                color_changed: bool = pos_attr.GetTextColour() != last_attr_obj_for_segment.GetTextColour()
                if font_changed or color_changed: is_new_segment = True

            # Si es un nuevo segmento y el segmento actual no está vacío, serializa el segmento anterior
            if is_new_segment and current_segment:
                font_open: str; font_close: str
                # Obtiene las etiquetas <font> para el estilo del segmento anterior
                font_open, font_close = self._text_attr_to_html_font_tag(last_attr_obj_for_segment)
                styled_segment: str = current_segment
                l_font: wx.Font = last_attr_obj_for_segment.GetFont()
                # Aplica etiquetas de estilo (u, i, b)
                if l_font.GetUnderlined(): styled_segment = f"<u>{styled_segment}</u>"
                if l_font.GetStyle() == wx.FONTSTYLE_ITALIC: styled_segment = f"<i>{styled_segment}</i>"
                if l_font.GetWeight() == wx.FONTWEIGHT_BOLD: styled_segment = f"<b>{styled_segment}</b>"
                # Envuelve con la etiqueta <font> si es necesario
                if font_open: styled_segment = f"{font_open}{styled_segment}{font_close}"
                html_output.append(styled_segment)
                current_segment = "" # Reinicia el segmento actual

            # Si el carácter es un salto de línea, serializa el segmento actual (si existe) y añade <br />
            if char_text == '\n':
                if current_segment:
                    font_open_nl: str; font_close_nl: str
                    font_open_nl, font_close_nl = self._text_attr_to_html_font_tag(last_attr_obj_for_segment)
                    styled_segment_nl: str = current_segment
                    l_font_nl: wx.Font = last_attr_obj_for_segment.GetFont()
                    if l_font_nl.GetUnderlined(): styled_segment_nl = f"<u>{styled_segment_nl}</u>"
                    if l_font_nl.GetStyle() == wx.FONTSTYLE_ITALIC: styled_segment_nl = f"<i>{styled_segment_nl}</i>"
                    if l_font_nl.GetWeight() == wx.FONTWEIGHT_BOLD: styled_segment_nl = f"<b>{styled_segment_nl}</b>"
                    if font_open_nl: styled_segment_nl = f"{font_open_nl}{styled_segment_nl}{font_close_nl}"
                    html_output.append(styled_segment_nl)
                    current_segment = ""
                html_output.append("<br />") # Representa el salto de línea como <br />
            else:
                # Añade el carácter al segmento actual
                current_segment += char_text

            # Actualiza el atributo del último segmento para la siguiente iteración
            last_attr_obj_for_segment = wx.TextAttr(pos_attr)

        # Serializa cualquier segmento restante al final del texto
        if current_segment and last_attr_obj_for_segment:
            font_open_end: str; font_close_end: str
            font_open_end, font_close_end = self._text_attr_to_html_font_tag(last_attr_obj_for_segment)
            styled_segment_end: str = current_segment
            l_font_end: wx.Font = last_attr_obj_for_segment.GetFont()
            if l_font_end.GetUnderlined(): styled_segment_end = f"<u>{styled_segment_end}</u>"
            if l_font_end.GetStyle() == wx.FONTSTYLE_ITALIC: styled_segment_end = f"<i>{styled_segment_end}</i>"
            if l_font_end.GetWeight() == wx.FONTWEIGHT_BOLD: styled_segment_end = f"<b>{styled_segment_end}</b>"
            if font_open_end: styled_segment_end = f"{font_open_end}{styled_segment_end}{font_close_end}"
            html_output.append(styled_segment_end)

        # Une todas las partes serializadas
        result: str = "".join(html_output)
        return result

    def _parse_html_to_text_attrs(self, html_content: str):
        """
        Parsea una cadena HTML simple y aplica los estilos correspondientes
        al `wx.TextCtrl`.

        Convierte etiquetas HTML (<b>, <i>, <u>, <font>, <br />) en atributos
        de texto de wxWidgets y escribe el texto en el control.

        Args:
            html_content (str): La cadena HTML a parsear y cargar en el TextCtrl.
        """
        if self.content_ctrl is None: return
        self.content_ctrl.Clear() # Limpia el contenido actual

        # Establece el estilo por defecto inicial del TextCtrl
        default_style_for_parse: wx.TextAttr = wx.TextAttr()
        default_style_for_parse.SetFont(self.default_font); default_style_for_parse.SetTextColour(wx.BLACK)
        self.content_ctrl.SetDefaultStyle(wx.TextAttr(default_style_for_parse))

        # Reemplaza las etiquetas <br /> por saltos de línea de texto plano
        processed_content: str = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)

        # Divide el contenido en partes de texto y etiquetas HTML
        parts: List[str] = re.split(r'(<[^>]+>)', processed_content)

        # Pila de atributos para manejar etiquetas anidadas
        attr_stack: List[wx.TextAttr] = [wx.TextAttr(default_style_for_parse)]

        # Procesa cada parte (texto o etiqueta)
        for part in parts:
            if not part: continue # Ignora partes vacías

            if part.startswith('<') and part.endswith('>'):
                # Es una etiqueta HTML
                tag_content: str = part[1:-1].strip()
                is_closing_tag: bool = tag_content.startswith('/')
                # Obtiene el atributo actual de la cima de la pila
                current_attr_from_stack: wx.TextAttr = wx.TextAttr(attr_stack[-1])

                if is_closing_tag:
                    # Es una etiqueta de cierre
                    tag_name: str = tag_content[1:].lower()
                    # Si es una etiqueta de estilo o fuente, saca el atributo de la pila
                    if tag_name in ["font", "b", "i", "u"]:
                        if len(attr_stack) > 1: attr_stack.pop()
                    # Actualiza el estilo por defecto del TextCtrl al de la cima de la pila
                    self.content_ctrl.SetDefaultStyle(wx.TextAttr(attr_stack[-1]))
                else:
                    # Es una etiqueta de apertura
                    # Crea un nuevo atributo basado en el actual para aplicar las modificaciones de la etiqueta
                    new_applied_attr: wx.TextAttr = wx.TextAttr(current_attr_from_stack)
                    match_tag: Optional[re.Match[str]] = re.match(r'([\w-]+)(.*)', tag_content)
                    if not match_tag: continue # Ignora etiquetas mal formadas

                    tag_name_open: str = match_tag.group(1).lower()
                    attrs_str: str = match_tag.group(2)

                    # Prepara la fuente base para modificar
                    base_font_for_modification: wx.Font
                    if new_applied_attr.HasFont(): base_font_for_modification = new_applied_attr.GetFont()
                    else: base_font_for_modification = self.default_font
                    font_to_modify: wx.Font = wx.Font(base_font_for_modification)
                    font_modified: bool = False

                    # Aplica atributos según el nombre de la etiqueta
                    if tag_name_open == "font":
                        # Parsea atributos de la etiqueta <font>
                        face_match: Optional[re.Match[str]] = re.search(r'face="([^"]*)"',attrs_str,re.IGNORECASE)
                        size_match: Optional[re.Match[str]] = re.search(r'data-point-size="(\d+)"',attrs_str,re.IGNORECASE)
                        color_match: Optional[re.Match[str]] = re.search(r'color="(#[0-9a-fA-F]{6})"',attrs_str,re.IGNORECASE)
                        if face_match and face_match.group(1): font_to_modify.SetFaceName(face_match.group(1)); font_modified=True
                        if size_match: font_to_modify.SetPointSize(int(size_match.group(1))); font_modified=True
                        if color_match: new_applied_attr.SetTextColour(color_match.group(1))
                    elif tag_name_open == "b":
                        font_to_modify.SetWeight(wx.FONTWEIGHT_BOLD); font_modified=True
                    elif tag_name_open == "i":
                        font_to_modify.SetStyle(wx.FONTSTYLE_ITALIC); font_modified=True
                    elif tag_name_open == "u":
                        font_to_modify.SetUnderlined(True); font_modified=True
                        # Asegura que el flag de subrayado esté activo en el atributo
                        current_flags_u: int = new_applied_attr.GetFlags(); new_flags_u: int = current_flags_u|wx.TEXT_ATTR_FONT_UNDERLINE
                        new_applied_attr.SetFlags(new_flags_u)

                    # Si la fuente fue modificada, actualiza el atributo
                    if font_modified: new_applied_attr.SetFont(font_to_modify)

                    # Añade el nuevo atributo a la pila y actualiza el estilo por defecto del TextCtrl
                    attr_stack.append(new_applied_attr)
                    self.content_ctrl.SetDefaultStyle(wx.TextAttr(new_applied_attr))
            else:
                # Es texto plano
                # Desescapa entidades HTML como &amp; a &
                text_to_write: str = html.unescape(part)
                # Escribe el texto en el TextCtrl con el estilo actual de la pila
                self.content_ctrl.WriteText(text_to_write)

        # Restablece el estilo por defecto del TextCtrl a la fuente base al finalizar
        final_default_style_after_parse: wx.TextAttr = wx.TextAttr()
        final_default_style_after_parse.SetFont(self.default_font); final_default_style_after_parse.SetTextColour(wx.BLACK)
        self.content_ctrl.SetDefaultStyle(final_default_style_after_parse)
        self.content_ctrl.SetInsertionPoint(0) # Mueve el cursor al inicio

    def _create_controls(self):
        """
        Crea todos los controles de UI que componen la vista del contenido
        del capítulo.

        Incluye la etiqueta, el `wx.TextCtrl` para el contenido, y las barras
        de herramientas de modo edición y formato. También configura las opciones
        iniciales de los controles de formato y enlaza los eventos.
        """
        # Etiqueta para indicar el contenido
        self.content_label = wx.StaticText(self, label="Contenido del Capítulo:")

        # Control de texto enriquecido para el contenido
        self.content_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_PROCESS_ENTER | wx.TE_AUTO_URL)
        self.content_ctrl.SetEditable(False) # Inicia en modo lectura
        # Establece el color de fondo por defecto (color de ventana)
        bg_color_window: wx.Colour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        self.content_ctrl.SetBackgroundColour(bg_color_window)

        # Barra de herramientas para alternar el modo edición
        self.edit_mode_toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_TEXT)
        icon_size_toolbar: wx.Size = wx.Size(24,24)
        # Carga el icono para el botón de edición
        self.edit_tool_icon = self._load_tool_icon("edit.png", icon_size_toolbar)
        # Añade el botón de modo edición a la barra
        self.edit_tool = self.edit_mode_toolbar.AddTool(wx.ID_EDIT, "Modo Edición", self.edit_tool_icon, shortHelp="Activar/Desactivar Modo Edición (Ctrl+E)")
        self.edit_mode_toolbar.Realize() # Finaliza la construcción de la barra

        # Barra de herramientas para formato de texto
        self.format_toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_TEXT)

        # Control ComboBox para seleccionar la familia de fuente
        font_names: List[str] = self.get_system_font_facenames()
        default_facename: str = self.default_font.GetFaceName()
        # Asegura que la fuente por defecto esté en la lista si es posible
        if default_facename not in font_names and font_names:
             is_really_not_in_list: bool = not default_facename or not any(f.lower() == default_facename.lower() for f in font_names)
             if is_really_not_in_list : default_facename = font_names[0]
        combo_size: wx.Size = wx.Size(150,-1)
        self.font_facename_combo = wx.ComboBox(self.format_toolbar, ID_FONT_FACENAME_COMBO, value=default_facename, choices=font_names, style=wx.CB_READONLY | wx.CB_SORT, size=combo_size)
        self.font_facename_combo.SetToolTip("Familia de Fuente")
        self.format_toolbar.AddControl(self.font_facename_combo)

        # Control Choice para seleccionar el tamaño de fuente
        choice_size: wx.Size = wx.Size(60,-1)
        self.font_size_choice = wx.Choice(self.format_toolbar, ID_FONT_SIZE_CHOICE, choices=self.font_sizes, size=choice_size)
        # Intenta seleccionar el tamaño de fuente por defecto
        try: self.font_size_choice.SetStringSelection(str(self.default_font.GetPointSize()))
        except ValueError:
             # Si el tamaño por defecto no está en la lista, intenta "11" o el primero
             if "11" in self.font_sizes: self.font_size_choice.SetStringSelection("11")
             elif self.font_sizes: self.font_size_choice.SetSelection(0)
        self.font_size_choice.SetToolTip("Tamaño de Fuente")
        self.format_toolbar.AddControl(self.font_size_choice)

        self.format_toolbar.AddSeparator() # Separador visual

        # Botones de formato (Negrita, Cursiva, Subrayado)
        bold_icon: wx.Bitmap = self._load_tool_icon("bold.png")
        italic_icon: wx.Bitmap = self._load_tool_icon("italic.png")
        underline_icon: wx.Bitmap = self._load_tool_icon("underline.png")
        self.bold_tool = self.format_toolbar.AddCheckTool(ID_FORMAT_BOLD, "", bold_icon, shortHelp="Negrita (Ctrl+B)")
        self.italic_tool = self.format_toolbar.AddCheckTool(ID_FORMAT_ITALIC, "", italic_icon, shortHelp="Cursiva (Ctrl+I)")
        self.underline_tool = self.format_toolbar.AddCheckTool(ID_FORMAT_UNDERLINE, "", underline_icon, shortHelp="Subrayado (Ctrl+U)")

        self.format_toolbar.AddSeparator() # Separador visual

        # Control ColourPicker para seleccionar el color del texto
        picker_size: wx.Size = wx.Size(32,24)
        self.font_colour_picker = wx.ColourPickerCtrl(self.format_toolbar, ID_FONT_COLOUR_PICKER, wx.BLACK, size=picker_size)
        self.font_colour_picker.SetToolTip("Color del Texto")
        self.format_toolbar.AddControl(self.font_colour_picker)

        self.format_toolbar.AddSeparator() # Separador visual

        # Control Choice para seleccionar estilos de texto predefinidos
        self.text_style_choice = wx.Choice(self.format_toolbar, ID_TEXT_STYLE_CHOICE, choices=list(self.text_styles_map.keys()))
        self.text_style_choice.SetSelection(0) # Selecciona el primer estilo ("Normal") por defecto
        self.text_style_choice.SetToolTip("Estilo de Texto")
        self.format_toolbar.AddControl(self.text_style_choice)

        self.format_toolbar.Realize() # Finaliza la construcción de la barra de formato

        # Enlace de eventos
        if self.content_ctrl:
            # Eventos de cambio de texto para marcar la vista como sucia
            self.content_ctrl.Bind(wx.EVT_TEXT, self.on_text_changed)
            self.content_ctrl.Bind(wx.EVT_TEXT_PASTE, self.on_text_changed)
            # Eventos de teclado y ratón para actualizar la barra de formato
            self.content_ctrl.Bind(wx.EVT_KEY_UP, self.on_content_key_up_or_mouse_up)
            self.content_ctrl.Bind(wx.EVT_LEFT_UP, self.on_content_key_up_or_mouse_up)

        # Enlace del evento del botón de modo edición
        self.Bind(wx.EVT_TOOL, self.on_edit_button_click, id=wx.ID_EDIT)

        # Enlace de eventos de los controles de formato
        if self.font_facename_combo: self.font_facename_combo.Bind(wx.EVT_COMBOBOX, self.on_font_facename_selected, id=ID_FONT_FACENAME_COMBO)
        if self.font_size_choice: self.font_size_choice.Bind(wx.EVT_CHOICE, self.on_font_size_selected, id=ID_FONT_SIZE_CHOICE)
        self.Bind(wx.EVT_TOOL, self.on_format_bold, id=ID_FORMAT_BOLD)
        self.Bind(wx.EVT_TOOL, self.on_format_italic, id=ID_FORMAT_ITALIC)
        self.Bind(wx.EVT_TOOL, self.on_format_underline, id=ID_FORMAT_UNDERLINE)
        if self.font_colour_picker: self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.on_font_colour_picked, id=ID_FONT_COLOUR_PICKER)
        if self.text_style_choice: self.text_style_choice.Bind(wx.EVT_CHOICE, self.on_text_style_selected, id=ID_TEXT_STYLE_CHOICE)

        # Configura atajos de teclado (Ctrl+E, Ctrl+B, Ctrl+I, Ctrl+U)
        accel_list: List[TypingTuple[int,int,int]]
        accel_list = [(wx.ACCEL_CTRL,ord('E'),wx.ID_EDIT),(wx.ACCEL_CTRL,ord('B'),ID_FORMAT_BOLD),(wx.ACCEL_CTRL,ord('I'),ID_FORMAT_ITALIC),(wx.ACCEL_CTRL,ord('U'),ID_FORMAT_UNDERLINE)]
        accel_tbl: wx.AcceleratorTable = wx.AcceleratorTable(accel_list)
        self.SetAcceleratorTable(accel_tbl)

    def _layout_controls(self):
        """
        Organiza los controles de UI dentro del panel utilizando sizers.

        Establece la disposición vertical de la barra de modo edición, la barra
        de formato, la etiqueta y el control de texto principal.
        """
        main_sizer: wx.BoxSizer = wx.BoxSizer(wx.VERTICAL)

        # Añade la barra de modo edición en la parte superior
        if self.edit_mode_toolbar: main_sizer.Add(self.edit_mode_toolbar,0,wx.EXPAND)
        # Añade la barra de formato debajo, con un pequeño espacio superior
        if self.format_toolbar: main_sizer.Add(self.format_toolbar,0,wx.EXPAND|wx.TOP,2)
        # Añade la etiqueta del contenido
        if self.content_label: main_sizer.Add(self.content_label,0,wx.ALL|wx.EXPAND,5)
        # Añade el control de texto, expandiéndose para llenar el espacio restante
        if self.content_ctrl: main_sizer.Add(self.content_ctrl,1,wx.EXPAND|wx.ALL,5)

        # Establece el sizer principal para el panel
        self.SetSizer(main_sizer)
        # Actualiza la UI para reflejar el estado inicial (modo lectura)
        self._update_edit_mode_ui()

    def _set_view_dirty(self, is_dirty: bool = True):
        """
        Establece el estado 'sucio' (con cambios sin guardar) de esta vista.

        Si la vista está en modo edición y el estado 'sucio' cambia a True,
        notifica al manejador de la aplicación.

        Args:
            is_dirty (bool): True para marcar la vista como sucia, False para limpiarla.
        """
        # Solo marca como sucio si está en modo edición
        if self._is_in_edit_mode:
            # Solo actualiza si el estado cambia
            if self._is_dirty_view != is_dirty:
                self._is_dirty_view = is_dirty
                # Notifica al manejador de la aplicación si se vuelve sucio
                if self._is_dirty_view:
                    self.app_handler.set_dirty(True)

    def _update_edit_mode_ui(self):
        """
        Actualiza la interfaz de usuario (controles y barras de herramientas)
        para reflejar el estado actual del modo edición (`_is_in_edit_mode`).

        Cambia la editabilidad del TextCtrl, el color de fondo y la habilitación
        de la barra de formato. También actualiza el texto y el icono del botón
        de modo edición.
        """
        # Verifica que los controles necesarios existan
        if not (self.content_ctrl and self.edit_mode_toolbar and self.format_toolbar and self.edit_tool):
            return

        # Determina si la edición es posible (hay un capítulo cargado y el panel está habilitado)
        can_edit_at_all: bool = self.chapter_id is not None and self.IsEnabled()

        current_label: str; current_short_help: str
        if self._is_in_edit_mode and can_edit_at_all:
            # Configuración para el modo edición activo
            current_label = "Modo Lectura"; current_short_help = "Finalizar Edición y Guardar Cambios (Ctrl+E)"
            self.content_ctrl.SetEditable(True)
            # Cambia el color de fondo para indicar que es editable
            edit_bg_color: wx.Colour = wx.Colour(255,255,220) # Un amarillo claro
            self.content_ctrl.SetBackgroundColour(edit_bg_color)
            self.format_toolbar.Enable(True) # Habilita la barra de formato
            self._update_format_toolbar_state(True) # Actualiza el estado de los controles de formato
        else:
            # Configuración para el modo lectura
            current_label = "Modo Edición"; current_short_help = "Activar Modo Edición (Ctrl+E)"
            self.content_ctrl.SetEditable(False)
            # Restaura el color de fondo por defecto
            window_bg_color: wx.Colour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
            self.content_ctrl.SetBackgroundColour(window_bg_color)
            self.format_toolbar.Enable(False) # Deshabilita la barra de formato

        # Actualiza el botón de la barra de modo edición
        old_tool_pos: int = -1; idx: int
        # Busca la posición actual del botón de edición
        for idx in range(self.edit_mode_toolbar.GetToolsCount()):
            tool_item: Optional[wx.ToolBarToolBase] = self.edit_mode_toolbar.GetToolByPos(idx)
            if tool_item and tool_item.GetId() == wx.ID_EDIT:
                old_tool_pos = idx; break
        # Elimina el botón antiguo si se encontró
        if old_tool_pos != -1: self.edit_mode_toolbar.DeleteToolByPos(old_tool_pos)

        # Determina el icono a usar (el cargado o uno genérico si falla)
        current_icon: wx.Bitmap
        if self.edit_tool_icon and self.edit_tool_icon.IsOk(): current_icon = self.edit_tool_icon
        else:
            tool_bitmap_size: wx.Size = self.edit_mode_toolbar.GetToolBitmapSize()
            current_icon = wx.ArtProvider.GetBitmap(wx.ART_EDIT, wx.ART_TOOLBAR, tool_bitmap_size)

        # Inserta el nuevo botón con el texto y tooltip actualizados
        self.edit_mode_toolbar.InsertTool(0, wx.ID_EDIT, current_label, current_icon, shortHelp=current_short_help)
        # Habilita/deshabilita el botón de edición según si hay un capítulo cargado
        self.edit_mode_toolbar.EnableTool(wx.ID_EDIT, can_edit_at_all)
        self.edit_mode_toolbar.Realize() # Finaliza la actualización de la barra

        self.content_ctrl.Refresh() # Fuerza un repintado del TextCtrl

    def _update_format_toolbar_state(self, editable: bool):
        """
        Actualiza el estado visual de los controles en la barra de herramientas
        de formato (ComboBox, Choice, botones, ColourPicker) para reflejar
        los atributos de texto en la posición actual del cursor o la selección.

        Args:
            editable (bool): Indica si la barra de herramientas debe estar habilitada.
                             Aunque la barra se habilita/deshabilita completamente
                             en `_update_edit_mode_ui`, este parámetro se usa
                             para verificar si tiene sentido actualizar el estado
                             individual de los controles.
        """
        # Verifica que los controles necesarios existan
        if not (self.format_toolbar and self.content_ctrl and self.font_facename_combo and self.font_size_choice and self.font_colour_picker): return

        # Habilita o deshabilita la barra completa
        self.format_toolbar.Enable(editable)

        # Si no es editable, no hay nada más que actualizar
        if not editable: return
        # Si el TextCtrl no es editable, tampoco actualiza el estado de formato
        if not self.content_ctrl.IsEditable(): return

        # Obtiene la selección actual o la posición del cursor
        start_sel: int; end_sel: int
        start_sel, end_sel = self.content_ctrl.GetSelection()

        attr_to_reflect: wx.TextAttr = wx.TextAttr()
        valid_style_fetched: bool = False

        # Intenta obtener el estilo en la posición del cursor o inicio de selección
        if self.content_ctrl.GetLastPosition() > 0:
            pos_to_check: int = start_sel
            # Si el cursor está al final, verifica el estilo del carácter anterior
            if start_sel == self.content_ctrl.GetLastPosition() and start_sel > 0: pos_to_check = start_sel - 1
            try:
                valid_style_fetched = self.content_ctrl.GetStyle(pos_to_check, attr_to_reflect)
            except Exception:
                valid_style_fetched = False

        # Si no se pudo obtener un estilo válido, usa el estilo por defecto del control
        if not valid_style_fetched:
            default_ctrl_style: wx.TextAttr = self.content_ctrl.GetDefaultStyle()
            attr_to_reflect.Merge(default_ctrl_style)

        # Actualiza el ComboBox de familia de fuente
        current_font: wx.Font
        if attr_to_reflect.HasFont(): current_font = attr_to_reflect.GetFont()
        else: current_font = self.default_font # Usa la fuente por defecto si no hay una específica
        current_facename: str = current_font.GetFaceName()
        if self.font_facename_combo.GetValue() != current_facename:
            if current_facename in self.font_facename_combo.GetItems(): self.font_facename_combo.SetValue(current_facename)

        # Actualiza el Choice de tamaño de fuente
        current_point_size_str: str = str(current_font.GetPointSize())
        if self.font_size_choice.GetStringSelection() != current_point_size_str:
            if current_point_size_str in self.font_sizes: self.font_size_choice.SetStringSelection(current_point_size_str)

        # Actualiza el estado de los botones Negrita, Cursiva, Subrayado
        is_bold: bool = (current_font.GetWeight() == wx.FONTWEIGHT_BOLD)
        if self.format_toolbar.GetToolState(ID_FORMAT_BOLD) != is_bold: self.format_toolbar.ToggleTool(ID_FORMAT_BOLD, is_bold)
        is_italic: bool = (current_font.GetStyle() == wx.FONTSTYLE_ITALIC)
        if self.format_toolbar.GetToolState(ID_FORMAT_ITALIC) != is_italic: self.format_toolbar.ToggleTool(ID_FORMAT_ITALIC, is_italic)
        is_underlined: bool = current_font.GetUnderlined()
        if self.format_toolbar.GetToolState(ID_FORMAT_UNDERLINE) != is_underlined: self.format_toolbar.ToggleTool(ID_FORMAT_UNDERLINE, is_underlined)

        # Actualiza el ColourPicker de color de texto
        current_colour: wx.Colour
        if attr_to_reflect.HasTextColour(): current_colour = attr_to_reflect.GetTextColour()
        else: current_colour = self.content_ctrl.GetForegroundColour() # Usa el color de primer plano por defecto
        if self.font_colour_picker.GetColour() != current_colour: self.font_colour_picker.SetColour(current_colour)

        # Nota: El Choice de estilo de texto no se actualiza automáticamente
        # para reflejar el estilo actual, solo se usa para aplicar estilos predefinidos.

    def _reset_format_toolbar_to_default(self, font: Optional[wx.Font] = None):
        """
        Restablece los controles de la barra de herramientas de formato a un
        estado por defecto, basado opcionalmente en una fuente proporcionada.

        Args:
            font (Optional[wx.Font]): La fuente a usar como base para el estado
                                     por defecto. Si es None, usa `self.default_font`.
        """
        # Verifica que los controles necesarios existan
        if not (self.font_facename_combo and self.font_size_choice and self.format_toolbar and self.font_colour_picker and self.text_style_choice): return

        font_to_use: wx.Font = font if font else self.default_font

        # Restablece el ComboBox de familia de fuente
        default_facename: str = font_to_use.GetFaceName()
        if default_facename in self.font_facename_combo.GetItems(): self.font_facename_combo.SetValue(default_facename)
        elif self.font_facename_combo.GetCount() > 0: self.font_facename_combo.SetSelection(0) # Selecciona el primero si el por defecto no está

        # Restablece el Choice de tamaño de fuente
        try: self.font_size_choice.SetStringSelection(str(font_to_use.GetPointSize()))
        except ValueError:
            # Si el tamaño por defecto no está, intenta "11" o el primero
            if str(self.default_font.GetPointSize()) in self.font_sizes: self.font_size_choice.SetStringSelection(str(self.default_font.GetPointSize()))
            elif "11" in self.font_sizes: self.font_size_choice.SetStringSelection("11")
            elif self.font_sizes: self.font_size_choice.SetSelection(0)

        # Restablece el estado de los botones Negrita, Cursiva, Subrayado
        is_bold_default: bool = font_to_use.GetWeight() == wx.FONTWEIGHT_BOLD
        self.format_toolbar.ToggleTool(ID_FORMAT_BOLD, is_bold_default)
        is_italic_default: bool = font_to_use.GetStyle() == wx.FONTSTYLE_ITALIC
        self.format_toolbar.ToggleTool(ID_FORMAT_ITALIC, is_italic_default)
        is_underline_default: bool = font_to_use.GetUnderlined()
        self.format_toolbar.ToggleTool(ID_FORMAT_UNDERLINE, is_underline_default)

        # Restablece el ColourPicker a negro
        self.font_colour_picker.SetColour(wx.BLACK)
        # Restablece el Choice de estilo de texto a "Normal" (el primero)
        self.text_style_choice.SetSelection(0)

    def load_content(self, chapter_id: Optional[int]):
        """
        Carga el contenido de un capítulo específico en la vista.

        Limpia el contenido actual, establece el ID del capítulo, recupera
        el contenido del manejador de la aplicación y lo carga en el TextCtrl.
        Siempre inicia en modo lectura después de la carga.

        Args:
            chapter_id (Optional[int]): El ID del capítulo cuyo contenido se
                                       debe cargar. Si es None, la vista se
                                       limpia y se muestra un mensaje indicando
                                       que se seleccione un capítulo.
        """
        # Verifica que los controles necesarios existan
        if not (self.content_ctrl and self.content_label): return

        self._loading_data=True # Activa la bandera de carga
        self.chapter_id=chapter_id
        self.content_ctrl.Clear() # Limpia el contenido actual del TextCtrl

        # Establece el estilo por defecto del TextCtrl
        default_style: wx.TextAttr = wx.TextAttr()
        default_style.SetFont(self.default_font); default_style.SetTextColour(wx.BLACK)
        self.content_ctrl.SetDefaultStyle(default_style)

        if self.chapter_id is not None:
            # Si hay un ID de capítulo, actualiza la etiqueta y carga el contenido
            self.content_label.SetLabel("Contenido del Capítulo:")
            details: Optional[Dict[str, Any]] = self.app_handler.get_chapter_details(self.chapter_id)
            if details:
                if 'content' in details:
                    content_html: str = details['content'] or ""
                    if content_html:
                        # Parsea y carga el contenido HTML en el TextCtrl
                        self._parse_html_to_text_attrs(content_html)
            elif details is None:
                # Mensaje de advertencia si no se encontraron detalles para el ID
                print(f"Advertencia (CCV): No se encontraron detalles para el capítulo con ID {self.chapter_id}")
        else:
            # Si no hay ID de capítulo, muestra un mensaje para seleccionar uno
            self.content_label.SetLabel("Contenido: (Seleccione un capítulo)")

        self.content_ctrl.SetInsertionPoint(0) # Mueve el cursor al inicio
        self._is_dirty_view=False # Limpia el estado sucio
        self._is_in_edit_mode=False # Asegura que esté en modo lectura
        self._update_edit_mode_ui() # Actualiza la UI al modo lectura
        self._loading_data=False # Desactiva la bandera de carga

    def save_changes(self) -> bool:
        """
        Serializa el contenido actual del `wx.TextCtrl` a HTML y lo guarda
        a través del manejador de la aplicación, si la vista está marcada como sucia.

        Returns:
            bool: True si los cambios se guardaron correctamente o si no había
                  cambios que guardar. False si ocurrió un error durante el guardado.
        """
        # Verifica que el TextCtrl exista
        if not self.content_ctrl : return False

        # Solo guarda si la vista está marcada como sucia
        if not self._is_dirty_view: return True # No hay cambios, considera que el guardado fue "exitoso"

        # No se puede guardar si no hay un capítulo cargado
        if self.chapter_id is None: return True # No hay capítulo, no hay nada que guardar

        # Serializa el contenido del TextCtrl a HTML
        content: str = self._serialize_content_to_html()

        # Llama al manejador de la aplicación para actualizar el contenido
        success: bool = self.app_handler.update_chapter_content_via_handler(self.chapter_id, content)

        # Si el guardado fue exitoso, limpia el estado sucio y notifica al manejador
        if success:
            self._is_dirty_view=False
            self.app_handler.set_dirty(True) # Notifica al manejador que el estado general de la app está sucio
        return success

    def on_text_changed(self,event:wx.CommandEvent):
        """
        Manejador de eventos para `wx.EVT_TEXT` y `wx.EVT_TEXT_PASTE` en el TextCtrl.

        Marca la vista como sucia si el panel está en modo edición y no está
        cargando datos.

        Args:
            event (wx.CommandEvent): El evento de cambio de texto.
        """
        # Verifica que el TextCtrl exista
        if not self.content_ctrl: event.Skip(); return

        # Ignora los eventos de cambio de texto si se están cargando datos programáticamente
        if self._loading_data: event.Skip(); return

        # Solo marca como sucio si el TextCtrl es editable (está en modo edición)
        if not self.content_ctrl.IsEditable(): event.Skip(); return

        # Si está en modo edición, marca la vista como sucia
        if self._is_in_edit_mode: self._set_view_dirty(True)

        event.Skip() # Permite que el evento se propague

    def on_idle(self,event:wx.IdleEvent):
        """
        Manejador para el evento `wx.EVT_IDLE`.

        Actualmente no realiza ninguna acción específica, solo permite que el
        evento se propague.

        Args:
            event (wx.IdleEvent): El evento de inactividad.
        """
        event.Skip() # Permite que el evento se propague

    def on_content_key_up_or_mouse_up(self,event:wx.KeyEvent):
        """
        Manejador de eventos para `wx.EVT_KEY_UP` y `wx.EVT_LEFT_UP` en el TextCtrl.

        Utilizado para actualizar el estado de la barra de herramientas de formato
        cuando el usuario mueve el cursor o cambia la selección con el teclado
        o el ratón.

        Args:
            event (wx.KeyEvent): El evento de teclado o ratón.
        """
        # Solo actualiza la barra si el TextCtrl existe, está en modo edición y es editable
        if not (self.content_ctrl and self._is_in_edit_mode and self.content_ctrl.IsEditable()): event.Skip(); return

        should_update_toolbar: bool = False
        event_type: int = event.GetEventType()

        # Actualiza la barra después de un clic izquierdo
        if event_type == wx.wxEVT_LEFT_UP: should_update_toolbar = True
        # Actualiza la barra después de soltar ciertas teclas de navegación
        elif event_type == wx.wxEVT_KEY_UP:
            key_code: int = event.GetKeyCode()
            nav_keys: List[int] = [wx.WXK_LEFT,wx.WXK_RIGHT,wx.WXK_UP,wx.WXK_DOWN,wx.WXK_PAGEUP,wx.WXK_PAGEDOWN,wx.WXK_HOME,wx.WXK_END]
            if key_code in nav_keys: should_update_toolbar = True

        # Si se debe actualizar la barra, programa la actualización para después
        # de que el evento actual haya sido completamente procesado
        if should_update_toolbar: wx.CallAfter(self._update_format_toolbar_state,True)

        event.Skip() # Permite que el evento se propague

    def on_edit_button_click(self,event:wx.CommandEvent):
        """
        Manejador de eventos para el clic en el botón de la barra de modo edición.

        Alterna entre el modo lectura y el modo edición. Si se sale del modo
        edición y hay cambios sin guardar, intenta guardarlos.

        Args:
            event (wx.CommandEvent): El evento de clic del botón.
        """
        # No hace nada si no hay un capítulo cargado o el panel está deshabilitado
        if self.chapter_id is None or not self.IsEnabled(): return

        if self._is_in_edit_mode:
            # Si está en modo edición, intenta guardar y cambia a modo lectura
            if self._is_dirty_view:
                save_ok: bool = self.save_changes()
                if not save_ok:
                    # Muestra un mensaje de error si el guardado falla
                    wx.MessageBox("Error al guardar el contenido. No se pudo finalizar la edición.","Error",wx.OK|wx.ICON_ERROR,self)
                    return # No cambia de modo si no se pudo guardar
            self._is_in_edit_mode = False # Cambia al modo lectura
        else:
            # Si está en modo lectura, cambia a modo edición
            self._is_in_edit_mode = True
            # Establece el foco en el TextCtrl al entrar en modo edición
            if self.content_ctrl: self.content_ctrl.SetFocus()

        # Actualiza la UI para reflejar el nuevo modo
        self._update_edit_mode_ui()

    def _apply_text_attribute(self, attr_modifier: Callable[[wx.TextAttr], None]):
        """
        Aplica una modificación de atributo de texto (fuente, color, estilo)
        a la selección actual en el `wx.TextCtrl` o al estilo por defecto
        en la posición del cursor.

        Si hay una selección, aplica el atributo a todo el rango seleccionado.
        Si no hay selección, aplica el atributo al estilo por defecto del
        TextCtrl en la posición del cursor, con lógica para manejar límites
        de palabras.

        Args:
            attr_modifier (Callable[[wx.TextAttr], None]): Una función que toma
                                                          un objeto `wx.TextAttr`
                                                          y lo modifica según el
                                                          formato deseado.
        """
        # Verifica que el TextCtrl exista
        if self.content_ctrl is None: return
        # Solo aplica formato si está en modo edición
        if not self._is_in_edit_mode: return
        # Solo aplica formato si el TextCtrl es editable
        if not self.content_ctrl.IsEditable(): return

        start_sel: int; end_sel: int
        start_sel, end_sel = self.content_ctrl.GetSelection()

        attribute_to_apply: wx.TextAttr = wx.TextAttr()

        if start_sel != end_sel:
            # Si hay una selección, obtiene el estilo del inicio de la selección
            # y lo aplica a todo el rango seleccionado después de modificarlo.
            base_style_for_selection: wx.TextAttr = wx.TextAttr()
            style_found: bool = self.content_ctrl.GetStyle(start_sel, base_style_for_selection)
            if style_found: attribute_to_apply.Merge(base_style_for_selection)
            else: attribute_to_apply.Merge(self.content_ctrl.GetDefaultStyle()) # Usa el estilo por defecto si no se encuentra estilo en la posición
            attr_modifier(attribute_to_apply) # Modifica el atributo
            self.content_ctrl.SetStyle(start_sel, end_sel, attribute_to_apply) # Aplica el estilo al rango
        else:
            # Si no hay selección, aplica el atributo al estilo por defecto en la posición del cursor.
            insertion_point: int = self.content_ctrl.GetInsertionPoint()
            text_len: int = self.content_ctrl.GetLastPosition()

            # Lógica para determinar si el cursor está sobre una palabra
            char_before_cursor: str = ""; char_at_cursor: str = ""
            if insertion_point > 0: char_before_cursor = self.content_ctrl.GetRange(insertion_point - 1, insertion_point)
            if insertion_point < text_len: char_at_cursor = self.content_ctrl.GetRange(insertion_point, insertion_point + 1)

            is_on_word: bool = False
            # Casos para considerar que el cursor está "sobre" una palabra
            c1:bool = char_before_cursor.isalnum() and char_at_cursor.isalnum() # Cursor en medio de palabra
            c2:bool = (not char_before_cursor.isalnum()) and char_at_cursor.isalnum() # Cursor al inicio de palabra
            c3p1:bool = char_before_cursor.isalnum() and (not char_at_cursor.isalnum()); c3p2:bool = (insertion_point == text_len); c3:bool = c3p1 or c3p2 # Cursor al final de palabra o al final del texto
            c4p1:bool = char_before_cursor.isalnum() and (char_at_cursor == ""); c4p2:bool = (insertion_point == text_len); c4:bool = c4p1 and c4p2 # Redundante con c3p2, pero mantiene la lógica original

            if c1 or c2 or c3 or c4: is_on_word = True

            if is_on_word:
                # Si está sobre una palabra, encuentra los límites de la palabra
                word_start: int = insertion_point
                while word_start > 0:
                    prev_char:str = self.content_ctrl.GetRange(word_start-1,word_start); prev_is_alnum:bool = prev_char.isalnum()
                    if not prev_is_alnum: break
                    word_start -= 1

                word_end: int = insertion_point
                while word_end < text_len:
                    curr_char:str = self.content_ctrl.GetRange(word_end,word_end+1); curr_is_alnum:bool = curr_char.isalnum()
                    if not curr_is_alnum: break
                    word_end += 1

                if word_start < word_end :
                    # Si se encontró una palabra, aplica el estilo a toda la palabra
                    base_style_word: wx.TextAttr = wx.TextAttr()
                    style_found_word: bool = self.content_ctrl.GetStyle(word_start,base_style_word)
                    if style_found_word: attribute_to_apply.Merge(base_style_word)
                    else: attribute_to_apply.Merge(self.content_ctrl.GetDefaultStyle())
                    attr_modifier(attribute_to_apply) # Modifica el atributo
                    self.content_ctrl.SetStyle(word_start,word_end,attribute_to_apply) # Aplica el estilo a la palabra
                    # Actualiza el estilo por defecto del TextCtrl para que el texto futuro tenga este estilo
                    default_copy: wx.TextAttr = wx.TextAttr(attribute_to_apply)
                    self.content_ctrl.SetDefaultStyle(default_copy)
                else:
                    # Si no se encontró una palabra (ej. solo un carácter no alfanumérico), no está "sobre" una palabra
                    is_on_word = False

            if not is_on_word:
                # Si no está sobre una palabra, aplica el estilo al estilo por defecto en la posición del cursor
                style_at_cursor: wx.TextAttr = wx.TextAttr()
                check_pos: int = insertion_point
                # Si el cursor está al inicio de un segmento con estilo por defecto, verifica el carácter anterior
                if insertion_point > 0:
                    temp_attr: wx.TextAttr = wx.TextAttr()
                    is_style_default: bool = True
                    got_style: bool = self.content_ctrl.GetStyle(insertion_point,temp_attr)
                    if got_style:
                        has_any_style_prop: bool = temp_attr.HasFont() or temp_attr.HasTextColour() or temp_attr.HasBackgroundColour()
                        is_style_default = not has_any_style_prop # Considera estilo por defecto si no tiene propiedades explícitas
                    if is_style_default: check_pos = max(0, insertion_point - 1)

                style_found_at_cursor: bool = self.content_ctrl.GetStyle(check_pos, style_at_cursor)
                if style_found_at_cursor: attribute_to_apply.Merge(style_at_cursor)
                else: attribute_to_apply.Merge(self.content_ctrl.GetDefaultStyle()) # Usa el estilo por defecto si no se encuentra estilo
                attr_modifier(attribute_to_apply) # Modifica el atributo
                self.content_ctrl.SetDefaultStyle(attribute_to_apply) # Establece el nuevo estilo como por defecto para el texto futuro

        self._set_view_dirty(True) # Marca la vista como sucia después de aplicar formato
        if self.content_ctrl: self.content_ctrl.SetFocus() # Mantiene el foco en el TextCtrl
        # Actualiza el estado de la barra de herramientas para reflejar el nuevo estilo
        wx.CallAfter(self._update_format_toolbar_state, True)

    # --- Manejadores de eventos para formato ---
    def on_font_facename_selected(self, event: wx.CommandEvent):
        """
        Manejador para el evento de selección en el ComboBox de familia de fuente.

        Aplica la familia de fuente seleccionada a la selección actual o al
        estilo por defecto en la posición del cursor.

        Args:
            event (wx.CommandEvent): El evento de selección del ComboBox.
        """
        if self.font_facename_combo is None: return
        selected_facename: str = self.font_facename_combo.GetStringSelection()
        if not selected_facename: return # No hace nada si no hay selección válida

        # Define la función modificadora de atributos
        def modifier(attr: wx.TextAttr):
            font: wx.Font
            if attr.HasFont(): font = attr.GetFont() # Usa la fuente existente si la hay
            else: font = wx.Font(self.default_font) # Si no, usa la fuente por defecto como base
            font.SetFaceName(selected_facename) # Establece la nueva familia de fuente
            attr.SetFont(font) # Aplica la fuente modificada al atributo
            # Asegura que el flag de fuente esté activo en el atributo
            if not attr.HasFont(): current_flags:int=attr.GetFlags(); new_flags:int=current_flags|wx.TEXT_ATTR_FONT; attr.SetFlags(new_flags)

        # Aplica la modificación usando el método auxiliar
        self._apply_text_attribute(modifier)

    def on_font_size_selected(self, event: wx.CommandEvent):
        """
        Manejador para el evento de selección en el Choice de tamaño de fuente.

        Aplica el tamaño de fuente seleccionado a la selección actual o al
        estilo por defecto en la posición del cursor.

        Args:
            event (wx.CommandEvent): El evento de selección del Choice.
        """
        if self.font_size_choice is None: return
        size_str: str = self.font_size_choice.GetStringSelection()
        try: size: int = int(size_str) # Convierte el tamaño a entero
        except ValueError: return # Ignora si la selección no es un número válido

        # Define la función modificadora de atributos
        def modifier(attr: wx.TextAttr):
            font: wx.Font
            if attr.HasFont(): font = attr.GetFont() # Usa la fuente existente si la hay
            else: font = wx.Font(self.default_font) # Si no, usa la fuente por defecto como base
            font.SetPointSize(size) # Establece el nuevo tamaño de fuente
            attr.SetFont(font) # Aplica la fuente modificada al atributo
            # Asegura que el flag de fuente esté activo en el atributo
            if not attr.HasFont(): current_flags:int=attr.GetFlags(); new_flags:int=current_flags|wx.TEXT_ATTR_FONT; attr.SetFlags(new_flags)

        # Aplica la modificación usando el método auxiliar
        self._apply_text_attribute(modifier)

    def on_format_bold(self, event: wx.CommandEvent):
        """
        Manejador para el evento de clic en el botón de Negrita.

        Alterna el estado de negrita (bold) para la selección actual o el
        estilo por defecto en la posición del cursor.

        Args:
            event (wx.CommandEvent): El evento de herramienta (clic en el botón).
        """
        if self.format_toolbar is None: return
        is_checked: bool = self.format_toolbar.GetToolState(ID_FORMAT_BOLD) # Obtiene el estado actual del botón (marcado/desmarcado)

        # Define la función modificadora de atributos
        def modifier(attr: wx.TextAttr):
            font: wx.Font
            if attr.HasFont(): font = attr.GetFont() # Usa la fuente existente si la hay
            else: font = wx.Font(self.default_font) # Si no, usa la fuente por defecto como base
            if is_checked: font.SetWeight(wx.FONTWEIGHT_BOLD) # Si el botón está marcado, aplica negrita
            else: font.SetWeight(wx.FONTWEIGHT_NORMAL) # Si no, aplica peso normal
            attr.SetFont(font) # Aplica la fuente modificada al atributo
            # Asegura que el flag de fuente esté activo en el atributo
            if not attr.HasFont(): current_flags:int=attr.GetFlags(); new_flags:int=current_flags|wx.TEXT_ATTR_FONT; attr.SetFlags(new_flags)

        # Aplica la modificación usando el método auxiliar
        self._apply_text_attribute(modifier)

    def on_format_italic(self, event: wx.CommandEvent):
        """
        Manejador para el evento de clic en el botón de Cursiva.

        Alterna el estado de cursiva (italic) para la selección actual o el
        estilo por defecto en la posición del cursor.

        Args:
            event (wx.CommandEvent): El evento de herramienta (clic en el botón).
        """
        if self.format_toolbar is None: return
        is_checked: bool = self.format_toolbar.GetToolState(ID_FORMAT_ITALIC) # Obtiene el estado actual del botón

        # Define la función modificadora de atributos
        def modifier(attr: wx.TextAttr):
            font: wx.Font
            if attr.HasFont(): font = attr.GetFont() # Usa la fuente existente si la hay
            else: font = wx.Font(self.default_font) # Si no, usa la fuente por defecto como base
            if is_checked: font.SetStyle(wx.FONTSTYLE_ITALIC) # Si el botón está marcado, aplica cursiva
            else: font.SetStyle(wx.FONTSTYLE_NORMAL) # Si no, aplica estilo normal
            attr.SetFont(font) # Aplica la fuente modificada al atributo
            # Asegura que el flag de fuente esté activo en el atributo
            if not attr.HasFont(): current_flags:int=attr.GetFlags(); new_flags:int=current_flags|wx.TEXT_ATTR_FONT; attr.SetFlags(new_flags)

        # Aplica la modificación usando el método auxiliar
        self._apply_text_attribute(modifier)

    def on_format_underline(self, event: wx.CommandEvent):
        """
        Manejador para el evento de clic en el botón de Subrayado.

        Alterna el estado de subrayado (underline) para la selección actual o el
        estilo por defecto en la posición del cursor.

        Args:
            event (wx.CommandEvent): El evento de herramienta (clic en el botón).
        """
        if self.format_toolbar is None: return
        is_checked: bool = self.format_toolbar.GetToolState(ID_FORMAT_UNDERLINE) # Obtiene el estado actual del botón

        # Define la función modificadora de atributos
        def modifier(attr: wx.TextAttr):
            font: wx.Font
            if attr.HasFont(): font = attr.GetFont() # Usa la fuente existente si la hay
            else: font = wx.Font(self.default_font) # Si no, usa la fuente por defecto como base
            font.SetUnderlined(is_checked) # Establece el estado de subrayado en la fuente
            attr.SetFont(font) # Aplica la fuente modificada al atributo

            # Actualiza el flag de subrayado en el atributo
            current_flags: int = attr.GetFlags(); new_flags: int
            if is_checked: new_flags = current_flags | wx.TEXT_ATTR_FONT_UNDERLINE
            else: new_flags = current_flags & ~wx.TEXT_ATTR_FONT_UNDERLINE
            attr.SetFlags(new_flags)

            # Asegura que el flag de fuente esté activo en el atributo
            if not attr.HasFont():
                current_flags_after:int=attr.GetFlags(); new_flags_after:int=current_flags_after|wx.TEXT_ATTR_FONT
                attr.SetFlags(new_flags_after)

        # Aplica la modificación usando el método auxiliar
        self._apply_text_attribute(modifier)

    def on_font_colour_picked(self, event: wx.ColourPickerEvent):
        """
        Manejador para el evento de selección de color en el ColourPickerCtrl.

        Aplica el color seleccionado al texto en la selección actual o al
        estilo por defecto en la posición del cursor.

        Args:
            event (wx.ColourPickerEvent): El evento de selección de color.
        """
        colour: wx.Colour = event.GetColour() # Obtiene el color seleccionado

        # Define la función modificadora de atributos
        def modifier(attr: wx.TextAttr):
            attr.SetTextColour(colour) # Establece el color de texto en el atributo
            # Asegura que el flag de color de texto esté activo en el atributo
            if not attr.HasTextColour(): current_flags:int=attr.GetFlags(); new_flags:int=current_flags|wx.TEXT_ATTR_TEXT_COLOUR; attr.SetFlags(new_flags)

        # Aplica la modificación usando el método auxiliar
        self._apply_text_attribute(modifier)

    def on_text_style_selected(self, event: wx.CommandEvent):
        """
        Manejador para el evento de selección en el Choice de estilo de texto.

        Aplica un estilo de texto predefinido (como Título 1, Normal, etc.)
        a la selección actual o al estilo por defecto en la posición del cursor.

        Args:
            event (wx.CommandEvent): El evento de selección del Choice.
        """
        if self.text_style_choice is None: return
        style_name: str = self.text_style_choice.GetStringSelection() # Obtiene el nombre del estilo seleccionado
        style_props: Optional[Dict[str, Any]] = self.text_styles_map.get(style_name) # Busca las propiedades del estilo en el mapa

        if not style_props: return # No hace nada si el nombre del estilo no es válido

        # Define la función modificadora de atributos
        def modifier(attr: wx.TextAttr):
            font: wx.Font
            if attr.HasFont(): font = attr.GetFont() # Usa la fuente existente si la hay
            else: font = wx.Font(self.default_font) # Si no, usa la fuente por defecto como base

            # Aplica el tamaño de fuente según las propiedades del estilo
            point_size_prop: Optional[int] = style_props.get("point_size")
            size_delta_prop: Optional[int] = style_props.get("size_delta")
            if point_size_prop is not None: font.SetPointSize(point_size_prop) # Si se especifica un tamaño absoluto
            elif size_delta_prop is not None: # Si se especifica un delta respecto al tamaño por defecto
                new_size: int = self.default_font.GetPointSize() + size_delta_prop
                font.SetPointSize(new_size)

            # Aplica el peso (negrita) según las propiedades del estilo
            is_bold_prop: bool = style_props.get("bold",False)
            if is_bold_prop: font.SetWeight(wx.FONTWEIGHT_BOLD)
            else: font.SetWeight(wx.FONTWEIGHT_NORMAL)

            # Aplica el estilo (cursiva) según las propiedades del estilo
            is_italic_prop: bool = style_props.get("italic",False)
            if is_italic_prop: font.SetStyle(wx.FONTSTYLE_ITALIC)
            else: font.SetStyle(wx.FONTSTYLE_NORMAL)

            # Aplica el subrayado según las propiedades del estilo
            is_underline_prop: bool = style_props.get("underline",False)
            font.SetUnderlined(is_underline_prop)

            attr.SetFont(font) # Aplica la fuente modificada al atributo
            # Asegura que el flag de fuente esté activo
            if not attr.HasFont(): current_flags_font:int=attr.GetFlags(); attr.SetFlags(current_flags_font|wx.TEXT_ATTR_FONT)

            # Aplica el color de texto según las propiedades del estilo
            color_str: Optional[str] = style_props.get("color")
            if color_str:
                attr.SetTextColour(wx.Colour(color_str))
                # Asegura que el flag de color de texto esté activo
                if not attr.HasTextColour(): current_flags_color:int=attr.GetFlags(); attr.SetFlags(current_flags_color|wx.TEXT_ATTR_TEXT_COLOUR)

        # Aplica la modificación usando el método auxiliar
        self._apply_text_attribute(modifier)

    def is_editable(self) -> bool:
        """
        Verifica si la vista del contenido del capítulo está actualmente
        en modo edición.

        Returns:
            bool: True si el panel está en modo edición, False en modo lectura.
        """
        return self._is_in_edit_mode

    def is_dirty(self) -> bool:
        """
        Verifica si la vista del contenido del capítulo tiene cambios sin guardar
        mientras está en modo edición.

        Returns:
            bool: True si la vista está en modo edición y tiene cambios sin guardar.
        """
        is_dirty_and_editing: bool = self._is_dirty_view and self._is_in_edit_mode
        return is_dirty_and_editing

    def enable_view(self, enable: bool):
        """
        Habilita o deshabilita la interacción con esta vista completa.

        Si se deshabilita la vista mientras está en modo edición, cambia
        automáticamente a modo lectura.

        Args:
            enable (bool): True para habilitar la vista, False para deshabilitarla.
        """
        self.Enable(enable) # Habilita/deshabilita el panel
        if not enable:
            # Si se deshabilita, sale del modo edición si estaba activo
            if self._is_in_edit_mode: self._is_in_edit_mode = False
        self._update_edit_mode_ui() # Actualiza la UI para reflejar el estado de habilitación/modo

    def force_save_if_dirty(self) -> bool:
        """
        Intenta guardar los cambios si la vista está en modo edición y marcada
        como sucia.

        Este método es útil para asegurar que los cambios se guarden antes de
        realizar una acción que podría perderlos (ej. cerrar la aplicación,
        cambiar de capítulo).

        Returns:
            bool: True si el guardado fue exitoso o no fue necesario guardar.
                  False si ocurrió un error durante el guardado.
        """
        # Verifica si se necesita guardar (está en modo edición y sucio)
        should_save: bool = self._is_in_edit_mode and self._is_dirty_view
        if should_save:
            # Si se necesita guardar, llama al método de guardado
            save_result: bool = self.save_changes()
            return save_result # Devuelve el resultado del guardado
        return True # Si no se necesitaba guardar, considera que la operación fue exitosa