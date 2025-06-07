# -*- coding: utf-8 -*-
"""
Archivo: AppHandler.py
Descripción: Gestiona la lógica de la aplicación ReinventProse 2.0, actuando como intermediario entre la UI y la capa de datos. Implementa el patrón Singleton.
Autor: AutoDoc AI
Fecha: 07/06/2025
Versión: 0.0.1
Licencia: MIT License
"""
import wx
from DBManager import (DBManager, DatabaseError, BookCreationError, BookUpdateError, BookNotFoundError, BookDeletionError,
                     ChapterCreationError, ChapterUpdateError, ChapterNotFoundError, ChapterDeletionError,
                     ConcreteIdeaError)
from typing import Callable, List, Dict, Optional, Any

class AppHandler:
    """
    Clase Singleton que centraliza la lógica de negocio y la interacción
    entre la interfaz de usuario (UI) y la base de datos para la aplicación
    ReinventProse 2.0.

    Es responsable de la inicialización de la base de datos, la gestión del
    estado de cambios no guardados ('dirty'), y proporciona métodos para
    operaciones CRUD en libros, capítulos e ideas concretas, delegando las
    operaciones de persistencia a la clase DBManager. También maneja la
    presentación de diálogos de error al usuario y mantiene una referencia
    a la ventana principal de la aplicación.
    """
    _instance: Optional['AppHandler'] = None # Variable de clase para mantener la única instancia

    def __init__(self, db_manager: DBManager, db_name: Optional[str] = "reinventprose_v2_data.db"):
        """
        Constructor privado de la clase AppHandler.

        Este constructor está diseñado para ser llamado internamente por el
        método de clase `get_instance` para asegurar el patrón Singleton.
        No debe ser llamado directamente desde fuera de la clase.

        Args:
            db_manager (DBManager): Una instancia del gestor de base de datos (DBManager).
                                    Esta instancia es esencial para todas las operaciones
                                    de persistencia de datos.
            db_name (Optional[str]): El nombre del archivo de la base de datos. Este
                                     argumento es principalmente relevante si `db_manager`
                                     es `None` en `get_instance` y se necesita crear
                                     una instancia de DBManager internamente.
        """
        # Verifica si la instancia ya ha sido inicializada para evitar re-inicialización
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized: bool = True # Marca la instancia como inicializada
        self.db_manager: DBManager = db_manager # Almacena la instancia del gestor de BD
        self.main_window: Optional[wx.Frame] = None # Referencia a la ventana principal de la UI
        self._is_dirty: bool = False # Bandera para indicar si hay cambios sin guardar

    @classmethod
    def get_instance(cls, db_manager: Optional[DBManager] = None, db_name: Optional[str] = "reinventprose_v2_data.db") -> 'AppHandler':
        """
        Método de clase para obtener la única instancia de AppHandler (Singleton).

        Si la instancia no existe, la crea utilizando la instancia de DBManager
        proporcionada o creando una nueva si no se proporciona ninguna.

        Args:
            db_manager (Optional[DBManager]): Una instancia opcional de DBManager.
                                              Si se proporciona, se utiliza. Si es `None`,
                                              se intenta obtener la instancia Singleton
                                              de DBManager.
            db_name (Optional[str]): El nombre del archivo de la base de datos. Solo
                                     se utiliza si `db_manager` es `None` y se necesita
                                     crear la instancia de DBManager.

        Returns:
            AppHandler: La única instancia de la clase AppHandler.
        """
        # Si la instancia Singleton aún no ha sido creada
        if not cls._instance:
            # Obtiene o crea la instancia de DBManager
            db_mngr = db_manager if db_manager else DBManager.get_instance(db_name or "reinventprose_v2_data.db")
            # Crea la instancia de AppHandler pasándole el DBManager
            cls._instance = AppHandler(db_manager=db_mngr, db_name=db_name)
        return cls._instance # Devuelve la instancia existente o recién creada

    def initialize_database(self):
        """
        Inicializa la base de datos.

        Delega la creación de tablas al DBManager. Si ocurre un error durante
        la inicialización, muestra un mensaje al usuario y termina la aplicación.

        Raises:
            SystemExit: Si ocurre un error crítico al inicializar la base de datos.
        """
        try:
            self.db_manager.create_database() # Llama al método del DBManager para crear las tablas
        except DatabaseError as e:
            # Muestra un mensaje de error al usuario si falla la inicialización de la BD
            wx.MessageBox(f"Error al inicializar la base de datos: {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR)
            # Termina la aplicación ya que no puede operar sin una BD funcional
            raise SystemExit(f"Fallo en la inicialización de la Base de Datos: {e}")

    def set_main_window(self, main_window: wx.Frame):
        """
        Establece la referencia a la ventana principal de la aplicación.

        Esta referencia es necesaria para mostrar diálogos modales con un padre
        específico y para notificar a la UI sobre cambios en el estado 'dirty'.

        Args:
            main_window (wx.Frame): La instancia de la ventana principal (MainWindow).
        """
        self.main_window = main_window # Almacena la referencia a la ventana principal

    def get_main_window(self) -> Optional[wx.Frame]:
        """
        Obtiene la referencia a la ventana principal de la aplicación.

        Returns:
            Optional[wx.Frame]: La instancia de la ventana principal, o `None` si no ha sido establecida.
        """
        return self.main_window # Devuelve la referencia almacenada

    # --- Métodos para Libros ---
    def create_new_book(self, title: str, author: str, synopsis: str, prologue: str, back_cover_text: str, cover_image_path: str) -> Optional[int]:
        """
        Crea un nuevo libro en la base de datos.

        Delega la operación de creación al DBManager. Si la creación es exitosa,
        establece el estado 'dirty' de la aplicación. Maneja excepciones
        específicas de creación de libros y errores generales.

        Args:
            title (str): El título del nuevo libro.
            author (str): El autor del nuevo libro.
            synopsis (str): La sinopsis del nuevo libro.
            prologue (str): El prólogo del nuevo libro.
            back_cover_text (str): El texto para la contraportada del nuevo libro.
            cover_image_path (str): La ruta al archivo de imagen de la portada.

        Returns:
            Optional[int]: El ID del libro recién creado si la operación fue exitosa,
                           o `None` si ocurrió un error durante la creación.
        """
        try:
            # Llama al DBManager para crear el libro y obtener su ID
            book_id = self.db_manager.create_book(title, author, synopsis, prologue, back_cover_text, cover_image_path)
            if book_id:
                self.set_dirty(True) # Indica que hay cambios sin guardar
                return book_id # Devuelve el ID del libro creado
            # Si create_book devuelve None (aunque DBManager debería lanzar excepción), se maneja
        except BookCreationError as e:
            # Muestra un mensaje de error específico si falla la creación del libro
            wx.MessageBox(f"Error al crear el libro: {e}", "Error de Creación de Libro", wx.OK | wx.ICON_ERROR, parent=self.main_window)
        except Exception as e_gen:
            # Muestra un mensaje para cualquier otro error inesperado
            wx.MessageBox(f"Un error inesperado ocurrió al crear el libro: {e_gen}", "Error Inesperado", wx.OK | wx.ICON_ERROR, parent=self.main_window)
        return None # Retorna None si la creación falla

    def get_all_books(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los libros almacenados en la base de datos.

        Delega la consulta al DBManager. Maneja errores de base de datos.

        Returns:
            List[Dict[str, Any]]: Una lista de diccionarios, donde cada diccionario
                                  representa un libro con sus detalles. Retorna una
                                  lista vacía si ocurre un error.
        """
        try:
            return self.db_manager.get_all_books() # Llama al DBManager para obtener todos los libros
        except DatabaseError as e:
            # Muestra un mensaje de error si falla la consulta
            wx.MessageBox(f"Error al obtener la lista de libros: {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return [] # Retorna una lista vacía en caso de error

    def get_book_details(self, book_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles completos de un libro específico por su ID.

        Delega la consulta al DBManager. Maneja el caso en que el libro no sea
        encontrado y errores generales de base de datos.

        Args:
            book_id (int): El identificador único del libro a buscar.

        Returns:
            Optional[Dict[str, Any]]: Un diccionario con los detalles del libro si
                                      se encuentra, o `None` si el libro no existe
                                      o si ocurre un error de base de datos.
        """
        try:
            return self.db_manager.get_book_by_id(book_id) # Llama al DBManager para obtener el libro por ID
        except BookNotFoundError:
            # Si el libro no se encuentra, simplemente retorna None sin mostrar un error.
            # La UI que llama a este método es responsable de manejar el caso "no encontrado".
            return None
        except DatabaseError as e:
            # Muestra un mensaje de error si ocurre un problema de base de datos
            wx.MessageBox(f"Error al obtener los detalles del libro (ID: {book_id}): {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return None # Retorna None en caso de error

    def update_book_details(self, book_id: int, title: str, author: str, synopsis: str, prologue: str, back_cover_text: str, cover_image_path: str) -> bool:
        """
        Actualiza los detalles de un libro existente en la base de datos.

        Delega la operación de actualización al DBManager. Maneja excepciones
        específicas de actualización o no encontrado.

        Args:
            book_id (int): El identificador único del libro a actualizar.
            title (str): El nuevo título del libro.
            author (str): El nuevo autor del libro.
            synopsis (str): La nueva sinopsis del libro.
            prologue (str): El nuevo prólogo del libro.
            back_cover_text (str): El nuevo texto de contraportada.
            cover_image_path (str): La nueva ruta a la imagen de portada.

        Returns:
            bool: `True` si la actualización fue exitosa, `False` en caso contrario.
        """
        try:
            # Llama al DBManager para actualizar el libro.
            # La UI que llama a este método ya debería haber marcado la aplicación como dirty.
            # El estado dirty se reseteará globalmente después de un guardado completo.
            return self.db_manager.update_book(book_id, title, author, synopsis, prologue, back_cover_text, cover_image_path)
        except (BookUpdateError, BookNotFoundError) as e:
            # Muestra un mensaje de error si falla la actualización o el libro no se encuentra
            wx.MessageBox(f"Error al actualizar el libro (ID: {book_id}): {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return False # Retorna False si la actualización falla

    # --- Métodos para Capítulos ---
    def get_chapters_by_book_id(self, book_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los capítulos asociados a un libro específico.

        Delega la consulta al DBManager. Maneja errores de base de datos.

        Args:
            book_id (int): El identificador único del libro cuyos capítulos se desean obtener.

        Returns:
            List[Dict[str, Any]]: Una lista de diccionarios, donde cada diccionario
                                  representa un capítulo. Retorna una lista vacía
                                  si el libro no tiene capítulos o si ocurre un error.
        """
        try:
            return self.db_manager.get_chapters_by_book_id(book_id) # Llama al DBManager para obtener capítulos por libro
        except DatabaseError as e:
            # Muestra un mensaje de error si falla la consulta
            wx.MessageBox(f"Error al obtener los capítulos (Libro ID: {book_id}): {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return [] # Retorna una lista vacía en caso de error

    def get_chapter_details(self, chapter_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles completos de un capítulo específico por su ID.

        Delega la consulta al DBManager. Maneja el caso en que el capítulo no sea
        encontrado y errores generales de base de datos.

        Args:
            chapter_id (int): El identificador único del capítulo a buscar.

        Returns:
            Optional[Dict[str, Any]]: Un diccionario con los detalles del capítulo si
                                      se encuentra, o `None` si el capítulo no existe
                                      o si ocurre un error de base de datos.
        """
        try:
            return self.db_manager.get_chapter_by_id(chapter_id) # Llama al DBManager para obtener el capítulo por ID
        except ChapterNotFoundError:
            # Si el capítulo no se encuentra, retorna None sin mostrar error.
            return None
        except DatabaseError as e:
            # Muestra un mensaje de error si ocurre un problema de base de datos
            wx.MessageBox(f"Error al obtener los detalles del capítulo (ID: {chapter_id}): {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return None # Retorna None en caso de error

    def create_new_chapter(self, book_id: int, chapter_number: int, title: str,
                          content: str = "", abstract_idea: str = "") -> Optional[int]:
        """
        Crea un nuevo capítulo para un libro específico en la base de datos.

        Delega la operación de creación al DBManager. Si la creación es exitosa,
        establece el estado 'dirty' de la aplicación. Maneja excepciones
        específicas de creación de capítulos y errores generales.

        Args:
            book_id (int): El identificador único del libro al que pertenece el capítulo.
            chapter_number (int): El número de orden del capítulo dentro del libro.
            title (str): El título del nuevo capítulo.
            content (str): El contenido del capítulo (texto principal). Por defecto es una cadena vacía.
            abstract_idea (str): La idea abstracta o resumen del capítulo. Por defecto es una cadena vacía.

        Returns:
            Optional[int]: El ID del capítulo recién creado si la operación fue exitosa,
                           o `None` si ocurrió un error durante la creación.
        """
        try:
            # Llama al DBManager para crear el capítulo y obtener su ID
            chapter_id = self.db_manager.create_chapter(book_id, chapter_number, title, content, abstract_idea)
            if chapter_id:
                self.set_dirty(True) # Indica que hay cambios sin guardar
                return chapter_id # Devuelve el ID del capítulo creado
            # Si create_chapter devuelve None (aunque DBManager debería lanzar excepción), se maneja
            return None # Retorna None si la creación falla sin lanzar excepción (caso improbable)
        except ChapterCreationError as e:
            # Muestra un mensaje de error específico si falla la creación del capítulo
            wx.MessageBox(f"Error al crear el capítulo: {e}", "Error de Creación de Capítulo", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return None # Retorna None en caso de error
        except Exception as e_gen:
            # Muestra un mensaje para cualquier otro error inesperado
            wx.MessageBox(f"Un error inesperado ocurrió al crear el capítulo: {e_gen}", "Error Inesperado", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return None # Retorna None en caso de error

    def delete_chapter(self, chapter_id: int) -> bool:
        """
        Elimina un capítulo específico y todas sus ideas concretas asociadas de la base de datos.

        Delega la operación de eliminación al DBManager. Si la eliminación es exitosa,
        establece el estado 'dirty' de la aplicación. Maneja excepciones
        específicas de eliminación o no encontrado, y errores generales.

        Args:
            chapter_id (int): El identificador único del capítulo a eliminar.

        Returns:
            bool: `True` si la eliminación fue exitosa, `False` en caso contrario.
        """
        try:
            # Llama al DBManager para eliminar el capítulo
            success = self.db_manager.delete_chapter(chapter_id)
            if success:
                self.set_dirty(True) # Indica que hay cambios sin guardar
            return success # Devuelve el resultado de la operación
        except (ChapterDeletionError, ChapterNotFoundError) as e:
            # Muestra un mensaje de error específico si falla la eliminación o el capítulo no se encuentra
            wx.MessageBox(f"Error al eliminar el capítulo (ID: {chapter_id}): {e}", "Error de Eliminación", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return False # Retorna False en caso de error
        except Exception as e_gen:
            # Muestra un mensaje para cualquier otro error inesperado
            wx.MessageBox(f"Un error inesperado ocurrió al eliminar el capítulo: {e_gen}", "Error Inesperado", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return False # Retorna False en caso de error

    def update_chapter_content_via_handler(self, chapter_id: int, content: str) -> bool:
        """
        Actualiza únicamente el contenido (texto principal) de un capítulo específico.

        Este método es un wrapper para la operación de actualización de contenido
        del DBManager. La gestión del estado 'dirty' para esta operación
        normalmente la realiza la vista que llama a este método (ej. ChapterContentView).

        Args:
            chapter_id (int): El identificador único del capítulo a actualizar.
            content (str): El nuevo contenido de texto para el capítulo.

        Returns:
            bool: `True` si la actualización fue exitosa, `False` en caso contrario.
        """
        try:
            # Llama al DBManager para actualizar solo el contenido.
            # La vista que llama a esto es responsable de llamar a set_dirty(True).
            return self.db_manager.update_chapter_content_only(chapter_id, content)
        except (ChapterUpdateError, ChapterNotFoundError) as e:
            # Muestra un mensaje de error si falla la actualización o el capítulo no se encuentra
            wx.MessageBox(f"Error al actualizar el contenido del capítulo (ID: {chapter_id}): {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return False # Retorna False en caso de error

    def update_chapter_abstract_idea_via_handler(self, chapter_id: int, abstract_idea: str) -> bool:
        """
        Actualiza únicamente la idea abstracta de un capítulo específico.

        Este método es un wrapper para la operación de actualización de idea abstracta
        del DBManager. La gestión del estado 'dirty' para esta operación
        normalmente la realiza la vista que llama a este método (ej. AbstractIdeaView).

        Args:
            chapter_id (int): El identificador único del capítulo a actualizar.
            abstract_idea (str): La nueva idea abstracta para el capítulo.

        Returns:
            bool: `True` si la actualización fue exitosa, `False` en caso contrario.
        """
        try:
            # Llama al DBManager para actualizar solo la idea abstracta.
            # La vista que llama a esto es responsable de llamar a set_dirty(True).
            return self.db_manager.update_chapter_abstract_idea(chapter_id, abstract_idea)
        except (ChapterUpdateError, ChapterNotFoundError) as e:
            # Muestra un mensaje de error si falla la actualización o el capítulo no se encuentra
            wx.MessageBox(f"Error al actualizar la idea abstracta del capítulo (ID: {chapter_id}): {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return False # Retorna False en caso de error

    # --- Métodos para Ideas Concretas ---
    def get_concrete_ideas_for_chapter(self, chapter_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todas las ideas concretas asociadas a un capítulo específico.

        Delega la consulta al DBManager. Maneja errores específicos de ideas concretas.

        Args:
            chapter_id (int): El identificador único del capítulo cuyas ideas concretas se desean obtener.

        Returns:
            List[Dict[str, Any]]: Una lista de diccionarios, donde cada diccionario
                                  representa una idea concreta. Retorna una lista vacía
                                  si el capítulo no tiene ideas concretas o si ocurre un error.
        """
        try:
            return self.db_manager.get_concrete_ideas_by_chapter_id(chapter_id) # Llama al DBManager para obtener ideas concretas por capítulo
        except ConcreteIdeaError as e:
            # Muestra un mensaje de error si falla la consulta de ideas concretas
            wx.MessageBox(f"Error al obtener las ideas concretas (Capítulo ID: {chapter_id}): {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return [] # Retorna una lista vacía en caso de error

    def add_concrete_idea_for_chapter(self, chapter_id: int, idea_text: str) -> Optional[int]:
        """
        Añade una nueva idea concreta a un capítulo específico en la base de datos.

        Delega la operación de adición al DBManager. La gestión del estado 'dirty'
        para esta operación normalmente la realiza la vista que llama a este método
        (ej. ConcreteIdeaView). Maneja errores específicos de ideas concretas.

        Args:
            chapter_id (int): El identificador único del capítulo al que se añadirá la idea.
            idea_text (str): El texto de la nueva idea concreta.

        Returns:
            Optional[int]: El ID de la idea concreta recién creada si la operación fue exitosa,
                           o `None` si ocurrió un error.
        """
        try:
            # Llama al DBManager para añadir la idea concreta.
            # La vista que llama a esto es responsable de llamar a set_dirty(True).
            idea_id = self.db_manager.add_concrete_idea(chapter_id, idea_text)
            return idea_id # Devuelve el ID de la idea creada
        except ConcreteIdeaError as e:
            # Muestra un mensaje de error si falla la adición de la idea concreta
            wx.MessageBox(f"Error al agregar la idea concreta: {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return None # Retorna None en caso de error

    def update_concrete_idea_text(self, concrete_idea_id: int, new_text: str) -> bool:
        """
        Actualiza el texto de una idea concreta existente en la base de datos.

        Delega la operación de actualización al DBManager. La gestión del estado 'dirty'
        para esta operación normalmente la realiza la vista que llama a este método
        (ej. ConcreteIdeaView). Maneja errores específicos de ideas concretas.

        Args:
            concrete_idea_id (int): El identificador único de la idea concreta a actualizar.
            new_text (str): El nuevo texto para la idea concreta.

        Returns:
            bool: `True` si la actualización fue exitosa, `False` en caso contrario.
        """
        try:
            # Llama al DBManager para actualizar la idea concreta.
            # La vista que llama a esto es responsable de llamar a set_dirty(True).
            return self.db_manager.update_concrete_idea(concrete_idea_id, new_text)
        except ConcreteIdeaError as e:
            # Muestra un mensaje de error si falla la actualización de la idea concreta
            wx.MessageBox(f"Error al actualizar la idea concreta (ID: {concrete_idea_id}): {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return False # Retorna False en caso de error

    def delete_concrete_idea_by_id(self, concrete_idea_id: int) -> bool:
        """
        Elimina una idea concreta específica de la base de datos por su ID.

        Delega la operación de eliminación al DBManager. La gestión del estado 'dirty'
        para esta operación normalmente la realiza la vista que llama a este método
        (ej. ConcreteIdeaView). Maneja errores específicos de ideas concretas.

        Args:
            concrete_idea_id (int): El identificador único de la idea concreta a eliminar.

        Returns:
            bool: `True` si la eliminación fue exitosa, `False` en caso contrario.
        """
        try:
            # Llama al DBManager para eliminar la idea concreta.
            # La vista que llama a esto es responsable de llamar a set_dirty(True).
            return self.db_manager.delete_concrete_idea(concrete_idea_id)
        except ConcreteIdeaError as e:
            # Muestra un mensaje de error si falla la eliminación de la idea concreta
            wx.MessageBox(f"Error al eliminar la idea concreta (ID: {concrete_idea_id}): {e}", "Error de Base de Datos", wx.OK | wx.ICON_ERROR, parent=self.main_window)
            return False # Retorna False en caso de error

    # --- Gestión del Estado 'Dirty' ---
    def set_dirty(self, is_dirty: bool = True):
        """
        Establece el estado 'dirty' (con cambios sin guardar) de la aplicación.

        Si el nuevo estado 'dirty' es diferente al estado actual, actualiza la
        bandera interna y notifica a la ventana principal (si existe y tiene
        el método `set_dirty_status_in_title`) para que actualice su representación
        visual (ej. añadir/quitar un '*' en el título).

        Args:
            is_dirty (bool): `True` para indicar que hay cambios sin guardar,
                             `False` para indicar que todos los cambios han sido guardados.
                             Por defecto es `True`.
        """
        # Solo actualiza y notifica si el estado cambia
        if self._is_dirty != is_dirty:
            self._is_dirty = is_dirty # Actualiza la bandera interna
            # Si hay una ventana principal y tiene el método de notificación
            if self.main_window and hasattr(self.main_window, 'set_dirty_status_in_title'):
                # Llama al método de la ventana principal para actualizar la UI
                self.main_window.set_dirty_status_in_title(self._is_dirty)

    def is_application_dirty(self) -> bool:
        """
        Comprueba si la aplicación tiene cambios sin guardar.

        Returns:
            bool: `True` si hay cambios sin guardar, `False` en caso contrario.
        """
        return self._is_dirty # Devuelve el estado actual de la bandera dirty

    def prompt_save_changes(self, on_save: Callable[[], None], on_discard: Callable[[], None], on_cancel: Callable[[], None]) -> None:
        """
        Muestra un diálogo modal al usuario preguntando si desea guardar, descartar
        o cancelar los cambios pendientes si la aplicación está en estado 'dirty'.

        Ejecuta el callback correspondiente (`on_save`, `on_discard`, o `on_cancel`)
        basado en la respuesta del usuario. Requiere que la ventana principal
        haya sido establecida previamente.

        Args:
            on_save (Callable[[], None]): Función a ejecutar si el usuario elige guardar.
            on_discard (Callable[[], None]): Función a ejecutar si el usuario elige descartar.
            on_cancel (Callable[[], None]): Función a ejecutar si el usuario elige cancelar.
        """
        # Si no hay ventana principal, no se puede mostrar el diálogo.
        # En este caso, se asume una cancelación para evitar acciones no deseadas.
        if not self.main_window:
            print("Advertencia (AppHandler): prompt_save_changes llamado sin main_window. Se cancela la acción.")
            on_cancel() # Ejecuta el callback de cancelación por defecto
            return

        # Crea y muestra el diálogo de mensaje con opciones Guardar, Descartar, Cancelar
        dlg = wx.MessageDialog(self.main_window,
                               "¿Desea guardar los cambios realizados?",
                               "Guardar Cambios",
                               wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal() # Muestra el diálogo y espera la respuesta
        dlg.Destroy() # Destruye el diálogo después de obtener la respuesta

        # Ejecuta el callback apropiado basado en la respuesta del usuario
        if result == wx.ID_YES:
            on_save() # El usuario eligió guardar
        elif result == wx.ID_NO:
            on_discard() # El usuario eligió descartar
        elif result == wx.ID_CANCEL:
            on_cancel() # El usuario eligió cancelar