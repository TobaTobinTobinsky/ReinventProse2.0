# -*- coding: utf-8 -*-
"""
Archivo: main.py
Descripción: Punto de entrada principal para la aplicación ReinventProse 2.0.
             Inicializa la aplicación wxPython, gestiona la ruta de la base de datos,
             configura los manejadores de lógica y base de datos, y lanza la ventana principal.
Autor: AutoDoc AI
Fecha: 07/06/2025
Versión: 0.0.1
Licencia: MIT License
"""

import wx
import os
import sys
from AppHandler import AppHandler
from DBManager import DBManager
from MainWindow import MainWindow

# Nombre constante para la aplicación
APP_NAME: str
APP_NAME = "ReinventProse 2.0"

def main():
    """
    Función principal que inicializa y ejecuta la aplicación ReinventProse 2.0.

    Esta función configura el entorno de la aplicación, determina la ruta de la base de datos,
    inicializa los manejadores de la base de datos y la lógica de la aplicación,
    crea y muestra la ventana principal, e inicia el bucle de eventos de la GUI.

    Maneja excepciones básicas para errores críticos durante la inicialización o ejecución.
    """
    app: Optional[wx.App]
    app = None
    try:
        # Inicializar la aplicación wxPython.
        app = wx.App(False)

        # Definir el nombre del archivo de la base de datos.
        db_file_name: str
        db_file_name = "reinventprose_v2_data.db"

        # Determinar la ruta del directorio de la aplicación.
        # Esto es crucial para que la BD se cree/encuentre en el lugar correcto,
        # especialmente cuando está empaquetada con PyInstaller.
        app_path: str
        if hasattr(sys, '_MEIPASS'):
            # Si se ejecuta como un ejecutable empaquetado por PyInstaller,
            # la ruta del ejecutable es la base.
            # pyright: ignore[reportGeneralTypeIssues, reportUnknownMemberType]
            app_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # Si se ejecuta como script Python normal,
            # la ruta del script principal es la base.
            app_path = os.path.dirname(os.path.abspath(sys.argv[0]))

        # Construir la ruta completa al archivo de la base de datos.
        db_full_path: str
        db_full_path = os.path.join(app_path, db_file_name)

        # Obtener o crear la instancia singleton de DBManager.
        db_manager: DBManager
        db_manager = DBManager.get_instance(db_full_path)

        # Obtener o crear la instancia singleton de AppHandler.
        app_handler: AppHandler
        app_handler = AppHandler.get_instance(db_manager=db_manager, db_name=db_full_path)

        # Inicializar la base de datos (crea tablas si no existen).
        app_handler.initialize_database()

        # Crear la ventana principal de la aplicación.
        main_window: MainWindow
        main_window = MainWindow(None, APP_NAME, app_handler)

        # Establecer la referencia de la ventana principal en AppHandler para comunicación bidireccional.
        app_handler.set_main_window(main_window)

        # Mostrar la ventana principal.
        main_window.Show()

        # Iniciar el bucle principal de eventos de wxPython.
        # Este bucle mantiene la aplicación GUI en ejecución y responde a las interacciones del usuario.
        if app is not None:
            app.MainLoop()

    except SystemExit as se:
        # Capturar SystemExit para permitir una finalización controlada.
        error_message_system_exit: str
        error_message_system_exit = f"Aplicación ({APP_NAME}) terminada: {se}"
        print(error_message_system_exit)
    except Exception as e:
        # Capturar cualquier otra excepción imprevista durante la inicialización o ejecución.
        error_message_fatal: str
        error_message_fatal = f"Error fatal al inicializar o ejecutar la aplicación ({APP_NAME}): {e}"
        print(error_message_fatal)

        # Imprimir el traceback completo en la consola para facilitar la depuración.
        import traceback
        traceback.print_exc()

        # Intentar mostrar un cuadro de mensaje gráfico si la aplicación wx se inicializó.
        parent_for_msgbox: Optional[wx.Window] = None
        if wx.GetApp():
            # Usar la ventana activa como padre si existe una aplicación wx.
            parent_for_msgbox = wx.GetActiveWindow()

        error_dialog_message: str
        error_dialog_message = f"Ocurrió un error crítico en {APP_NAME}:\n\n{e}\n\nConsulte la consola para más detalles."
        error_dialog_title: str
        error_dialog_title = f"Error Crítico de Aplicación - {APP_NAME}"

        # Mostrar el cuadro de mensaje con el error.
        wx.MessageBox(
            error_dialog_message,
            error_dialog_title,
            wx.OK | wx.ICON_ERROR,
            parent=parent_for_msgbox
        )
    finally:
        # Bloque finally para cualquier limpieza necesaria, aunque a menudo no es crítico aquí.
        pass

if __name__ == '__main__':
    # Este bloque asegura que la función main() se ejecute solo cuando el script
    # se ejecuta directamente (no cuando se importa como módulo).
    main()