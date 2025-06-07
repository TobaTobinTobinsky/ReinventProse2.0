# -*- coding: utf-8 -*-
"""
Archivo: MainWindow.py
Descripción:
    Ventana principal de la aplicación "ReinventProse 2.0".
    Este módulo define la clase `MainWindow`, que constituye el núcleo de la
    interfaz de usuario. Gestiona la disposición de todos los paneles de la
    aplicación (biblioteca, detalles del libro, lista de capítulos, pestañas de
    edición de contenido, ideas abstractas y concretas) utilizando el AUI Manager
    de wxPython para una interfaz flexible y personalizable.

    Coordina el flujo de la aplicación y la interacción entre las diferentes vistas
    y el `AppHandler` (que maneja la lógica de negocio y el acceso a datos).
    Se encarga de actualizar dinámicamente la barra de herramientas y los menús
    según el contexto de la aplicación, persistir el layout de la ventana entre
    sesiones, gestionar la carga y guardado de datos, y ofrecer funcionalidades
    adicionales como la exportación de libros a múltiples formatos (TXT, DOCX, PDF)
    y una ventana "Acerca de" personalizada.
Autor: AutoDoc AI
Fecha: 07/06/2025
Versión: 0.0.1
Licencia: MIT License
"""
import wx
import wx.aui
import os
import sys
from typing import Optional, Dict, Any, List, Tuple, Callable

from AppHandler import AppHandler
from BookDetailsView import BookDetailsView
from ChapterContentView import ChapterContentView
from AbstractIdeaView import AbstractIdeaView
from ConcreteIdeaView import ConcreteIdeaView
from Util import load_image
from LibraryView import LibraryView
from NewBookDialog import NewBookDialog
from ChapterListView import ChapterListView
from Exporter import TxtExporter, DocxExporter, PdfExporter, PYTHON_DOCX_AVAILABLE, REPORTLAB_AVAILABLE
from CustomAboutDialog import ReinventProseAboutInfo, ReinventProseAboutFrame

ID_TOOL_NEW_BOOK: int
ID_TOOL_NEW_BOOK = wx.ID_NEW
ID_TOOL_EDIT_BOOK: wx.WindowIDRef
ID_TOOL_EDIT_BOOK = wx.NewIdRef()
ID_TOOL_SAVE_BOOK: int
ID_TOOL_SAVE_BOOK = wx.ID_SAVE
ID_TOOL_BACK_TO_LIBRARY: wx.WindowIDRef
ID_TOOL_BACK_TO_LIBRARY = wx.NewIdRef()
ID_TOOL_UNDO: int
ID_TOOL_UNDO = wx.ID_UNDO
ID_TOOL_REDO: wx.WindowIDRef
ID_TOOL_REDO = wx.NewIdRef()

ID_EXPORT_TXT: wx.WindowIDRef
ID_EXPORT_TXT = wx.NewIdRef()
ID_EXPORT_DOCX: wx.WindowIDRef
ID_EXPORT_DOCX = wx.NewIdRef()
ID_EXPORT_PDF: wx.WindowIDRef
ID_EXPORT_PDF = wx.NewIdRef()

STATE_LIBRARY_VIEW: int
STATE_LIBRARY_VIEW = 0
STATE_BOOK_DETAILS_VIEW: int
STATE_BOOK_DETAILS_VIEW = 1
STATE_BOOK_EDIT_MODE: int
STATE_BOOK_EDIT_MODE = 2


class MainWindow(wx.Frame):
    """
    Ventana principal de la aplicación ReinventProse 2.0.

    Hereda de wx.Frame y actúa como el contenedor principal para todos los
    componentes de la interfaz de usuario y el gestor de layout AUI. Orquesta
    las diferentes vistas, la barra de herramientas, la barra de menú y la
    barra de estado, interactuando con el AppHandler para la lógica de negocio.
    """
    CONFIG_DIR_NAME: str
    CONFIG_DIR_NAME = ".reinventprose_v2_config"
    PERSPECTIVE_FILE_NAME: str
    PERSPECTIVE_FILE_NAME = "main_window_perspective.txt"
    APP_ICON_FILENAME: str
    APP_ICON_FILENAME = "app_icon.ico"
    APP_VERSION: str
    APP_VERSION = "2.0.42"

    app_name: str
    app_handler: AppHandler
    base_panel: wx.Panel
    aui_manager: wx.aui.AuiManager
    current_book_id: Optional[int]
    current_chapter_id: Optional[int]
    current_app_state: int
    toolbar_tools_config: Dict[int, Dict[str, Any]]
    toolbar: Optional[wx.ToolBar]
    status_bar: Optional[wx.StatusBar]

    library_view: Optional[LibraryView]
    book_details_view: Optional[BookDetailsView]
    chapter_list_view: Optional[ChapterListView]

    edit_notebook: Optional[wx.aui.AuiNotebook]
    chapter_content_view_notebook: Optional[ChapterContentView]
    abstract_idea_view_notebook: Optional[AbstractIdeaView]
    concrete_idea_view_notebook: Optional[ConcreteIdeaView]

    toggle_library_view_menu_item: Optional[wx.MenuItem]
    toggle_chapter_list_view_menu_item: Optional[wx.MenuItem]
    toggle_book_details_view_menu_item: Optional[wx.MenuItem]
    toggle_edit_notebook_menu_item: Optional[wx.MenuItem]


    def __init__(self, parent: Optional[wx.Window], title: str, app_handler: AppHandler):
        """
        Constructor de la clase MainWindow.

        Inicializa la ventana principal, establece sus propiedades básicas,
        carga el icono de la aplicación, crea y configura el AUI Manager,
        inicializa las vistas principales, la barra de menú, la barra de herramientas
        y la barra de estado. También carga el estado de la perspectiva AUI guardada
        y establece el estado inicial de la aplicación.

        Args:
            parent (Optional[wx.Window]): La ventana padre de esta frame.
            title (str): El título que se mostrará en la barra de título de la ventana.
            app_handler (AppHandler): La instancia del manejador de la lógica de la aplicación.
        """
        super().__init__(parent, id=wx.ID_ANY, title=title, size=(1366, 768))

        self._set_application_icon()

        self.app_name = title
        self.app_handler = app_handler
        self.app_handler.set_main_window(self)

        self.base_panel = wx.Panel(self)
        self.aui_manager = wx.aui.AuiManager()
        self.aui_manager.SetManagedWindow(self.base_panel)

        self.current_book_id = None
        self.current_chapter_id = None
        self.current_app_state = -1

        self.toolbar_tools_config = {}
        self.toolbar = None
        self.status_bar = None

        self.library_view = None
        self.book_details_view = None
        self.chapter_list_view = None

        self.edit_notebook = None
        self.chapter_content_view_notebook = None
        self.abstract_idea_view_notebook = None
        self.concrete_idea_view_notebook = None

        self.toggle_library_view_menu_item = None
        self.toggle_chapter_list_view_menu_item = None
        self.toggle_book_details_view_menu_item = None
        self.toggle_edit_notebook_menu_item = None

        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._create_views()

        sizer: wx.BoxSizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.base_panel, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self._load_state()
        self.on_show_library_as_center(event=None, force_clean=True)
        self.Centre()

        self._bind_events()

    def _bind_events(self):
        """
        Centraliza los bindings de eventos de la ventana principal y de la UI.
        Este método se llama una vez durante la inicialización.
        """
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_MAXIMIZE, self.on_maximize)

        self.Bind(wx.EVT_UPDATE_UI, self.on_update_ui_save_button, id=ID_TOOL_SAVE_BOOK)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_ui_undo_redo, id=ID_TOOL_UNDO)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_ui_undo_redo, id=ID_TOOL_REDO)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_ui_edit_book, id=ID_TOOL_EDIT_BOOK)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_ui_export_menu_items, id=ID_EXPORT_TXT)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_ui_export_menu_items, id=ID_EXPORT_DOCX)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_ui_export_menu_items, id=ID_EXPORT_PDF)

    def _get_resource_path(self, file_name: str) -> Optional[str]:
        """
        Obtiene la ruta a un archivo de recurso, considerando el empaquetado.
        Busca primero en la raíz (o `_MEIPASS`) y luego en una subcarpeta `assets`.

        Args:
            file_name (str): El nombre del archivo de recurso (ej. "app_icon.ico").

        Returns:
            Optional[str]: La ruta absoluta al archivo si se encuentra, o None.
        """
        base_path: str
        # Determina la ruta base, considerando si la aplicación está empaquetada con PyInstaller
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS # pyright: ignore [reportGeneralTypeIssues, reportUnknownMemberType]
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        resource_path: str
        # Intenta encontrar el recurso en la ruta base
        resource_path = os.path.join(base_path, file_name)
        path_exists: bool
        path_exists = os.path.exists(resource_path)
        if path_exists:
            return resource_path
        resource_path_assets: str
        # Si no se encuentra, intenta en una subcarpeta 'assets'
        resource_path_assets = os.path.join(base_path, "assets", file_name)
        path_exists_assets: bool
        path_exists_assets = os.path.exists(resource_path_assets)
        if path_exists_assets:
            return resource_path_assets
        # Si no se encuentra en ninguna parte, imprime una advertencia y retorna None
        print(f"Advertencia: No se encontró el archivo de recurso '{file_name}' en '{base_path}' ni en 'assets'.")
        return None

    def _set_application_icon(self):
        """
        Carga y establece el icono para la ventana de la aplicación (barra de título, barra de tareas).
        Utiliza el archivo definido en `self.APP_ICON_FILENAME`.
        """
        icon_path: Optional[str]
        icon_path = self._get_resource_path(self.APP_ICON_FILENAME)
        if icon_path:
            try:
                icon: wx.Icon
                icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
                if icon.IsOk():
                    self.SetIcon(icon)
                else:
                    print(f"Error: No se pudo cargar el icono desde '{icon_path}' (wx.Icon.IsOk() falló).")
            except Exception as e:
                print(f"Error al cargar el icono de aplicación desde '{icon_path}': {e}")
        else:
            print(f"Advertencia: Icono de aplicación '{self.APP_ICON_FILENAME}' no encontrado. Se usará el icono por defecto del sistema.")

    def _load_tool_icon(self, icon_name: str, icon_size: wx.Size) -> wx.Bitmap:
        """
        Carga un icono para la barra de herramientas desde un archivo.
        Utiliza `_get_resource_path` para encontrar el archivo y luego lo carga como `wx.Bitmap`.
        Si falla, recurre a un icono de `wx.ArtProvider`.

        Args:
            icon_name (str): Nombre del archivo del icono (ej. "new_book.png").
            icon_size (wx.Size): Tamaño deseado del bitmap del icono.

        Returns:
            wx.Bitmap: El bitmap del icono cargado o un bitmap de fallback.
        """
        icon_path: Optional[str]
        icon_path = self._get_resource_path(icon_name)
        if icon_path:
            try:
                img: wx.Image
                img = wx.Image(icon_path)
                if img.IsOk():
                    # Escala la imagen al tamaño deseado con alta calidad
                    img.Rescale(icon_size.GetWidth(), icon_size.GetHeight(), wx.IMAGE_QUALITY_HIGH)
                    return wx.Bitmap(img)
                else:
                    print(f"Error: wx.Image no pudo cargar el archivo de icono '{icon_name}' desde '{icon_path}'.")
            except Exception as e:
                print(f"Excepción al cargar el icono de herramienta '{icon_name}' desde '{icon_path}': {e}")
        # Si falla la carga del archivo, usa un icono de wx.ArtProvider como fallback
        art_map: Dict[str, str]
        art_map = {
            "new_book.png": wx.ART_NEW,
            "edit2.png": wx.ART_EDIT,
            "save.png": wx.ART_FILE_SAVE,
            "library.png": wx.ART_GO_HOME,
            "undo.png": wx.ART_UNDO,
            "redo.png": wx.ART_REDO
        }
        art_id: str
        art_id = art_map.get(icon_name, wx.ART_QUESTION)
        return wx.ArtProvider.GetBitmap(art_id, wx.ART_TOOLBAR, icon_size)

    def _add_tool_to_toolbar(self, tool_id: int, label: str, icon_filename: str, short_help: str, handler: Callable[[wx.CommandEvent], None], kind: int = wx.ITEM_NORMAL):
        """
        Añade una herramienta a la configuración interna de la barra de herramientas.
        La barra de herramientas se (re)construye visualmente en `_update_toolbar_state`.

        Args:
            tool_id (int): El ID único para la herramienta.
            label (str): El texto que se mostrará para la herramienta (si TB_TEXT está activo).
            icon_filename (str): El nombre del archivo del icono para la herramienta.
            short_help (str): El texto de ayuda corta (tooltip) para la herramienta.
            handler (Callable[[wx.CommandEvent], None]): La función manejadora para el evento de la herramienta.
            kind (int, opcional): El tipo de herramienta (wx.ITEM_NORMAL, wx.ITEM_CHECK, etc.).
                                  Por defecto es wx.ITEM_NORMAL.
        """
        if self.toolbar is None:
            print("Error: self.toolbar no está inicializada al llamar a _add_tool_to_toolbar.")
            return
        bitmap: wx.Bitmap
        bitmap = self._load_tool_icon(icon_filename, self.toolbar.GetToolBitmapSize())
        # Almacena la configuración de la herramienta para su uso posterior
        self.toolbar_tools_config[tool_id] = {
            "id": tool_id,
            "label": label,
            "bitmap": bitmap,
            "short_help": short_help,
            "kind": kind,
            "handler": handler
        }

    def _create_toolbar(self):
        """
        Crea la instancia de la barra de herramientas principal y define la
        configuración de todas las herramientas que podrían mostrarse.
        La barra se poblará dinámicamente según el estado de la aplicación
        mediante `_update_toolbar_state`.
        """
        # Crea la barra de herramientas con estilos específicos
        self.toolbar = self.CreateToolBar(
            style=wx.TB_HORIZONTAL | wx.TB_TEXT | wx.TB_FLAT | wx.TB_HORZ_LAYOUT
        )
        if self.toolbar is None:
            print("Error crítico: No se pudo crear la barra de herramientas.")
            return
        # Establece el tamaño de los iconos
        self.toolbar.SetToolBitmapSize(wx.Size(24, 24))
        # Limpia cualquier configuración previa
        self.toolbar_tools_config.clear()
        # Añade la configuración de cada herramienta posible
        self._add_tool_to_toolbar(ID_TOOL_NEW_BOOK, "Nuevo", "new_book.png", "Crear un nuevo libro (Ctrl+N)", self.on_menu_new_book)
        self._add_tool_to_toolbar(ID_TOOL_EDIT_BOOK, "Editar Libro", "edit2.png", "Editar el libro actual (Ctrl+E)", self.on_edit_book_tool_click)
        self._add_tool_to_toolbar(ID_TOOL_SAVE_BOOK, "Guardar", "save.png", "Guardar cambios (Ctrl+S)", self.on_save_current_book_tool_click)
        self._add_tool_to_toolbar(ID_TOOL_BACK_TO_LIBRARY, "Biblioteca", "library.png", "Volver a la biblioteca (Ctrl+L)", self.on_back_to_library_tool_click)
        self._add_tool_to_toolbar(ID_TOOL_UNDO, "Deshacer", "undo.png", "Deshacer (Ctrl+Z)", self.on_undo_tool_click)
        self._add_tool_to_toolbar(ID_TOOL_REDO, "Rehacer", "redo.png", "Rehacer (Ctrl+Y)", self.on_redo_tool_click)

    def _update_toolbar_state(self, new_state: int):
        """
        Actualiza las herramientas visibles en la barra de herramientas según el estado
        actual de la aplicación. Este método es responsable de limpiar y repoblar
        la barra de herramientas.

        Args:
            new_state (int): El nuevo estado de la aplicación (ej. STATE_LIBRARY_VIEW).
        """
        if self.toolbar is None:
            return
        self.current_app_state = new_state
        self.toolbar.Freeze()
        # Limpiar todas las herramientas existentes
        current_tool_count: int
        current_tool_count = self.toolbar.GetToolsCount()
        i: int
        for i in range(current_tool_count):
            self.toolbar.DeleteToolByPos(0)
        # Definir qué herramientas mostrar para el nuevo estado
        tools_to_show_ids: List[Any]
        tools_to_show_ids = []
        if new_state == STATE_LIBRARY_VIEW:
            tools_to_show_ids = [ID_TOOL_NEW_BOOK]
        elif new_state == STATE_BOOK_DETAILS_VIEW:
            tools_to_show_ids = [
                ID_TOOL_NEW_BOOK,
                ID_TOOL_EDIT_BOOK,
                ID_TOOL_SAVE_BOOK,
                ID_TOOL_BACK_TO_LIBRARY
            ]
        elif new_state == STATE_BOOK_EDIT_MODE:
            tools_to_show_ids = [
                ID_TOOL_BACK_TO_LIBRARY,
                ID_TOOL_SAVE_BOOK,
                wx.ID_SEPARATOR,
                ID_TOOL_UNDO,
                ID_TOOL_REDO
            ]
        # Añadir las herramientas seleccionadas
        tool_id_or_sep: Any
        for tool_id_or_sep in tools_to_show_ids:
            if tool_id_or_sep == wx.ID_SEPARATOR:
                self.toolbar.AddSeparator()
                continue
            config: Optional[Dict[str, Any]]
            config = self.toolbar_tools_config.get(tool_id_or_sep)
            if config:
                self.toolbar.AddTool(
                    config["id"],
                    config["label"],
                    config["bitmap"],
                    config["short_help"],
                    config["kind"]
                )
            else:
                print(f"Advertencia: Configuración no encontrada para tool_id {tool_id_or_sep}")
        self.toolbar.Realize()
        self.toolbar.Thaw()

    def on_update_ui_save_button(self, event: wx.UpdateUIEvent):
        """
        Actualiza el estado de habilitación del botón/menú Guardar.
        Se habilita si hay cambios pendientes (`is_application_dirty()`) y la aplicación
        está en un estado donde guardar es relevante y hay un libro/capítulo cargado.

        Args:
            event (wx.UpdateUIEvent): El evento de actualización de UI.
        """
        can_save: bool
        can_save = False
        # Solo se puede guardar si hay cambios pendientes
        if self.app_handler.is_application_dirty():
            # Y si el estado actual permite guardar (detalles del libro o edición)
            if self.current_app_state == STATE_BOOK_DETAILS_VIEW or \
               self.current_app_state == STATE_BOOK_EDIT_MODE:
                # Y si hay un libro cargado
                if self.current_book_id is not None:
                    can_save = True
        event.Enable(can_save)

    def on_update_ui_undo_redo(self, event: wx.UpdateUIEvent):
        """
        Actualiza el estado de habilitación de los botones/menús Deshacer y Rehacer.
        Se habilitan si el control con foco es un `wx.TextCtrl` editable que soporta
        dichas acciones, y si la aplicación está en modo de edición de libro
        y el panel de contenido del capítulo está en modo edición.

        Args:
            event (wx.UpdateUIEvent): El evento de actualización de UI.
        """
        target: Optional[wx.Window]
        target = wx.Window.FindFocus()
        can_undo: bool
        can_undo = False
        can_redo: bool
        can_redo = False
        # Verificar si el control con foco es un TextCtrl editable y soporta Undo/Redo
        if isinstance(target, wx.TextCtrl):
            if target.IsEditable():
                can_undo = target.CanUndo()
                can_redo = target.CanRedo()
        # Adicionalmente, solo habilitar si estamos en el contexto adecuado (editando contenido de capítulo)
        edit_mode_active_for_text: bool
        edit_mode_active_for_text = False
        if self.current_app_state == STATE_BOOK_EDIT_MODE:
            if self.edit_notebook is not None:
                current_page_index: int
                current_page_index = self.edit_notebook.GetSelection()
                if current_page_index != wx.NOT_FOUND:
                    page_window: Optional[wx.Window]
                    page_window = self.edit_notebook.GetPage(current_page_index)
                    # Verificar si la página activa es la vista de contenido del capítulo y si está en modo edición
                    if page_window == self.chapter_content_view_notebook:
                        if self.chapter_content_view_notebook is not None:
                             if self.chapter_content_view_notebook.is_editable():
                                edit_mode_active_for_text = True
        event_id: int
        event_id = event.GetId()
        # Habilitar el evento solo si la acción es posible en el TextCtrl y el contexto es el de edición de contenido
        if event_id == ID_TOOL_UNDO:
            event.Enable(can_undo and edit_mode_active_for_text)
        elif event_id == ID_TOOL_REDO:
            event.Enable(can_redo and edit_mode_active_for_text)
        else:
            event.Skip()

    def on_update_ui_edit_book(self, event: wx.UpdateUIEvent):
        """
        Actualiza el estado de habilitación del botón/menú "Editar Libro".
        Se habilita si la aplicación está en la vista de detalles de un libro
        (STATE_BOOK_DETAILS_VIEW) y hay un libro actualmente seleccionado
        (`current_book_id` no es None).

        Args:
            event (wx.UpdateUIEvent): El evento de actualización de UI.
        """
        can_edit_book: bool
        can_edit_book = False
        # Habilitar solo si estamos en la vista de detalles del libro y hay un libro seleccionado
        if self.current_app_state == STATE_BOOK_DETAILS_VIEW:
            if self.current_book_id is not None:
                can_edit_book = True
        event.Enable(can_edit_book)

    def _create_menu_bar(self):
        """
        Crea y configura la barra de menú principal de la aplicación, incluyendo
        los menús Archivo, Editar, Ver, Exportar y Ayuda con sus respectivos ítems.
        """
        menu_bar: wx.MenuBar
        menu_bar = wx.MenuBar()
        # --- Menú Archivo ---
        file_menu: wx.Menu
        file_menu = wx.Menu()
        new_book_item: wx.MenuItem
        new_book_item = file_menu.Append(ID_TOOL_NEW_BOOK, "Nuevo Libro\tCtrl+N", "Crear un nuevo proyecto de libro")
        file_menu.AppendSeparator()
        edit_book_item: wx.MenuItem
        edit_book_item = file_menu.Append(ID_TOOL_EDIT_BOOK, "Editar Libro Seleccionado\tCtrl+E", "Abrir el libro seleccionado para edición de capítulos")
        save_changes_item: wx.MenuItem
        save_changes_item = file_menu.Append(ID_TOOL_SAVE_BOOK, "Guardar Cambios\tCtrl+S", "Guardar todos los cambios pendientes")
        file_menu.AppendSeparator()
        # Submenú Exportar
        export_menu: wx.Menu
        export_menu = wx.Menu()
        export_txt_item: wx.MenuItem
        export_txt_item = export_menu.Append(ID_EXPORT_TXT, "Como TXT...", "Exportar el libro actual a formato de texto plano")
        export_docx_item: wx.MenuItem
        export_docx_item = export_menu.Append(ID_EXPORT_DOCX, "Como DOCX...", "Exportar el libro actual a formato DOCX")
        export_pdf_item: wx.MenuItem
        export_pdf_item = export_menu.Append(ID_EXPORT_PDF, "Como PDF...", "Exportar el libro actual a formato PDF")
        file_menu.AppendSubMenu(export_menu, "E&xportar")
        file_menu.AppendSeparator()
        show_library_item: wx.MenuItem
        show_library_item = file_menu.Append(ID_TOOL_BACK_TO_LIBRARY, "Mostrar Biblioteca\tCtrl+L", "Volver a la vista de la biblioteca")
        file_menu.AppendSeparator()
        exit_item: wx.MenuItem
        exit_item = file_menu.Append(wx.ID_EXIT, "Salir\tCtrl+Q", "Cerrar la aplicación")
        menu_bar.Append(file_menu, "&Archivo")
        # --- Menú Editar ---
        edit_main_menu: wx.Menu
        edit_main_menu = wx.Menu()
        undo_item: wx.MenuItem
        undo_item = edit_main_menu.Append(ID_TOOL_UNDO, "Deshacer\tCtrl+Z", "Deshacer la última acción de edición de texto")
        redo_item: wx.MenuItem
        redo_item = edit_main_menu.Append(ID_TOOL_REDO, "Rehacer\tCtrl+Y", "Rehacer la última acción deshecha")
        menu_bar.Append(edit_main_menu, "&Editar")
        # --- Menú Ver ---
        view_menu: wx.Menu
        view_menu = wx.Menu()
        self.toggle_library_view_menu_item = view_menu.AppendCheckItem(wx.ID_ANY, "Panel Biblioteca", "Mostrar/Ocultar el panel de la Biblioteca")
        self.toggle_chapter_list_view_menu_item = view_menu.AppendCheckItem(wx.ID_ANY, "Panel Lista de Capítulos", "Mostrar/Ocultar el panel de Lista de Capítulos")
        self.toggle_book_details_view_menu_item = view_menu.AppendCheckItem(wx.ID_ANY, "Panel Detalles del Libro", "Mostrar/Ocultar el panel de Detalles del Libro")
        self.toggle_edit_notebook_menu_item = view_menu.AppendCheckItem(wx.ID_ANY, "Panel Edición Pestañas", "Mostrar/Ocultar el panel de edición con pestañas")
        menu_bar.Append(view_menu, "&Ver")
        # --- Menú Ayuda ---
        help_menu: wx.Menu
        help_menu = wx.Menu()
        about_item: wx.MenuItem
        about_item = help_menu.Append(wx.ID_ABOUT, f"Acerca de {self.app_name}...\tF1", f"Información sobre {self.app_name}")
        menu_bar.Append(help_menu, "A&yuda")
        self.SetMenuBar(menu_bar)
        # --- Binds de Menú ---
        self.Bind(wx.EVT_MENU, self.on_menu_new_book, id=ID_TOOL_NEW_BOOK)
        self.Bind(wx.EVT_MENU, self.on_edit_book_tool_click, id=ID_TOOL_EDIT_BOOK)
        self.Bind(wx.EVT_MENU, self.on_save_current_book_tool_click, id=ID_TOOL_SAVE_BOOK)
        self.Bind(wx.EVT_MENU, self.on_back_to_library_tool_click, id=ID_TOOL_BACK_TO_LIBRARY)
        self.Bind(wx.EVT_MENU, self.on_menu_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_undo_tool_click, id=ID_TOOL_UNDO)
        self.Bind(wx.EVT_MENU, self.on_redo_tool_click, id=ID_TOOL_REDO)
        self.Bind(wx.EVT_MENU, self.on_menu_about, source=about_item)
        # Binds para el menú Ver
        if self.toggle_library_view_menu_item:
            self.Bind(wx.EVT_MENU, lambda evt, name="library_view", item=self.toggle_library_view_menu_item: self._toggle_pane_visibility_and_menu(name, item, evt), source=self.toggle_library_view_menu_item)
        if self.toggle_chapter_list_view_menu_item:
            self.Bind(wx.EVT_MENU, lambda evt, name="chapter_list_view_pane", item=self.toggle_chapter_list_view_menu_item: self._toggle_pane_visibility_and_menu(name, item, evt), source=self.toggle_chapter_list_view_menu_item)
        if self.toggle_book_details_view_menu_item:
            self.Bind(wx.EVT_MENU, lambda evt, name="book_details_view", item=self.toggle_book_details_view_menu_item: self._toggle_pane_visibility_and_menu(name, item, evt), source=self.toggle_book_details_view_menu_item)
        if self.toggle_edit_notebook_menu_item:
            self.Bind(wx.EVT_MENU, lambda evt, name="edit_notebook_pane", item=self.toggle_edit_notebook_menu_item: self._toggle_pane_visibility_and_menu(name, item, evt), source=self.toggle_edit_notebook_menu_item)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_ui_view_menu)
        # Binds para el menú Exportar
        self.Bind(wx.EVT_MENU, self.on_export_txt, id=ID_EXPORT_TXT)
        self.Bind(wx.EVT_MENU, self.on_export_docx, id=ID_EXPORT_DOCX)
        self.Bind(wx.EVT_MENU, self.on_export_pdf, id=ID_EXPORT_PDF)

    def on_update_ui_export_menu_items(self, event: wx.UpdateUIEvent):
        """
        Actualiza dinámicamente el estado de los ítems del menú "Exportar".
        Habilita las opciones si hay un libro cargado y la librería
        correspondiente está disponible.

        Args:
            event (wx.UpdateUIEvent): El evento de actualización de UI.
        """
        can_export_book: bool
        # Solo se puede exportar si hay un libro seleccionado
        can_export_book = self.current_book_id is not None
        event_id: int
        event_id = event.GetId()
        # Habilitar opciones según la disponibilidad de la librería y si hay libro
        if event_id == ID_EXPORT_TXT:
            event.Enable(can_export_book)
        elif event_id == ID_EXPORT_DOCX:
            event.Enable(can_export_book and PYTHON_DOCX_AVAILABLE)
        elif event_id == ID_EXPORT_PDF:
            event.Enable(can_export_book and REPORTLAB_AVAILABLE)
        else:
            event.Skip()

    def on_export_txt(self, event: wx.CommandEvent):
        """
        Manejador para la acción de exportar el libro actual a formato TXT.
        Invoca al TxtExporter para generar el archivo.

        Args:
            event (wx.CommandEvent): El evento de menú que disparó esta acción.
        """
        if self.current_book_id is None:
            wx.MessageBox("Por favor, seleccione o abra un libro para exportar.",
                          "Sin Libro Seleccionado", wx.OK | wx.ICON_INFORMATION, self)
            return
        book_details: Optional[Dict[str, Any]]
        book_details = self.app_handler.get_book_details(self.current_book_id)
        if not book_details:
            wx.MessageBox("No se pudieron obtener los detalles del libro seleccionado.",
                          "Error", wx.OK | wx.ICON_ERROR, self)
            return
        # Crear nombre de archivo por defecto seguro a partir del título del libro
        book_title_safe: str
        book_title_safe = book_details.get('title', 'libro_exportado')
        default_filename_base: str
        default_filename_base = "".join(
            c if c.isalnum() or c in (' ', '-', '_') else '' for c in book_title_safe
        ).rstrip().replace(' ', '_')
        default_filename: str
        default_filename = default_filename_base + ".txt"
        # Mostrar diálogo para seleccionar la ruta de guardado
        with wx.FileDialog(self, "Guardar como archivo TXT",
                           wildcard="Archivos de Texto (*.txt)|*.txt",
                           defaultFile=default_filename,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname: str
            pathname = file_dialog.GetPath()
            # Obtener datos de los capítulos y exportar
            chapters_data: List[Dict[str, Any]]
            chapters_data = self.app_handler.get_chapters_by_book_id(self.current_book_id)
            exporter: TxtExporter
            exporter = TxtExporter()
            success: bool
            success = exporter.export(book_details, chapters_data, pathname)
            # Mostrar resultado de la exportación
            if success:
                wx.MessageBox(f"Libro exportado exitosamente a:\n{pathname}",
                              "Exportación Exitosa", wx.OK | wx.ICON_INFORMATION, self)
            else:
                wx.MessageBox("Ocurrió un error durante la exportación a TXT.",
                              "Error de Exportación", wx.OK | wx.ICON_ERROR, self)

    def on_export_docx(self, event: wx.CommandEvent):
        """
        Manejador para la acción de exportar el libro actual a formato DOCX.
        Verifica disponibilidad de `python-docx` e invoca al `DocxExporter`.

        Args:
            event (wx.CommandEvent): El evento de menú que disparó esta acción.
        """
        # Verificar si la librería python-docx está disponible
        if not PYTHON_DOCX_AVAILABLE:
            wx.MessageBox("La funcionalidad de exportación a DOCX requiere la librería 'python-docx'.\n"
                          "Por favor, instálela (ej: pip install python-docx) y reinicie la aplicación.",
                          "Librería Faltante", wx.OK | wx.ICON_ERROR, self)
            return
        if self.current_book_id is None:
            wx.MessageBox("Por favor, seleccione o abra un libro para exportar.",
                          "Sin Libro Seleccionado", wx.OK | wx.ICON_INFORMATION, self)
            return
        book_details: Optional[Dict[str, Any]]
        book_details = self.app_handler.get_book_details(self.current_book_id)
        if not book_details:
            wx.MessageBox("No se pudieron obtener los detalles del libro seleccionado.",
                          "Error", wx.OK | wx.ICON_ERROR, self)
            return
        # Crear nombre de archivo por defecto seguro
        book_title_safe: str
        book_title_safe = book_details.get('title', 'libro_exportado')
        default_filename_base: str
        default_filename_base = "".join(
            c if c.isalnum() or c in (' ', '-', '_') else '' for c in book_title_safe
        ).rstrip().replace(' ', '_')
        default_filename: str
        default_filename = default_filename_base + ".docx"
        # Mostrar diálogo para seleccionar la ruta de guardado
        with wx.FileDialog(self, "Guardar como archivo DOCX",
                           wildcard="Documentos Word (*.docx)|*.docx",
                           defaultFile=default_filename,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname: str
            pathname = file_dialog.GetPath()
            # Obtener datos de los capítulos y exportar
            chapters_data: List[Dict[str, Any]]
            chapters_data = self.app_handler.get_chapters_by_book_id(self.current_book_id)
            exporter: DocxExporter
            exporter = DocxExporter()
            success: bool
            success = exporter.export(book_details, chapters_data, pathname)
            # Mostrar resultado de la exportación
            if success:
                wx.MessageBox(f"Libro exportado exitosamente a:\n{pathname}",
                              "Exportación DOCX Exitosa", wx.OK | wx.ICON_INFORMATION, self)
            else:
                wx.MessageBox("Ocurrió un error durante la exportación a DOCX. "
                              "Verifique la consola para más detalles si la librería 'python-docx' está instalada.",
                              "Error de Exportación", wx.OK | wx.ICON_ERROR, self)

    def on_export_pdf(self, event: wx.CommandEvent):
        """
        Manejador para la acción de exportar el libro actual a formato PDF.
        Verifica disponibilidad de `reportlab` e invoca al `PdfExporter`.

        Args:
            event (wx.CommandEvent): El evento de menú que disparó esta acción.
        """
        # Verificar si la librería reportlab está disponible
        if not REPORTLAB_AVAILABLE:
            wx.MessageBox("La funcionalidad de exportación a PDF requiere la librería 'reportlab'.\n"
                          "Por favor, instálela (ej: pip install reportlab) y reinicie la aplicación.",
                          "Librería Faltante", wx.OK | wx.ICON_ERROR, self)
            return
        if self.current_book_id is None:
            wx.MessageBox("Por favor, seleccione o abra un libro para exportar.",
                          "Sin Libro Seleccionado", wx.OK | wx.ICON_INFORMATION, self)
            return
        book_details: Optional[Dict[str, Any]]
        book_details = self.app_handler.get_book_details(self.current_book_id)
        if not book_details:
            wx.MessageBox("No se pudieron obtener los detalles del libro seleccionado.",
                          "Error", wx.OK | wx.ICON_ERROR, self)
            return
        # Crear nombre de archivo por defecto seguro
        book_title_safe: str
        book_title_safe = book_details.get('title', 'libro_exportado')
        default_filename_base: str
        default_filename_base = "".join(
            c if c.isalnum() or c in (' ', '-', '_') else '' for c in book_title_safe
        ).rstrip().replace(' ', '_')
        default_filename: str
        default_filename = default_filename_base + ".pdf"
        # Mostrar diálogo para seleccionar la ruta de guardado
        with wx.FileDialog(self, "Guardar como archivo PDF",
                           wildcard="Archivos PDF (*.pdf)|*.pdf",
                           defaultFile=default_filename,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname: str
            pathname = file_dialog.GetPath()
            # Obtener datos de los capítulos y exportar
            chapters_data: List[Dict[str, Any]]
            chapters_data = self.app_handler.get_chapters_by_book_id(self.current_book_id)
            exporter: PdfExporter
            exporter = PdfExporter()
            success: bool
            success = exporter.export(book_details, chapters_data, pathname)
            # Mostrar resultado de la exportación
            if success:
                wx.MessageBox(f"Libro exportado exitosamente a:\n{pathname}",
                              "Exportación PDF Exitosa", wx.OK | wx.ICON_INFORMATION, self)
            else:
                wx.MessageBox("Ocurrió un error durante la exportación a PDF. "
                              "Verifique la consola para más detalles si la librería 'reportlab' está instalada.",
                              "Error de Exportación", wx.OK | wx.ICON_ERROR, self)

    def on_menu_about(self, event: wx.CommandEvent):
        """
        Muestra la ventana "Acerca de" personalizada (ReinventProseAboutFrame),
        utilizando ReinventProseAboutInfo para configurar su contenido.

        Args:
            event (wx.CommandEvent): El evento de menú que disparó esta acción.
        """
        info: ReinventProseAboutInfo
        info = ReinventProseAboutInfo()

        info.SetName(self.app_name)
        info.SetVersion(self.APP_VERSION)

        description: str
        description = (
            f"Una aplicación de escritorio para la gestión integral y organización "
            f"de proyectos de escritura creativa, desde la concepción de la idea "
            f"hasta la estructuración de capítulos y la exportación del manuscrito.\n\n"
            f"{self.app_name} forma parte de la innovadora suite de herramientas para escritores."
        )
        info.SetDescription(description)

        info.SetCopyright("(C) 2023-2024 Mauricio José Tobares. Todos los derechos reservados.")

        licence_full_text: str
        licence_full_text = (
            "MIT License\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy "
            "of this software and associated documentation files (the \"Software\"), to deal "
            "in the Software without restriction, including without limitation the rights "
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
            "copies of the Software, and to permit persons to whom the Software is "
            "furnished to do so, subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in all "
            "copies or substantial portions of the Software.\n\n"
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR "
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
            "SOFTWARE."
        )
        info.SetLicence(licence_full_text)

        icon_path: Optional[str]
        icon_path = self._get_resource_path(self.APP_ICON_FILENAME)
        if icon_path:
            try:
                app_icon_for_info: wx.Icon
                app_icon_for_info = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
                if app_icon_for_info.IsOk():
                    info.SetIcon(app_icon_for_info)
            except Exception as e_icon_about:
                print(f"Advertencia (About): No se pudo cargar el icono para la información: {e_icon_about}")

        info.AddDeveloper("Mauricio José Tobares (El Jefe) - Ideólogo y Director del Proyecto")
        info.AddDeveloper("PJ (Programador Jefe Asistente IA) - Desarrollo Principal y Arquitectura")
        info.AddDocWriter("GP (Planificador de Proyectos IA) - Documentación Técnica y Planificación")
        info.AddArtist("DUXUI (Diseñador UX/UI IA) - Diseño de Interfaz y Experiencia de Usuario")
        info.AddDeveloper("IP (Ingeniero de Pruebas IA) - Aseguramiento de Calidad")

        info.AddCollaborator("Amigo Tester #1", "Valiosas pruebas y sugerencias de usabilidad.")
        info.AddCollaborator("Comunidad de Betas Anónimos", "Por el feedback constructivo.")

        about_window: ReinventProseAboutFrame
        about_window = ReinventProseAboutFrame(self, info)
        about_window.Show()

    def _create_status_bar(self):
        """
        Crea la barra de estado de la aplicación con dos campos.
        El primer campo es flexible para mensajes generales, y el segundo
        tiene un ancho fijo para mostrar el ID del libro actual.
        """
        self.status_bar = self.CreateStatusBar(2)
        if self.status_bar:
            # Configura los anchos de los campos: -1 para flexible, 200 para fijo
            self.status_bar.SetStatusWidths([-1, 200])
            self.status_bar.SetStatusText("Listo", 0)
            self.status_bar.SetStatusText("Libro ID: N/A", 1)
        else:
            print("Error: No se pudo crear la barra de estado.")

    def _create_views(self):
        """
        Crea las instancias de las vistas principales (LibraryView, BookDetailsView,
        ChapterListView) y las añade al AUI Manager, configurándolas inicialmente
        como ocultas. El estado inicial de visibilidad se gestiona en
        `on_show_library_as_center`.
        """
        # Crea las instancias de las vistas, pasando el panel base y el app_handler
        self.library_view = LibraryView(self.base_panel, self.app_handler)
        # Configura el callback para cuando se selecciona una tarjeta de libro
        self.library_view.set_on_book_card_selected_callback(self.on_library_book_selected)

        self.book_details_view = BookDetailsView(self.base_panel, self.app_handler)

        self.chapter_list_view = ChapterListView(self.base_panel, self.app_handler)
        # Configura el callback para cuando se selecciona un capítulo
        self.chapter_list_view.set_on_chapter_selected_callback(self.on_main_window_chapter_selected)

        # Añade los paneles al AUI Manager. Inicialmente se configuran como ocultos
        # o con un layout por defecto que será sobreescrito por la perspectiva guardada.
        self.aui_manager.AddPane(
            self.library_view,
            wx.aui.AuiPaneInfo().Name("library_view").Caption("Biblioteca").CenterPane().Hide()
        )
        self.aui_manager.AddPane(
            self.book_details_view,
            wx.aui.AuiPaneInfo().Name("book_details_view").Caption("Detalles del Libro").CenterPane().Hide()
        )
        self.aui_manager.AddPane(
            self.chapter_list_view,
            wx.aui.AuiPaneInfo().Name("chapter_list_view_pane").Caption("Capítulos").Left().Layer(0).Position(0).BestSize((300, -1)).Floatable(True).Resizable(True).Hide()
        )
        # El AuiNotebook para edición se crea y añade dinámicamente en _ensure_edit_notebook

        # Cargar libros en la biblioteca al inicio
        if self.library_view:
            self.library_view.load_books()

    def _ensure_edit_notebook(self):
        """
        Asegura que el AuiNotebook para la edición de capítulos y sus vistas
        internas existan. Si no existen, los crea y los añade al AUI Manager.
        """
        if self.edit_notebook is None:
            # Crea el AuiNotebook con estilos para pestañas en la parte superior
            self.edit_notebook = wx.aui.AuiNotebook(
                self.base_panel,
                style=wx.aui.AUI_NB_TOP | wx.aui.AUI_NB_TAB_SPLIT | wx.aui.AUI_NB_TAB_MOVE | wx.aui.AUI_NB_SCROLL_BUTTONS
            )
            # Crea las vistas internas y las añade como páginas al notebook
            self.chapter_content_view_notebook = ChapterContentView(self.edit_notebook, self.app_handler)
            self.edit_notebook.AddPage(self.chapter_content_view_notebook, "Contenido del Capítulo")

            self.abstract_idea_view_notebook = AbstractIdeaView(self.edit_notebook, self.app_handler)
            self.edit_notebook.AddPage(self.abstract_idea_view_notebook, "Idea Abstracta")

            self.concrete_idea_view_notebook = ConcreteIdeaView(self.edit_notebook, self.app_handler)
            self.edit_notebook.AddPage(self.concrete_idea_view_notebook, "Ideas Concretas")

            # Añade el notebook al AUI Manager, inicialmente oculto
            self.aui_manager.AddPane(
                self.edit_notebook,
                wx.aui.AuiPaneInfo().Name("edit_notebook_pane").Caption("Edición de Capítulo").CenterPane().Hide()
            )

    def _update_library_view_layout(self, is_sidebar: bool):
        """
        Actualiza el layout de la vista de biblioteca (LibraryView) para mostrarse
        como panel central o como barra lateral.

        Args:
            is_sidebar (bool): True si LibraryView debe ser una barra lateral,
                               False si debe ser el panel central.
        """
        if self.library_view:
            self.library_view.set_layout_mode(is_sidebar)
        # Resalta el libro activo si la vista de biblioteca se muestra como barra lateral
        active_book_to_highlight: Optional[int]
        active_book_to_highlight = self.current_book_id if is_sidebar else None
        self._highlight_active_book_in_library(active_book_to_highlight)

    def _highlight_active_book_in_library(self, active_book_id: Optional[int]):
        """
        Resalta (o des-resalta) la tarjeta del libro correspondiente en LibraryView.

        Args:
            active_book_id (Optional[int]): El ID del libro a resaltar. Si es None,
                                            ningún libro se resalta.
        """
        # Itera sobre las tarjetas de libro en LibraryView y aplica el estilo activo
        if self.library_view is not None and hasattr(self.library_view, 'book_card_panels'):
            card: Any
            for card in self.library_view.book_card_panels:
                card.set_active_style(card.book['id'] == active_book_id)

    def on_show_library_as_center(self, event: Optional[wx.CommandEvent] = None, force_clean: bool = False):
        """
        Configura la UI para mostrar la LibraryView como el panel central principal.
        Oculta los paneles de detalles del libro, lista de capítulos y edición.
        Pregunta al usuario si desea descartar cambios si los hay, a menos que
        `force_clean` sea True.

        Args:
            event (Optional[wx.CommandEvent]): Evento que disparó la acción (puede ser None).
            force_clean (bool): Si es True, fuerza la limpieza del estado 'dirty' sin preguntar.
        """
        # Si ya estamos en la vista de biblioteca y no se fuerza la limpieza, no hacer nada
        if self.current_app_state == STATE_LIBRARY_VIEW and not force_clean:
            self._update_library_view_layout(is_sidebar=False)
            self.aui_manager.Update()
            return
        # Si hay cambios sin guardar, preguntar antes de continuar (a menos que force_clean)
        if not force_clean and self.app_handler.is_application_dirty():
            if not self._confirm_discard_changes():
                return
        # Proceder a cambiar a la vista de biblioteca
        self.current_book_id = None
        self._clear_chapter_views_and_selection()
        if self.book_details_view:
            self.book_details_view.load_book_details(None)
        # Actualizar barra de estado
        if self.status_bar:
            self.status_bar.SetStatusText("Biblioteca", 0)
            self.status_bar.SetStatusText("Libro ID: N/A", 1)
        # Gestionar paneles AUI: Ocultar paneles de detalles, capítulos y edición
        library_pane_info: wx.aui.AuiPaneInfo
        library_pane_info = self.aui_manager.GetPane("library_view")
        book_details_pane_info: wx.aui.AuiPaneInfo
        book_details_pane_info = self.aui_manager.GetPane("book_details_view")
        chapter_list_pane_info: wx.aui.AuiPaneInfo
        chapter_list_pane_info = self.aui_manager.GetPane("chapter_list_view_pane")
        edit_notebook_pane_info: wx.aui.AuiPaneInfo
        edit_notebook_pane_info = self.aui_manager.GetPane("edit_notebook_pane")
        if book_details_pane_info.IsOk():
            book_details_pane_info.Hide()
        if chapter_list_pane_info.IsOk():
            chapter_list_pane_info.Hide()
        if edit_notebook_pane_info.IsOk():
            edit_notebook_pane_info.Hide()
        # Configurar LibraryView como panel central y mostrarlo
        if library_pane_info.IsOk():
            library_pane_info.CentrePane()
            library_pane_info.Show()
        else:
            print(f"ERROR CRÍTICO ({self.app_name}): El panel 'library_view' no existe en AUI Manager.")
        self._update_library_view_layout(is_sidebar=False)
        # Limpiar estado 'dirty' si se forzó o si ya no hay vistas 'dirty' activas
        if force_clean or self.app_handler.is_application_dirty():
            self.app_handler.set_dirty(False)
        # Actualizar barra de herramientas y título de la ventana
        self._update_toolbar_state(STATE_LIBRARY_VIEW)
        self.set_dirty_status_in_title(self.app_handler.is_application_dirty())
        # Aplicar cambios de AUI
        self.aui_manager.Update()

    def on_library_book_selected(self, selected_book_id: int):
        """
        Manejador para cuando un libro es seleccionado en la LibraryView.
        Configura la UI para mostrar los detalles del libro seleccionado,
        con LibraryView como panel lateral.

        Args:
            selected_book_id (int): El ID del libro que fue seleccionado.
        """
        # Si se selecciona el mismo libro y ya estamos en vista de detalles/edición,
        # volver a la vista de biblioteca.
        if selected_book_id == self.current_book_id and \
           (self.current_app_state == STATE_BOOK_DETAILS_VIEW or self.current_app_state == STATE_BOOK_EDIT_MODE):
            self.on_show_library_as_center(event=None)
            return
        # Si hay cambios, preguntar antes de cambiar de libro
        if self.app_handler.is_application_dirty():
            if not self._confirm_discard_changes():
                # Si el usuario cancela, re-resaltar el libro previamente activo
                self._highlight_active_book_in_library(self.current_book_id)
                return
        # Guardar estado anterior para manejo de paneles
        previous_app_state: int
        previous_app_state = self.current_app_state
        # Si estábamos en modo edición, ocultar paneles de edición y limpiar vistas de capítulo
        if previous_app_state == STATE_BOOK_EDIT_MODE:
            self._clear_chapter_views_and_selection()
            edit_notebook_pane: wx.aui.AuiPaneInfo
            edit_notebook_pane = self.aui_manager.GetPane("edit_notebook_pane")
            if edit_notebook_pane.IsOk():
                edit_notebook_pane.Hide()
            chapter_list_pane: wx.aui.AuiPaneInfo
            chapter_list_pane = self.aui_manager.GetPane("chapter_list_view_pane")
            if chapter_list_pane.IsOk():
                chapter_list_pane.Hide()
        # Actualizar ID del libro actual y cargar sus detalles
        self.current_book_id = selected_book_id
        book_details_data: Optional[Dict[str, Any]]
        book_details_data = self.app_handler.get_book_details(selected_book_id)
        book_title: str
        book_title = "Desconocido"
        if book_details_data:
            book_title = book_details_data.get('title', "Desconocido")
        # Actualizar barra de estado
        if self.status_bar:
            self.status_bar.SetStatusText(f"Libro: {book_title}", 0)
            self.status_bar.SetStatusText(f"Libro ID: {selected_book_id}", 1)
        # Cargar detalles en la vista correspondiente
        if self.book_details_view:
            self.book_details_view.load_book_details(selected_book_id)
        # Configurar paneles AUI para la vista de detalles del libro
        library_pane: wx.aui.AuiPaneInfo
        library_pane = self.aui_manager.GetPane("library_view")
        book_details_pane: wx.aui.AuiPaneInfo
        book_details_pane = self.aui_manager.GetPane("book_details_view")
        # Asegurarse que chapter_list y edit_notebook están ocultos
        chapter_list_pane: wx.aui.AuiPaneInfo
        chapter_list_pane = self.aui_manager.GetPane("chapter_list_view_pane")
        if chapter_list_pane.IsOk() and chapter_list_pane.IsShown():
            chapter_list_pane.Hide()
        if self.edit_notebook:
            edit_notebook_pane: wx.aui.AuiPaneInfo
            edit_notebook_pane = self.aui_manager.GetPane("edit_notebook_pane")
            if edit_notebook_pane.IsOk() and edit_notebook_pane.IsShown():
                edit_notebook_pane.Hide()
        # Configurar library_view como panel lateral y mostrarlo
        if library_pane.IsOk():
            library_pane.Left().Layer(0).Position(0).BestSize((250, -1)).Show()
        # Configurar book_details_view como panel central y mostrarlo
        if book_details_pane.IsOk():
            book_details_pane.CentrePane().Show()
        # Actualizar layout de LibraryView y barra de herramientas
        self._update_library_view_layout(is_sidebar=True)
        self._update_toolbar_state(STATE_BOOK_DETAILS_VIEW)
        # Al cargar un nuevo libro, se resetea el estado 'dirty'
        self.app_handler.set_dirty(False)
        self.set_dirty_status_in_title(False)
        # Aplicar cambios de AUI
        self.aui_manager.Update()

    def on_edit_book_tool_click(self, event: Optional[wx.CommandEvent]):
        """
        Manejador para el botón/menú "Editar Libro".
        Configura la UI para el modo de edición de capítulos, mostrando
        la lista de capítulos y el notebook de edición. Pregunta al usuario
        si desea guardar los cambios en los detalles del libro si los hay.

        Args:
            event (Optional[wx.CommandEvent]): Evento que disparó la acción.
        """
        if not self.current_book_id:
            wx.MessageBox("Por favor, seleccione un libro para editar sus capítulos.",
                          "Sin Libro Seleccionado", wx.OK | wx.ICON_INFORMATION, self)
            return
        # Si estamos en vista de detalles y hay cambios, preguntar si guardar
        if self.current_app_state == STATE_BOOK_DETAILS_VIEW and \
           self.book_details_view and self.book_details_view.is_dirty():
            dlg_bd: wx.MessageDialog
            dlg_bd = wx.MessageDialog(self,
                                      "Hay cambios sin guardar en los detalles del libro. ¿Desea guardarlos antes de pasar a editar los capítulos?",
                                      "Guardar Detalles del Libro",
                                      wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            result: int
            result = dlg_bd.ShowModal()
            dlg_bd.Destroy()
            if result == wx.ID_YES:
                # Intentar guardar los detalles del libro
                if self.book_details_view and not self.book_details_view.save_changes():
                    wx.MessageBox("No se pudieron guardar los detalles del libro. No se puede continuar a la edición de capítulos.",
                                  "Error de Guardado", wx.OK | wx.ICON_ERROR, self)
                    return
            elif result == wx.ID_CANCEL:
                return
            else:
                # Descartar cambios en BookDetailsView
                if self.book_details_view:
                    self.book_details_view._set_view_dirty(False)
                self._reevaluate_global_dirty_state()
        # Asegurar que el notebook de edición y sus paneles existan
        self._ensure_edit_notebook()
        # Configurar paneles AUI para el modo de edición
        library_pane: wx.aui.AuiPaneInfo
        library_pane = self.aui_manager.GetPane("library_view")
        book_details_pane: wx.aui.AuiPaneInfo
        book_details_pane = self.aui_manager.GetPane("book_details_view")
        chapter_list_pane: wx.aui.AuiPaneInfo
        chapter_list_pane = self.aui_manager.GetPane("chapter_list_view_pane")
        edit_notebook_pane: wx.aui.AuiPaneInfo
        edit_notebook_pane = self.aui_manager.GetPane("edit_notebook_pane")
        # Ocultar paneles de biblioteca y detalles del libro
        if library_pane.IsOk():
            library_pane.Hide()
        if book_details_pane.IsOk():
            book_details_pane.Hide()
        # Mostrar lista de capítulos a la izquierda
        if chapter_list_pane.IsOk():
            chapter_list_pane.Left().Layer(0).Position(0).BestSize((300, -1)).Show()
        # Cargar capítulos y configurar vistas de edición (inicialmente sin capítulo seleccionado)
        self._update_notebook_pages_state(False)
        if self.chapter_list_view:
            self.chapter_list_view.load_chapters(self.current_book_id)
        if self.edit_notebook:
            self.edit_notebook.Layout()
        # Mostrar notebook de edición como panel central
        if edit_notebook_pane.IsOk():
            if not edit_notebook_pane.IsShown():
                edit_notebook_pane.CentrePane().Show()
        # Aplicar cambios AUI
        self.aui_manager.Update()
        # Seleccionar la primera pestaña del notebook de edición si existe
        if self.edit_notebook and self.edit_notebook.GetPageCount() > 0:
            self.edit_notebook.SetSelection(0)
        # Actualizar barra de herramientas y título
        self._update_toolbar_state(STATE_BOOK_EDIT_MODE)
        self.set_dirty_status_in_title(self.app_handler.is_application_dirty())

    def _update_notebook_pages_state(self, chapter_is_selected: bool):
        """
        Habilita o deshabilita el AuiNotebook de edición y sus vistas internas
        según si un capítulo está seleccionado.

        Args:
            chapter_is_selected (bool): True si un capítulo está seleccionado, False si no.
        """
        if not self.edit_notebook:
            return
        # Habilita/deshabilita el notebook completo
        self.edit_notebook.Enable(chapter_is_selected)
        # Habilita/deshabilita vistas individuales dentro del notebook
        if self.chapter_content_view_notebook is not None:
            self.chapter_content_view_notebook.enable_view(chapter_is_selected)
        if self.abstract_idea_view_notebook is not None:
            self.abstract_idea_view_notebook.enable_view(chapter_is_selected)
        if self.concrete_idea_view_notebook is not None:
            self.concrete_idea_view_notebook.enable_view(chapter_is_selected)

    def _load_chapter_data_into_edit_views(self, chapter_id: Optional[int]):
        """
        Carga los datos del capítulo especificado en las vistas correspondientes
        del notebook de edición. Si chapter_id es None, limpia las vistas.

        Args:
            chapter_id (Optional[int]): El ID del capítulo a cargar, o None para limpiar.
        """
        if not self.edit_notebook:
            self._ensure_edit_notebook()
        # Cargar datos en cada vista del notebook
        if self.chapter_content_view_notebook is not None:
            self.chapter_content_view_notebook.load_content(chapter_id)
        if self.abstract_idea_view_notebook is not None:
            self.abstract_idea_view_notebook.load_idea(chapter_id)
        if self.concrete_idea_view_notebook is not None:
            self.concrete_idea_view_notebook.load_ideas(chapter_id)

    def on_main_window_chapter_selected(self, chapter_id: Optional[int]):
        """
        Manejador para cuando un capítulo es seleccionado en ChapterListView.
        Carga los datos del capítulo en las vistas de edición, actualiza su estado
        y maneja los cambios pendientes en el capítulo anterior.

        Args:
            chapter_id (Optional[int]): El ID del capítulo seleccionado, o None si se deselecciona.
        """
        current_chapter_views_dirty: bool
        current_chapter_views_dirty = False
        # Comprobar si hay cambios en las vistas del capítulo actual *antes* de cambiar
        if self.current_chapter_id is not None and chapter_id != self.current_chapter_id:
            if self.chapter_content_view_notebook and self.chapter_content_view_notebook.is_dirty():
                current_chapter_views_dirty = True
            if not current_chapter_views_dirty and \
               self.abstract_idea_view_notebook and self.abstract_idea_view_notebook.is_dirty():
                current_chapter_views_dirty = True
        # Si hay cambios en las vistas del capítulo anterior, preguntar si guardar
        if current_chapter_views_dirty:
            prev_chap_details: Optional[Dict[str, Any]]
            prev_chap_details = self.app_handler.get_chapter_details(self.current_chapter_id) if self.current_chapter_id else None
            prev_chap_title: str
            prev_chap_title = f"'{prev_chap_details['title']}'" if prev_chap_details and prev_chap_details.get('title') else "el capítulo anterior"
            dlg_chap: wx.MessageDialog
            dlg_chap = wx.MessageDialog(self,
                                        f"Hay cambios sin guardar en {prev_chap_title}. ¿Desea guardarlos antes de cambiar de capítulo?",
                                        "Guardar Cambios del Capítulo",
                                        wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            result: int
            result = dlg_chap.ShowModal()
            dlg_chap.Destroy()
            if result == wx.ID_YES:
                save_ok: bool
                save_ok = True
                # Intentar guardar cambios en las vistas del capítulo
                if self.chapter_content_view_notebook and self.chapter_content_view_notebook.is_dirty():
                    if not self.chapter_content_view_notebook.save_changes():
                        save_ok = False
                if self.abstract_idea_view_notebook and self.abstract_idea_view_notebook.is_dirty():
                     if not self.abstract_idea_view_notebook.save_changes():
                        save_ok = False
                if not save_ok:
                    wx.MessageBox("No se pudieron guardar todos los cambios del capítulo. El cambio de capítulo se ha cancelado.",
                                  "Error de Guardado", wx.OK | wx.ICON_ERROR, self)
                    if self.chapter_list_view:
                        # Re-seleccionar el capítulo anterior en la lista si el guardado falló
                        self.chapter_list_view.select_chapter_by_id(self.current_chapter_id)
                    return
            elif result == wx.ID_CANCEL:
                if self.chapter_list_view:
                    # Re-seleccionar el capítulo anterior si el usuario canceló
                    self.chapter_list_view.select_chapter_by_id(self.current_chapter_id)
                return
            else:
                # Descartar cambios en las vistas del capítulo
                if self.chapter_content_view_notebook:
                    self.chapter_content_view_notebook._set_view_dirty(False)
                if self.abstract_idea_view_notebook:
                    self.abstract_idea_view_notebook._set_view_dirty(False)
        # Actualizar el ID del capítulo actual y cargar sus datos en las vistas de edición
        self.current_chapter_id = chapter_id
        self._load_chapter_data_into_edit_views(chapter_id)
        # Habilitar/deshabilitar vistas del notebook según si hay capítulo seleccionado
        self._update_notebook_pages_state(chapter_id is not None)
        # Reevaluar el estado 'dirty' global después del cambio de capítulo
        self._reevaluate_global_dirty_state()

    def _reevaluate_global_dirty_state(self):
        """
        Reevalúa el estado 'dirty' global de la aplicación basándose en el estado
        de las vistas activas y notifica a AppHandler. También actualiza el título.
        """
        is_app_dirty: bool
        is_app_dirty = False
        # Comprobar BookDetailsView si está en ese estado y está sucio
        if self.current_app_state == STATE_BOOK_DETAILS_VIEW:
            if self.book_details_view and self.book_details_view.is_dirty():
                is_app_dirty = True
        # Comprobar vistas del notebook de edición si está en ese estado
        elif self.current_app_state == STATE_BOOK_EDIT_MODE:
            if self.edit_notebook:
                # Comprobar si alguna de las vistas del notebook está sucia
                if self.chapter_content_view_notebook and self.chapter_content_view_notebook.is_dirty():
                    is_app_dirty = True
                if not is_app_dirty and self.abstract_idea_view_notebook and self.abstract_idea_view_notebook.is_dirty():
                    is_app_dirty = True
                # ConcreteIdeaView actualiza el dirty global directamente.
                # Si ninguna vista específica está sucia pero app_handler dice que sí, confiar en app_handler.
                if not is_app_dirty and self.app_handler.is_application_dirty():
                     is_app_dirty = True
        # Si ninguna vista específica está sucia pero app_handler dice que sí, confiar en app_handler
        if not is_app_dirty and self.app_handler.is_application_dirty():
             is_app_dirty = True
        # Actualizar el estado 'dirty' en AppHandler y el título de la ventana
        self.app_handler.set_dirty(is_app_dirty)

    def on_save_current_book_tool_click(self, event: Optional[wx.CommandEvent]):
        """
        Manejador para el botón/menú "Guardar". Guarda los cambios pendientes
        en la vista activa (detalles del libro o vistas de edición de capítulo).

        Args:
            event (Optional[wx.CommandEvent]): Evento que disparó la acción.
        """
        if not self.current_book_id:
            return
        all_saves_successful: bool
        all_saves_successful = True
        something_was_dirty_and_saved: bool
        something_was_dirty_and_saved = False
        # Guardar detalles del libro si estamos en esa vista y está sucio
        if self.current_app_state == STATE_BOOK_DETAILS_VIEW:
            if self.book_details_view and self.book_details_view.is_dirty():
                if not self.book_details_view.save_changes():
                    all_saves_successful = False
                else:
                    something_was_dirty_and_saved = True
        # Guardar contenido/idea abstracta del capítulo si estamos en modo edición
        elif self.current_app_state == STATE_BOOK_EDIT_MODE:
            if self.current_chapter_id:
                if self.chapter_content_view_notebook and self.chapter_content_view_notebook.is_dirty():
                    if not self.chapter_content_view_notebook.save_changes():
                        all_saves_successful = False
                    else:
                        something_was_dirty_and_saved = True
                if self.abstract_idea_view_notebook and self.abstract_idea_view_notebook.is_dirty():
                    if not self.abstract_idea_view_notebook.save_changes():
                        all_saves_successful = False
                    else:
                        something_was_dirty_and_saved = True
            # ConcreteIdeaView ya guarda a través de AppHandler y marca dirty global.
            # Si solo ConcreteIdeaView hizo cambios, app_handler.is_application_dirty() será true.
            if not something_was_dirty_and_saved and self.app_handler.is_application_dirty():
                something_was_dirty_and_saved = True
        # Después de intentar todos los guardados
        if all_saves_successful:
            if something_was_dirty_and_saved:
                pass
            # Si todos los guardados fueron exitosos (o no había nada que guardar desde aquí),
            # y app_handler dice que está dirty, es porque las vistas limpiaron su dirty local
            # pero el dirty global aún no se limpió.
            self.app_handler.set_dirty(False)
        else:
            wx.MessageBox("Algunos cambios no pudieron guardarse. Revise los mensajes de error si los hubo.",
                          "Error de Guardado", wx.OK | wx.ICON_ERROR, self)
        # Reevaluar y actualizar título
        self._reevaluate_global_dirty_state()

    def on_back_to_library_tool_click(self, event: Optional[wx.CommandEvent]):
        """
        Manejador para el botón/menú "Volver a la Biblioteca".
        Llama a `on_show_library_as_center`.

        Args:
            event (Optional[wx.CommandEvent]): Evento que disparó la acción.
        """
        self.on_show_library_as_center(event)

    def on_undo_tool_click(self, event: Optional[wx.CommandEvent]):
        """
        Manejador para la acción Deshacer en el control de texto con foco.
        Solo actúa si el control con foco es un `wx.TextCtrl` editable y
        la aplicación está en el contexto de edición de contenido de capítulo.

        Args:
            event (Optional[wx.CommandEvent]): Evento que disparó la acción.
        """
        target: Optional[wx.Window]
        target = wx.Window.FindFocus()
        can_perform_action: bool
        can_perform_action = False
        # Verificar si el control con foco es un TextCtrl editable y soporta Undo
        if isinstance(target, wx.TextCtrl) and target.CanUndo() and target.IsEditable():
            # Adicionalmente, verificar el contexto de la aplicación (modo edición de capítulo, pestaña de contenido)
            if self.current_app_state == STATE_BOOK_EDIT_MODE:
                if self.edit_notebook:
                    current_page_index: int
                    current_page_index = self.edit_notebook.GetSelection()
                    if current_page_index != wx.NOT_FOUND:
                        page_window: Optional[wx.Window]
                        page_window = self.edit_notebook.GetPage(current_page_index)
                        if page_window == self.chapter_content_view_notebook:
                             if self.chapter_content_view_notebook and self.chapter_content_view_notebook.is_editable():
                                can_perform_action = True
        # Si la acción es posible, ejecutar Undo
        if can_perform_action and isinstance(target, wx.TextCtrl):
            target.Undo()
        else:
            wx.Bell()

    def on_redo_tool_click(self, event: Optional[wx.CommandEvent]):
        """
        Manejador para la acción Rehacer en el control de texto con foco.
        Solo actúa si el control con foco es un `wx.TextCtrl` editable y
        la aplicación está en el contexto de edición de contenido de capítulo.

        Args:
            event (Optional[wx.CommandEvent]): Evento que disparó la acción.
        """
        target: Optional[wx.Window]
        target = wx.Window.FindFocus()
        can_perform_action: bool
        can_perform_action = False
        # Verificar si el control con foco es un TextCtrl editable y soporta Redo
        if isinstance(target, wx.TextCtrl) and target.CanRedo() and target.IsEditable():
            # Adicionalmente, verificar el contexto de la aplicación (modo edición de capítulo, pestaña de contenido)
            if self.current_app_state == STATE_BOOK_EDIT_MODE:
                if self.edit_notebook:
                    current_page_index: int
                    current_page_index = self.edit_notebook.GetSelection()
                    if current_page_index != wx.NOT_FOUND:
                        page_window: Optional[wx.Window]
                        page_window = self.edit_notebook.GetPage(current_page_index)
                        if page_window == self.chapter_content_view_notebook:
                            if self.chapter_content_view_notebook and self.chapter_content_view_notebook.is_editable():
                                can_perform_action = True
        # Si la acción es posible, ejecutar Redo
        if can_perform_action and isinstance(target, wx.TextCtrl):
            target.Redo()
        else:
            wx.Bell()

    def _clear_chapter_views_and_selection(self):
        """
        Limpia el ID del capítulo actual, y las vistas relacionadas con la edición
        de capítulos (ChapterListView y las pestañas del edit_notebook).
        """
        self.current_chapter_id = None
        # Limpiar y deshabilitar lista de capítulos
        if self.chapter_list_view:
            self.chapter_list_view.load_chapters(None)
        # Limpiar y deshabilitar vistas en el notebook de edición
        if self.edit_notebook:
            self._load_chapter_data_into_edit_views(None)
            self._update_notebook_pages_state(False)

    def _confirm_discard_changes(self) -> bool:
        """
        Si hay cambios sin guardar en la aplicación, pregunta al usuario si desea
        descartarlos. Si el usuario acepta descartar, limpia el estado 'dirty'
        de las vistas relevantes y el estado 'dirty' global.

        Returns:
            bool: True si el usuario desea descartar los cambios o no había cambios.
                  False si el usuario cancela la acción (no desea descartar).
        """
        if not self.app_handler.is_application_dirty():
            return True
        # Construir mensaje de advertencia
        book_title_addon: str
        book_title_addon = ""
        if self.current_book_id:
            book_data: Optional[Dict[str, Any]]
            book_data = self.app_handler.get_book_details(self.current_book_id)
            if book_data and book_data.get('title'):
                book_title_str: str
                book_title_str = str(book_data['title'])
                book_title_addon = f" en '{book_title_str}'"
        msg: str
        msg = f"Hay cambios sin guardar{book_title_addon}. ¿Desea descartarlos y continuar?"
        # Mostrar diálogo de confirmación
        dlg: wx.MessageDialog
        dlg = wx.MessageDialog(self, msg, "Descartar Cambios",
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        result: int
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            # Limpiar el estado 'dirty' de las vistas específicas si están sucias
            if self.current_app_state == STATE_BOOK_DETAILS_VIEW and \
               self.book_details_view and self.book_details_view.is_dirty():
                self.book_details_view._set_view_dirty(False)
            elif self.current_app_state == STATE_BOOK_EDIT_MODE:
                if self.chapter_content_view_notebook and self.chapter_content_view_notebook.is_dirty():
                    self.chapter_content_view_notebook._set_view_dirty(False)
                if self.abstract_idea_view_notebook and self.abstract_idea_view_notebook.is_dirty():
                    self.abstract_idea_view_notebook._set_view_dirty(False)
            # Limpiar el estado 'dirty' global de la aplicación
            self.app_handler.set_dirty(False)
            return True
        return False

    def on_maximize(self, event: wx.MaximizeEvent):
        """
        Manejador para el evento de maximizar la ventana.
        Asegura que el layout de AUI se actualice correctamente.

        Args:
            event (wx.MaximizeEvent): El evento de maximización.
        """
        self.Layout()
        # Llama a aui_manager.Update después del layout del frame
        wx.CallAfter(self.aui_manager.Update)
        event.Skip()

    def _get_config_path(self, filename: str) -> str:
        """
        Construye la ruta a un archivo de configuración dentro de un directorio
        específico de la aplicación en el directorio home del usuario.
        Crea el directorio de configuración si no existe.

        Args:
            filename (str): El nombre del archivo de configuración (ej. "perspective.txt").

        Returns:
            str: La ruta absoluta al archivo de configuración.
        """
        home_dir: str
        home_dir = os.path.expanduser("~")
        config_dir: str
        config_dir = os.path.join(home_dir, self.CONFIG_DIR_NAME)
        # Crea el directorio de configuración si no existe
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, filename)

    def _get_perspective_string_from_file(self) -> str:
        """
        Lee la cadena de perspectiva AUI guardada desde un archivo de configuración.

        Returns:
            str: La cadena de perspectiva leída, o una cadena vacía si el archivo
                 no existe o hay un error al leerlo.
        """
        state_file_path: str
        state_file_path = self._get_config_path(self.PERSPECTIVE_FILE_NAME)
        perspective_str: str
        perspective_str = ""
        # Intenta leer el archivo de perspectiva
        if os.path.exists(state_file_path):
            try:
                with open(state_file_path, 'r', encoding='utf-8') as f:
                    perspective_str = f.read()
            except Exception as e:
                print(f"Error al leer archivo de perspectiva AUI ({state_file_path}): {e}")
        return perspective_str

    def _save_state(self):
        """
        Guarda la perspectiva actual del AUI Manager a un archivo de configuración.
        """
        perspective_str: str
        perspective_str = ""
        try:
            # Obtiene la cadena de perspectiva del AUI Manager
            perspective_str = self.aui_manager.SavePerspective()
        except Exception as e_persp:
            print(f"Advertencia: No se pudo obtener la perspectiva AUI para guardar: {e_persp}")
            return
        state_file_path: str
        state_file_path = self._get_config_path(self.PERSPECTIVE_FILE_NAME)
        # Intenta escribir la cadena de perspectiva en el archivo
        try:
            if perspective_str:
                with open(state_file_path, 'w', encoding='utf-8') as f:
                    f.write(perspective_str)
        except IOError as e:
            print(f"Error al escribir archivo de perspectiva AUI ({state_file_path}): {e}")
        except Exception as e_gen:
            print(f"Error inesperado al guardar archivo de perspectiva AUI ({state_file_path}): {e_gen}")

    def _load_state(self):
        """
        Carga la perspectiva del AUI Manager desde un archivo de configuración, si existe.
        Si hay un error al cargar o procesar la perspectiva, se usa el layout por defecto
        y se intenta eliminar el archivo de perspectiva corrupto.
        """
        perspective_str: str
        perspective_str = self._get_perspective_string_from_file()
        if perspective_str:
            try:
                # Cargar la perspectiva. update=True aplica los cambios inmediatamente.
                self.aui_manager.LoadPerspective(perspective_str, update=True)
            except Exception as e:
                print(f"Error al cargar o procesar la perspectiva AUI guardada: {e}. Se usará el layout por defecto.")
                # Si la perspectiva es inválida, intentar eliminar el archivo para evitar errores futuros
                state_file_path: str
                state_file_path = self._get_config_path(self.PERSPECTIVE_FILE_NAME)
                if os.path.exists(state_file_path):
                    try:
                        os.remove(state_file_path)
                        print(f"Archivo de perspectiva AUI corrupto eliminado: {state_file_path}")
                    except OSError as e_remove:
                        print(f"Advertencia: No se pudo eliminar el archivo de perspectiva AUI corrupto '{state_file_path}': {e_remove}")
        # Asegurar que el estado de los ítems del menú "Ver" refleje la visibilidad de los paneles
        wx.CallAfter(self._update_view_menu_items_state)
        # Forzar una actualización final de AUI y layout del frame
        wx.CallAfter(self.aui_manager.Update)
        wx.CallAfter(self.Layout)

    def on_menu_new_book(self, event: Optional[wx.CommandEvent]):
        """
        Manejador para el ítem de menú "Nuevo Libro" o la herramienta correspondiente.
        Muestra el diálogo `NewBookDialog` para crear un nuevo libro.
        Si hay cambios sin guardar, pide confirmación para descartarlos.

        Args:
            event (Optional[wx.CommandEvent]): Evento que disparó la acción.
        """
        # Si hay cambios sin guardar, preguntar antes de crear un nuevo libro
        if self.app_handler.is_application_dirty():
            if not self._confirm_discard_changes():
                return
        # Crear y mostrar el diálogo para nuevo libro
        dlg: NewBookDialog
        dlg = NewBookDialog(self, self.app_handler, dialog_title=f"Nuevo Libro - {self.app_name}")
        if dlg.ShowModal() == wx.ID_OK:
            book_data: Dict[str, str]
            book_data = dlg.get_book_data()
            if book_data:
                # Crear el libro a través del AppHandler
                new_book_id: Optional[int]
                new_book_id = self.app_handler.create_new_book(**book_data)
                if new_book_id:
                    # Limpiar el estado dirty después de la creación exitosa
                    self.app_handler.set_dirty(False)
                    self.set_dirty_status_in_title(False)
                    # Recargar la biblioteca y seleccionar el nuevo libro
                    if self.library_view:
                        self.library_view.load_books()
                    self.on_library_book_selected(new_book_id)
        dlg.Destroy()

    def on_menu_exit(self, event: Optional[wx.CommandEvent]):
        """
        Manejador para el ítem de menú Salir.
        Cierra la ventana principal, lo que activará el evento `on_close`.

        Args:
            event (Optional[wx.CommandEvent]): Evento que disparó la acción.
        """
        self.Close(True)

    def _toggle_pane_visibility_and_menu(self, pane_name: str, menu_item: wx.MenuItem, event: wx.CommandEvent):
        """
        Alterna la visibilidad de un panel AUI y actualiza el estado 'check'
        del ítem de menú correspondiente.

        Args:
            pane_name (str): El nombre del panel AUI a alternar.
            menu_item (wx.MenuItem): El ítem de menú asociado al panel.
            event (wx.CommandEvent): El evento de menú.
        """
        pane: wx.aui.AuiPaneInfo
        pane = self.aui_manager.GetPane(pane_name)
        if pane.IsOk():
            is_shown: bool
            is_shown = pane.IsShown()
            # Alternar la visibilidad del panel
            pane.Show(not is_shown)
            # Aplicar cambios de AUI y re-layout del frame
            self.aui_manager.Update()
            self.Layout()
        else:
            print(f"Advertencia ({self.app_name}): No se encontró el panel AUI '{pane_name}' para alternar visibilidad.")
        event.Skip()

    def _update_view_menu_items_state(self):
        """
        Actualiza el estado 'check' de los ítems del menú "Ver" para que
        reflejen la visibilidad actual de los paneles AUI correspondientes.
        También habilita/deshabilita los ítems si el panel AUI no existe.
        """
        # Mapeo de nombres de paneles AUI a sus ítems de menú correspondientes
        pane_menu_map: Dict[str, Optional[wx.MenuItem]]
        pane_menu_map = {
            "library_view": self.toggle_library_view_menu_item,
            "chapter_list_view_pane": self.toggle_chapter_list_view_menu_item,
            "book_details_view": self.toggle_book_details_view_menu_item,
            "edit_notebook_pane": self.toggle_edit_notebook_menu_item
        }
        pane_name: str
        menu_item: Optional[wx.MenuItem]
        # Itera sobre el mapeo y actualiza el estado de cada ítem de menú
        for pane_name, menu_item in pane_menu_map.items():
            if menu_item:
                pane: wx.aui.AuiPaneInfo
                pane = self.aui_manager.GetPane(pane_name)
                # Habilitar el ítem de menú solo si el panel existe
                menu_item.Enable(pane.IsOk())
                if pane.IsOk():
                    # Marcar el ítem si el panel está visible
                    menu_item.Check(pane.IsShown())
                else:
                    # Desmarcar si el panel no existe
                    menu_item.Check(False)

    def on_update_ui_view_menu(self, event: wx.UpdateUIEvent):
        """
        Manejador para el evento EVT_UPDATE_UI del menú "Ver".
        Llama a `_update_view_menu_items_state` para actualizar el estado
        de los check ítems según la visibilidad actual de los paneles.

        Args:
            event (wx.UpdateUIEvent): El evento de actualización de UI.
        """
        self._update_view_menu_items_state()
        event.Skip()

    def on_close(self, event: wx.CloseEvent):
        """
        Manejador para el evento de cierre de la ventana principal.
        Guarda el estado de la perspectiva AUI. Si hay cambios sin guardar,
        pregunta al usuario si desea descartarlos antes de cerrar.
        Si el usuario cancela, se veta el cierre.

        Args:
            event (wx.CloseEvent): El evento de cierre.
        """
        self._save_state()
        can_destroy: bool
        can_destroy = True
        # Si hay cambios sin guardar, preguntar al usuario
        if self.app_handler.is_application_dirty():
            if not self._confirm_discard_changes():
                can_destroy = False
        # Si se puede destruir (no hay cambios o el usuario los descartó)
        if can_destroy:
            if self.aui_manager:
                self.aui_manager.UnInit()
            self.Destroy()
        elif event:
            # Si el usuario canceló, vetar el evento de cierre
            event.Veto()

    def set_dirty_status_in_title(self, is_dirty: bool):
        """
        Actualiza el título de la ventana para incluir un asterisco (*) si hay
        cambios sin guardar. El título base también refleja el libro actual si uno
        está cargado en modo de detalle o edición.

        Args:
            is_dirty (bool): True si hay cambios sin guardar, False en caso contrario.
        """
        base_title_for_app: str
        base_title_for_app = self.app_name
        final_title_to_display: str
        final_title_to_display = base_title_for_app
        # Añadir nombre del libro si estamos en vista de detalles o edición y hay un libro seleccionado
        if self.current_book_id and \
           (self.current_app_state == STATE_BOOK_DETAILS_VIEW or self.current_app_state == STATE_BOOK_EDIT_MODE):
            book_details: Optional[Dict[str, Any]]
            book_details = self.app_handler.get_book_details(self.current_book_id)
            if book_details and book_details.get('title'):
                book_title_str: str
                book_title_str = str(book_details['title'])
                final_title_to_display = f"{base_title_for_app} - {book_title_str}"
        # Añadir asterisco si hay cambios sin guardar
        if is_dirty:
            self.SetTitle(final_title_to_display + "*")
        else:
            self.SetTitle(final_title_to_display)