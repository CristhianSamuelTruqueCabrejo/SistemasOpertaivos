import tkinter as tk
import threading
import time
import random

# Variables globales para el algoritmo de Dekker
flag = [False, False]  # Indica intención de entrar a sección crítica
turn = 0               # Define a quién le toca entrar
contador = 0           # Recurso compartido (sección crítica)

# Lock para evitar condiciones de carrera al actualizar GUI desde hilos
gui_lock = threading.Lock()

# Clase para la interfaz gráfica
class DekkerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Algoritmo de Dekker - Versión 4")

        # Etiquetas para mostrar el estado de cada proceso
        self.status_p0 = tk.Label(root, text="Proceso 0: Inactivo", bg="lightgray", width=40)
        self.status_p0.pack(pady=5)

        self.status_p1 = tk.Label(root, text="Proceso 1: Inactivo", bg="lightgray", width=40)
        self.status_p1.pack(pady=5)

        # Etiqueta para mostrar el valor del contador compartido
        self.counter_label = tk.Label(root, text="Contador: 0", font=("Arial", 14))
        self.counter_label.pack(pady=20)

        # Botón para iniciar los procesos
        self.start_button = tk.Button(root, text="Iniciar procesos", command=self.iniciar)
        self.start_button.pack(pady=10)

    def actualizar_estado(self, id_proceso, texto, color):
        """Actualiza el estado visual del proceso en la GUI"""
        if id_proceso == 0:
            self.status_p0.config(text=texto, bg=color)
        else:
            self.status_p1.config(text=texto, bg=color)

    def actualizar_contador(self, valor):
        """Actualiza el valor del contador en la GUI"""
        self.counter_label.config(text=f"Contador: {valor}")

    def iniciar(self):
        """Inicia ambos procesos como hilos separados"""
        threading.Thread(target=self.proceso, args=(0,)).start()
        threading.Thread(target=self.proceso, args=(1,)).start()

    def proceso(self, pid):
        """Simula la ejecución del proceso con ID pid (0 o 1)"""
        global flag, turn, contador

        for _ in range(5):  # Cada proceso entra 5 veces a la sección crítica
            # Sección no crítica
            self.actualizar_estado(pid, f"Proceso {pid}: Esperando", "orange")
            time.sleep(random.uniform(0.5, 1.5))  # Simula trabajo externo

            # Algoritmo de Dekker
            flag[pid] = True  # Declaro que quiero entrar a la sección crítica
            while flag[1 - pid]:  # Si el otro también quiere entrar
                if turn != pid:  # Si no es mi turno
                    flag[pid] = False  # Cedo el paso
                    while turn != pid:  # Espero mi turno activamente
                        pass
                    flag[pid] = True  # Retomo el intento

            # Sección crítica
            self.actualizar_estado(pid, f"Proceso {pid}: EN SECCIÓN CRÍTICA", "lightgreen")
            with gui_lock:  # Asegura que GUI no se actualice en simultáneo
                valor_actual = contador
                time.sleep(0.5)  # Simula trabajo dentro de sección crítica
                contador = valor_actual + 1
                self.actualizar_contador(contador)

            # Salida de la sección crítica
            turn = 1 - pid      # Le cedo el turno al otro proceso
            flag[pid] = False   # Ya no quiero entrar
            self.actualizar_estado(pid, f"Proceso {pid}: Fuera de sección crítica", "lightblue")
            time.sleep(1)

        # Proceso ha terminado
        self.actualizar_estado(pid, f"Proceso {pid}: Finalizado", "gray")

# Crear ventana principal de tkinter
if __name__ == "__main__":
    root = tk.Tk()
    app = DekkerGUI(root)
    root.mainloop()
