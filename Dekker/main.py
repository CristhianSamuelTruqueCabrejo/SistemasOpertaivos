import threading
import time
import tkinter as tk
from tkinter import ttk

class DekkerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Algoritmo de Dekker - Comparación V1 vs V4")

        # Estado compartido
        self.want = [False, False]
        self.turn = 0

        # Control de ejecución
        self.running_v1 = False
        self.running_v4 = False

        # Interface gráfica
        self.canvas = tk.Canvas(master, width=600, height=300)
        self.canvas.pack()

        # Etiquetas
        self.canvas.create_text(100, 20, text="Versión 1 - Sin turno (alto acoplamiento)", font=("Arial", 10, "bold"))
        self.canvas.create_text(400, 20, text="Versión 4 - Con turno (sin interbloqueo)", font=("Arial", 10, "bold"))
        self.canvas.create_text(100, 230, text="P0 (rápido)", font=("Arial", 10))
        self.canvas.create_text(100, 280, text="P1 (lento)", font=("Arial", 10))
        self.canvas.create_text(400, 230, text="P0 (rápido)", font=("Arial", 10))
        self.canvas.create_text(400, 280, text="P1 (lento)", font=("Arial", 10))

        # Rectángulos de estado
        self.boxes_v1 = [
            self.canvas.create_rectangle(50, 50 + i*50, 150, 90 + i*50, fill="white") for i in range(2)
        ]
        self.boxes_v4 = [
            self.canvas.create_rectangle(350, 50 + i*50, 450, 90 + i*50, fill="white") for i in range(2)
        ]

        # Leyenda de colores
        self.canvas.create_text(300, 180, text="🟢 Verde: en sección crítica\n🟡 Amarillo: esperando acceso\n⚪ Blanco: fuera de sección crítica\n🟠 Naranja: esperando turno", font=("Arial", 9))

        # Botones
        self.start_button_v1 = ttk.Button(master, text="Iniciar Versión 1", command=self.run_v1)
        self.start_button_v1.pack(pady=5)

        self.start_button_v4 = ttk.Button(master, text="Iniciar Versión 4", command=self.run_v4)
        self.start_button_v4.pack(pady=5)

    def set_color(self, version, pid, color):
        if version == 1:
            self.canvas.itemconfig(self.boxes_v1[pid], fill=color)
        else:
            self.canvas.itemconfig(self.boxes_v4[pid], fill=color)

    def proceso_v1(self, pid):
        other = 1 - pid
        delay = 0.2 if pid == 0 else 1.5  # Proceso 0 es rápido, Proceso 1 es lento
        while self.running_v1:
            self.want[pid] = True
            while self.want[other]:
                self.set_color(1, pid, "yellow")  # Esperando turno
                time.sleep(0.1)
            self.set_color(1, pid, "green")  # Entrando sección crítica
            time.sleep(delay)
            self.want[pid] = False
            self.set_color(1, pid, "white")  # Saliendo
            time.sleep(delay)

    def run_v1(self):
        if not self.running_v1:
            self.running_v1 = True
            self.want = [False, False]
            threading.Thread(target=self.proceso_v1, args=(0,), daemon=True).start()
            threading.Thread(target=self.proceso_v1, args=(1,), daemon=True).start()

    def proceso_v4(self, pid):
        other = 1 - pid
        delay = 0.2 if pid == 0 else 1.5  # Proceso 0 es rápido, Proceso 1 es lento
        while self.running_v4:
            self.want[pid] = True
            while self.want[other]:
                if self.turn != pid:
                    self.want[pid] = False
                    self.set_color(2, pid, "orange")  # Esperando turno
                    while self.turn != pid:
                        time.sleep(0.1)
                    self.want[pid] = True
            self.set_color(2, pid, "green")  # Entrando sección crítica
            time.sleep(delay)
            self.turn = other
            self.want[pid] = False
            self.set_color(2, pid, "white")
            time.sleep(delay)

    def run_v4(self):
        if not self.running_v4:
            self.running_v4 = True
            self.want = [False, False]
            self.turn = 0
            threading.Thread(target=self.proceso_v4, args=(0,), daemon=True).start()
            threading.Thread(target=self.proceso_v4, args=(1,), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = DekkerGUI(root)
    root.mainloop()