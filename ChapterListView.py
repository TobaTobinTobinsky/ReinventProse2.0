# -*- coding: utf-8 -*-
"""
File Name: ChapterListView.py
Description: Vista que muestra la lista de capítulos de un libro seleccionado en la aplicación "ReinventProse 2.0". Permite añadir, eliminar y seleccionar capítulos.
Author: AutoDoc AI
Date: 07/06/2025
Version: 0.0.1
License: MIT License
"""
import wx
from typing import Optional, List, Dict, Any, Callable

# Definición de IDs para los botones
ID_ADD_CHAPTER = wx.NewIdRef()
ID_DELETE_CHAPTER = wx.NewIdRef()

class ChapterListView(wx.Panel):
    """
    Panel de wxPython que muestra una lista de capítulos asociados a un libro
    y proporciona funcionalidades para añadir, eliminar y seleccionar capítulos.
    """
    def __init__(self, parent: wx.Window, app_handler: Any):
        """
        Inicializa la vista de lista de capítulos.

        Args:
            parent (wx.Window): La ventana padre de este panel.
            app_handler (Any): Un objeto manejador de la aplicación que proporciona
                               métodos para interactuar con los datos (libros, capítulos).
        """
        super().__init__(parent)
        # Almacena la referencia al manejador de la aplicación
        self.app_handler = app_handler
        # ID del libro actualmente cargado (None si no hay libro seleccionado)
        self.book_id: Optional[int] = None
        # Lista de diccionarios que representan los datos de los capítulos cargados
        self.chapters_data: List[Dict[str, Any]] = []
        # Callback a ejecutar cuando se selecciona un capítulo
        self.on_chapter_selected_callback: Optional[Callable[[Optional[int]], None]] = None

        # Crea los controles visuales
        self._create_controls()
        # Organiza los controles en el panel
        self._layout_controls()
        # Actualiza el estado inicial de los botones
        self._update_button_states()

    def _create_controls(self):
        """
        Crea los controles individuales (etiqueta, lista, botones) del panel.
        También enlaza los eventos de los controles a sus manejadores.
        """
        # Etiqueta para indicar qué se muestra en la lista
        self.list_label = wx.StaticText(self, label="Capítulos del Libro:")
        # Control ListBox para mostrar los nombres de los capítulos
        # wx.LB_SINGLE: Permite seleccionar solo un elemento a la vez.
        # wx.LB_SORT: Mantiene los elementos ordenados alfabéticamente.
        self.chapter_list_ctrl = wx.ListBox(self, style=wx.LB_SINGLE | wx.LB_SORT)
        # Botón para añadir un nuevo capítulo
        self.add_chapter_button = wx.Button(self, ID_ADD_CHAPTER, "Añadir Capítulo")
        # Botón para eliminar el capítulo seleccionado
        self.delete_chapter_button = wx.Button(self, ID_DELETE_CHAPTER, "Eliminar Capítulo")

        # Enlaza eventos de la lista a sus métodos manejadores
        self.chapter_list_ctrl.Bind(wx.EVT_LISTBOX, self.on_listbox_select)
        self.chapter_list_ctrl.Bind(wx.EVT_LISTBOX_DCLICK, self.on_listbox_dclick)
        # Enlaza eventos de los botones a sus métodos manejadores
        self.add_chapter_button.Bind(wx.EVT_BUTTON, self.on_add_chapter)
        self.delete_chapter_button.Bind(wx.EVT_BUTTON, self.on_delete_chapter)

    def _layout_controls(self):
        """
        Define la disposición de los controles dentro del panel utilizando sizers.
        """
        # Sizer principal vertical
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        # Añade la etiqueta con margen y expansión horizontal
        main_sizer.Add(self.list_label, 0, wx.ALL | wx.EXPAND, 5)
        # Añade la lista de capítulos, permitiendo que se expanda vertical y horizontalmente
        main_sizer.Add(self.chapter_list_ctrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        # Sizer horizontal para los botones
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Añade el botón de añadir con margen a la derecha
        button_sizer.Add(self.add_chapter_button, 0, wx.RIGHT, 5)
        # Añade el botón de eliminar con margen a la derecha
        button_sizer.Add(self.delete_chapter_button, 0, wx.RIGHT, 5)
        # Añade el sizer de botones al sizer principal, alineado a la izquierda
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        # Establece el sizer principal para el panel
        self.SetSizer(main_sizer)

    def set_on_chapter_selected_callback(self, callback: Callable[[Optional[int]], None]):
        """
        Establece una función de callback que se ejecutará cuando se seleccione
        un capítulo en la lista.

        Args:
            callback (Callable[[Optional[int]], None]): La función de callback.
                                                         Recibe el ID del capítulo seleccionado
                                                         (o None si no hay selección).
        """
        self.on_chapter_selected_callback = callback

    def _update_button_states(self):
        """
        Actualiza el estado de habilitación de los botones (Añadir, Eliminar)
        y la lista de capítulos basándose en si hay un libro cargado y si hay
        un capítulo seleccionado.
        """
        # Verifica si hay un libro cargado (book_id no es None)
        has_book = self.book_id is not None
        # Obtiene el índice del elemento seleccionado en la lista
        selection_index = self.chapter_list_ctrl.GetSelection()
        # Verifica si hay algún elemento seleccionado
        has_selection = selection_index != wx.NOT_FOUND

        # Habilita el botón Añadir solo si hay un libro cargado
        self.add_chapter_button.Enable(has_book)
        # Habilita el botón Eliminar solo si hay un libro cargado Y un capítulo seleccionado
        self.delete_chapter_button.Enable(has_book and has_selection)
        # Habilita la lista de capítulos solo si hay un libro cargado
        self.chapter_list_ctrl.Enable(has_book)

    def load_chapters(self, book_id: Optional[int]):
        """
        Carga y muestra la lista de capítulos para un libro específico.
        Si book_id es None, limpia la lista y restablece el estado.

        Args:
            book_id (Optional[int]): El ID del libro cuyos capítulos se cargarán,
                                     o None para limpiar la vista.
        """
        # Almacena el ID del libro actual
        self.book_id = book_id
        # Limpia la lista visual de capítulos
        self.chapter_list_ctrl.Clear()
        # Limpia los datos internos de los capítulos
        self.chapters_data.clear()

        # Si no hay libro seleccionado, actualiza la etiqueta y el estado, y notifica al callback
        if self.book_id is None:
            self.list_label.SetLabel("Capítulos: (Seleccione un libro)")
            self._update_button_states()
            # Notifica al callback que no hay capítulo seleccionado
            if self.on_chapter_selected_callback:
                self.on_chapter_selected_callback(None)
            return # Sale de la función

        # Obtiene los detalles del libro para mostrar su título
        book_details = self.app_handler.get_book_details(self.book_id)
        # Extrae el título o usa "Desconocido" si no se encuentran detalles
        book_title = book_details['title'] if book_details else "Desconocido"
        # Actualiza la etiqueta para mostrar el título del libro (truncado si es largo)
        self.list_label.SetLabel(f"Capítulos de: {book_title[:30]}{'...' if len(book_title)>30 else ''}")

        # Obtiene los datos de los capítulos del manejador de la aplicación
        self.chapters_data = self.app_handler.get_chapters_by_book_id(self.book_id)

        # Si hay capítulos, los añade a la lista visual
        if self.chapters_data:
            for chapter in self.chapters_data:
                # Formatea el texto a mostrar en la lista
                display_text = f"Cap. {chapter['chapter_number']}: {chapter['title']}"
                # Añade el texto a la lista, asociando el ID del capítulo como ClientData
                self.chapter_list_ctrl.Append(display_text, chapter['id'])

        # Actualiza el estado de los botones basado en la nueva lista
        self._update_button_states()

        # Si no hay selección después de cargar (por ejemplo, si la lista estaba vacía),
        # notifica al callback que no hay capítulo seleccionado.
        if self.chapter_list_ctrl.GetSelection() == wx.NOT_FOUND and self.on_chapter_selected_callback:
            self.on_chapter_selected_callback(None)

    def on_listbox_select(self, event: wx.CommandEvent):
        """
        Manejador de evento para la selección de un elemento en la lista de capítulos.
        Notifica al callback con el ID del capítulo seleccionado.

        Args:
            event (wx.CommandEvent): El evento de selección de ListBox.
        """
        selected_chapter_id: Optional[int] = None
        # Obtiene el índice del elemento seleccionado
        selection_index = self.chapter_list_ctrl.GetSelection()
        # Si hay un elemento seleccionado, obtiene su ClientData (que es el ID del capítulo)
        if selection_index != wx.NOT_FOUND:
            selected_chapter_id = self.chapter_list_ctrl.GetClientData(selection_index)

        # Si hay un callback registrado, lo ejecuta con el ID del capítulo seleccionado
        if self.on_chapter_selected_callback:
            self.on_chapter_selected_callback(selected_chapter_id)

        # Actualiza el estado de los botones
        self._update_button_states()
        # Permite que el evento continúe su procesamiento estándar
        event.Skip()

    def on_listbox_dclick(self, event: wx.CommandEvent):
        """
        Manejador de evento para el doble clic en un elemento de la lista de capítulos.
        Actualmente, simplemente llama al manejador de selección simple.

        Args:
            event (wx.CommandEvent): El evento de doble clic de ListBox.
        """
        # Trata el doble clic como una selección simple
        self.on_listbox_select(event)

    def on_add_chapter(self, event: wx.CommandEvent):
        """
        Manejador de evento para el botón "Añadir Capítulo".
        Solicita un título al usuario, crea un nuevo capítulo y actualiza la lista.

        Args:
            event (wx.CommandEvent): El evento del botón.
        """
        # Si no hay libro cargado, no se puede añadir un capítulo
        if self.book_id is None:
            return

        # Abre un diálogo para que el usuario introduzca el título del nuevo capítulo
        with wx.TextEntryDialog(self, "Título del nuevo capítulo:", "Añadir Capítulo") as dlg_title:
            # Si el usuario pulsa OK en el diálogo
            if dlg_title.ShowModal() == wx.ID_OK:
                # Obtiene el título introducido y elimina espacios en blanco al inicio/final
                title = dlg_title.GetValue().strip()
                # Valida que el título no esté vacío
                if not title:
                    wx.MessageBox("El título del capítulo no puede estar vacío.", "Error de Validación", wx.OK | wx.ICON_ERROR, self)
                    return # Sale si el título está vacío

                # Calcula el número del siguiente capítulo. Si ya hay capítulos, es el máximo + 1.
                next_chapter_number = 1
                if self.chapters_data:
                    # Encuentra el número de capítulo más alto existente y le suma 1
                    next_chapter_number = max(c['chapter_number'] for c in self.chapters_data) + 1

                # Llama al manejador de la aplicación para crear el nuevo capítulo en la base de datos
                new_chapter_id = self.app_handler.create_new_chapter(self.book_id, next_chapter_number, title)

                # Si la creación fue exitosa (se devolvió un ID)
                if new_chapter_id:
                    # Marca la aplicación como no modificada después de guardar el nuevo capítulo
                    self.app_handler.set_dirty(False)
                    # Recarga la lista de capítulos para mostrar el nuevo
                    self.load_chapters(self.book_id)

                    # Busca el índice del nuevo capítulo en la lista visual por su ID
                    new_idx = wx.NOT_FOUND
                    for i in range(self.chapter_list_ctrl.GetCount()):
                        if self.chapter_list_ctrl.GetClientData(i) == new_chapter_id:
                            new_idx = i
                            break # Sale del bucle una vez encontrado

                    # Si se encontró el nuevo capítulo en la lista
                    if new_idx != wx.NOT_FOUND:
                        # Selecciona el nuevo capítulo en la lista
                        self.chapter_list_ctrl.SetSelection(new_idx)
                        # Envía un evento de selección para notificar a los oyentes (como el callback)
                        wx.PostEvent(self.chapter_list_ctrl, wx.CommandEvent(wx.wxEVT_COMMAND_LISTBOX_SELECTED, self.chapter_list_ctrl.GetId()))

                    # REQ-Jefe-004: Eliminado wx.MessageBox de confirmación

    def on_delete_chapter(self, event: wx.CommandEvent):
        """
        Manejador de evento para el botón "Eliminar Capítulo".
        Confirma la eliminación con el usuario, elimina el capítulo y actualiza la lista.

        Args:
            event (wx.CommandEvent): El evento del botón.
        """
        # Si no hay libro cargado, no se puede eliminar un capítulo
        if self.book_id is None:
            return

        # Obtiene el índice del capítulo seleccionado en la lista
        selected_index = self.chapter_list_ctrl.GetSelection()
        # Si no hay capítulo seleccionado, muestra un mensaje de error
        if selected_index == wx.NOT_FOUND:
            wx.MessageBox("Por favor, seleccione un capítulo para eliminar.", "Sin Selección", wx.OK | wx.ICON_ERROR, self)
            return # Sale si no hay selección

        # Obtiene el ID del capítulo a eliminar (almacenado como ClientData)
        chapter_id_to_delete = self.chapter_list_ctrl.GetClientData(selected_index)
        # Obtiene el texto visible del capítulo seleccionado para mostrar en el mensaje de confirmación
        chapter_text = self.chapter_list_ctrl.GetString(selected_index)

        # Prepara el mensaje de confirmación para el usuario
        msg = f"¿Está seguro de que desea eliminar el capítulo:\n\n'{chapter_text}'?\n\nEsta acción es irreversible y también eliminará todo su contenido e ideas asociadas."
        # Muestra un diálogo de confirmación
        with wx.MessageDialog(self, msg, "Confirmar Eliminación de Capítulo", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING) as dlg:
            # Si el usuario confirma (pulsa YES)
            if dlg.ShowModal() == wx.ID_YES:
                # Llama al manejador de la aplicación para eliminar el capítulo de la base de datos
                success = self.app_handler.delete_chapter(chapter_id_to_delete)
                # Si la eliminación fue exitosa
                if success:
                    # Marca la aplicación como no modificada después de guardar los cambios
                    self.app_handler.set_dirty(False)
                    # Recarga la lista de capítulos para reflejar la eliminación
                    self.load_chapters(self.book_id)
                    # REQ-Jefe-004: Eliminado wx.MessageBox de confirmación

    def get_selected_chapter_id(self) -> Optional[int]:
        """
        Obtiene el ID del capítulo actualmente seleccionado en la lista.

        Returns:
            Optional[int]: El ID del capítulo seleccionado, o None si no hay selección.
        """
        # Obtiene el índice del elemento seleccionado
        idx = self.chapter_list_ctrl.GetSelection()
        # Si el índice es válido (no wx.NOT_FOUND), devuelve el ClientData (ID del capítulo),
        # de lo contrario, devuelve None.
        return self.chapter_list_ctrl.GetClientData(idx) if idx != wx.NOT_FOUND else None

    def select_chapter_by_id(self, chapter_id: Optional[int]):
        """
        Selecciona un capítulo en la lista basándose en su ID.
        Si chapter_id es None, deselecciona cualquier capítulo.

        Args:
            chapter_id (Optional[int]): El ID del capítulo a seleccionar, o None
                                        para deseleccionar.
        """
        # Si se pide deseleccionar
        if chapter_id is None:
            # Obtiene la selección actual
            current_selection = self.chapter_list_ctrl.GetSelection()
            # Si hay algo seleccionado, lo deselecciona
            if current_selection != wx.NOT_FOUND:
                self.chapter_list_ctrl.SetSelection(wx.NOT_FOUND)
                # Envía un evento de selección (con None) para notificar a los oyentes
                wx.PostEvent(self.chapter_list_ctrl, wx.CommandEvent(wx.wxEVT_COMMAND_LISTBOX_SELECTED, self.chapter_list_ctrl.GetId()))
            # Actualiza el estado de los botones
            self._update_button_states()
            return # Sale de la función

        # Si se pide seleccionar un capítulo por ID
        # Itera sobre todos los elementos de la lista
        for i in range(self.chapter_list_ctrl.GetCount()):
            # Compara el ClientData (ID del capítulo) del elemento actual con el ID buscado
            if self.chapter_list_ctrl.GetClientData(i) == chapter_id:
                # Si el elemento encontrado no es el que ya está seleccionado
                if self.chapter_list_ctrl.GetSelection() != i:
                    # Establece la selección en el índice encontrado
                    self.chapter_list_ctrl.SetSelection(i)
                    # Envía un evento de selección para notificar a los oyentes
                    wx.PostEvent(self.chapter_list_ctrl, wx.CommandEvent(wx.wxEVT_COMMAND_LISTBOX_SELECTED, self.chapter_list_ctrl.GetId()))
                else:
                    # Si ya estaba seleccionado, simplemente actualiza el estado de los botones
                    self._update_button_states()
                return # Sale de la función una vez que el capítulo es encontrado y seleccionado

        # Si el bucle termina y el capítulo con el ID dado no fue encontrado en la lista actual
        # Deselecciona cualquier capítulo que pudiera estar seleccionado previamente
        if self.chapter_list_ctrl.GetSelection() != wx.NOT_FOUND:
            self.chapter_list_ctrl.SetSelection(wx.NOT_FOUND)
            # Envía un evento de selección (con None) para notificar a los oyentes
            wx.PostEvent(self.chapter_list_ctrl, wx.CommandEvent(wx.wxEVT_COMMAND_LISTBOX_SELECTED, self.chapter_list_ctrl.GetId()))
        # Actualiza el estado de los botones
        self._update_button_states()