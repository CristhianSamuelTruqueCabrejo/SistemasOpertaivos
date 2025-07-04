import Proceso
from queue import PriorityQueue
import time, random, threading
import tkinter as tk
from tkinter import ttk, messagebox

class PrioridadScheduler:
    def __init__(self):
        self.cola = PriorityQueue()

    def agregar_proceso(self, proceso):
        self.cola.put((proceso.prioridad, proceso))

    def ejecutar(self, callback=None):
        while not self.cola.empty():
            prioridad, proceso = self.cola.get()
            if callback:
                callback(proceso.nombre, prioridad)
            proceso.ejecutar()
            time.sleep(1)

class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Planificador por Prioridad")
        self.scheduler = PrioridadScheduler()
        self.procesos = []

        self.frame = ttk.Frame(root, padding=10)
        self.frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(self.frame, text="Nombre del Proceso:").grid(row=0, column=0)
        self.nombre_entry = ttk.Entry(self.frame)
        self.nombre_entry.grid(row=0, column=1)

        ttk.Label(self.frame, text="Prioridad:").grid(row=1, column=0)
        self.prioridad_entry = ttk.Entry(self.frame)
        self.prioridad_entry.grid(row=1, column=1)

        self.agregar_btn = ttk.Button(self.frame, text="Agregar Proceso", command=self.agregar_proceso)
        self.agregar_btn.grid(row=2, column=0, columnspan=2, pady=5)

        self.lista = tk.Listbox(self.frame, width=40)
        self.lista.grid(row=3, column=0, columnspan=2, pady=5)

        self.ejecutar_btn = ttk.Button(self.frame, text="Ejecutar", command=self.ejecutar_scheduler)
        self.ejecutar_btn.grid(row=4, column=0, columnspan=2, pady=5)

        self.random_btn = ttk.Button(self.frame, text="Llegada Aleatoria", command=self.llegada_aleatoria)
        self.random_btn.grid(row=5, column=0, columnspan=2, pady=5)

        self.running_random = False

    def agregar_proceso(self):
        nombre = self.nombre_entry.get()
        try:
            prioridad = int(self.prioridad_entry.get())
        except ValueError:
            messagebox.showerror("Error", "La prioridad debe ser un número entero.")
            return
        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío.")
            return
        proceso = Proceso.Proceso(nombre, prioridad=prioridad)
        self.scheduler.agregar_proceso(proceso)
        self.lista.insert(tk.END, f"{nombre} (Prioridad: {prioridad})")
        self.nombre_entry.delete(0, tk.END)
        self.prioridad_entry.delete(0, tk.END)

    def ejecutar_scheduler(self):
        self.lista.delete(0, tk.END)
        def mostrar(nombre, prioridad):
            self.lista.insert(tk.END, f"Ejecutando: {nombre} (Prioridad: {prioridad})")
            self.root.update()
        threading.Thread(target=self.scheduler.ejecutar, args=(mostrar,), daemon=True).start()

    def llegada_aleatoria(self):
        if self.running_random:
            return
        self.running_random = True
        def generar_procesos():
            nombres = ["A", "B", "C", "D", "E", "F", "G", "H"]
            while self.running_random:
                nombre = random.choice(nombres) + str(random.randint(1, 100))
                prioridad = random.randint(1, 10)
                proceso = Proceso.Proceso(nombre, prioridad=prioridad)
                self.scheduler.agregar_proceso(proceso)
                self.lista.insert(tk.END, f"{nombre} (Prioridad: {prioridad})")
                self.root.update()
                time.sleep(random.uniform(1, 3))
        threading.Thread(target=generar_procesos, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerGUI(root)
    root.mainloop()