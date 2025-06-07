# -*- coding: utf-8 -*-
"""
File Name: BookDetailsView.py
Description: Panel de wxPython para mostrar y editar los detalles de un libro.
Author: AutoDoc AI
Date: 07/06/2025
Version: 0.0.1
License: MIT License
"""
import wx
import os
from typing import Optional
from Util import load_image, create_placeholder_bitmap

class BookDetailsView(wx.Panel):
    """
    Panel que muestra y permite editar los detalles de un libro seleccionado.

    Gestiona la visualización de campos como título, autor, sinopsis, prólogo,
    texto de contraportada e imagen de portada. Permite la edición de estos
    campos y notifica al manejador de la aplicación cuando hay cambios pendientes.
    """
    def __init__(self, parent, app_handler):
        """
        Inicializa el panel BookDetailsView.

        Args:
            parent (wx.Window): La ventana padre de este panel.
            app_handler (object): Un objeto que maneja la lógica de la aplicación,
                                  proporcionando métodos para obtener/actualizar datos
                                  y notificar cambios globales.
        """
        super().__init__(parent)
        # Referencia al manejador de la aplicación para interactuar con la lógica de negocio
        self.app_handler = app_handler
        # ID del libro actualmente cargado en la vista. None si no hay libro seleccionado.
        self.book_id: Optional[int] = None
        # Bandera que indica si los datos mostrados en la vista han sido modificados.
        self._is_dirty_view: bool = False
        # Ruta del archivo de imagen de portada actualmente cargado.
        self.current_cover_image_path: Optional[str] = None
        # Bandera para evitar que los eventos de texto marquen la vista como sucia
        # mientras se cargan datos programáticamente.
        self._loading_data: bool = False

        # Crea los controles de la interfaz de usuario
        self._create_controls()
        # Organiza los controles en el panel
        self._layout_controls()
        # Carga los detalles de un libro (inicialmente None para limpiar la vista)
        self.load_book_details(None)

    def _create_controls(self):
        """
        Crea todos los controles (etiquetas, campos de texto, imagen) para la vista de detalles del libro.
        """
        # Etiquetas para los campos de entrada
        self.title_label = wx.StaticText(self, label="Título (*):")
        self.author_label = wx.StaticText(self, label="Autor (*):")
        self.synopsis_label = wx.StaticText(self, label="Sinopsis:")
        self.prologue_label = wx.StaticText(self, label="Prólogo:")
        self.back_cover_text_label = wx.StaticText(self, label="Texto de Contraportada:")
        self.cover_image_label_text = wx.StaticText(self, label="Imagen de Portada:")

        # Campos de entrada de texto
        self.title_ctrl = wx.TextCtrl(self)
        self.author_ctrl = wx.TextCtrl(self)
        # Campos de texto multilínea con tamaño inicial sugerido
        self.synopsis_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 80))
        self.prologue_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 80))
        self.back_cover_text_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 80))

        # Control para mostrar la imagen de portada. Inicialmente muestra un placeholder.
        self.cover_image_display = wx.StaticBitmap(self, wx.ID_ANY,
                                                   create_placeholder_bitmap(100, 150, "Portada"),
                                                   size=(100, 150))
        # Vincula el evento de clic izquierdo a la imagen para permitir cambiarla
        self.cover_image_display.Bind(wx.EVT_LEFT_DOWN, self.on_image_clicked)

        # Lista de controles de texto que deben notificar cambios
        controls_to_bind = [self.title_ctrl, self.author_ctrl, self.synopsis_ctrl,
                            self.prologue_ctrl, self.back_cover_text_ctrl]
        # Vincula el evento de cambio de texto a cada control
        for ctrl in controls_to_bind:
            ctrl.Bind(wx.EVT_TEXT, self.on_text_changed)

    def _layout_controls(self):
        """
        Organiza los controles creados utilizando sizers para definir el diseño del panel.
        """
        # Sizer principal que organiza los elementos verticalmente
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        # Sizer flexible en forma de cuadrícula para organizar etiquetas y campos de entrada
        form_sizer = wx.FlexGridSizer(rows=0, cols=2, vgap=10, hgap=10)
        # Permite que la segunda columna (campos de entrada) se expanda horizontalmente
        form_sizer.AddGrowableCol(1)

        # Añade las etiquetas y sus controles correspondientes al sizer de formulario
        form_sizer.Add(self.title_label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(self.title_ctrl, 1, wx.EXPAND)
        form_sizer.Add(self.author_label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(self.author_ctrl, 1, wx.EXPAND)
        form_sizer.Add(self.synopsis_label, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.TOP, 5)
        form_sizer.Add(self.synopsis_ctrl, 1, wx.EXPAND)
        form_sizer.Add(self.prologue_label, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.TOP, 5)
        form_sizer.Add(self.prologue_ctrl, 1, wx.EXPAND)
        form_sizer.Add(self.back_cover_text_label, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.TOP, 5)
        form_sizer.Add(self.back_cover_text_ctrl, 1, wx.EXPAND)
        form_sizer.Add(self.cover_image_label_text, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(self.cover_image_display, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        # Añade el sizer de formulario al sizer principal, permitiendo que se expanda
        main_sizer.Add(form_sizer, 1, wx.EXPAND | wx.ALL, 10)

        # Establece el sizer principal para el panel
        self.SetSizer(main_sizer)
        # Actualiza el estado inicial de los controles (habilitados/deshabilitados)
        self._update_controls_state()

    def _set_view_dirty(self, is_dirty: bool = True):
        """
        Establece el estado 'sucio' (modificado) de la vista y notifica al manejador de la aplicación.

        Args:
            is_dirty (bool): True si la vista tiene cambios sin guardar, False en caso contrario.
                             Por defecto es True.
        """
        # Solo actualiza si el estado cambia
        if self._is_dirty_view != is_dirty:
            self._is_dirty_view = is_dirty
            # Si la vista se vuelve sucia, notifica al manejador de la aplicación
            if self._is_dirty_view:
                 self.app_handler.set_dirty(True)

    def _update_controls_state(self):
        """
        Habilita o deshabilita los controles de entrada de la vista
        basándose en si hay un libro cargado (book_id no es None).
        """
        # Determina si los controles deben estar habilitados
        are_controls_enabled = self.book_id is not None
        # Itera sobre los controles relevantes y establece su estado de habilitación
        for ctrl in [self.title_ctrl, self.author_ctrl, self.synopsis_ctrl,
                     self.prologue_ctrl, self.back_cover_text_ctrl, self.cover_image_display]:
            ctrl.Enable(are_controls_enabled)

    def load_book_details(self, book_id: Optional[int]):
        """
        Carga los detalles de un libro específico en los controles de la vista.

        Si book_id es None, limpia los controles.

        Args:
            book_id (Optional[int]): El ID del libro cuyos detalles se van a cargar,
                                     o None para limpiar la vista.
        """
        # Establece la bandera de carga para evitar eventos de texto durante la carga
        self._loading_data = True
        # Almacena el ID del libro cargado
        self.book_id = book_id
        # Reinicia la ruta de la imagen de portada actual
        self.current_cover_image_path = None

        # Si no hay ID de libro, limpia todos los campos
        if book_id is None:
            self.title_ctrl.SetValue("")
            self.author_ctrl.SetValue("")
            self.synopsis_ctrl.SetValue("")
            self.prologue_ctrl.SetValue("")
            self.back_cover_text_ctrl.SetValue("")
            # Establece la imagen de portada al placeholder por defecto
            self.cover_image_display.SetBitmap(create_placeholder_bitmap(100, 150, "Portada"))
        else:
            # Si hay un ID, intenta obtener los detalles del libro del manejador
            book_data = self.app_handler.get_book_details(book_id)
            if book_data:
                # Rellena los campos con los datos obtenidos
                self.title_ctrl.SetValue(book_data.get('title', ''))
                self.author_ctrl.SetValue(book_data.get('author', ''))
                self.synopsis_ctrl.SetValue(book_data.get('synopsis', ''))
                self.prologue_ctrl.SetValue(book_data.get('prologue', ''))
                self.back_cover_text_ctrl.SetValue(book_data.get('back_cover_text', ''))

                # Carga la imagen de portada si la ruta existe
                self.current_cover_image_path = book_data.get('cover_image_path')
                if self.current_cover_image_path:
                    img_bmp = load_image(self.current_cover_image_path)
                    # Si la imagen se carga correctamente, la escala y la muestra
                    if img_bmp and img_bmp.IsOk():
                        self.cover_image_display.SetBitmap(wx.Bitmap(img_bmp.ConvertToImage().Rescale(100, 150, wx.IMAGE_QUALITY_HIGH)))
                    else:
                        # Si falla la carga, muestra un placeholder de error y limpia la ruta
                        self.cover_image_display.SetBitmap(create_placeholder_bitmap(100, 150, "Error Portada"))
                        self.current_cover_image_path = None # Asegura que la ruta inválida no se guarde
                else:
                    # Si no hay ruta de imagen, muestra el placeholder por defecto
                    self.cover_image_display.SetBitmap(create_placeholder_bitmap(100, 150, "Portada"))
            else:
                # Si no se encuentran los datos del libro, limpia los campos y muestra un placeholder
                self.title_ctrl.SetValue("")
                self.author_ctrl.SetValue("")
                self.synopsis_ctrl.SetValue("")
                self.prologue_ctrl.SetValue("")
                self.back_cover_text_ctrl.SetValue("")
                self.cover_image_display.SetBitmap(create_placeholder_bitmap(100, 150, "No Encontrado"))

        # Después de cargar, la vista no está sucia
        self._is_dirty_view = False
        # Actualiza el estado de habilitación de los controles
        self._update_controls_state()
        # Desactiva la bandera de carga
        self._loading_data = False

    def save_changes(self) -> bool:
        """
        Guarda los cambios realizados en los detalles del libro actual.

        Solo guarda si la vista está marcada como sucia y hay un libro cargado.
        Realiza una validación básica (título y autor obligatorios).

        Returns:
            bool: True si los cambios se guardaron exitosamente, False en caso contrario.
        """
        # No guardar si la vista no está sucia o no hay un libro cargado
        if not self._is_dirty_view or self.book_id is None:
            return False

        # Obtiene los valores de los campos y elimina espacios en blanco al inicio/final
        title = self.title_ctrl.GetValue().strip()
        author = self.author_ctrl.GetValue().strip()

        # Validación: Título y autor son obligatorios
        if not title or not author:
            wx.MessageBox("Título y autor son obligatorios para guardar los detalles del libro.", "Error", wx.OK | wx.ICON_WARNING, self)
            return False

        # Llama al manejador de la aplicación para actualizar los datos del libro
        success = self.app_handler.update_book_details(
            book_id=self.book_id,
            title=title,
            author=author,
            synopsis=self.synopsis_ctrl.GetValue(),
            prologue=self.prologue_ctrl.GetValue(),
            back_cover_text=self.back_cover_text_ctrl.GetValue(),
            cover_image_path=self.current_cover_image_path or "" # Usa la ruta actual o cadena vacía si es None
        )

        # Si el guardado fue exitoso, marca la vista como no sucia
        if success:
            self._set_view_dirty(False)
            # La notificación de éxito se maneja a nivel global (MainWindow)
            return True

        # Si el guardado falló, el manejador de la aplicación ya debería haber mostrado un error
        return False

    def on_text_changed(self, event):
        """
        Manejador de eventos para los cambios de texto en los controles de entrada.

        Marca la vista como sucia si el texto cambia y no se está cargando data.

        Args:
            event (wx.Event): El evento de cambio de texto.
        """
        # Ignora el evento si se está cargando data o si los controles están deshabilitados
        if self._loading_data or not self.title_ctrl.IsEnabled():
            event.Skip() # Permite que el evento se propague si es necesario
            return

        # Marca la vista como sucia
        self._set_view_dirty(True)
        event.Skip() # Permite que el evento se propague

    def on_image_clicked(self, event):
        """
        Manejador de eventos para el clic en la imagen de portada.

        Abre un diálogo de archivo para seleccionar una nueva imagen de portada.

        Args:
            event (wx.Event): El evento de clic del ratón.
        """
        # No permite cambiar la imagen si el control está deshabilitado
        if not self.cover_image_display.IsEnabled():
            return

        # Abre un diálogo para seleccionar un archivo de imagen
        with wx.FileDialog(self, "Seleccionar imagen",
                           wildcard="Imágenes (*.png;*.jpg;*.jpeg)|*.png;*.jpg;*.jpeg",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:

            # Si el usuario selecciona un archivo y hace clic en OK
            if dialog.ShowModal() == wx.ID_OK:
                new_path = dialog.GetPath()
                # Intenta cargar la imagen seleccionada
                img_bmp = load_image(new_path)

                # Si la imagen se carga correctamente
                if img_bmp and img_bmp.IsOk():
                    # Escala la imagen y la muestra en el control StaticBitmap
                    self.cover_image_display.SetBitmap(wx.Bitmap(img_bmp.ConvertToImage().Rescale(100, 150, wx.IMAGE_QUALITY_HIGH)))
                    # Si la nueva ruta es diferente a la actual, actualiza la ruta y marca la vista como sucia
                    if self.current_cover_image_path != new_path:
                        self.current_cover_image_path = new_path
                        self._set_view_dirty(True)
                else:
                    # Si falla la carga de la imagen, muestra un mensaje de error
                    wx.MessageBox("No se pudo cargar la imagen.", "Error", wx.OK | wx.ICON_ERROR, self)

    def get_current_image_path(self) -> Optional[str]:
        """
        Obtiene la ruta del archivo de la imagen de portada actualmente mostrada.

        Returns:
            Optional[str]: La ruta del archivo de imagen o None si no hay imagen cargada.
        """
        return self.current_cover_image_path

    def is_dirty(self) -> bool:
        """
        Verifica si la vista de detalles del libro tiene cambios sin guardar.

        Returns:
            bool: True si la vista está sucia (tiene cambios sin guardar), False en caso contrario.
        """
        return self._is_dirty_view

    def enable_view(self, enable: bool):
        """
        Habilita o deshabilita todos los controles de entrada de la vista.

        Args:
            enable (bool): True para habilitar los controles, False para deshabilitarlos.
        """
        # Itera sobre los controles de entrada y establece su estado de habilitación
        for ctrl in [self.title_ctrl, self.author_ctrl, self.synopsis_ctrl,
                     self.prologue_ctrl, self.back_cover_text_ctrl, self.cover_image_display]:
            ctrl.Enable(enable)
        # Nota: Deshabilitar la vista no limpia automáticamente el estado 'dirty'.
        # El estado dirty debe persistir hasta que los cambios se guarden o descarten explícitamente.