import tkinter as tk
from tkinter import ttk, messagebox
import random
import queue
from collections import deque
import threading
import time

class Proceso:
    def __init__(self, id_proceso, tiempo_llegada, rafaga, prioridad=None):
        self.id_proceso = id_proceso
        self.tiempo_llegada = tiempo_llegada
        self.rafaga = rafaga
        self.rafaga_restante = rafaga
        self.prioridad = prioridad
        self.tiempo_comienzo = -1
        self.tiempo_final = -1
        self.tiempo_retorno = -1
        self.tiempo_espera = -1
    
    def calcular_metricas(self, tiempo_actual):
        if self.tiempo_comienzo == -1:
            self.tiempo_comienzo = tiempo_actual
        
        self.tiempo_final = tiempo_actual
        self.tiempo_retorno = self.tiempo_final - self.tiempo_llegada
        self.tiempo_espera = self.tiempo_retorno - self.rafaga
    
    def __str__(self):
        return f"Proceso {self.id_proceso} (Llegada: {self.tiempo_llegada}, Rafaga: {self.rafaga}, Prioridad: {self.prioridad})"

class SimuladorMulticolas:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Multicolas con Prioridades")
        
        # Configuración inicial
        self.quantum = 2
        self.tiempo_actual = 0
        self.proceso_actual = None
        self.en_ejecucion = False
        self.ultimo_id = 0
        
        # Colas de prioridad
        self.cola_rr = deque()  # Round Robin (prioridad 1)
        self.cola_fifo = queue.Queue()  # FIFO (prioridad 2)
        self.cola_prioridades = []  # Prioridades (prioridad 3)
        
        # Historial de procesos completados
        self.procesos_completados = []
        
        # Configurar interfaz gráfica
        self.setup_ui()
        
        # Hilo para la simulación
        self.simulacion_thread = None
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Panel de control
        control_frame = ttk.LabelFrame(main_frame, text="Control", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Button(control_frame, text="Iniciar Simulación", command=self.iniciar_simulacion).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="Pausar Simulación", command=self.pausar_simulacion).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="Agregar Proceso", command=self.agregar_proceso_manual).grid(row=0, column=2, padx=5, pady=5)
        
        # Configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(config_frame, text="Quantum RR:").grid(row=0, column=0, padx=5, pady=5)
        self.quantum_entry = ttk.Entry(config_frame, width=5)
        self.quantum_entry.grid(row=0, column=1, padx=5, pady=5)
        self.quantum_entry.insert(0, str(self.quantum))
        
        ttk.Button(config_frame, text="Aplicar", command=self.aplicar_configuracion).grid(row=0, column=2, padx=5, pady=5)
        
        # Visualización de colas
        colas_frame = ttk.LabelFrame(main_frame, text="Colas de Procesos", padding="10")
        colas_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Cola Round Robin
        ttk.Label(colas_frame, text="Round Robin (Prioridad 1)", foreground="red").grid(row=0, column=0, padx=5, pady=5)
        self.rr_tree = ttk.Treeview(colas_frame, columns=("id", "llegada", "rafaga", "rafaga_restante"), show="headings", height=5)
        self.rr_tree.heading("id", text="ID")
        self.rr_tree.heading("llegada", text="Llegada")
        self.rr_tree.heading("rafaga", text="Ráfaga")
        self.rr_tree.heading("rafaga_restante", text="Ráfaga Restante")
        self.rr_tree.grid(row=1, column=0, padx=5, pady=5)
        
        # Cola FIFO
        ttk.Label(colas_frame, text="FIFO (Prioridad 2)", foreground="blue").grid(row=0, column=1, padx=5, pady=5)
        self.fifo_tree = ttk.Treeview(colas_frame, columns=("id", "llegada", "rafaga"), show="headings", height=5)
        self.fifo_tree.heading("id", text="ID")
        self.fifo_tree.heading("llegada", text="Llegada")
        self.fifo_tree.heading("rafaga", text="Ráfaga")
        self.fifo_tree.grid(row=1, column=1, padx=5, pady=5)
        
        # Cola Prioridades
        ttk.Label(colas_frame, text="Prioridades (Prioridad 3)", foreground="green").grid(row=0, column=2, padx=5, pady=5)
        self.prioridades_tree = ttk.Treeview(colas_frame, columns=("id", "llegada", "rafaga", "prioridad"), show="headings", height=5)
        self.prioridades_tree.heading("id", text="ID")
        self.prioridades_tree.heading("llegada", text="Llegada")
        self.prioridades_tree.heading("rafaga", text="Ráfaga")
        self.prioridades_tree.heading("prioridad", text="Prioridad")
        self.prioridades_tree.grid(row=1, column=2, padx=5, pady=5)
        
        # Proceso en ejecución
        ejecucion_frame = ttk.LabelFrame(main_frame, text="Proceso en Ejecución", padding="10")
        ejecucion_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.ejecucion_label = ttk.Label(ejecucion_frame, text="Ninguno", font=('Helvetica', 12, 'bold'))
        self.ejecucion_label.grid(row=0, column=0, padx=5, pady=5)
        
        # Tiempo actual
        tiempo_frame = ttk.LabelFrame(main_frame, text="Tiempo Actual", padding="10")
        tiempo_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.tiempo_label = ttk.Label(tiempo_frame, text="0", font=('Helvetica', 14))
        self.tiempo_label.grid(row=0, column=0, padx=5, pady=5)
        
        # Historial de procesos completados
        historial_frame = ttk.LabelFrame(main_frame, text="Procesos Completados", padding="10")
        historial_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        columns = ("id", "llegada", "rafaga", "comienzo", "final", "retorno", "espera", "prioridad")
        self.historial_tree = ttk.Treeview(historial_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.historial_tree.heading(col, text=col.capitalize())
            self.historial_tree.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(historial_frame, orient="vertical", command=self.historial_tree.yview)
        self.historial_tree.configure(yscrollcommand=scrollbar.set)
        
        self.historial_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Auto-generar procesos
        self.auto_generar = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Auto-generar procesos", variable=self.auto_generar).grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
    
    def aplicar_configuracion(self):
        try:
            self.quantum = int(self.quantum_entry.get())
            messagebox.showinfo("Configuración", f"Quantum actualizado a {self.quantum}")
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un valor numérico para el quantum")
    
    def agregar_proceso(self, proceso):
        if proceso.prioridad == 1:
            self.cola_rr.append(proceso)
        elif proceso.prioridad == 2:
            self.cola_fifo.put(proceso)
        elif proceso.prioridad == 3:
            self.cola_prioridades.append(proceso)
            # Ordenar por prioridad (menor número = mayor prioridad)
            self.cola_prioridades.sort(key=lambda x: x.prioridad)
        
        self.actualizar_interfaz()
    
    def agregar_proceso_manual(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Proceso")
        
        ttk.Label(dialog, text="Prioridad (1: RR, 2: FIFO, 3: Prioridades):").grid(row=0, column=0, padx=5, pady=5)
        prioridad_entry = ttk.Entry(dialog)
        prioridad_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Ráfaga:").grid(row=1, column=0, padx=5, pady=5)
        rafaga_entry = ttk.Entry(dialog)
        rafaga_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Prioridad (solo para cola 3):").grid(row=2, column=0, padx=5, pady=5)
        sub_prioridad_entry = ttk.Entry(dialog)
        sub_prioridad_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def agregar():
            try:
                prioridad = int(prioridad_entry.get())
                rafaga = int(rafaga_entry.get())
                
                if prioridad not in [1, 2, 3]:
                    raise ValueError("Prioridad debe ser 1, 2 o 3")
                
                sub_prioridad = None
                if prioridad == 3:
                    sub_prioridad = int(sub_prioridad_entry.get())
                
                self.ultimo_id += 1
                proceso = Proceso(self.ultimo_id, self.tiempo_actual, rafaga, prioridad if prioridad != 3 else sub_prioridad)
                self.agregar_proceso(proceso)
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
        
        ttk.Button(dialog, text="Agregar", command=agregar).grid(row=3, column=0, columnspan=2, pady=10)
    
    def generar_proceso_aleatorio(self):
        if not self.auto_generar.get():
            return
        
        if random.random() < 0.3:  # 30% de probabilidad de generar un proceso
            self.ultimo_id += 1
            prioridad = random.choices([1, 2, 3], weights=[0.3, 0.4, 0.3])[0]
            rafaga = random.randint(1, 10)
            
            if prioridad == 3:
                sub_prioridad = random.randint(1, 5)  # Prioridades del 1 al 5 (1 es más alta)
                proceso = Proceso(self.ultimo_id, self.tiempo_actual, rafaga, sub_prioridad)
            else:
                proceso = Proceso(self.ultimo_id, self.tiempo_actual, rafaga, prioridad)
            
            self.agregar_proceso(proceso)
    
    def seleccionar_proceso(self):
        # Prioridad 1: Round Robin
        if self.cola_rr:
            return self.cola_rr.popleft()
        
        # Prioridad 2: FIFO
        if not self.cola_fifo.empty():
            return self.cola_fifo.get()
        
        # Prioridad 3: Prioridades
        if self.cola_prioridades:
            return self.cola_prioridades.pop(0)
        
        return None
    
    def expulsar_proceso_actual(self):
        if self.proceso_actual:
            # Reinsertar el proceso en su cola original con la ráfaga restante
            if self.proceso_actual.prioridad == 1:
                self.cola_rr.appendleft(self.proceso_actual)
            elif self.proceso_actual.prioridad == 2:
                # Para FIFO, necesitamos recrear la cola para insertar al frente
                temp_queue = queue.Queue()
                temp_queue.put(self.proceso_actual)
                while not self.cola_fifo.empty():
                    temp_queue.put(self.cola_fifo.get())
                self.cola_fifo = temp_queue
            elif self.proceso_actual.prioridad >= 3:  # Prioridades
                self.cola_prioridades.insert(0, self.proceso_actual)
                self.cola_prioridades.sort(key=lambda x: x.prioridad)
            
            self.proceso_actual = None
    
    def ejecutar_proceso(self):
        # Verificar si hay un proceso de mayor prioridad que el actual
        if self.proceso_actual:
            if (self.cola_rr and self.proceso_actual.prioridad > 1) or \
               (not self.cola_fifo.empty() and self.proceso_actual.prioridad > 2):
                self.expulsar_proceso_actual()
        
        # Si no hay proceso actual, seleccionar uno nuevo
        if not self.proceso_actual:
            self.proceso_actual = self.seleccionar_proceso()
            if self.proceso_actual and self.proceso_actual.tiempo_comienzo == -1:
                self.proceso_actual.tiempo_comienzo = self.tiempo_actual
        
        # Ejecutar el proceso actual
        if self.proceso_actual:
            # Reducir ráfaga restante
            self.proceso_actual.rafaga_restante -= 1
            
            # Verificar si el proceso ha terminado
            if self.proceso_actual.rafaga_restante <= 0:
                self.proceso_actual.calcular_metricas(self.tiempo_actual + 1)
                self.procesos_completados.append(self.proceso_actual)
                self.proceso_actual = None
            # Verificar si es tiempo de cambiar de proceso (solo para RR)
            elif self.proceso_actual.prioridad == 1 and \
                 (self.proceso_actual.rafaga - self.proceso_actual.rafaga_restante) % self.quantum == 0:
                self.expulsar_proceso_actual()
    
    def actualizar_interfaz(self):
        # Actualizar tiempo actual
        self.tiempo_label.config(text=str(self.tiempo_actual))
        
        # Actualizar proceso en ejecución
        if self.proceso_actual:
            texto = f"Proceso {self.proceso_actual.id_proceso} (Prioridad: {self.proceso_actual.prioridad}, Rafaga restante: {self.proceso_actual.rafaga_restante})"
            color = "red" if self.proceso_actual.prioridad == 1 else \
                   "blue" if self.proceso_actual.prioridad == 2 else "green"
            self.ejecucion_label.config(text=texto, foreground=color)
        else:
            self.ejecucion_label.config(text="Ninguno", foreground="black")
        
        # Actualizar colas
        self.actualizar_cola_treeview(self.rr_tree, list(self.cola_rr))
        self.actualizar_cola_treeview(self.fifo_tree, list(self.cola_fifo.queue))
        self.actualizar_cola_treeview(self.prioridades_tree, self.cola_prioridades)
        
        # Actualizar historial
        self.actualizar_historial()
    
    def actualizar_cola_treeview(self, treeview, cola):
        # Limpiar el treeview
        for item in treeview.get_children():
            treeview.delete(item)
        
        # Agregar los procesos actuales
        for proceso in cola:
            if treeview == self.rr_tree:
                treeview.insert("", "end", values=(
                    proceso.id_proceso,
                    proceso.tiempo_llegada,
                    proceso.rafaga,
                    proceso.rafaga_restante
                ))
            elif treeview == self.fifo_tree:
                treeview.insert("", "end", values=(
                    proceso.id_proceso,
                    proceso.tiempo_llegada,
                    proceso.rafaga
                ))
            elif treeview == self.prioridades_tree:
                treeview.insert("", "end", values=(
                    proceso.id_proceso,
                    proceso.tiempo_llegada,
                    proceso.rafaga,
                    proceso.prioridad
                ))
    
    def actualizar_historial(self):
        # Limpiar el treeview
        for item in self.historial_tree.get_children():
            self.historial_tree.delete(item)
        
        # Agregar procesos completados
        for proceso in self.procesos_completados:
            self.historial_tree.insert("", "end", values=(
                proceso.id_proceso,
                proceso.tiempo_llegada,
                proceso.rafaga,
                proceso.tiempo_comienzo,
                proceso.tiempo_final,
                proceso.tiempo_retorno,
                proceso.tiempo_espera,
                proceso.prioridad if proceso.prioridad in [1, 2] else f"3.{proceso.prioridad}"
            ))
    
    def iniciar_simulacion(self):
        if not self.en_ejecucion:
            self.en_ejecucion = True
            self.simulacion_thread = threading.Thread(target=self.simular, daemon=True)
            self.simulacion_thread.start()
    
    def pausar_simulacion(self):
        self.en_ejecucion = False
    
    def simular(self):
        while self.en_ejecucion:
            # Generar proceso aleatorio
            self.generar_proceso_aleatorio()
            
            # Ejecutar paso de simulación
            self.ejecutar_proceso()
            
            # Incrementar tiempo
            self.tiempo_actual += 1
            
            # Actualizar interfaz
            self.root.after(0, self.actualizar_interfaz)
            
            # Esperar un segundo (para simulación en tiempo real)
            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorMulticolas(root)
    root.mainloop()