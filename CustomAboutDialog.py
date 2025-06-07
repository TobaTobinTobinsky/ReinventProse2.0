# -*- coding: utf-8 -*-
"""
File Name: CustomAboutDialog.py
Description: Define una ventana emergente "Acerca de" personalizada (wx.Frame)
             para la aplicación ReinventProse 2.0. Implementa un diseño
             específico con logo y un wx.Notebook, asegurando que los
             TextCtrl internos permitan desplazamiento aunque sean de solo lectura.
Author: AutoDoc AI
Date: 07/06/2025
Version: 0.0.1
License: MIT License
"""

import wx
import wx.adv
from typing import List, Optional, Tuple, Any
import os
import sys

# Nombre del archivo de imagen para el logo
LOGO_IMAGE_FILENAME: str = "app_icon.ico"
# Tamaño deseado para el logo en píxeles
LOGO_SIZE: wx.Size = wx.Size(100, 100)

class ReinventProseAboutInfo:
    """
    Clase contenedora de datos para la ventana "Acerca de" personalizada.

    Almacena la información básica de la aplicación (nombre, versión, copyright,
    descripción, etc.) y listas de colaboradores en diferentes roles.
    """
    def __init__(self):
        """
        Constructor de la clase ReinventProseAboutInfo.

        Inicializa un objeto wx.adv.AboutDialogInfo interno y una lista
        para colaboradores personalizados.
        """
        # Objeto wx.adv.AboutDialogInfo para almacenar datos estándar
        self._wx_about_info: wx.adv.AboutDialogInfo
        self._wx_about_info = wx.adv.AboutDialogInfo()
        # Lista para almacenar colaboradores personalizados (nombre, contribución)
        self._collaborators: List[Tuple[str, Optional[str]]]
        self._collaborators = []

    def SetName(self, name: str):
        """
        Establece el nombre de la aplicación.

        Args:
            name (str): El nombre de la aplicación.
        """
        self._wx_about_info.SetName(name)

    def GetName(self) -> str:
        """
        Obtiene el nombre de la aplicación.

        Returns:
            str: El nombre de la aplicación.
        """
        name: str
        name = self._wx_about_info.GetName()
        return name

    def SetVersion(self, version: str):
        """
        Establece la versión de la aplicación.

        Args:
            version (str): La cadena de versión.
        """
        self._wx_about_info.SetVersion(version)

    def GetVersion(self) -> str:
        """
        Obtiene la versión de la aplicación.

        Returns:
            str: La cadena de versión.
        """
        version: str
        version = self._wx_about_info.GetVersion()
        return version

    def SetDescription(self, description: str):
        """
        Establece la descripción de la aplicación.

        Args:
            description (str): La descripción detallada.
        """
        self._wx_about_info.SetDescription(description)

    def GetDescription(self) -> str:
        """
        Obtiene la descripción de la aplicación.

        Returns:
            str: La descripción detallada.
        """
        description: str
        description = self._wx_about_info.GetDescription()
        return description

    def SetCopyright(self, copyright_text: str):
        """
        Establece el texto de copyright.

        Args:
            copyright_text (str): La cadena de copyright.
        """
        self._wx_about_info.SetCopyright(copyright_text)

    def GetCopyright(self) -> str:
        """
        Obtiene el texto de copyright.

        Returns:
            str: La cadena de copyright.
        """
        copyright_text: str
        copyright_text = self._wx_about_info.GetCopyright()
        return copyright_text

    def SetLicence(self, licence_text: str):
        """
        Establece el texto de la licencia (alias para SetLicense).

        Args:
            licence_text (str): El texto completo de la licencia.
        """
        self._wx_about_info.SetLicence(licence_text)

    def SetLicense(self, licence_text: str):
        """
        Establece el texto de la licencia.

        Args:
            licence_text (str): El texto completo de la licencia.
        """
        self._wx_about_info.SetLicense(licence_text)

    def GetLicence(self) -> str:
        """
        Obtiene el texto de la licencia (alias para GetLicense).

        Returns:
            str: El texto completo de la licencia.
        """
        licence_text: str
        licence_text = self._wx_about_info.GetLicence()
        return licence_text

    def GetLicense(self) -> str:
        """
        Obtiene el texto de la licencia.

        Returns:
            str: El texto completo de la licencia.
        """
        license_text: str
        license_text = self._wx_about_info.GetLicense()
        return license_text

    def HasLicence(self) -> bool:
        """
        Comprueba si se ha establecido un texto de licencia (alias para HasLicense).

        Returns:
            bool: True si hay texto de licencia, False en caso contrario.
        """
        has_licence: bool
        has_licence = self._wx_about_info.HasLicence()
        return has_licence

    def HasLicense(self) -> bool:
        """
        Comprueba si se ha establecido un texto de licencia.

        Returns:
            bool: True si hay texto de licencia, False en caso contrario.
        """
        has_license: bool
        has_license = self._wx_about_info.HasLicense()
        return has_license

    def SetWebSite(self, url: str, desc: Optional[str] = None):
        """
        Establece la URL y descripción del sitio web.

        Args:
            url (str): La URL del sitio web.
            desc (Optional[str]): La descripción del sitio web. Si es None, se usa la URL.
        """
        actual_desc: str
        if desc is None:
            actual_desc = url
        else:
            actual_desc = desc
        self._wx_about_info.SetWebSite(url, actual_desc)

    def GetWebSiteURL(self) -> str:
        """
        Obtiene la URL del sitio web.

        Returns:
            str: La URL del sitio web.
        """
        url: str
        url = self._wx_about_info.GetWebSiteURL()
        return url

    def GetWebSiteDescription(self) -> str:
        """
        Obtiene la descripción del sitio web.

        Returns:
            str: La descripción del sitio web.
        """
        description: str
        description = self._wx_about_info.GetWebSiteDescription()
        return description

    def GetWebSite(self) -> Optional[Tuple[str, str]]:
        """
        Obtiene la URL y descripción del sitio web como una tupla.

        Returns:
            Optional[Tuple[str, str]]: Una tupla (url, descripción) si hay sitio web,
                                       None en caso contrario.
        """
        has_site: bool
        has_site = self._wx_about_info.HasWebSite()
        if has_site:
            url: str
            url = self._wx_about_info.GetWebSiteURL()
            desc: str
            desc = self._wx_about_info.GetWebSiteDescription()
            result_tuple: Tuple[str, str]
            result_tuple = (url, desc)
            return result_tuple
        else:
            return None

    def HasWebSite(self) -> bool:
        """
        Comprueba si se ha establecido un sitio web.

        Returns:
            bool: True si hay sitio web, False en caso contrario.
        """
        has_website: bool
        has_website = self._wx_about_info.HasWebSite()
        return has_website

    def SetIcon(self, icon: wx.Icon):
        """
        Establece el icono asociado a los datos (no el icono de la ventana).

        Args:
            icon (wx.Icon): El objeto wx.Icon.
        """
        self._wx_about_info.SetIcon(icon)

    def GetIcon(self) -> wx.Icon:
        """
        Obtiene el icono asociado a los datos.

        Returns:
            wx.Icon: El objeto wx.Icon.
        """
        icon: wx.Icon
        icon = self._wx_about_info.GetIcon()
        return icon

    def AddDeveloper(self, developer: str):
        """
        Añade un nombre a la lista de desarrolladores.

        Args:
            developer (str): El nombre del desarrollador.
        """
        self._wx_about_info.AddDeveloper(developer)

    def GetDevelopers(self) -> List[str]:
        """
        Obtiene la lista de nombres de desarrolladores.

        Returns:
            List[str]: Una lista de cadenas con los nombres de los desarrolladores.
        """
        developers: List[str]
        developers = self._wx_about_info.GetDevelopers()
        return developers

    def AddDocWriter(self, writer: str):
        """
        Añade un nombre a la lista de escritores de documentación.

        Args:
            writer (str): El nombre del escritor de documentación.
        """
        self._wx_about_info.AddDocWriter(writer)

    def GetDocWriters(self) -> List[str]:
        """
        Obtiene la lista de nombres de escritores de documentación.

        Returns:
            List[str]: Una lista de cadenas con los nombres.
        """
        doc_writers: List[str]
        doc_writers = self._wx_about_info.GetDocWriters()
        return doc_writers

    def AddArtist(self, artist: str):
        """
        Añade un nombre a la lista de artistas.

        Args:
            artist (str): El nombre del artista.
        """
        self._wx_about_info.AddArtist(artist)

    def GetArtists(self) -> List[str]:
        """
        Obtiene la lista de nombres de artistas.

        Returns:
            List[str]: Una lista de cadenas con los nombres.
        """
        artists: List[str]
        artists = self._wx_about_info.GetArtists()
        return artists

    def AddTranslator(self, translator: str):
        """
        Añade un nombre a la lista de traductores.

        Args:
            translator (str): El nombre del traductor.
        """
        self._wx_about_info.AddTranslator(translator)

    def GetTranslators(self) -> List[str]:
        """
        Obtiene la lista de nombres de traductores.

        Returns:
            List[str]: Una lista de cadenas con los nombres.
        """
        translators: List[str]
        translators = self._wx_about_info.GetTranslators()
        return translators

    def AddCollaborator(self, name: str, contribution: Optional[str] = None):
        """
        Añade un colaborador personalizado con una contribución opcional.

        Args:
            name (str): El nombre del colaborador.
            contribution (Optional[str]): Descripción opcional de la contribución.
        """
        collaborator_entry: Tuple[str, Optional[str]]
        collaborator_entry = (name, contribution)
        self._collaborators.append(collaborator_entry)

    def SetCollaborators(self, collaborators: List[Tuple[str, Optional[str]]]):
        """
        Establece la lista completa de colaboradores personalizados.

        Args:
            collaborators (List[Tuple[str, Optional[str]]]): La lista de colaboradores.
        """
        self._collaborators = collaborators

    def GetCollaborators(self) -> List[Tuple[str, Optional[str]]]:
        """
        Obtiene la lista de colaboradores personalizados.

        Returns:
            List[Tuple[str, Optional[str]]]: Una lista de tuplas (nombre, contribución).
        """
        return self._collaborators

class ReinventProseAboutFrame(wx.Frame):
    """
    Ventana "Acerca de" personalizada implementada como un wx.Frame.

    Esta ventana está diseñada para permanecer siempre al frente (wx.STAY_ON_TOP).
    Contiene un logo en la parte superior y un wx.Notebook debajo.
    Todas las pestañas del Notebook contienen un wx.TextCtrl configurado para
    ser multilínea, de solo lectura, sin borde y habilitado para permitir
    el desplazamiento interno.
    """
    # Nombre del archivo de icono para la ventana del frame
    APP_ICON_FILENAME_FOR_WINDOW: str
    APP_ICON_FILENAME_FOR_WINDOW = "app_icon.ico"

    # Atributos para almacenar los datos y controles de la UI
    info: ReinventProseAboutInfo
    logo_bitmap_ctrl: Optional[wx.StaticBitmap]
    notebook: Optional[wx.Notebook]
    general_page_panel: Optional[wx.Panel]
    licence_page_panel: Optional[wx.Panel]
    developers_page_panel: Optional[wx.Panel]
    doc_writers_page_panel: Optional[wx.Panel]
    artists_page_panel: Optional[wx.Panel]
    translators_page_panel: Optional[wx.Panel]
    collaborators_page_panel: Optional[wx.Panel]

    general_text_ctrl: Optional[wx.TextCtrl]
    licence_text_ctrl: Optional[wx.TextCtrl]
    developers_text_ctrl: Optional[wx.TextCtrl]
    doc_writers_text_ctrl: Optional[wx.TextCtrl]
    artists_text_ctrl: Optional[wx.TextCtrl]
    translators_text_ctrl: Optional[wx.TextCtrl]
    collaborators_text_ctrl: Optional[wx.TextCtrl]


    def __init__(self, parent: Optional[wx.Window], info: ReinventProseAboutInfo):
        """
        Constructor de la ventana ReinventProseAboutFrame.

        Inicializa el frame con el título, estilo (siempre al frente),
        establece el icono de la ventana, crea la UI, llena los datos
        y configura el tamaño y la posición iniciales.

        Args:
            parent (Optional[wx.Window]): La ventana padre para este frame.
            info (ReinventProseAboutInfo): El objeto que contiene los datos
                                          a mostrar en la ventana "Acerca de".
        """
        # Construye el título del frame
        frame_title: str
        frame_title = f"Acerca de {info.GetName()}"
        # Define el estilo del frame: estilo por defecto más STAY_ON_TOP
        frame_style: int
        frame_style = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
        # Llama al constructor de la clase base wx.Frame
        super().__init__(parent, title=frame_title, style=frame_style)

        # Almacena los datos de información
        self.info = info

        # Establece el icono de la ventana del frame
        self._set_frame_window_icon()

        # Inicializa los atributos de los controles a None
        self.logo_bitmap_ctrl = None
        self.notebook = None
        self.general_page_panel = None
        self.licence_page_panel = None
        self.developers_page_panel = None
        self.doc_writers_page_panel = None
        self.artists_page_panel = None
        self.translators_page_panel = None
        self.collaborators_page_panel = None
        self.general_text_ctrl = None
        self.licence_text_ctrl = None
        self.developers_text_ctrl = None
        self.doc_writers_text_ctrl = None
        self.artists_text_ctrl = None
        self.translators_text_ctrl = None
        self.collaborators_text_ctrl = None

        # Crea los elementos de la interfaz de usuario
        self._create_ui()
        # Llena los controles con los datos proporcionados
        self._populate_data()

        # Vincula el evento de cambio de tamaño para actualizar el layout
        self.Bind(wx.EVT_SIZE, self.on_size)

        # Establece el tamaño mínimo de la ventana
        min_width: int
        min_width = 500
        min_height: int
        # Altura mínima basada en el logo y un espacio para el notebook
        min_height = 400 + LOGO_SIZE.GetHeight() + 20
        self.SetMinSize(wx.Size(min_width, min_height))

        # Calcula el tamaño preferido y ajusta el tamaño inicial
        preferred_size: wx.Size
        preferred_size = self.GetBestSize()
        initial_width: int
        initial_width = max(min_width, preferred_size.GetWidth())
        initial_height: int
        initial_height = max(min_height, preferred_size.GetHeight())

        # Establece un tamaño inicial máximo para evitar ventanas excesivamente grandes
        max_initial_width: int
        max_initial_width = 700
        max_initial_height: int
        max_initial_height = 600 + LOGO_SIZE.GetHeight()
        initial_width = min(initial_width, max_initial_width)
        initial_height = min(initial_height, max_initial_height)

        # Establece el tamaño inicial de la ventana
        self.SetSize(wx.Size(initial_width, initial_height))
        # Centra la ventana respecto a su padre (o la pantalla si no hay padre)
        self.CentreOnParent()
        # Realiza el layout inicial de los controles
        self.Layout()

    def _get_resource_path(self, file_name: str) -> Optional[str]:
        """
        Obtiene la ruta absoluta a un archivo de recurso.

        Busca el archivo en el directorio de ejecución o en un subdirectorio 'assets'.
        Útil para aplicaciones empaquetadas (como con PyInstaller).

        Args:
            file_name (str): El nombre del archivo de recurso.

        Returns:
            Optional[str]: La ruta absoluta al archivo si se encuentra, None en caso contrario.
        """
        base_path: str
        # Determina la ruta base: directorio temporal de PyInstaller o directorio del script
        if hasattr(sys, "_MEIPASS"):
            # pyright: ignore[reportUnknownMemberType]
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        # Intenta encontrar el archivo en la ruta base
        resource_path: str
        resource_path = os.path.join(base_path, file_name)
        if os.path.exists(resource_path):
            return resource_path

        # Si no se encuentra, intenta buscar en un subdirectorio 'assets'
        resource_path_assets: str
        resource_path_assets = os.path.join(base_path, "assets", file_name)
        if os.path.exists(resource_path_assets):
            return resource_path_assets

        # Si no se encuentra en ninguna parte, retorna None
        return None

    def _set_frame_window_icon(self):
        """
        Establece el icono de la ventana del frame.

        Busca el archivo de icono especificado y lo aplica al frame si es válido.
        Ignora errores si el icono no se puede cargar.
        """
        # Obtiene la ruta al archivo de icono
        icon_path: Optional[str]
        icon_path = self._get_resource_path(self.APP_ICON_FILENAME_FOR_WINDOW)

        # Si se encuentra la ruta, intenta cargar y establecer el icono
        if icon_path:
            try:
                icon: wx.Icon
                icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
                # Verifica si el icono se cargó correctamente antes de establecerlo
                if icon.IsOk():
                    self.SetIcon(icon)
            except Exception:
                # Ignora cualquier excepción durante la carga o establecimiento del icono
                pass

    def _create_panel_for_readonly_text_ctrl_tab(
            self,
            parent_notebook: Optional[wx.Notebook],
            text_ctrl_attr_name: str
        ) -> Optional[wx.Panel]:
        """
        Crea un wx.Panel que contiene un wx.TextCtrl multilínea, de solo lectura,
        sin borde y habilitado para ser usado como una pestaña en el Notebook.

        El TextCtrl está explícitamente habilitado (`Enable(True)`) para asegurar
        que sus barras de desplazamiento internas funcionen, a pesar de ser
        de solo lectura (`wx.TE_READONLY`).

        Args:
            parent_notebook (Optional[wx.Notebook]): El wx.Notebook que será el padre
                                                   del panel.
            text_ctrl_attr_name (str): El nombre del atributo en `self` donde se
                                       almacenará la referencia al wx.TextCtrl creado.

        Returns:
            Optional[wx.Panel]: El panel creado con el TextCtrl, o None si el
                                parent_notebook es None.
        """
        # Verifica que el notebook padre sea válido
        if parent_notebook is None:
            return None

        # Crea el panel que contendrá el TextCtrl
        tab_panel: wx.Panel
        tab_panel = wx.Panel(parent_notebook)

        # Define los estilos para el TextCtrl
        text_ctrl_style: int
        text_ctrl_style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.BORDER_NONE

        # Crea el TextCtrl con los estilos definidos
        text_ctrl: wx.TextCtrl
        text_ctrl = wx.TextCtrl(tab_panel, style=text_ctrl_style)

        # HABILITA explícitamente el TextCtrl. Esto es crucial para que las
        # barras de desplazamiento internas funcionen, incluso si es de solo lectura.
        text_ctrl.Enable(True)

        # Almacena la referencia al TextCtrl en el atributo especificado de la instancia
        setattr(self, text_ctrl_attr_name, text_ctrl)

        # Crea un sizer para el panel y añade el TextCtrl
        panel_sizer: wx.BoxSizer
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        # Añade el TextCtrl al sizer, expandiéndolo para llenar el panel
        panel_sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 0) # Sin borde alrededor del TextCtrl dentro del sizer

        # Establece el sizer para el panel
        tab_panel.SetSizer(panel_sizer)

        # Retorna el panel creado
        return tab_panel

    def _create_logo_bitmap(self) -> wx.Bitmap:
        """
        Carga la imagen del logo desde un archivo o crea un bitmap de marcador
        de posición si el archivo no se encuentra.

        La imagen cargada se reescala al tamaño definido por LOGO_SIZE.

        Returns:
            wx.Bitmap: Un objeto wx.Bitmap que contiene el logo o un marcador de posición.
        """
        # Obtiene la ruta al archivo de imagen del logo
        logo_path: Optional[str]
        logo_path = self._get_resource_path(LOGO_IMAGE_FILENAME)

        logo_img: Optional[wx.Image] = None
        # Si se encuentra la ruta, intenta cargar la imagen
        if logo_path:
            logo_img = wx.Image(logo_path, wx.BITMAP_TYPE_ANY)
            # Si la imagen se cargó correctamente, la reescala
            if logo_img.IsOk():
                logo_img.Rescale(LOGO_SIZE.GetWidth(), LOGO_SIZE.GetHeight(), wx.IMAGE_QUALITY_HIGH)
                # Convierte la imagen reescalada a un bitmap y lo retorna
                return wx.Bitmap(logo_img)

        # Si el archivo no se encuentra o la carga falla, crea un bitmap de marcador de posición
        placeholder_bmp: wx.Bitmap
        placeholder_bmp = wx.Bitmap(LOGO_SIZE.GetWidth(), LOGO_SIZE.GetHeight())
        mem_dc: wx.MemoryDC
        mem_dc = wx.MemoryDC()
        mem_dc.SelectObject(placeholder_bmp)
        # Dibuja un fondo gris y un borde
        mem_dc.SetBackground(wx.Brush(wx.Colour(200, 200, 200)))
        mem_dc.Clear()
        mem_dc.SetPen(wx.Pen(wx.BLACK, 1))
        mem_dc.DrawRectangle(0,0, LOGO_SIZE.GetWidth(), LOGO_SIZE.GetHeight())
        # Añade texto indicando que es un marcador de posición
        mem_dc.DrawText("Logo", 5, 5)
        # Deselecciona el bitmap del DC de memoria
        mem_dc.SelectObject(wx.NullBitmap)

        # Retorna el bitmap del marcador de posición
        return placeholder_bmp

    def _create_ui(self):
        """
        Crea la estructura principal de la interfaz de usuario del frame.

        Consiste en un wx.StaticBitmap para el logo en la parte superior
        y un wx.Notebook que ocupa el espacio restante debajo.
        Se crean paneles con TextCtrl para cada pestaña estándar y se añaden al Notebook.
        """
        # Crea el sizer principal para organizar los elementos verticalmente
        frame_main_sizer: wx.BoxSizer
        frame_main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Crea el bitmap para mostrar el logo
        logo_display_bitmap: wx.Bitmap
        logo_display_bitmap = self._create_logo_bitmap()
        # Crea el control StaticBitmap para mostrar el logo
        self.logo_bitmap_ctrl = wx.StaticBitmap(self, wx.ID_ANY, logo_display_bitmap)
        # Añade el logo al sizer principal, centrado horizontalmente
        frame_main_sizer.Add(self.logo_bitmap_ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        # Crea el control Notebook para las pestañas
        self.notebook = wx.Notebook(self, style=wx.NB_TOP | wx.NB_MULTILINE)

        # Crea y añade la pestaña "General"
        self.general_page_panel = self._create_panel_for_readonly_text_ctrl_tab(self.notebook, "general_text_ctrl")
        if self.notebook and self.general_page_panel:
            self.notebook.AddPage(self.general_page_panel, "General")

        # Crea y añade la pestaña "Licencia"
        self.licence_page_panel = self._create_panel_for_readonly_text_ctrl_tab(self.notebook, "licence_text_ctrl")
        if self.notebook and self.licence_page_panel:
            self.notebook.AddPage(self.licence_page_panel, "Licencia")

        # Crea y añade la pestaña "Equipo de Desarrollo"
        self.developers_page_panel = self._create_panel_for_readonly_text_ctrl_tab(self.notebook, "developers_text_ctrl")
        if self.notebook and self.developers_page_panel:
            self.notebook.AddPage(self.developers_page_panel, "Equipo de Desarrollo")

        # Crea y añade la pestaña "Documentadores"
        self.doc_writers_page_panel = self._create_panel_for_readonly_text_ctrl_tab(self.notebook, "doc_writers_text_ctrl")
        if self.notebook and self.doc_writers_page_panel:
            self.notebook.AddPage(self.doc_writers_page_panel, "Documentadores")

        # Crea y añade la pestaña "Artistas"
        self.artists_page_panel = self._create_panel_for_readonly_text_ctrl_tab(self.notebook, "artists_text_ctrl")
        if self.notebook and self.artists_page_panel:
            self.notebook.AddPage(self.artists_page_panel, "Artistas")

        # Crea la pestaña "Traductores" (se añadirá condicionalmente en _populate_data)
        self.translators_page_panel = self._create_panel_for_readonly_text_ctrl_tab(self.notebook, "translators_text_ctrl")

        # Crea y añade la pestaña "Colaboradores"
        self.collaborators_page_panel = self._create_panel_for_readonly_text_ctrl_tab(self.notebook, "collaborators_text_ctrl")
        if self.notebook and self.collaborators_page_panel:
            self.notebook.AddPage(self.collaborators_page_panel, "Colaboradores")

        # Añade el Notebook al sizer principal, expandiéndolo para llenar el espacio restante
        if self.notebook is not None:
            frame_main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        # Establece el sizer principal para el frame
        self.SetSizer(frame_main_sizer)

    def _populate_data(self):
        """
        Llena los wx.TextCtrl de cada pestaña del Notebook con los datos
        obtenidos del objeto ReinventProseAboutInfo.

        Maneja la adición condicional de la pestaña "Traductores" si hay datos.
        """
        # Prepara y llena la pestaña "General"
        general_text_parts: List[str]
        general_text_parts = []
        general_text_parts.append(f"{self.info.GetName()} {self.info.GetVersion()}")
        general_text_parts.append(f"\n{self.info.GetCopyright()}")
        general_text_parts.append(f"\n\n{self.info.GetDescription()}")
        website_tuple: Optional[Tuple[str, str]]
        website_tuple = self.info.GetWebSite()
        if website_tuple and website_tuple[0]:
            general_text_parts.append(f"\n\nSitio Web: {website_tuple[1]} ({website_tuple[0]})")
        if self.general_text_ctrl:
            full_general_text: str
            full_general_text = "\n".join(general_text_parts)
            self.general_text_ctrl.SetValue(full_general_text)
            # Mueve el punto de inserción al inicio para que el scrollbar esté arriba
            self.general_text_ctrl.SetInsertionPoint(0)

        # Llena la pestaña "Licencia"
        if self.licence_text_ctrl:
            self.licence_text_ctrl.SetValue(self.info.GetLicence())
            self.licence_text_ctrl.SetInsertionPoint(0)

        # Llena la pestaña "Equipo de Desarrollo"
        dev_list: List[str]
        dev_list = self.info.GetDevelopers()
        if self.developers_text_ctrl:
            self.developers_text_ctrl.SetValue("\n".join([f"- {d}" for d in dev_list]) if dev_list else "(No especificado)")
            self.developers_text_ctrl.SetInsertionPoint(0)

        # Llena la pestaña "Documentadores"
        doc_list: List[str]
        doc_list = self.info.GetDocWriters()
        if self.doc_writers_text_ctrl:
            self.doc_writers_text_ctrl.SetValue("\n".join([f"- {d}" for d in doc_list]) if doc_list else "(No especificado)")
            self.doc_writers_text_ctrl.SetInsertionPoint(0)

        # Llena la pestaña "Artistas"
        art_list: List[str]
        art_list = self.info.GetArtists()
        if self.artists_text_ctrl:
            self.artists_text_ctrl.SetValue("\n".join([f"- {a}" for a in art_list]) if art_list else "(No especificado)")
            self.artists_text_ctrl.SetInsertionPoint(0)

        # Maneja la pestaña "Traductores": la añade solo si hay traductores
        if self.notebook and self.translators_page_panel and self.translators_text_ctrl:
            trans_list: List[str]
            trans_list = self.info.GetTranslators()
            # Busca si la pestaña "Traductores" ya existe
            translator_page_idx: int = -1
            for i in range(self.notebook.GetPageCount()):
                if self.notebook.GetPageText(i) == "Traductores":
                    translator_page_idx = i
                    break

            if trans_list:
                # Si hay traductores, llena el TextCtrl
                self.translators_text_ctrl.SetValue("\n".join([f"- {t}" for t in trans_list]))
                self.translators_text_ctrl.SetInsertionPoint(0)
                # Si la pestaña no existía, la inserta antes de "Colaboradores" o al final
                if translator_page_idx == -1:
                    collaborators_page_idx: int = -1
                    for j_idx in range(self.notebook.GetPageCount()):
                        if self.notebook.GetPageText(j_idx) == "Colaboradores":
                            collaborators_page_idx = j_idx
                            break
                    # Inserta la página en la posición de "Colaboradores" o al final
                    insert_pos: int
                    insert_pos = collaborators_page_idx if collaborators_page_idx != -1 else self.notebook.GetPageCount()
                    self.notebook.InsertPage(insert_pos, self.translators_page_panel, "Traductores")
            elif translator_page_idx != -1:
                # Si no hay traductores pero la pestaña existía, la elimina
                current_page_at_idx: Optional[wx.Window]
                current_page_at_idx = self.notebook.GetPage(translator_page_idx)
                # Verifica que la página en ese índice sea realmente la de traductores antes de eliminar
                if current_page_at_idx == self.translators_page_panel:
                    self.notebook.RemovePage(translator_page_idx)

            # Actualiza el layout del notebook después de posibles adiciones/eliminaciones
            if self.notebook:
                self.notebook.Layout()

        # Llena la pestaña "Colaboradores"
        collaborators_list: List[Tuple[str, Optional[str]]]
        collaborators_list = self.info.GetCollaborators()
        # Formatea la lista de colaboradores para mostrar nombre y contribución
        collaborators_formatted_list: List[str]
        collaborators_formatted_list = [f"- {name}{f': {contrib}' if contrib else ''}" for name, contrib in collaborators_list]
        if self.collaborators_text_ctrl:
            self.collaborators_text_ctrl.SetValue("\n".join(collaborators_formatted_list) if collaborators_formatted_list else "(Ninguno especificado)")
            self.collaborators_text_ctrl.SetInsertionPoint(0)

        # Asegura que el layout del notebook se actualice al final
        if self.notebook:
            self.notebook.Layout()


    def on_size(self, event: wx.SizeEvent):
        """
        Manejador para el evento de cambio de tamaño del frame.

        Simplemente llama a Layout() para asegurar que los controles se
        redimensionen y reposicionen correctamente dentro del frame.

        Args:
            event (wx.SizeEvent): El evento de cambio de tamaño.
        """
        # Realiza el layout de los controles dentro del frame
        self.Layout()
        # Permite que el evento sea procesado por otros manejadores si los hay
        event.Skip()


# Bloque de ejecución principal para pruebas
if __name__ == '__main__':
    # Crea una instancia de la aplicación wx
    app = wx.App(False)

    # Crea un objeto ReinventProseAboutInfo con datos de prueba
    about_info_test = ReinventProseAboutInfo()
    about_info_test.SetName("ReinventProse 2.0 (Prueba de Documentación)")
    about_info_test.SetVersion("v0.0.1")
    about_info_test.SetCopyright("(C) 2025 AutoDoc AI. Documentación Generada.")
    description_main_test: str
    description_main_test = (
        "Esta es una ventana 'Acerca de' personalizada para ReinventProse 2.0.\n"
        "Diseñada para demostrar la estructura con logo, notebook y pestañas.\n"
        "Los campos de texto son de solo lectura pero permiten desplazamiento.\n"
        "La ventana permanece siempre al frente."
    )
    about_info_test.SetDescription(description_main_test)

    # Texto de licencia largo para probar el scroll
    long_licence_text: str
    long_licence_text = "MIT License - Texto de Licencia de Prueba\n\n" + ("Este es un texto de licencia ejemplar, suficientemente largo y repetitivo para asegurar que las barras de desplazamiento del wx.TextCtrl (habilitado, pero de solo lectura) sean funcionales y visibles cuando sea necesario. " * 50)
    about_info_test.SetLicence(long_licence_text)

    # Añade datos a las listas
    about_info_test.AddDeveloper("AutoDoc AI (Generador de Documentación)")
    about_info_test.AddDeveloper("Usuario Original (Autor del Código Base)")
    about_info_test.AddDocWriter("AutoDoc AI (Escritor de Docs)")
    about_info_test.AddArtist("Artista de Prueba")
    about_info_test.AddCollaborator("Colaborador 1", "Ayuda General")
    about_info_test.AddCollaborator("Colaborador 2") # Colaborador sin contribución específica
    about_info_test.AddTranslator("Traductor de Prueba (Español)")

    # Establece datos del sitio web
    website_url_test: str = "http://www.ejemplo.com/reinventprose"
    website_desc_test: str = "Sitio Web de Ejemplo"
    about_info_test.SetWebSite(website_url_test, website_desc_test)

    # Crea una instancia de la ventana "Acerca de"
    about_frame_instance = ReinventProseAboutFrame(None, about_info_test)
    # Muestra la ventana
    about_frame_instance.Show()

    # Inicia el bucle principal de eventos de wxWidgets
    app.MainLoop()