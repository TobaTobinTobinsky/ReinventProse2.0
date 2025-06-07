# -*- coding: utf-8 -*-
"""
Archivo: LibraryView.py
Propósito: Vista que muestra la colección de libros como tarjetas en "ReinventProse 2.0".
Gestiona dinámicamente su layout entre una vista central (WrapSizer) y una
vista lateral (BoxSizer vertical).
Autor: AutoDoc AI
Fecha: 07/06/2025
Versión: 0.0.1
Licencia: MIT License
"""

import wx
import wx.lib.scrolledpanel as scrolled
from Util import load_image, create_placeholder_bitmap
from typing import Callable, Optional, List, Dict, Any

# Constante para el nombre de la aplicación, usada en mensajes.
APP_NAME = "ReinventProse 2.0"

class BookCardPanel(wx.Panel):
    """
    Representa un panel individual que muestra la información de un libro
    en formato de tarjeta visual.

    Permite mostrar la portada, título y autor del libro, y responde a clics.
    Soporta un estilo visual activo/inactivo.
    """
    # Dimensiones y colores constantes para la apariencia de la tarjeta.
    CARD_WIDTH = 150
    IMAGE_WIDTH = 100
    IMAGE_HEIGHT = 150
    ACTIVE_BG_COLOUR = wx.Colour(220, 235, 255)
    INACTIVE_BG_COLOUR = wx.Colour(255, 255, 255)
    ACTIVE_BORDER_COLOUR = wx.Colour(0, 0, 128)
    INACTIVE_BORDER_COLOUR = wx.Colour(180, 180, 180)
    ACTIVE_BORDER_WIDTH = 2
    INACTIVE_BORDER_WIDTH = 1

    def __init__(self, parent: wx.Window, book: dict, app_handler: Any, on_card_selected_callback: Callable[[int], None]):
        """
        Inicializa una nueva instancia de BookCardPanel.

        Args:
            parent (wx.Window): La ventana padre para este panel.
            book (dict): Un diccionario que contiene los datos del libro (debe incluir 'id', 'title', 'author', opcionalmente 'cover_image_path').
            app_handler (Any): Una referencia al manejador principal de la aplicación (usado para acceder a datos o lógica si es necesario, aunque no directamente en esta clase).
            on_card_selected_callback (Callable[[int], None]): Una función de callback que se llama cuando se hace clic en la tarjeta, pasando el ID del libro.
        """
        # Llama al constructor de la clase base wx.Panel.
        super().__init__(parent, style=wx.BORDER_NONE)

        # Almacena las referencias y datos del libro.
        self.book = book
        self.app_handler = app_handler
        self.on_card_selected_callback = on_card_selected_callback

        # Estado inicial del estilo y configuración de dibujado.
        self.is_active_style = False
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT) # Indica que el fondo se dibujará manualmente.
        self.SetMinSize(wx.Size(self.CARD_WIDTH, -1)) # Establece el ancho mínimo de la tarjeta.

        # Crea y organiza los controles internos.
        self._create_controls()
        self._layout_controls()

        # Establece el estilo inicial como inactivo.
        self.set_active_style(False)

        # Vincula los eventos de clic y pintado.
        self.Bind(wx.EVT_LEFT_DOWN, self.on_internal_card_click)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def _create_controls(self):
        """
        Crea los controles internos del panel de la tarjeta (imagen, título, autor).
        """
        # Carga la imagen de portada o crea un placeholder si falla.
        img_bitmap = load_image(self.book.get('cover_image_path', ''))
        if img_bitmap and img_bitmap.IsOk():
            # Escala la imagen al tamaño deseado.
            image = img_bitmap.ConvertToImage().Rescale(self.IMAGE_WIDTH, self.IMAGE_HEIGHT, wx.IMAGE_QUALITY_HIGH)
            self.cover_image_ctrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(image))
        else:
            # Crea un bitmap placeholder si no hay imagen válida.
            self.cover_image_ctrl = wx.StaticBitmap(self, wx.ID_ANY, create_placeholder_bitmap(self.IMAGE_WIDTH, self.IMAGE_HEIGHT, "Portada"))

        # Crea las etiquetas para el título y el autor.
        self.title_label = wx.StaticText(self, label=self.book['title'], style=wx.ALIGN_CENTER_HORIZONTAL | wx.ST_NO_AUTORESIZE)
        self.title_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)) # Fuente para el título.
        self.author_label = wx.StaticText(self, label="por " + self.book['author'], style=wx.ALIGN_CENTER_HORIZONTAL | wx.ST_NO_AUTORESIZE)
        self.author_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)) # Fuente para el autor.

        # Vincula el evento de clic a los controles internos para que toda la tarjeta sea clicable.
        self.cover_image_ctrl.Bind(wx.EVT_LEFT_DOWN, self.on_internal_card_click)
        self.title_label.Bind(wx.EVT_LEFT_DOWN, self.on_internal_card_click)
        self.author_label.Bind(wx.EVT_LEFT_DOWN, self.on_internal_card_click)

    def _layout_controls(self):
        """
        Organiza los controles internos usando un BoxSizer vertical.
        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        # Añade la imagen con alineación central y margen.
        sizer.Add(self.cover_image_ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        # Añade el título con expansión horizontal y margen.
        sizer.Add(self.title_label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        # Añade el autor con expansión horizontal y margen.
        sizer.Add(self.author_label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Establece el sizer para el panel.
        self.SetSizer(sizer)

        # Ajusta el texto de las etiquetas para que quepa dentro del ancho de la tarjeta.
        self.title_label.Wrap(self.CARD_WIDTH - 10)
        self.author_label.Wrap(self.CARD_WIDTH - 10)

    def on_internal_card_click(self, event: wx.MouseEvent):
        """
        Maneja el evento de clic del ratón en la tarjeta o sus controles internos.

        Llama a la función de callback proporcionada durante la inicialización.

        Args:
            event (wx.MouseEvent): El evento de clic del ratón.
        """
        # Llama al callback si está definido, pasando el ID del libro.
        if self.on_card_selected_callback:
            self.on_card_selected_callback(self.book['id'])
        # Detiene la propagación del evento para evitar que llegue al padre.
        event.StopPropagation()

    def set_active_style(self, is_active: bool):
        """
        Establece el estilo visual de la tarjeta a activo o inactivo.

        Args:
            is_active (bool): True para aplicar el estilo activo, False para el inactivo.
        """
        # Solo actualiza y refresca si el estado cambia.
        if self.is_active_style != is_active:
            self.is_active_style = is_active
            self.Refresh() # Fuerza un evento de pintado para redibujar la tarjeta.

    def on_paint(self, event: wx.PaintEvent):
        """
        Maneja el evento de pintado para dibujar el fondo y el borde de la tarjeta
        con esquinas redondeadas, aplicando el estilo activo o inactivo.

        Args:
            event (wx.PaintEvent): El evento de pintado.
        """
        # Crea un contexto de pintado con doble buffer para evitar parpadeo.
        dc = wx.AutoBufferedPaintDC(self)
        # Crea un contexto gráfico para dibujar formas vectoriales.
        gc = wx.GraphicsContext.Create(dc)

        if gc:
            # Obtiene las dimensiones del panel.
            width, height = self.GetClientSize()
            # Crea un camino gráfico para un rectángulo con esquinas redondeadas.
            path = gc.CreatePath()
            # Dibuja el rectángulo ligeramente desplazado para que el borde completo sea visible.
            path.AddRoundedRectangle(0.5, 0.5, width - 1, height - 1, 3)

            # Configura el pincel y la pluma según el estado activo/inactivo.
            if self.is_active_style:
                gc.SetBrush(wx.Brush(self.ACTIVE_BG_COLOUR))
                gc.SetPen(wx.Pen(self.ACTIVE_BORDER_COLOUR, self.ACTIVE_BORDER_WIDTH))
            else:
                gc.SetBrush(wx.Brush(self.INACTIVE_BG_COLOUR))
                gc.SetPen(wx.Pen(self.INACTIVE_BORDER_COLOUR, self.INACTIVE_BORDER_WIDTH))

            # Rellena y traza el camino (el rectángulo redondeado).
            gc.FillPath(path)
            gc.StrokePath(path)


class LibraryView(scrolled.ScrolledPanel):
    """
    Un panel desplazable que actúa como contenedor para mostrar una colección
    de BookCardPanels.

    Permite alternar entre dos modos de layout: uno central que envuelve las
    tarjetas (WrapSizer) y uno lateral vertical (BoxSizer).
    """
    def __init__(self, parent: wx.Window, app_handler: Any):
        """
        Inicializa una nueva instancia de LibraryView.

        Args:
            parent (wx.Window): La ventana padre para este panel.
            app_handler (Any): Una referencia al manejador principal de la aplicación,
                               usado para obtener la lista de libros.
        """
        # Llama al constructor de la clase base scrolled.ScrolledPanel.
        super().__init__(parent, style=wx.BORDER_NONE)

        # Almacena la referencia al manejador de la aplicación.
        self.app_handler = app_handler

        # Lista para mantener referencias a las tarjetas de libros creadas.
        self.book_card_panels: List[BookCardPanel] = []
        # Callback para manejar la selección de una tarjeta de libro.
        self.on_book_card_selected_callback: Optional[Callable[[int], None]] = None

        # Bandera para rastrear el modo de layout actual.
        self.current_is_sidebar_layout = False

        # Establece el color de fondo del panel.
        self.SetBackgroundColour(wx.Colour(240, 240, 240))

        # Crea los dos sizers posibles para los layouts.
        self.wrap_sizer = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)
        self.box_sizer_vertical = wx.BoxSizer(wx.VERTICAL)

        # Crea el widget que se muestra cuando no hay libros.
        self._no_books_message_widget = self._create_no_books_message_widget()
        # Inicialmente, el widget de mensaje está oculto.
        self._no_books_message_widget.Show(False)

        # Establece el sizer inicial (por defecto, el wrap_sizer para la vista central).
        self.SetSizer(self.wrap_sizer)

        # Configura el desplazamiento del panel (solo vertical).
        self.SetupScrolling(scroll_x=False, scroll_y=True, rate_x=1, rate_y=1)

    def _create_no_books_message_widget(self) -> wx.Panel:
        """
        Crea y configura un panel con un mensaje centrado para mostrar
        cuando la biblioteca está vacía.

        Returns:
            wx.Panel: El panel que contiene el mensaje.
        """
        panel = wx.Panel(self)
        # Etiqueta de texto inicial (el texto se actualiza en load_books).
        text_label = wx.StaticText(panel, label="Placeholder - este texto se cambiará")
        text_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        # Sizer para centrar el texto verticalmente dentro del panel de mensaje.
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1) # Espaciador superior.
        sizer.Add(text_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5) # Etiqueta centrada.
        sizer.AddStretchSpacer(1) # Espaciador inferior.
        panel.SetSizer(sizer)
        return panel

    def _clear_and_destroy_book_cards(self):
        """
        Destruye todas las instancias de BookCardPanel existentes y limpia
        la lista interna que las referencia.

        Este método se usa antes de repoblar la vista o cambiar de layout.
        No afecta al widget de mensaje "no hay libros".
        """
        # Itera sobre la lista de tarjetas.
        for card in self.book_card_panels:
            card.Destroy() # Llama al método Destroy() de cada panel wx.
        # Limpia la lista de referencias.
        self.book_card_panels.clear()

    def set_on_book_card_selected_callback(self, callback: Callable[[int], None]):
        """
        Establece la función de callback que se ejecutará cuando se seleccione
        una tarjeta de libro (haciendo clic en ella).

        Args:
            callback (Callable[[int], None]): La función a llamar, que recibe el ID del libro.
        """
        self.on_book_card_selected_callback = callback

    def set_layout_mode(self, is_sidebar: bool):
        """
        Establece el modo de layout de la vista de la biblioteca.

        Alterna entre el layout central (WrapSizer) y el layout lateral
        (BoxSizer vertical). Gestiona la transición de elementos entre sizers.

        Args:
            is_sidebar (bool): True para usar el layout lateral (sidebar),
                               False para usar el layout central.
        """
        # Si el layout ya es el solicitado, simplemente actualiza y sale.
        if self.current_is_sidebar_layout == is_sidebar:
            self.Layout()
            self.FitInside() # Asegura que el ScrolledPanel ajuste su tamaño interno.
            return

        # Congela la ventana para evitar parpadeo durante la actualización.
        self.Freeze()
        try:
            # Limpiar y destruir tarjetas existentes antes de cambiar de sizer.
            self._clear_and_destroy_book_cards()

            # Determinar cuál es el sizer actual y cuál será el nuevo.
            old_sizer = self.GetSizer()
            new_sizer: wx.Sizer

            if is_sidebar:
                new_sizer = self.box_sizer_vertical
                self.current_is_sidebar_layout = True
            else:
                new_sizer = self.wrap_sizer
                self.current_is_sidebar_layout = False

            # Asegurarse de que ambos sizers estén vacíos de SizerItems.
            # delete_windows=False es crucial aquí porque las BookCardPanel
            # ya fueron destruidas por _clear_and_destroy_book_cards, y
            # _no_books_message_widget es reutilizable y se gestiona explícitamente.
            if old_sizer:
                old_sizer.Clear(delete_windows=False)
            # Limpiar el nuevo sizer también por si acaso contenía algo residual.
            new_sizer.Clear(delete_windows=False)

            # Ocultar el widget de mensaje "no hay libros" antes de cambiar de sizer.
            # load_books() decidirá si mostrarlo en el nuevo sizer.
            self._no_books_message_widget.Show(False)

            # Establece el nuevo sizer para el panel. deleteOld=False para no destruir los objetos sizer.
            self.SetSizer(new_sizer, deleteOld=False)

            # Vuelve a cargar los libros. Esto poblará el nuevo sizer activo.
            self.load_books()

            # Reconfigura el desplazamiento si es necesario (aunque aquí siempre es vertical).
            self.SetupScrolling(scroll_x=False, scroll_y=True)
        finally:
            # Descongela la ventana.
            self.Thaw()

        # Fuerza la actualización del layout y el ajuste del panel desplazable.
        self.Layout()
        self.FitInside()
        self.Refresh() # Fuerza un redibujado.


    def load_books(self):
        """
        Carga la lista de libros desde el manejador de la aplicación, crea
        BookCardPanels para cada libro y los añade al sizer actualmente activo.

        Si no hay libros, muestra un mensaje indicando que la biblioteca está vacía.
        """
        # Congela la ventana para evitar parpadeo.
        self.Freeze()
        try:
            # Obtiene el sizer actualmente activo.
            active_sizer = self.GetSizer()
            if not active_sizer:
                # Si no hay sizer, no hay nada que hacer.
                self.Thaw()
                return

            # Limpiar y destruir las tarjetas existentes.
            self._clear_and_destroy_book_cards()
            # Asegurarse de que el mensaje "no hay libros" no esté en el sizer
            # si se va a repoblar con tarjetas.
            if active_sizer.GetItem(self._no_books_message_widget):
                active_sizer.Detach(self._no_books_message_widget)
            # Asegurarse de que el widget de mensaje esté oculto inicialmente.
            self._no_books_message_widget.Show(False)

            # Obtiene la lista de libros del manejador de la aplicación.
            books = self.app_handler.get_all_books()

            if not books:
                # Si no hay libros, configura y muestra el widget de mensaje.
                self._no_books_message_widget.Show(True)
                # Accede a la etiqueta de texto dentro del panel de mensaje.
                label_widget_inside_panel = self._no_books_message_widget.GetChildren()[0]
                if isinstance(label_widget_inside_panel, wx.StaticText):
                    # Ajusta el texto y la fuente del mensaje según el layout actual.
                    is_sidebar_layout = (active_sizer == self.box_sizer_vertical)
                    if is_sidebar_layout:
                        label_widget_inside_panel.SetLabel("No hay libros.")
                        label_widget_inside_panel.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
                    else:
                        label_widget_inside_panel.SetLabel(f"No hay libros en la biblioteca de {APP_NAME}.")
                        label_widget_inside_panel.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
                    # Fuerza el layout del panel de mensaje para que el texto ajustado se muestre correctamente.
                    self._no_books_message_widget.Layout()

                # Añade el widget de mensaje al sizer activo, con factor de expansión 1 para que ocupe el espacio.
                active_sizer.Add(self._no_books_message_widget, 1, wx.EXPAND | wx.ALL, 10)
            else:
                # Si hay libros, crea y añade las tarjetas al sizer activo.
                for book in books:
                    # Crea una nueva tarjeta para cada libro.
                    card_panel = BookCardPanel(self, book, self.app_handler, self.on_book_card_selected_callback)
                    # Añade la tarjeta a la lista de seguimiento.
                    self.book_card_panels.append(card_panel)
                    # Añade la tarjeta al sizer activo con diferentes flags según el layout.
                    if active_sizer == self.box_sizer_vertical: # Layout de sidebar
                         active_sizer.Add(card_panel, 0, wx.EXPAND | wx.ALL, 5)
                    else: # Layout central (wrap_sizer)
                         active_sizer.Add(card_panel, 0, wx.ALL, 10)
        finally:
            # Descongela la ventana.
            self.Thaw()

        # Fuerza la actualización del layout y el ajuste del panel desplazable.
        self.Layout()
        self.FitInside()
        self.Refresh() # Fuerza un redibujado.

    def Clear(self):
        """
        Limpia completamente la vista, eliminando todas las tarjetas de libros
        y ocultando el mensaje de "no hay libros".
        """
        # Congela la ventana.
        self.Freeze()
        try:
            # Obtiene el sizer activo.
            active_sizer = self.GetSizer()
            if active_sizer:
                # Limpiar y destruir todas las tarjetas.
                self._clear_and_destroy_book_cards()
                # Ocultar y desvincular el widget de mensaje si está en el sizer.
                if active_sizer.GetItem(self._no_books_message_widget):
                    active_sizer.Detach(self._no_books_message_widget)
                self._no_books_message_widget.Show(False)
                # Actualiza el layout del sizer ahora vacío.
                active_sizer.Layout()
        finally:
            # Descongela la ventana.
            self.Thaw()
        # Fuerza la actualización final del layout y el ajuste.
        self.Layout()
        self.FitInside()
        self.Refresh()