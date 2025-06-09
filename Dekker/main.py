import tkinter as tk
from threading import Thread
import time

# ------------------------------
# Implementación de Dekker V1
# ------------------------------
class DekkerV1:
    def __init__(self):
        # flags indican si cada proceso quiere entrar a la sección crítica
        self.flag = [False, False]
        self.counter = 0

    def run_p0(self, update_gui):
        while True:
            self.flag[0] = True  # Proceso 0 quiere entrar
            while self.flag[1]:  # Espera activa si el otro también quiere entrar
                update_gui("P0", "Esperando", "yellow")
                time.sleep(0.1)
            update_gui("P0", "Entrando", "green")
            self.counter += 1  # Simula trabajo en la sección crítica
            time.sleep(1)
            update_gui("P0", "Saliendo", "red")
            self.flag[0] = False  # Sale de la sección crítica
            time.sleep(1)

    def run_p1(self, update_gui):
        while True:
            self.flag[1] = True
            while self.flag[0]:
                update_gui("P1", "Esperando", "yellow")
                time.sleep(0.1)
            update_gui("P1", "Entrando", "green")
            self.counter += 1
            time.sleep(1)
            update_gui("P1", "Saliendo", "red")
            self.flag[1] = False
            time.sleep(1)

# ------------------------------
# Implementación de Dekker V4
# ------------------------------
class DekkerV4:
    def __init__(self):
        self.flag = [False, False]
        self.turn = 0  # variable de turno para ceder el paso al otro proceso
        self.counter = 0

    def run_p0(self, update_gui):
        while True:
            self.flag[0] = True
            while self.flag[1]:
                if self.turn != 0:
                    self.flag[0] = False
                    while self.turn != 0:
                        update_gui("P0", "Esperando turno", "yellow")
                        time.sleep(0.1)
                    self.flag[0] = True
            update_gui("P0", "Entrando", "green")
            self.counter += 1
            time.sleep(1)
            update_gui("P0", "Saliendo", "red")
            self.turn = 1
            self.flag[0] = False
            time.sleep(1)

    def run_p1(self, update_gui):
        while True:
            self.flag[1] = True
            while self.flag[0]:
                if self.turn != 1:
                    self.flag[1] = False
                    while self.turn != 1:
                        update_gui("P1", "Esperando turno", "yellow")
                        time.sleep(0.1)
                    self.flag[1] = True
            update_gui("P1", "Entrando", "green")
            self.counter += 1
            time.sleep(1)
            update_gui("P1", "Saliendo", "red")
            self.turn = 0
            self.flag[1] = False
            time.sleep(1)

# ------------------------------
# Interfaz gráfica con Tkinter
# ------------------------------
def start_gui():
    root = tk.Tk()
    root.title("Algoritmos de Dekker V1 vs V4")
    root.geometry("800x400")

    # Dividir pantalla en dos partes
    left_frame = tk.Frame(root, width=400, height=400, bg="lightblue")
    right_frame = tk.Frame(root, width=400, height=400, bg="lightgreen")
    left_frame.pack(side="left", fill="both", expand=True)
    right_frame.pack(side="right", fill="both", expand=True)

    # Elementos visuales para Versión 1 (izquierda)
    label_v1 = tk.Label(left_frame, text="Dekker Versión 1", font=("Arial", 16))
    label_v1.pack(pady=10)
    p0_v1_status = tk.Label(left_frame, text="P0: ---", font=("Arial", 12), bg="white")
    p0_v1_status.pack(pady=5)
    p1_v1_status = tk.Label(left_frame, text="P1: ---", font=("Arial", 12), bg="white")
    p1_v1_status.pack(pady=5)

    # Elementos visuales para Versión 4 (derecha)
    label_v4 = tk.Label(right_frame, text="Dekker Versión 4", font=("Arial", 16))
    label_v4.pack(pady=10)
    p0_v4_status = tk.Label(right_frame, text="P0: ---", font=("Arial", 12), bg="white")
    p0_v4_status.pack(pady=5)
    p1_v4_status = tk.Label(right_frame, text="P1: ---", font=("Arial", 12), bg="white")
    p1_v4_status.pack(pady=5)

    # Instancias de los algoritmos
    dekker1 = DekkerV1()
    dekker4 = DekkerV4()

    # Función para actualizar la GUI para V1
    def update_v1(process, status, color):
        if process == "P0":
            p0_v1_status.config(text=f"P0: {status}", bg=color)
        else:
            p1_v1_status.config(text=f"P1: {status}", bg=color)

    # Función para actualizar la GUI para V4
    def update_v4(process, status, color):
        if process == "P0":
            p0_v4_status.config(text=f"P0: {status}", bg=color)
        else:
            p1_v4_status.config(text=f"P1: {status}", bg=color)

    # Iniciar los hilos de ejecución (procesos simulados)
    Thread(target=dekker1.run_p0, args=(update_v1,), daemon=True).start()
    Thread(target=dekker1.run_p1, args=(update_v1,), daemon=True).start()
    Thread(target=dekker4.run_p0, args=(update_v4,), daemon=True).start()
    Thread(target=dekker4.run_p1, args=(update_v4,), daemon=True).start()

    root.mainloop()

# Punto de entrada
if __name__ == "__main__":
    start_gui()
