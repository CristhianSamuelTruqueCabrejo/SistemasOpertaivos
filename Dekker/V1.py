import tkinter as tk
import threading
import time
import random

flag = [False, False]
contador = 0
gui_lock = threading.Lock()

class DekkerV1GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dekker v1 - Problema de Acoplamiento")

        self.status_p0 = tk.Label(root, text="Proceso 0: Inactivo", bg="lightgray", width=50)
        self.status_p0.pack(pady=5)

        self.status_p1 = tk.Label(root, text="Proceso 1: Inactivo", bg="lightgray", width=50)
        self.status_p1.pack(pady=5)

        self.counter_label = tk.Label(root, text="Contador: 0", font=("Arial", 16))
        self.counter_label.pack(pady=20)

        self.start_button = tk.Button(root, text="Iniciar procesos", command=self.iniciar)
        self.start_button.pack(pady=10)

    def actualizar_estado(self, id_proceso, texto, color):
        if id_proceso == 0:
            self.status_p0.config(text=texto, bg=color)
        else:
            self.status_p1.config(text=texto, bg=color)

    def actualizar_contador(self, valor):
        self.counter_label.config(text=f"Contador: {valor}")

    def iniciar(self):
        # Proceso rápido
        threading.Thread(target=self.proceso, args=(0, 0.2)).start()
        # Proceso lento
        threading.Thread(target=self.proceso, args=(1, 2.0)).start()

    def proceso(self, pid, delay):
        global flag, contador

        for _ in range(5):
            self.actualizar_estado(pid, f"Proceso {pid}: Quiere entrar", "orange")
            time.sleep(random.uniform(0.2, 0.5))

            flag[pid] = True
            while flag[1 - pid]:
                self.actualizar_estado(pid, f"Proceso {pid}: Esperando al otro proceso", "red")
                time.sleep(0.1)  # Para visualizar la espera

            self.actualizar_estado(pid, f"Proceso {pid}: EN SECCIÓN CRÍTICA", "lightgreen")
            with gui_lock:
                valor_actual = contador
                time.sleep(0.5)
                contador = valor_actual + 1
                self.actualizar_contador(contador)

            time.sleep(delay)  # Lento o rápido aquí

            flag[pid] = False
            self.actualizar_estado(pid, f"Proceso {pid}: Terminó sección crítica", "lightblue")
            time.sleep(0.5)

        self.actualizar_estado(pid, f"Proceso {pid}: Finalizado", "gray")

# Ejecutar
root = tk.Tk()
app = DekkerV1GUI(root)
root.mainloop()
