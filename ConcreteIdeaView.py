# -*- coding: utf-8 -*-
"""
File Name: ConcreteIdeaView.py
Descripción: Implementa una vista (panel wxPython) para mostrar y gestionar ideas concretas asociadas a un capítulo.
Author: AutoDoc AI
Date: 07/06/2025
Version: 0.0.1
License: MIT License
"""
import wx
from typing import List, Dict, Optional, Any

class ConcreteIdeaView(wx.Panel):
    """
    Panel wxPython que muestra una lista de ideas concretas para un capítulo seleccionado
    y proporciona botones para agregar, editar y eliminar ideas.

    Interactúa con un manejador de aplicación para cargar, guardar y modificar datos.
    """
    def __init__(self, parent: wx.Window, app_handler: Any):
        """
        Inicializa la vista de ideas concretas.

        Args:
            parent (wx.Window): La ventana padre de este panel.
            app_handler (Any): Una instancia del manejador de la aplicación que
                               proporciona métodos para interactuar con los datos.
        """
        super().__init__(parent)
        self.app_handler = app_handler # Referencia al manejador de la aplicación
        self.chapter_id: Optional[int] = None # ID del capítulo actualmente seleccionado
        self.ideas_data: List[Dict[str, Any]] = [] # Lista de diccionarios con los datos de las ideas (id, idea)

        self._create_controls() # Crea los widgets de la interfaz
        self._layout_controls() # Organiza los widgets en el panel

        # Carga inicial sin capítulo seleccionado
        self.load_ideas(None)

    def _create_controls(self):
        """
        Crea los controles (widgets) que componen la interfaz de usuario del panel.
        """
        self.info_label = wx.StaticText(self, label="Ideas Concretas del Capítulo:") # Etiqueta informativa
        self.concrete_idea_list_ctrl = wx.ListBox(self, style=wx.LB_SINGLE) # Lista para mostrar las ideas
        self.button_panel = wx.Panel(self) # Panel contenedor para los botones

        # Botones de acción
        self.add_button = wx.Button(self.button_panel, label="Agregar")
        self.edit_button = wx.Button(self.button_panel, label="Editar")
        self.delete_button = wx.Button(self.button_panel, label="Eliminar")

        # Enlazar eventos de botones a sus manejadores
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_button_click)
        self.edit_button.Bind(wx.EVT_BUTTON, self.on_edit_button_click)
        self.delete_button.Bind(wx.EVT_BUTTON, self.on_delete_button_click)

        # Enlazar eventos de la lista
        self.concrete_idea_list_ctrl.Bind(wx.EVT_LISTBOX_DCLICK, self.on_edit_button_click) # Doble click edita
        self.concrete_idea_list_ctrl.Bind(wx.EVT_LISTBOX, self.on_list_selection_changed) # Selección cambia estado de botones

    def _layout_controls(self):
        """
        Organiza los controles dentro del panel utilizando sizers.
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL) # Sizer principal vertical

        # Añadir etiqueta informativa
        main_sizer.Add(self.info_label, 0, wx.ALL | wx.EXPAND, 5)

        list_sizer = wx.BoxSizer(wx.HORIZONTAL) # Sizer horizontal para lista y botones
        # Añadir lista (expande horizontal y verticalmente)
        list_sizer.Add(self.concrete_idea_list_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)

        button_sizer = wx.BoxSizer(wx.VERTICAL) # Sizer vertical para los botones
        # Añadir botones al sizer de botones
        button_sizer.Add(self.add_button, 0, wx.EXPAND | wx.BOTTOM, 5)
        button_sizer.Add(self.edit_button, 0, wx.EXPAND | wx.BOTTOM, 5)
        button_sizer.Add(self.delete_button, 0, wx.EXPAND)

        # Establecer el sizer para el panel de botones
        self.button_panel.SetSizer(button_sizer)

        # Añadir el panel de botones al sizer horizontal (alineado arriba)
        list_sizer.Add(self.button_panel, 0, wx.ALIGN_TOP)

        # Añadir el sizer horizontal al sizer principal (expande horizontal y verticalmente)
        main_sizer.Add(list_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # Establecer el sizer principal para el panel
        self.SetSizer(main_sizer)

        # Actualizar el estado inicial de los botones
        self._update_button_states()

    def _update_button_states(self):
        """
        Actualiza el estado de habilitación/deshabilitación de los botones
        basándose en si hay un capítulo seleccionado, si hay un elemento
        seleccionado en la lista y si la vista general está habilitada.
        """
        view_enabled = self.IsEnabled() # Verifica si el panel ConcreteIdeaView está habilitado globalmente
        has_chapter = self.chapter_id is not None # Verifica si hay un capítulo cargado
        selection_index = self.concrete_idea_list_ctrl.GetSelection() # Obtiene el índice seleccionado
        has_selection = selection_index != wx.NOT_FOUND # Verifica si hay algún elemento seleccionado

        # Habilitar/deshabilitar botones según las condiciones
        self.add_button.Enable(view_enabled and has_chapter)
        self.edit_button.Enable(view_enabled and has_chapter and has_selection)
        self.delete_button.Enable(view_enabled and has_chapter and has_selection)
        # La lista también se deshabilita si no hay capítulo o la vista no está habilitada
        self.concrete_idea_list_ctrl.Enable(view_enabled and has_chapter)


    def on_list_selection_changed(self, event: wx.Event):
        """
        Manejador de evento para cuando cambia la selección en la lista de ideas.
        Actualiza el estado de los botones.

        Args:
            event (wx.Event): El evento de cambio de selección.
        """
        self._update_button_states() # Re-evalúa el estado de los botones
        event.Skip() # Permite que el evento se propague si es necesario

    def load_ideas(self, chapter_id: Optional[int]):
        """
        Carga las ideas concretas para un capítulo dado.

        Limpia la lista actual, actualiza la etiqueta informativa y carga
        las ideas desde el manejador de la aplicación si se proporciona un chapter_id.

        Args:
            chapter_id (Optional[int]): El ID del capítulo cuyas ideas se cargarán,
                                        o None para limpiar la vista.
        """
        self.chapter_id = chapter_id # Almacena el ID del capítulo actual
        self.concrete_idea_list_ctrl.Clear() # Limpia la lista visual
        self.ideas_data.clear() # Limpia los datos internos

        is_chapter_present = self.chapter_id is not None # Bandera para saber si hay capítulo

        # Actualiza la etiqueta informativa
        self.info_label.SetLabel("Ideas Concretas:" if is_chapter_present else "Ideas Concretas: (Seleccione un capítulo)")

        # Si hay un capítulo, carga las ideas
        if is_chapter_present:
            raw_ideas = self.app_handler.get_concrete_ideas_for_chapter(self.chapter_id) # Obtiene ideas del manejador
            if raw_ideas:
                # Añade cada idea a los datos internos y a la lista visual
                for idea_dict in raw_ideas:
                    self.ideas_data.append({'id': idea_dict['id'], 'idea': idea_dict['idea']})
                    self.concrete_idea_list_ctrl.Append(idea_dict['idea'])

        # Actualiza el estado de los botones y redibuja el layout
        self._update_button_states()
        self.Layout()

    def _add_idea_to_list(self, idea_id: int, idea_text: str):
        """
        Añade una nueva idea a los datos internos y a la lista visual.

        Args:
            idea_id (int): El ID de la nueva idea.
            idea_text (str): El texto de la nueva idea.
        """
        self.ideas_data.append({'id': idea_id, 'idea': idea_text}) # Añade a los datos internos
        self.concrete_idea_list_ctrl.Append(idea_text) # Añade a la lista visual
        self._update_button_states() # Actualiza el estado de los botones

    def _edit_idea_in_list(self, index: int, new_idea_text: str):
        """
        Edita una idea existente en los datos internos y en la lista visual por índice.

        Args:
            index (int): El índice de la idea a editar.
            new_idea_text (str): El nuevo texto para la idea.
        """
        # Verifica que el índice sea válido
        if 0 <= index < len(self.ideas_data):
            self.ideas_data[index]['idea'] = new_idea_text # Actualiza en los datos internos
            self.concrete_idea_list_ctrl.SetString(index, new_idea_text) # Actualiza en la lista visual
            self._update_button_states() # Actualiza el estado de los botones

    def _delete_idea_from_list(self, index: int):
        """
        Elimina una idea de los datos internos y de la lista visual por índice.

        Args:
            index (int): El índice de la idea a eliminar.
        """
        # Verifica que el índice sea válido
        if 0 <= index < len(self.ideas_data):
            del self.ideas_data[index] # Elimina de los datos internos
            self.concrete_idea_list_ctrl.Delete(index) # Elimina de la lista visual
            self._update_button_states() # Actualiza el estado de los botones

    def on_add_button_click(self, event: wx.Event):
        """
        Manejador de evento para el botón "Agregar".
        Abre un diálogo para ingresar una nueva idea y la añade si es válida.

        Args:
            event (wx.Event): El evento de click del botón.
        """
        # Verifica si hay un capítulo seleccionado y si la vista está habilitada
        if self.chapter_id is None or not self.IsEnabled():
            return

        # Abre un diálogo de entrada de texto
        with wx.TextEntryDialog(self, "Nueva idea concreta:", "Agregar Idea") as dlg:
            if dlg.ShowModal() == wx.ID_OK: # Si el usuario presiona OK
                new_idea_text = dlg.GetValue().strip() # Obtiene el texto y elimina espacios

                if new_idea_text: # Si el texto no está vacío
                    # Intenta añadir la idea a través del manejador de la aplicación
                    idea_id = self.app_handler.add_concrete_idea_for_chapter(self.chapter_id, new_idea_text)
                    if idea_id:
                        # Si se añadió con éxito, actualiza la lista visual y marca como sucio
                        self._add_idea_to_list(idea_id, new_idea_text)
                        self.app_handler.set_dirty(True) # Indica que los datos han cambiado
                        wx.Bell() # Emite un sonido para notificar
                    else:
                        # Muestra un mensaje de error si no se pudo añadir
                        wx.MessageBox(f"No se pudo agregar la idea.", "Error", wx.OK | wx.ICON_ERROR, self)
                else:
                    # Muestra un mensaje si el texto está vacío
                    wx.MessageBox("La idea no puede estar vacía.", "Info", wx.OK | wx.ICON_INFORMATION, self)

    def on_edit_button_click(self, event: wx.Event):
        """
        Manejador de evento para el botón "Editar" o doble click en la lista.
        Abre un diálogo para editar la idea seleccionada.

        Args:
            event (wx.Event): El evento de click del botón o doble click en la lista.
        """
        # Verifica si hay un capítulo seleccionado y si la vista está habilitada
        if self.chapter_id is None or not self.IsEnabled():
            return

        selected_index = self.concrete_idea_list_ctrl.GetSelection() # Obtiene el índice seleccionado

        # Verifica si hay un elemento seleccionado
        if selected_index == wx.NOT_FOUND:
            wx.MessageBox("Seleccione una idea para editar.", "Info", wx.OK | wx.ICON_INFORMATION, self)
            return

        # Obtiene los datos de la idea seleccionada
        idea_to_edit_dict = self.ideas_data[selected_index]
        current_idea_text = idea_to_edit_dict['idea']
        idea_id_to_edit = idea_to_edit_dict['id']

        # Abre un diálogo de entrada de texto con el valor actual
        with wx.TextEntryDialog(self, "Editar idea concreta:", "Editar Idea", current_idea_text) as dlg:
            if dlg.ShowModal() == wx.ID_OK: # Si el usuario presiona OK
                updated_idea_text = dlg.GetValue().strip() # Obtiene el nuevo texto

                # Verifica si el texto ha cambiado y no está vacío
                if updated_idea_text and updated_idea_text != current_idea_text:
                    # Intenta actualizar la idea a través del manejador
                    success = self.app_handler.update_concrete_idea_text(idea_id_to_edit, updated_idea_text)
                    if success:
                        # Si se actualizó con éxito, actualiza la lista visual y marca como sucio
                        self._edit_idea_in_list(selected_index, updated_idea_text)
                        self.app_handler.set_dirty(True) # Indica que los datos han cambiado
                    else:
                        # Muestra un mensaje de error si no se pudo editar
                        wx.MessageBox(f"No se pudo editar la idea.", "Error", wx.OK | wx.ICON_ERROR, self)
                elif not updated_idea_text:
                    # Muestra un mensaje si el texto queda vacío
                    wx.MessageBox("La idea no puede quedar vacía.", "Info", wx.OK | wx.ICON_INFORMATION, self)

    def on_delete_button_click(self, event: wx.Event):
        """
        Manejador de evento para el botón "Eliminar".
        Pide confirmación y elimina la idea seleccionada.

        Args:
            event (wx.Event): El evento de click del botón.
        """
        # Verifica si hay un capítulo seleccionado y si la vista está habilitada
        if self.chapter_id is None or not self.IsEnabled():
            return

        selected_index = self.concrete_idea_list_ctrl.GetSelection() # Obtiene el índice seleccionado

        # Verifica si hay un elemento seleccionado
        if selected_index == wx.NOT_FOUND:
            wx.MessageBox("Seleccione una idea para eliminar.", "Info", wx.OK | wx.ICON_INFORMATION, self)
            return

        # Obtiene los datos de la idea seleccionada
        idea_to_delete_dict = self.ideas_data[selected_index]
        idea_id_to_delete = idea_to_delete_dict['id']
        idea_text_to_delete = idea_to_delete_dict['idea']

        # Prepara el mensaje de confirmación
        msg = f"¿Eliminar la idea concreta:\n\n'{idea_text_to_delete}'?"

        # Abre un diálogo de confirmación
        with wx.MessageDialog(self, msg, "Confirmar Eliminación", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING) as dlg:
            if dlg.ShowModal() == wx.ID_YES: # Si el usuario confirma
                # Intenta eliminar la idea a través del manejador
                success = self.app_handler.delete_concrete_idea_by_id(idea_id_to_delete)
                if success:
                    # Si se eliminó con éxito, actualiza la lista visual y marca como sucio
                    self._delete_idea_from_list(selected_index)
                    self.app_handler.set_dirty(True) # Indica que los datos han cambiado
                else:
                    # Muestra un mensaje de error si no se pudo eliminar
                    wx.MessageBox(f"No se pudo eliminar la idea.", "Error", wx.OK | wx.ICON_ERROR, self)

    def enable_view(self, enable: bool):
        """
        Habilita o deshabilita la interacción con esta vista.

        Controla la habilitación de la lista y los botones.

        Args:
            enable (bool): True para habilitar la vista, False para deshabilitarla.
        """
        # La lista se habilita solo si la vista se habilita Y hay un capítulo seleccionado
        self.concrete_idea_list_ctrl.Enable(enable and self.chapter_id is not None)

        # Los botones se actualizan a través de _update_button_states, que ya considera self.IsEnabled().
        # Sin embargo, si se llama a enable_view(False) para "bloquear" lógicamente la vista,
        # deshabilitamos explícitamente los botones.
        if not enable:
            self.add_button.Enable(False)
            self.edit_button.Enable(False)
            self.delete_button.Enable(False)
        else:
            # Si se habilita la vista, re-evaluamos el estado de los botones
            # basándonos en la selección actual y si hay capítulo.
            self._update_button_states()