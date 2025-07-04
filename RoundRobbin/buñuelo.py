import tkinter as tk
from tkinter import ttk
from collections import deque
import random

class Proceso:
    def __init__(self, pid, llegada, rafaga, prioridad):
        self.pid = pid
        self.llegada = llegada
        self.rafaga = rafaga
        self.restante = rafaga
        self.prioridad = prioridad  # 1: RR, 2: FIFO, 3: Prioridades
        self.comienzo = None
        self.final = None
        self.retorno = None
        self.espera = None
        self.envejecimiento = 0

class Planificador:
    def __init__(self, gui):
        self.tiempo = 0
        self.rr_cola = deque()
        self.fifo_cola = deque()
        self.prio_cola = deque()
        self.procesos = []
        self.en_ejecucion = None
        self.quantum = 4
        self.gui = gui

    def agregar_proceso(self, proceso):
        self.procesos.append(proceso)
        if proceso.prioridad == 1:
            self.rr_cola.append(proceso)
        elif proceso.prioridad == 2:
            self.fifo_cola.append(proceso)
        else:
            self.prio_cola.append(proceso)
        self.gui.actualizar_colas()

    def obtener_siguiente_proceso(self):
        if self.rr_cola:
            return self.rr_cola.popleft(), 'RR'
        elif self.fifo_cola:
            return self.fifo_cola.popleft(), 'FIFO'
        elif self.prio_cola:
            return self.prio_cola.popleft(), 'PRIO'
        return None, None

    def ejecutar_ciclo(self):
        # Comprobamos envejecimiento
        for cola in [self.prio_cola, self.fifo_cola]:
            for p in list(cola):
                p.envejecimiento += 1
                if p.envejecimiento >= 3 * p.rafaga:
                    cola.remove(p)
                    p.envejecimiento = 0
                    if p.prioridad > 1:
                        p.prioridad -= 1
                        self.agregar_proceso(p)

        # Interrupciones por llegada de proceso más prioritario
        if self.en_ejecucion:
            if self.rr_cola and self.en_ejecucion.prioridad > 1:
                self.devolver_a_cola(self.en_ejecucion)
                self.en_ejecucion = None
            elif self.fifo_cola and self.en_ejecucion.prioridad > 2:
                self.devolver_a_cola(self.en_ejecucion)
                self.en_ejecucion = None

        if not self.en_ejecucion:
            self.en_ejecucion, tipo = self.obtener_siguiente_proceso()
            if self.en_ejecucion:
                if self.en_ejecucion.comienzo is None:
                    self.en_ejecucion.comienzo = self.tiempo

        if self.en_ejecucion:
            self.en_ejecucion.restante -= 1
            if self.en_ejecucion.restante <= 0:
                self.en_ejecucion.final = self.tiempo + 1
                self.en_ejecucion.retorno = self.en_ejecucion.final - self.en_ejecucion.llegada
                self.en_ejecucion.espera = self.en_ejecucion.retorno - self.en_ejecucion.rafaga
                self.en_ejecucion = None
            elif self.en_ejecucion.prioridad == 1 and (self.tiempo - self.en_ejecucion.comienzo + 1) % self.quantum == 0:
                self.devolver_a_cola(self.en_ejecucion)
                self.en_ejecucion = None

        self.tiempo += 1
        self.gui.actualizar_interfaz(self)
        self.gui.root.after(1000, self.ejecutar_ciclo)

    def devolver_a_cola(self, proceso):
        if proceso.prioridad == 1:
            self.rr_cola.append(proceso)
        elif proceso.prioridad == 2:
            self.fifo_cola.append(proceso)
        else:
            self.prio_cola.append(proceso)
        self.gui.actualizar_colas()

class Interfaz:
    def __init__(self, root):
        self.root = root
        self.root.title("Planificador Multicolas")

        self.colas_frame = ttk.Frame(root)
        self.colas_frame.pack(pady=10)

        self.colas = {}
        for nombre in ["Round Robin", "FIFO", "Prioridades"]:
            frame = ttk.LabelFrame(self.colas_frame, text=nombre)
            frame.pack(side=tk.LEFT, padx=10)
            listbox = tk.Listbox(frame, width=20)
            listbox.pack()
            self.colas[nombre] = listbox

        self.critica_label = ttk.Label(root, text="Sección Crítica: Ningún proceso", font=("Arial", 14))
        self.critica_label.pack(pady=10)

        self.tabla = ttk.Treeview(root, columns=("PID", "Llegada", "Ráfaga", "Comienzo", "Final", "Retorno", "Espera"), show="headings")
        for col in self.tabla["columns"]:
            self.tabla.heading(col, text=col)
        self.tabla.pack(pady=10)

        self.planificador = Planificador(self)
        self.root.after(1000, self.planificador.ejecutar_ciclo)
        self.generar_procesos()

    def actualizar_colas(self):
        self.colas["Round Robin"].delete(0, tk.END)
        for p in self.planificador.rr_cola:
            self.colas["Round Robin"].insert(tk.END, f"P{p.pid} ({p.restante})")
        self.colas["FIFO"].delete(0, tk.END)
        for p in self.planificador.fifo_cola:
            self.colas["FIFO"].insert(tk.END, f"P{p.pid} ({p.restante})")
        self.colas["Prioridades"].delete(0, tk.END)
        for p in self.planificador.prio_cola:
            self.colas["Prioridades"].insert(tk.END, f"P{p.pid} ({p.restante})")

    def actualizar_interfaz(self, planificador):
        if planificador.en_ejecucion:
            self.critica_label.config(text=f"Sección Crítica: P{planificador.en_ejecucion.pid} ({planificador.en_ejecucion.restante})")
        else:
            self.critica_label.config(text="Sección Crítica: Ningún proceso")

        self.tabla.delete(*self.tabla.get_children())
        for p in planificador.procesos:
            self.tabla.insert("", tk.END, values=(p.pid, p.llegada, p.rafaga, p.comienzo, p.final, p.retorno, p.espera))

    def generar_procesos(self):
        for i in range(5):
            llegada = 0
            rafaga = random.randint(3, 10)
            prioridad = random.randint(1, 3)
            proceso = Proceso(pid=i+1, llegada=llegada, rafaga=rafaga, prioridad=prioridad)
            self.planificador.agregar_proceso(proceso)

if __name__ == "__main__":
    root = tk.Tk()
    app = Interfaz(root)
    root.mainloop()
