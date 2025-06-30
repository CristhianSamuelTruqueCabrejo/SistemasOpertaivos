# dekker_gui_dual.py
import threading
import time
import tkinter as tk

class DekkerPanel:
    def __init__(self, parent, version=1):
        self.frame = tk.Frame(parent, bd=2, relief=tk.GROOVE, padx=10, pady=10)
        self.flag = [False, False]
        self.turn = 0
        self.version = version
        self.running = [False, False]
        self.labels = []
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.frame, text=f"Dekker v{self.version}", font=("Arial", 12, "bold")).pack(pady=5)
        for i in range(2):
            subframe = tk.Frame(self.frame)
            subframe.pack(pady=5)
            tk.Label(subframe, text=f"Proceso {i}").pack()
            label = tk.Label(subframe, text="No iniciado", width=25, bg="gray")
            label.pack()
            self.labels.append(label)
            btn = tk.Button(subframe, text=f"Iniciar Proceso {i}", command=lambda idx=i: self.start_process(idx))
            btn.pack()

    def start_process(self, idx):
        if not self.running[idx]:
            self.running[idx] = True
            threading.Thread(target=self.proceso, args=(idx,), daemon=True).start()

    def update_label(self, idx, text, color):
        self.labels[idx].config(text=text, bg=color)
        self.frame.update_idletasks()

    def proceso(self, id):
        otro = 1 - id
        while True:
            # Entrada
            self.flag[id] = True
            self.update_label(id, "Intentando entrar", "yellow")
            if self.version == 1:
                while self.flag[otro]:
                    self.update_label(id, "Esperando...", "orange")
                    time.sleep(0.1)
            elif self.version == 4:
                while self.flag[otro]:
                    if self.turn == otro:
                        self.flag[id] = False
                        self.update_label(id, "Cediendo turno", "orange")
                        while self.turn == otro:
                            time.sleep(0.1)
                        self.flag[id] = True
                        self.update_label(id, "Intentando entrar", "yellow")
                    else:
                        self.update_label(id, "Esperando...", "orange")
                        time.sleep(0.1)
            # Sección crítica
            self.update_label(id, "En sección crítica", "green")
            time.sleep(2)
            # Salida
            if self.version == 4:
                self.turn = otro
            self.flag[id] = False
            # Sección no crítica
            self.update_label(id, "En sección no crítica", "lightblue")
            time.sleep(2)

if __name__ == "__main__":
    root = tk.Tk()    # ...existing code...
    class DekkerPanel:
        def __init__(self, parent, version=1):
            self.frame = tk.Frame(parent, bd=2, relief=tk.GROOVE, padx=10, pady=10)
            self.flag = [False, False]
            self.turn = 0
            self.version = version
            self.running = [False, False]
            self.labels = []
            self.create_widgets()
    
        def create_widgets(self):
            tk.Label(self.frame, text=f"Dekker v{self.version}", font=("Arial", 12, "bold")).pack(pady=5)
            for i in range(2):
                subframe = tk.Frame(self.frame)
                subframe.pack(pady=5)
                tk.Label(subframe, text=f"Proceso {i}").pack()
                label = tk.Label(subframe, text="No iniciado", width=25, bg="gray")
                label.pack()
                self.labels.append(label)
                btn = tk.Button(subframe, text=f"Iniciar Proceso {i}", command=lambda idx=i: self.start_process(idx))
                btn.pack()
    
        def start_process(self, idx):
            if not self.running[idx]:
                self.running[idx] = True
                threading.Thread(target=self.proceso, args=(idx,), daemon=True).start()
    
        def update_label(self, idx, text, color):
            self.labels[idx].config(text=text, bg=color)
            self.frame.update_idletasks()
    
        def proceso(self, id):
            otro = 1 - id
            while True:
                self.flag[id] = True
                self.update_label(id, "Intentando entrar", "yellow")
                if self.version == 1:
                    while self.flag[otro]:
                        self.update_label(id, "Esperando...", "orange")
                        time.sleep(0.1)
                elif self.version == 4:
                    while self.flag[otro]:
                        if self.turn == otro:
                            self.flag[id] = False
                            self.update_label(id, "Cediendo turno", "orange")
                            while self.turn == otro:
                                time.sleep(0.1)
                            self.flag[id] = True
                            self.update_label(id, "Intentando entrar", "yellow")
                        else:
                            self.update_label(id, "Esperando...", "orange")
                            time.sleep(0.1)
                # Sección crítica
                self.update_label(id, "En sección crítica", "green")
                # --- Diferencia de velocidad ---
                if self.version == 1:
                    if id == 0:
                        time.sleep(0.5)   # Proceso 0: rápido
                    else:
                        time.sleep(3.0)   # Proceso 1: lento
                else:
                    time.sleep(2)
                # Salida de la sección crítica
                if self.version == 4:
                    self.turn = otro
                self.flag[id] = False
                # Sección no crítica
                self.update_label(id, "En sección no crítica", "lightblue")
                if self.version == 1:
                    if id == 0:
                        time.sleep(0.5)   # Proceso 0: rápido
                    else:
                        time.sleep(3.0)   # Proceso 1: lento
                else:
                    time.sleep(2)
    # ...existing code...    # ...existing code...
    class DekkerPanel:
        def __init__(self, parent, version=1):
            self.frame = tk.Frame(parent, bd=2, relief=tk.GROOVE, padx=10, pady=10)
            self.flag = [False, False]
            self.turn = 0
            self.version = version
            self.running = [False, False]
            self.labels = []
            self.create_widgets()
    
        def create_widgets(self):
            tk.Label(self.frame, text=f"Dekker v{self.version}", font=("Arial", 12, "bold")).pack(pady=5)
            for i in range(2):
                subframe = tk.Frame(self.frame)
                subframe.pack(pady=5)
                tk.Label(subframe, text=f"Proceso {i}").pack()
                label = tk.Label(subframe, text="No iniciado", width=25, bg="gray")
                label.pack()
                self.labels.append(label)
                btn = tk.Button(subframe, text=f"Iniciar Proceso {i}", command=lambda idx=i: self.start_process(idx))
                btn.pack()
    
        def start_process(self, idx):
            if not self.running[idx]:
                self.running[idx] = True
                threading.Thread(target=self.proceso, args=(idx,), daemon=True).start()
    
        def update_label(self, idx, text, color):
            self.labels[idx].config(text=text, bg=color)
            self.frame.update_idletasks()
    
        def proceso(self, id):
            otro = 1 - id
            while True:
                self.flag[id] = True
                self.update_label(id, "Intentando entrar", "yellow")
                if self.version == 1:
                    while self.flag[otro]:
                        self.update_label(id, "Esperando...", "orange")
                        time.sleep(0.1)
                elif self.version == 4:
                    while self.flag[otro]:
                        if self.turn == otro:
                            self.flag[id] = False
                            self.update_label(id, "Cediendo turno", "orange")
                            while self.turn == otro:
                                time.sleep(0.1)
                            self.flag[id] = True
                            self.update_label(id, "Intentando entrar", "yellow")
                        else:
                            self.update_label(id, "Esperando...", "orange")
                            time.sleep(0.1)
                # Sección crítica
                self.update_label(id, "En sección crítica", "green")
                # --- Diferencia de velocidad ---
                if self.version == 1:
                    if id == 0:
                        time.sleep(0.5)   # Proceso 0: rápido
                    else:
                        time.sleep(3.0)   # Proceso 1: lento
                else:
                    time.sleep(2)
                # Salida de la sección crítica
                if self.version == 4:
                    self.turn = otro
                self.flag[id] = False
                # Sección no crítica
                self.update_label(id, "En sección no crítica", "lightblue")
                if self.version == 1:
                    if id == 0:
                        time.sleep(0.5)   # Proceso 0: rápido
                    else:
                        time.sleep(3.0)   # Proceso 1: lento
                else:
                    time.sleep(2)
    # ...existing code...
    root.title("Algoritmo de Dekker: Primera y Cuarta Versión")

    # Panel para la primera versión
    panel1 = DekkerPanel(root, version=1)
    panel1.frame.pack(side=tk.LEFT, padx=20, pady=20)

    # Panel para la cuarta versión
    panel4 = DekkerPanel(root, version=4)
    panel4.frame.pack(side=tk.RIGHT, padx=20, pady=20)

    root.mainloop()