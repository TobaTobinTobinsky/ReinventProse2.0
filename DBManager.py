# -*- coding: utf-8 -*-
"""
File Name: DBManager.py
Descripción: Clase para gestionar la conexión y operaciones con la base de datos SQLite
             para almacenar información de libros, capítulos e ideas concretas.
Autor: AutoDoc AI
Fecha: 07/06/2025
Versión: 0.0.1
Licencia: MIT License
"""

import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import os

class DatabaseError(Exception):
    """Excepción base para errores relacionados con la base de datos."""
    pass

class BookError(DatabaseError):
    """Excepción base para errores relacionados con operaciones de libros."""
    pass

class BookCreationError(BookError):
    """Excepción para errores durante la creación de un libro."""
    pass

class BookUpdateError(BookError):
    """Excepción para errores durante la actualización de un libro."""
    pass

class BookNotFoundError(BookError):
    """Excepción cuando un libro específico no es encontrado."""
    pass

class BookDeletionError(BookError):
    """Excepción para errores durante la eliminación de un libro."""
    pass

class ChapterError(DatabaseError):
    """Excepción base para errores relacionados con operaciones de capítulos."""
    pass

class ChapterCreationError(ChapterError):
    """Excepción para errores durante la creación de un capítulo."""
    pass

class ChapterUpdateError(ChapterError):
    """Excepción para errores durante la actualización de un capítulo."""
    pass

class ChapterNotFoundError(ChapterError):
    """Excepción cuando un capítulo específico no es encontrado."""
    pass

class ChapterDeletionError(ChapterError):
    """Excepción para errores durante la eliminación de un capítulo."""
    pass

class ConcreteIdeaError(DatabaseError):
    """Excepción base para errores relacionados con operaciones de ideas concretas."""
    pass

class DBManager:
    """
    Gestiona la conexión y las operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
    para las tablas de libros, capítulos e ideas concretas en una base de datos SQLite.
    Implementa el patrón Singleton para asegurar una única instancia del gestor de BD.
    """
    _instance: Optional['DBManager'] = None

    def __new__(cls, db_path: str):
        """
        Implementa el patrón Singleton. Retorna la única instancia de DBManager.

        Args:
            db_path (str): La ruta al archivo de la base de datos SQLite.

        Returns:
            DBManager: La única instancia de la clase DBManager.
        """
        # Si no existe una instancia, crea una nueva
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: str):
        """
        Inicializa la instancia de DBManager. Solo se ejecuta una vez
        debido a la lógica del Singleton.

        Args:
            db_path (str): La ruta al archivo de la base de datos SQLite.
        """
        # Evita la reinicialización si la instancia ya existe
        if hasattr(self, '_initialized_dbm') and self._initialized_dbm:
            return

        self.db_path: str = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._initialized_dbm: bool = True # Marca la instancia como inicializada

    @classmethod
    def get_instance(cls, db_path: str) -> 'DBManager':
        """
        Obtiene la instancia Singleton de DBManager. Si no existe, la crea.
        Si ya existe pero con una ruta de BD diferente, emite una advertencia.

        Args:
            db_path (str): La ruta al archivo de la base de datos SQLite.

        Returns:
            DBManager: La única instancia de la clase DBManager.
        """
        # Si no hay instancia, crea una nueva usando el constructor
        if cls._instance is None:
            cls._instance = cls(db_path)
        # Si hay instancia pero la ruta de BD es diferente, emite una advertencia
        elif cls._instance.db_path != db_path:
            print(f"ADVERTENCIA: DBManager.get_instance llamado con un nuevo db_path ('{db_path}'). La instancia existente usa '{cls._instance.db_path}'.")
        return cls._instance

    def _connect(self) -> None:
        """
        Establece la conexión con la base de datos SQLite si no está ya conectada.

        Raises:
            DatabaseError: Si ocurre un error al intentar conectar con la base de datos.
        """
        try:
            # Conecta solo si no hay una conexión activa
            if self.connection is None:
                self.connection = sqlite3.connect(self.db_path)
                # Configura la conexión para retornar filas como objetos que se pueden acceder por nombre de columna
                self.connection.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            # Envuelve el error de SQLite en una excepción personalizada
            raise DatabaseError(f"Error al conectar con la base de datos: {e}") from e

    def _disconnect(self) -> None:
        """
        Cierra la conexión con la base de datos SQLite si está activa.
        Maneja errores durante el cierre de la conexión.
        """
        try:
            # Cierra la conexión solo si está activa
            if self.connection:
                self.connection.close()
                self.connection = None # Restablece la conexión a None
        except sqlite3.Error as e:
            # Imprime un mensaje de error si falla el cierre, pero no levanta excepción
            print(f"Error al cerrar la conexión de la base de datos: {e}")

    @contextmanager
    def transaction(self):
        """
        Proporciona un gestor de contexto para manejar transacciones de base de datos.
        Asegura que la conexión se establezca, se obtenga un cursor, se realice
        la operación, se haga commit si todo va bien, rollback en caso de error,
        y se cierre el cursor y la conexión al finalizar.

        Yields:
            sqlite3.Cursor: Un objeto cursor para ejecutar comandos SQL dentro de la transacción.

        Raises:
            DatabaseError: Si ocurre un error durante la transacción (SQLite o personalizado).
        """
        cursor = None
        try:
            self._connect() # Asegura que la conexión esté abierta
            if self.connection is None:
                 # Esto no debería ocurrir si _connect tiene éxito, pero es una salvaguarda
                raise DatabaseError("La conexión no se pudo establecer.")

            cursor = self.connection.cursor() # Obtiene un cursor
            yield cursor # Cede el control al bloque 'with'
            self.connection.commit() # Confirma los cambios si no hubo errores
        except sqlite3.Error as e_sql:
            # Si ocurre un error de SQLite, intenta hacer rollback
            if self.connection:
                self.connection.rollback()
            # Envuelve el error de SQLite en una excepción personalizada y la relanza
            raise DatabaseError(f"Error SQLite durante la transacción: {e_sql}") from e_sql
        except DatabaseError:
            # Si ocurre una excepción DatabaseError personalizada, intenta hacer rollback
            if self.connection:
                self.connection.rollback()
            raise # Relanza la excepción original
        except Exception as e_gen:
            # Captura cualquier otra excepción inesperada, intenta hacer rollback
            if self.connection:
                self.connection.rollback()
            # Envuelve la excepción genérica en una DatabaseError y la relanza
            raise DatabaseError(f"Error inesperado durante la transacción: {e_gen}") from e_gen
        finally:
            # Asegura que el cursor se cierre
            if cursor:
                cursor.close()
            self._disconnect() # Asegura que la conexión se cierre

    def create_database(self) -> None:
        """
        Crea las tablas 'books', 'chapters' y 'concrete_ideas' en la base de datos
        si no existen.

        Raises:
            DatabaseError: Si ocurre un error durante la creación de las tablas.
        """
        try:
            # Usa el gestor de contexto para una transacción segura
            with self.transaction() as cursor:
                # Crea la tabla 'books'
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL UNIQUE,
                        author TEXT NOT NULL,
                        synopsis TEXT,
                        prologue TEXT,
                        back_cover_text TEXT,
                        cover_image_path TEXT
                    )
                """)
                # Crea la tabla 'chapters' con clave foránea a 'books' y restricción de unicidad
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chapters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        book_id INTEGER NOT NULL,
                        chapter_number INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT,
                        abstract_idea TEXT,
                        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                        UNIQUE (book_id, chapter_number)
                    )
                """)
                # Crea la tabla 'concrete_ideas' con clave foránea a 'chapters'
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS concrete_ideas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chapter_id INTEGER NOT NULL,
                        idea TEXT NOT NULL,
                        FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
                    )
                """)
            print(f"Base de datos '{self.db_path}' verificada/inicializada con éxito.")
        except DatabaseError as e:
            # Captura y relanza errores específicos de la base de datos
            raise DatabaseError(f"Fallo durante la inicialización de la base de datos: {e}") from e

    def create_book(self, title: str, author: str, synopsis: str, prologue: str, back_cover_text: str, cover_image_path: str) -> int:
        """
        Crea un nuevo registro de libro en la tabla 'books'.

        Args:
            title (str): El título del libro (debe ser único).
            author (str): El autor del libro.
            synopsis (str): La sinopsis del libro.
            prologue (str): El prólogo del libro.
            back_cover_text (str): El texto de la contraportada del libro.
            cover_image_path (str): La ruta a la imagen de la portada del libro.

        Returns:
            int: El ID del libro recién creado.

        Raises:
            BookCreationError: Si ocurre un error durante la creación del libro,
                               incluyendo errores de integridad (título duplicado).
        """
        query = """
            INSERT INTO books (title, author, synopsis, prologue, back_cover_text, cover_image_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (title, author, synopsis, prologue, back_cover_text, cover_image_path)
        try:
            with self.transaction() as cursor:
                cursor.execute(query, params)
                book_id = cursor.lastrowid # Obtiene el ID de la última fila insertada
            if book_id is None:
                # Si lastrowid es None, la inserción falló de alguna manera inesperada
                raise BookCreationError(f"No se pudo obtener el ID para el libro: '{title}'")
            return book_id
        except sqlite3.IntegrityError as e_int:
            # Captura errores de unicidad (título duplicado) u otros errores de integridad
            raise BookCreationError(f"Error de integridad al crear el libro '{title}' (posible título duplicado): {e_int}") from e_int
        except DatabaseError as e:
            # Captura otros errores de base de datos durante la creación
            raise BookCreationError(f"Error de base de datos al crear el libro '{title}': {e}") from e

    def get_book_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera los datos de un libro por su ID.

        Args:
            book_id (int): El ID del libro a buscar.

        Returns:
            Optional[Dict[str, Any]]: Un diccionario con los datos del libro si se encuentra,
                                      o None si no se encuentra.

        Raises:
            BookNotFoundError: Si el libro con el ID especificado no es encontrado.
            DatabaseError: Si ocurre un error de base de datos diferente a BookNotFoundError.
        """
        query = "SELECT * FROM books WHERE id = ?"
        try:
            with self.transaction() as cursor:
                cursor.execute(query, (book_id,))
                book_data = cursor.fetchone() # Obtiene una única fila
            if book_data:
                return dict(book_data) # Convierte la fila (Row) a diccionario
            # Si no se encontró la fila, levanta BookNotFoundError
            raise BookNotFoundError(f"Libro con ID {book_id} no encontrado.")
        except DatabaseError as e:
            # Relanza la excepción si es BookNotFoundError, de lo contrario, imprime y relanza
            if not isinstance(e, BookNotFoundError):
                print(f"Error de base de datos al obtener libro con ID {book_id}: {e}")
            raise

    def get_all_books(self) -> List[Dict[str, Any]]:
        """
        Recupera los datos de todos los libros en la base de datos, ordenados por título.

        Returns:
            List[Dict[str, Any]]: Una lista de diccionarios, donde cada diccionario
                                  representa un libro. Retorna una lista vacía si no hay libros.

        Raises:
            DatabaseError: Si ocurre un error al recuperar los libros.
        """
        try:
            with self.transaction() as cursor:
                cursor.execute("SELECT * FROM books ORDER BY title")
                books_data = cursor.fetchall() # Obtiene todas las filas
            # Convierte cada fila (Row) a diccionario y retorna la lista
            return [dict(book) for book in books_data]
        except DatabaseError as e:
            # Captura y relanza errores de base de datos
            raise DatabaseError(f"Error al obtener todos los libros: {e}") from e

    def update_book(self, book_id: int, title: str, author: str, synopsis: str, prologue: str, back_cover_text: str, cover_image_path: str) -> bool:
        """
        Actualiza los datos de un libro existente por su ID.

        Args:
            book_id (int): El ID del libro a actualizar.
            title (str): El nuevo título del libro.
            author (str): El nuevo autor del libro.
            synopsis (str): La nueva sinopsis del libro.
            prologue (str): El nuevo prólogo del libro.
            back_cover_text (str): El nuevo texto de la contraportada del libro.
            cover_image_path (str): La nueva ruta a la imagen de la portada del libro.

        Returns:
            bool: True si la actualización fue exitosa.

        Raises:
            BookNotFoundError: Si el libro con el ID especificado no es encontrado.
            BookUpdateError: Si ocurre un error durante la actualización,
                             incluyendo errores de integridad (título duplicado).
        """
        query = """
            UPDATE books
            SET title = ?, author = ?, synopsis = ?, prologue = ?, back_cover_text = ?, cover_image_path = ?
            WHERE id = ?
        """
        params = (title, author, synopsis, prologue, back_cover_text, cover_image_path, book_id)
        try:
            with self.transaction() as cursor:
                cursor.execute(query, params)
                # Verifica cuántas filas fueron afectadas por la actualización
                if cursor.rowcount == 0:
                    # Si rowcount es 0, el libro con ese ID no existía o los datos eran idénticos.
                    # Realizamos una verificación explícita para distinguir.
                    check_cursor = cursor.connection.cursor()
                    check_cursor.execute("SELECT 1 FROM books WHERE id = ?", (book_id,))
                    # Si fetchone() retorna None, el libro no existe
                    if not check_cursor.fetchone():
                        raise BookNotFoundError(f"No se pudo actualizar: Libro con ID {book_id} no encontrado.")
                    # Si fetchone() retorna algo, el libro existe pero los datos no cambiaron.
                    # En este caso, consideramos la operación exitosa (el estado deseado ya existe).
            return True # Retorna True si la actualización afectó al menos una fila o si el libro existía pero no cambió
        except sqlite3.IntegrityError as e_int:
            # Captura errores de unicidad (título duplicado) u otros errores de integridad
            raise BookUpdateError(f"Error de integridad al actualizar libro con ID {book_id}: {e_int}") from e_int
        except DatabaseError as e:
            # Captura otros errores de base de datos durante la actualización
            raise BookUpdateError(f"Error de base de datos al actualizar libro con ID {book_id}: {e}") from e

    def delete_book(self, book_id: int) -> bool:
        """
        Elimina un libro de la base de datos por su ID.
        La eliminación de capítulos e ideas concretas asociadas se maneja
        automáticamente por la restricción ON DELETE CASCADE.

        Args:
            book_id (int): El ID del libro a eliminar.

        Returns:
            bool: True si el libro fue eliminado con éxito.

        Raises:
            BookNotFoundError: Si el libro con el ID especificado no es encontrado.
            BookDeletionError: Si ocurre un error de base de datos durante la eliminación.
        """
        try:
            with self.transaction() as cursor:
                cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
                # Verifica cuántas filas fueron afectadas por la eliminación
                if cursor.rowcount == 0:
                    # Si rowcount es 0, el libro con ese ID no existía
                    raise BookNotFoundError(f"No se pudo eliminar: Libro con ID {book_id} no encontrado.")
            return True # Retorna True si se eliminó al menos una fila
        except DatabaseError as e:
            # Captura y relanza errores de base de datos durante la eliminación
            raise BookDeletionError(f"Error de base de datos al eliminar libro con ID {book_id}: {e}") from e

    def create_chapter(self, book_id: int, chapter_number: int, title: str,
                       content: str = "", abstract_idea: str = "") -> int:
        """
        Crea un nuevo registro de capítulo asociado a un libro.

        Args:
            book_id (int): El ID del libro al que pertenece el capítulo.
            chapter_number (int): El número del capítulo dentro del libro (debe ser único por libro).
            title (str): El título del capítulo.
            content (str, optional): El contenido del capítulo. Por defecto es una cadena vacía.
            abstract_idea (str, optional): La idea abstracta principal del capítulo. Por defecto es una cadena vacía.

        Returns:
            int: El ID del capítulo recién creado.

        Raises:
            ChapterCreationError: Si ocurre un error durante la creación del capítulo,
                                  incluyendo errores de integridad (book_id inexistente
                                  o (book_id, chapter_number) duplicado).
        """
        query = """
            INSERT INTO chapters (book_id, chapter_number, title, content, abstract_idea)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (book_id, chapter_number, title, content, abstract_idea)
        try:
            with self.transaction() as cursor:
                cursor.execute(query, params)
                chapter_id = cursor.lastrowid # Obtiene el ID de la última fila insertada
                if chapter_id is None:
                    # Si lastrowid es None, la inserción falló de alguna manera inesperada
                    raise ChapterCreationError(f"No se pudo obtener ID para capítulo (libro ID {book_id}, N°{chapter_number})")
                return chapter_id
        except sqlite3.IntegrityError as e_int:
            # Captura errores de integridad: book_id inexistente o (book_id, chapter_number) duplicado
            raise ChapterCreationError(f"Error de integridad al crear capítulo (libro ID {book_id}, N°{chapter_number}, Título '{title}'): {e_int}") from e_int
        except DatabaseError as e:
            # Captura otros errores de base de datos durante la creación
            raise ChapterCreationError(f"Error de base de datos al crear capítulo: {e}") from e

    def get_chapter_by_id(self, chapter_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera los datos de un capítulo por su ID.

        Args:
            chapter_id (int): El ID del capítulo a buscar.

        Returns:
            Optional[Dict[str, Any]]: Un diccionario con los datos del capítulo si se encuentra,
                                      o None si no se encuentra.

        Raises:
            ChapterNotFoundError: Si el capítulo con el ID especificado no es encontrado.
            DatabaseError: Si ocurre un error de base de datos diferente a ChapterNotFoundError.
        """
        query = "SELECT * FROM chapters WHERE id = ?"
        try:
            with self.transaction() as cursor:
                cursor.execute(query, (chapter_id,))
                chapter_data = cursor.fetchone() # Obtiene una única fila
            if chapter_data:
                return dict(chapter_data) # Convierte la fila (Row) a diccionario
            # Si no se encontró la fila, levanta ChapterNotFoundError
            raise ChapterNotFoundError(f"Capítulo con ID {chapter_id} no encontrado.")
        except DatabaseError as e:
            # Relanza la excepción si es ChapterNotFoundError, de lo contrario, imprime y relanza
            if not isinstance(e, ChapterNotFoundError):
                print(f"Error de base de datos al obtener capítulo con ID {chapter_id}: {e}")
            raise

    def get_chapters_by_book_id(self, book_id: int) -> List[Dict[str, Any]]:
        """
        Recupera todos los capítulos asociados a un libro específico, ordenados por número de capítulo.

        Args:
            book_id (int): El ID del libro cuyos capítulos se desean recuperar.

        Returns:
            List[Dict[str, Any]]: Una lista de diccionarios, donde cada diccionario
                                  representa un capítulo. Retorna una lista vacía si el libro
                                  no tiene capítulos o si el libro no existe.

        Raises:
            DatabaseError: Si ocurre un error al recuperar los capítulos.
        """
        query = "SELECT * FROM chapters WHERE book_id = ? ORDER BY chapter_number"
        try:
            with self.transaction() as cursor:
                cursor.execute(query, (book_id,))
                chapters_data = cursor.fetchall() # Obtiene todas las filas
            # Convierte cada fila (Row) a diccionario y retorna la lista
            return [dict(chapter) for chapter in chapters_data]
        except DatabaseError as e:
            # Captura y relanza errores de base de datos
            raise DatabaseError(f"Error de base de datos al obtener capítulos para libro con ID {book_id}: {e}") from e

    def update_chapter(self, chapter_id: int, chapter_number: int, title: str, content: str, abstract_idea: str) -> bool:
        """
        Actualiza los datos de un capítulo existente por su ID.

        Args:
            chapter_id (int): El ID del capítulo a actualizar.
            chapter_number (int): El nuevo número del capítulo.
            title (str): El nuevo título del capítulo.
            content (str): El nuevo contenido del capítulo.
            abstract_idea (str): La nueva idea abstracta del capítulo.

        Returns:
            bool: True si la actualización fue exitosa.

        Raises:
            ChapterNotFoundError: Si el capítulo con el ID especificado no es encontrado.
            ChapterUpdateError: Si ocurre un error durante la actualización,
                                incluyendo errores de integridad ((book_id, chapter_number) duplicado).
        """
        query = """
            UPDATE chapters
            SET chapter_number = ?, title = ?, content = ?, abstract_idea = ?
            WHERE id = ?
        """
        params = (chapter_number, title, content, abstract_idea, chapter_id)
        try:
            with self.transaction() as cursor:
                cursor.execute(query, params)
                # Verifica cuántas filas fueron afectadas por la actualización
                if cursor.rowcount == 0:
                    # Si rowcount es 0, el capítulo con ese ID no existía o los datos eran idénticos.
                    # Realizamos una verificación explícita para distinguir.
                    check_cursor = cursor.connection.cursor()
                    check_cursor.execute("SELECT 1 FROM chapters WHERE id = ?", (chapter_id,))
                    # Si fetchone() retorna None, el capítulo no existe
                    if not check_cursor.fetchone():
                        raise ChapterNotFoundError(f"No se pudo actualizar: Capítulo con ID {chapter_id} no encontrado.")
                    # Si fetchone() retorna algo, el capítulo existe pero los datos no cambiaron.
                    # En este caso, consideramos la operación exitosa.
            return True # Retorna True si la actualización afectó al menos una fila o si el capítulo existía pero no cambió
        except sqlite3.IntegrityError as e_int:
            # Captura errores de unicidad ((book_id, chapter_number) duplicado) u otros errores de integridad
            raise ChapterUpdateError(f"Error de integridad al actualizar capítulo con ID {chapter_id}: {e_int}") from e_int
        except DatabaseError as e:
            # Captura otros errores de base de datos durante la actualización
            raise ChapterUpdateError(f"Error de base de datos al actualizar capítulo con ID {chapter_id}: {e}") from e

    def delete_chapter(self, chapter_id: int) -> bool:
        """
        Elimina un capítulo de la base de datos por su ID.
        La eliminación de ideas concretas asociadas se maneja
        automáticamente por la restricción ON DELETE CASCADE.

        Args:
            chapter_id (int): El ID del capítulo a eliminar.

        Returns:
            bool: True si el capítulo fue eliminado con éxito.

        Raises:
            ChapterNotFoundError: Si el capítulo con el ID especificado no es encontrado.
            ChapterDeletionError: Si ocurre un error de base de datos durante la eliminación.
        """
        query = "DELETE FROM chapters WHERE id = ?"
        try:
            with self.transaction() as cursor:
                cursor.execute(query, (chapter_id,))
                # Verifica cuántas filas fueron afectadas por la eliminación
                if cursor.rowcount == 0:
                    # Si rowcount es 0, el capítulo con ese ID no existía
                    raise ChapterNotFoundError(f"No se pudo eliminar: Capítulo con ID {chapter_id} no encontrado.")
                # Las ideas concretas asociadas a este capítulo se eliminan automáticamente
                # gracias a la restricción ON DELETE CASCADE definida en la tabla concrete_ideas.
                return True # Retorna True si se eliminó al menos una fila
        except DatabaseError as e:
            # Captura y relanza errores de base de datos durante la eliminación
            raise ChapterDeletionError(f"Error de base de datos al eliminar capítulo ID {chapter_id}: {e}") from e

    def update_chapter_abstract_idea(self, chapter_id: int, abstract_idea: str) -> bool:
        """
        Actualiza solo la idea abstracta de un capítulo existente por su ID.

        Args:
            chapter_id (int): El ID del capítulo a actualizar.
            abstract_idea (str): La nueva idea abstracta del capítulo.

        Returns:
            bool: True si la actualización fue exitosa o si el capítulo existía
                  pero la idea abstracta no cambió.

        Raises:
            ChapterNotFoundError: Si el capítulo con el ID especificado no es encontrado.
            ChapterUpdateError: Si ocurre un error de base de datos durante la actualización.
        """
        query = "UPDATE chapters SET abstract_idea = ? WHERE id = ?"
        try:
            with self.transaction() as cursor:
                cursor.execute(query, (abstract_idea, chapter_id))
                # Verifica si se afectó alguna fila. Si no, puede ser que el ID no exista
                # o que el valor ya fuera el mismo. Verificamos si el ID existe.
                if cursor.rowcount == 0:
                    check_cursor = cursor.connection.cursor()
                    check_cursor.execute("SELECT 1 FROM chapters WHERE id = ?", (chapter_id,))
                    if not check_cursor.fetchone():
                        raise ChapterNotFoundError(f"No se actualizó idea abstracta: Capítulo con ID {chapter_id} no encontrado.")
            return True # Retorna True si se actualizó o si el capítulo existía pero el valor no cambió
        except DatabaseError as e:
            # Captura y relanza errores de base de datos durante la actualización
            raise ChapterUpdateError(f"Error de base de datos al actualizar idea abstracta de capítulo ID {chapter_id}: {e}") from e

    def update_chapter_content_only(self, chapter_id: int, content: str) -> bool:
        """
        Actualiza solo el contenido de un capítulo existente por su ID.

        Args:
            chapter_id (int): El ID del capítulo a actualizar.
            content (str): El nuevo contenido del capítulo.

        Returns:
            bool: True si la actualización fue exitosa o si el capítulo existía
                  pero el contenido no cambió.

        Raises:
            ChapterNotFoundError: Si el capítulo con el ID especificado no es encontrado.
            ChapterUpdateError: Si ocurre un error de base de datos durante la actualización.
        """
        query = "UPDATE chapters SET content = ? WHERE id = ?"
        try:
            with self.transaction() as cursor:
                cursor.execute(query, (content, chapter_id))
                # Verifica si se afectó alguna fila. Si no, puede ser que el ID no exista
                # o que el valor ya fuera el mismo. Verificamos si el ID existe.
                if cursor.rowcount == 0:
                    check_cursor = cursor.connection.cursor()
                    check_cursor.execute("SELECT 1 FROM chapters WHERE id = ?", (chapter_id,))
                    if not check_cursor.fetchone():
                        raise ChapterNotFoundError(f"No se actualizó contenido: Capítulo con ID {chapter_id} no encontrado.")
            return True # Retorna True si se actualizó o si el capítulo existía pero el valor no cambió
        except DatabaseError as e:
            # Captura y relanza errores de base de datos durante la actualización
            raise ChapterUpdateError(f"Error de base de datos al actualizar contenido de capítulo ID {chapter_id}: {e}") from e

    def add_concrete_idea(self, chapter_id: int, idea: str) -> int:
        """
        Añade una nueva idea concreta asociada a un capítulo.

        Args:
            chapter_id (int): El ID del capítulo al que pertenece la idea concreta.
            idea (str): El texto de la idea concreta.

        Returns:
            int: El ID de la idea concreta recién creada.

        Raises:
            ConcreteIdeaError: Si ocurre un error durante la adición de la idea concreta,
                               incluyendo errores de integridad (chapter_id inexistente).
        """
        query = "INSERT INTO concrete_ideas (chapter_id, idea) VALUES (?, ?)"
        try:
            with self.transaction() as cursor:
                cursor.execute(query, (chapter_id, idea))
                idea_id = cursor.lastrowid # Obtiene el ID de la última fila insertada
            if idea_id is None:
                # Si lastrowid es None, la inserción falló de alguna manera inesperada
                raise ConcreteIdeaError(f"No se pudo obtener ID para idea concreta para capítulo ID {chapter_id}")
            return idea_id
        except sqlite3.IntegrityError as e_int:
            # Captura errores de integridad: chapter_id inexistente
            raise ConcreteIdeaError(f"Error de integridad al añadir idea concreta (capítulo ID {chapter_id}): {e_int}") from e_int
        except DatabaseError as e:
            # Captura otros errores de base de datos durante la adición
            raise ConcreteIdeaError(f"Error de base de datos al añadir idea concreta: {e}") from e

    def get_concrete_ideas_by_chapter_id(self, chapter_id: int) -> List[Dict[str, Any]]:
        """
        Recupera todas las ideas concretas asociadas a un capítulo específico.

        Args:
            chapter_id (int): El ID del capítulo cuyas ideas concretas se desean recuperar.

        Returns:
            List[Dict[str, Any]]: Una lista de diccionarios, donde cada diccionario
                                  representa una idea concreta. Retorna una lista vacía
                                  si el capítulo no tiene ideas concretas o si el capítulo no existe.

        Raises:
            ConcreteIdeaError: Si ocurre un error al recuperar las ideas concretas.
        """
        query = "SELECT * FROM concrete_ideas WHERE chapter_id = ?"
        try:
            with self.transaction() as cursor:
                cursor.execute(query, (chapter_id,))
                ideas_data = cursor.fetchall() # Obtiene todas las filas
            # Convierte cada fila (Row) a diccionario y retorna la lista
            return [dict(idea) for idea in ideas_data]
        except DatabaseError as e:
            # Captura y relanza errores de base de datos
            raise ConcreteIdeaError(f"Error de base de datos al obtener ideas concretas para capítulo ID {chapter_id}: {e}") from e

    def update_concrete_idea(self, idea_id: int, idea_text: str) -> bool:
        """
        Actualiza el texto de una idea concreta existente por su ID.

        Args:
            idea_id (int): El ID de la idea concreta a actualizar.
            idea_text (str): El nuevo texto de la idea concreta.

        Returns:
            bool: True si la actualización fue exitosa o si la idea existía
                  pero el texto no cambió.

        Raises:
            ConcreteIdeaError: Si ocurre un error de base de datos durante la actualización.
                               (No levanta error si la idea_id no existe, solo si hay un error de BD).
        """
        query = "UPDATE concrete_ideas SET idea = ? WHERE id = ?"
        try:
            with self.transaction() as cursor:
                cursor.execute(query, (idea_text, idea_id))
                # No verificamos cursor.rowcount == 0 aquí, ya que actualizar a un valor idéntico
                # resulta en rowcount == 0 pero no es un error. Si el ID no existe, la operación
                # simplemente no afecta ninguna fila, lo cual puede ser aceptable dependiendo del caso de uso.
                # Si se necesitara verificar la existencia, se añadiría una consulta SELECT similar a otros métodos update.
            return True # Retorna True si la operación de actualización se ejecutó sin errores de BD
        except DatabaseError as e:
            # Captura y relanza errores de base de datos durante la actualización
            raise ConcreteIdeaError(f"Error de base de datos al actualizar idea concreta con ID {idea_id}: {e}") from e

    def delete_concrete_idea(self, idea_id: int) -> bool:
        """
        Elimina una idea concreta de la base de datos por su ID.

        Args:
            idea_id (int): El ID de la idea concreta a eliminar.

        Returns:
            bool: True si la idea concreta fue eliminada con éxito.

        Raises:
            ConcreteIdeaError: Si la idea concreta con el ID especificado no es encontrada
                               o si ocurre un error de base de datos durante la eliminación.
        """
        query = "DELETE FROM concrete_ideas WHERE id = ?"
        try:
            with self.transaction() as cursor:
                cursor.execute(query, (idea_id,))
                # Verifica cuántas filas fueron afectadas por la eliminación
                if cursor.rowcount == 0:
                    # Si rowcount es 0, la idea concreta con ese ID no existía
                    raise ConcreteIdeaError(f"No se pudo eliminar: Idea concreta con ID {idea_id} no encontrada.")
            return True # Retorna True si se eliminó al menos una fila
        except DatabaseError as e:
            # Captura y relanza errores de base de datos durante la eliminación
            raise ConcreteIdeaError(f"Error de base de datos al eliminar idea concreta con ID {idea_id}: {e}") from e