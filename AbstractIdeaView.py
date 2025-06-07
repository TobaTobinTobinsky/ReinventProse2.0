# -*- coding: utf-8 -*-
"""
File Name: AbstractIdeaView.py
Description: Implementa un panel de wxPython para visualizar y editar la idea abstracta de un capítulo.
Author: AutoDoc AI
Date: 07/06/2025
Version: 0.0.1
License: MIT License
"""
import wx
from typing import Optional

class AbstractIdeaView(wx.Panel):
    """
    Panel de wxPython para gestionar la visualización y edición de la idea abstracta de un capítulo.

    Este panel contiene un control de texto multilinea para la idea abstracta
    y gestiona su estado de "sucio" (dirty) para indicar cambios no guardados.
    Interactúa con un manejador de aplicación para cargar y guardar datos.
    """
    def __init__(self, parent, app_handler):
        """
        Inicializa el panel AbstractIdeaView.

        Args:
            parent: La ventana padre de este panel.
            app_handler: Una instancia del manejador de la aplicación para interactuar
                         con los datos y el estado global.
        """
        super().__init__(parent)
        self.app_handler = app_handler
        # ID del capítulo actualmente cargado, None si no hay capítulo seleccionado
        self.chapter_id: Optional[int] = None
        # Bandera que indica si la vista tiene cambios no guardados
        self._is_dirty_view: bool = False
        # Bandera para evitar marcar la vista como sucia durante la carga de datos
        self._loading_data: bool = False
        self._create_controls()
        self._layout_controls()
        # Carga inicial sin capítulo seleccionado
        self.load_idea(None)

    def _create_controls(self):
        """
        Crea los controles visuales para el panel.

        Incluye el control de texto para la idea abstracta.
        """
        # Control de texto multilinea para la idea abstracta
        self.abstract_idea_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        # Vincula el evento de cambio de texto al manejador correspondiente
        self.abstract_idea_ctrl.Bind(wx.EVT_TEXT, self.on_text_changed)

    def _layout_controls(self):
        """
        Organiza los controles visuales dentro del panel usando sizers.
        """
        # Sizer principal vertical
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        # Etiqueta para el campo de texto
        main_sizer.Add(wx.StaticText(self, label="Idea Abstracta del Capítulo:"), 0, wx.ALL, 5)
        # Añade el control de texto, expandiéndose vertical y horizontalmente
        main_sizer.Add(self.abstract_idea_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        # Establece el sizer para el panel
        self.SetSizer(main_sizer)

    def _set_view_dirty(self, is_dirty: bool = True):
        """
        Establece el estado de "sucio" (dirty) de la vista.

        Si el estado cambia a sucio, notifica al manejador de la aplicación.

        Args:
            is_dirty: Booleano que indica si la vista debe marcarse como sucia (True)
                      o limpia (False). Por defecto es True.
        """
        # Solo actualiza si el estado cambia
        if self._is_dirty_view != is_dirty:
            self._is_dirty_view = is_dirty
            # Si la vista se marca como sucia, notifica al manejador global
            if self._is_dirty_view:
                self.app_handler.set_dirty(True)

    def load_idea(self, chapter_id: Optional[int]):
        """
        Carga la idea abstracta para un capítulo específico.

        Si chapter_id es None, limpia el control de texto y lo deshabilita.
        Si chapter_id es válido, carga la idea abstracta del manejador de aplicación.

        Args:
            chapter_id: El ID del capítulo cuya idea abstracta se va a cargar,
                        o None para limpiar la vista.
        """
        # Establece la bandera de carga para evitar marcar como sucio
        self._loading_data = True
        self.chapter_id = chapter_id
        # Limpia el control de texto
        self.abstract_idea_ctrl.SetValue("")
        # Determina si hay un capítulo seleccionado
        is_chapter_present = self.chapter_id is not None

        # Habilita o deshabilita el control de texto basado en si hay un capítulo
        self.abstract_idea_ctrl.Enable(is_chapter_present)

        # Si hay un capítulo, intenta cargar sus detalles
        if is_chapter_present:
            chapter_details = self.app_handler.get_chapter_details(self.chapter_id)
            # Si se encontraron detalles y contienen la idea abstracta
            if chapter_details and 'abstract_idea' in chapter_details:
                # Establece el valor del control de texto (usa "" si el valor es None)
                self.abstract_idea_ctrl.SetValue(chapter_details['abstract_idea'] or "")
            # Si no se encontraron detalles para el ID proporcionado
            elif chapter_details is None:
                print(f"Advertencia (AbstractIdeaView): No se encontraron detalles para capítulo ID {self.chapter_id}")

        # Mueve el punto de inserción al inicio del texto
        self.abstract_idea_ctrl.SetInsertionPoint(0)
        # Resetea el estado de sucio después de cargar
        self._is_dirty_view = False
        # Desactiva la bandera de carga
        self._loading_data = False

    def save_changes(self) -> bool:
        """
        Guarda los cambios en la idea abstracta si la vista está sucia y hay un capítulo seleccionado.

        Delega el guardado al manejador de la aplicación.

        Returns:
            True si los cambios se guardaron exitosamente, False en caso contrario
            (no hay cambios, no hay capítulo, o el manejador falló).
        """
        # No guarda si la vista no está sucia o no hay capítulo seleccionado
        if not self._is_dirty_view or self.chapter_id is None:
            return False

        # Llama al manejador para actualizar la idea abstracta del capítulo
        success = self.app_handler.update_chapter_abstract_idea_via_handler(
            chapter_id=self.chapter_id, abstract_idea=self.abstract_idea_ctrl.GetValue()
        )
        # Si el guardado fue exitoso, marca la vista como limpia
        if success:
            self._set_view_dirty(False)
            return True
        # Retorna False si el guardado falló
        return False

    def on_text_changed(self, event):
        """
        Manejador de evento para cambios en el texto del control de idea abstracta.

        Marca la vista como sucia si no está en proceso de carga de datos
        y el control está habilitado.

        Args:
            event: El evento wx.EVT_TEXT.
        """
        # Ignora el evento si se están cargando datos o el control está deshabilitado
        if self._loading_data or not self.abstract_idea_ctrl.IsEnabled():
            event.Skip()
            return
        # Marca la vista como sucia
        self._set_view_dirty(True)
        event.Skip() # Permite que el evento continúe su procesamiento

    def is_dirty(self) -> bool:
        """
        Verifica si la vista tiene cambios no guardados.

        Returns:
            True si la vista está marcada como sucia, False en caso contrario.
        """
        return self._is_dirty_view

    def enable_view(self, enable: bool):
        """
        Habilita o deshabilita la interacción con el control principal de esta vista.

        El control de texto solo se habilita si 'enable' es True Y hay un capítulo seleccionado.

        Args:
            enable: Booleano que indica si la vista debe habilitarse (True)
                    o deshabilitarse (False).
        """
        # Habilita el control de texto solo si se pide habilitar Y hay un capítulo cargado
        self.abstract_idea_ctrl.Enable(enable and self.chapter_id is not None)
        # No hay otros controles interactivos aquí además del TextCtrl.