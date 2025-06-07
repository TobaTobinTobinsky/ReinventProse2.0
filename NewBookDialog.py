# -*- coding: utf-8 -*-
"""
Archivo: NewBookDialog.py
Descripción: Define un diálogo wxPython para crear un nuevo libro con campos esenciales (Título, Autor, Sinopsis).
Autor: AutoDoc AI
Fecha: 07/06/2025
Versión: 0.0.1
Licencia: MIT License
"""

import wx
from typing import Dict

class NewBookDialog(wx.Dialog):
    """
    Diálogo wxPython para recopilar la información esencial para crear un nuevo libro.

    Este diálogo solicita el Título (obligatorio), el Autor (obligatorio) y
    opcionalmente una Sinopsis. Realiza una validación básica para asegurar
    que los campos obligatorios no estén vacíos antes de permitir que el
    diálogo se cierre con éxito.
    """
    def __init__(self, parent, app_handler, dialog_title: str = "Nuevo Libro"):
        """
        Inicializa una nueva instancia del diálogo NewBookDialog.

        Args:
            parent: La ventana o widget padre de este diálogo.
            app_handler: Una instancia del manejador de la aplicación (AppHandler)
                         para posibles interacciones futuras (aunque no se usa
                         directamente en este diálogo simplificado).
            dialog_title (str, opcional): El texto que se mostrará en la barra
                                          de título del diálogo. Por defecto es
                                          "Nuevo Libro".
        """
        # Llama al constructor de la clase base wx.Dialog
        super().__init__(parent, id=wx.ID_ANY, title=dialog_title, size=(500, 350))
        # Almacena el manejador de la aplicación
        self.app_handler = app_handler

        # Crea y organiza los controles del diálogo
        self._create_controls()
        self._layout_controls()
        # Centra el diálogo respecto a su ventana padre
        self.CentreOnParent()

    def _create_controls(self):
        """
        Crea todos los controles (etiquetas, campos de texto, botones) que
        forman la interfaz del diálogo.
        """
        # Panel principal para contener los controles del formulario
        self.form_panel = wx.Panel(self)

        # Etiquetas para los campos de entrada
        self.title_label = wx.StaticText(self.form_panel, label="Título (*):")
        self.author_label = wx.StaticText(self.form_panel, label="Autor (*):")
        self.synopsis_label = wx.StaticText(self.form_panel, label="Sinopsis:")

        # Campos de entrada de texto
        self.title_ctrl = wx.TextCtrl(self.form_panel)
        self.author_ctrl = wx.TextCtrl(self.form_panel)
        # Campo de sinopsis con estilo multilinea y tamaño inicial
        self.synopsis_ctrl = wx.TextCtrl(self.form_panel, style=wx.TE_MULTILINE, size=(-1, 100))

        # Botones estándar del diálogo (Aceptar y Cancelar)
        self.ok_btn = wx.Button(self, id=wx.ID_OK, label="Aceptar")
        self.cancel_btn = wx.Button(self, id=wx.ID_CANCEL, label="Cancelar")

        # Vincula el evento de clic del botón Aceptar al método on_ok
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)

    def _layout_controls(self):
        """
        Organiza los controles creados en el diálogo utilizando sizers para
        gestionar su posición y tamaño.
        """
        # Sizer principal para el diálogo (vertical)
        main_dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        # Sizer para el contenido del formulario (rejilla flexible)
        form_content_sizer = wx.FlexGridSizer(rows=0, cols=2, vgap=10, hgap=10)
        # Permite que la segunda columna (índice 1) se expanda horizontalmente
        form_content_sizer.AddGrowableCol(1)

        # Añade los pares etiqueta-control al sizer de la rejilla
        # Título
        form_content_sizer.Add(self.title_label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        form_content_sizer.Add(self.title_ctrl, 1, wx.EXPAND)

        # Autor
        form_content_sizer.Add(self.author_label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        form_content_sizer.Add(self.author_ctrl, 1, wx.EXPAND)

        # Sinopsis
        form_content_sizer.Add(self.synopsis_label, 0, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.TOP, 5)
        form_content_sizer.Add(self.synopsis_ctrl, 1, wx.EXPAND)

        # Establece el sizer de la rejilla en el panel del formulario
        self.form_panel.SetSizer(form_content_sizer)
        # Añade el panel del formulario al sizer principal del diálogo
        main_dialog_sizer.Add(self.form_panel, 1, wx.EXPAND | wx.ALL, 15)

        # Sizer estándar para los botones del diálogo
        button_sizer = wx.StdDialogButtonSizer()
        # Añade los botones Aceptar y Cancelar al sizer de botones
        button_sizer.AddButton(self.ok_btn)
        button_sizer.AddButton(self.cancel_btn)
        # Realiza el layout de los botones
        button_sizer.Realize()
        # Añade el sizer de botones al sizer principal del diálogo
        main_dialog_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.TOP, 10)

        # Establece el sizer principal en el diálogo
        self.SetSizer(main_dialog_sizer)
        # Ajusta el tamaño del diálogo a su contenido
        self.Layout()

    def on_ok(self, event: wx.CommandEvent):
        """
        Maneja el evento de clic en el botón "Aceptar".

        Realiza la validación de los campos obligatorios (Título y Autor).
        Si algún campo obligatorio está vacío, muestra un mensaje de advertencia
        y no cierra el diálogo. Si ambos campos obligatorios están completos,
        cierra el diálogo con el código de retorno wx.ID_OK.

        Args:
            event (wx.CommandEvent): El evento de botón que desencadenó esta llamada.
        """
        # Obtiene el texto de los campos de título y autor, eliminando espacios en blanco iniciales/finales
        title = self.title_ctrl.GetValue().strip()
        author = self.author_ctrl.GetValue().strip()

        # Valida si el campo de título está vacío
        if not title:
            # Muestra un mensaje de advertencia si el título está vacío
            wx.MessageBox("Por favor, ingrese un título para el libro.",
                          "Campo Obligatorio - Título", wx.OK | wx.ICON_WARNING, self)
            # Establece el foco en el campo de título
            self.title_ctrl.SetFocus()
            # Detiene el procesamiento del evento para no cerrar el diálogo
            return

        # Valida si el campo de autor está vacío
        if not author:
            # Muestra un mensaje de advertencia si el autor está vacío
            wx.MessageBox("Por favor, ingrese un autor para el libro.",
                          "Campo Obligatorio - Autor", wx.OK | wx.ICON_WARNING, self)
            # Establece el foco en el campo de autor
            self.author_ctrl.SetFocus()
            # Detiene el procesamiento del evento
            return

        # Si ambos campos obligatorios están completos, cierra el diálogo con éxito
        self.EndModal(wx.ID_OK)

    def get_book_data(self) -> Dict[str, str]:
        """
        Recopila y devuelve los datos ingresados por el usuario en el diálogo.

        Incluye el título, autor y sinopsis ingresados. Para mantener la
        compatibilidad con una estructura de datos de libro más completa,
        incluye campos adicionales como 'prologue', 'back_cover_text' y
        'cover_image_path' con cadenas vacías, ya que no se solicitan en
        este diálogo simplificado.

        Returns:
            Dict[str, str]: Un diccionario donde las claves son los nombres
                            de los campos del libro y los valores son las
                            cadenas de texto ingresadas por el usuario o
                            cadenas vacías para los campos no solicitados.
        """
        # Crea un diccionario con los datos recopilados y campos vacíos para los no usados
        book_data: Dict[str, str] = {
            'title': self.title_ctrl.GetValue().strip(), # Obtiene y limpia el título
            'author': self.author_ctrl.GetValue().strip(), # Obtiene y limpia el autor
            'synopsis': self.synopsis_ctrl.GetValue().strip(), # Obtiene y limpia la sinopsis
            'prologue': "", # Campo no usado en este diálogo
            'back_cover_text': "", # Campo no usado
            'cover_image_path': "", # Campo no usado
        }
        return book_data

if __name__ == '__main__':
    # Este bloque se ejecuta solo cuando el script se ejecuta directamente
    # Proporciona un ejemplo simple de cómo usar el diálogo para pruebas.

    # Crea una instancia de la aplicación wx
    app = wx.App(False)
    # Crea una ventana principal simple (necesaria como padre para el diálogo)
    frame = wx.Frame(None, title="Test NewBookDialog (Simplificado)")

    # Clase dummy para simular el AppHandler requerido por el constructor del diálogo
    class DummyAppHandler:
        pass
    dummy_handler = DummyAppHandler()

    # Crea una instancia del diálogo NewBookDialog
    dialog = NewBookDialog(frame, dummy_handler, dialog_title="Crear Nuevo Libro (Simplificado)")
    # Muestra el diálogo de forma modal (bloquea la ventana padre hasta que se cierra)
    result = dialog.ShowModal()

    # Verifica el resultado del diálogo (si se cerró con Aceptar o Cancelar)
    if result == wx.ID_OK:
        # Si se presionó Aceptar, obtiene los datos ingresados
        data = dialog.get_book_data()
        print("Datos del libro (simplificado) guardados:")
        # Imprime los datos recopilados
        for key, value in data.items():
            print(f"  {key}: '{value}'")
    else:
        # Si se presionó Cancelar o se cerró de otra manera
        print("Creación de libro cancelada.")

    # Destruye el diálogo y la ventana principal para liberar recursos
    dialog.Destroy()
    frame.Destroy()
    # Inicia el bucle principal de eventos de wx (necesario para que la GUI funcione)
    app.MainLoop()