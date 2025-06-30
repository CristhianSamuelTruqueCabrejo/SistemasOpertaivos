import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from collections import deque, defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch

class Proceso:
    COLORES_PROCESOS = [
        '#1f77b4', '#2ca02c', '#9467bd', '#e377c2',
        '#7f7f7f', '#bcbd22', '#17becf', '#ff7f0e'
    ]

    def __init__(self, nombre, tiempo_llegada, rafaga):
        self.nombre = nombre
        self.tiempo_llegada = tiempo_llegada
        self.rafaga_total = rafaga
        self.rafaga_restante = rafaga
        self.color = self.asignar_color(nombre)
        self.reingresos = []  # Historial de ejecuciones parciales

    def asignar_color(self, nombre):
        hash_val = hash(nombre)
        return self.COLORES_PROCESOS[hash_val % len(self.COLORES_PROCESOS)]

class Ejecucion:
    def __init__(self, proceso: Proceso, alias, rafaga, tiempo_llegada):
        self.original = proceso
        self.alias = alias
        self.rafaga_total = rafaga
        self.rafaga_ejecucion = 0
        self.rafaga_restante = rafaga
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_comienzo = -1
        self.tiempo_final = -1
        self.tiempo_espera = 0
        self.bloqueado = False
        self.tiempo_bloqueado = 0
        self.tiempo_en_bloqueado = 0
        self.quantum_usado = 0  # Contador de quantum usado

class RoundRobinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Round Robin")
        self.root.geometry("1200x900")

        self.quantum = tk.IntVar(value=3)
        self.tiempo_bloqueo = tk.IntVar(value=2)
        self.procesos = []
        self.ejecuciones = []
        self.reingresos_contador = defaultdict(int)
        self.proceso_actual = None
        self.tiempo_actual = 0
        self.ejecutando = False
        self.pausado = False
        self.cola_listos = deque()
        self.cola_bloqueados = deque()
        self.gantt_data = []
        self.simulation_thread = None

        self.setup_ui()

    def setup_ui(self):
        # Frame de controles
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(fill=tk.X)

        tk.Label(control_frame, text="Quantum:").grid(row=0, column=0, padx=5)
        quantum_entry = tk.Entry(control_frame, textvariable=self.quantum, width=5)
        quantum_entry.grid(row=0, column=1, padx=5)

        tk.Label(control_frame, text="Tiempo Bloqueo:").grid(row=0, column=2, padx=5)
        bloqueo_entry = tk.Entry(control_frame, textvariable=self.tiempo_bloqueo, width=5)
        bloqueo_entry.grid(row=0, column=3, padx=5)

        tk.Button(control_frame, text="Agregar Proceso", command=self.agregar_proceso).grid(row=0, column=4, padx=5)
        tk.Button(control_frame, text="Iniciar", command=self.iniciar_simulacion).grid(row=0, column=5, padx=5)
        tk.Button(control_frame, text="Pausar/Continuar", command=self.pausar_continuar).grid(row=0, column=6, padx=5)
        tk.Button(control_frame, text="Reiniciar", command=self.reiniciar).grid(row=0, column=7, padx=5)

        # Frame principal con paneles
        main_paned = tk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # Frame superior con tabla de procesos
        top_frame = tk.Frame(main_paned)
        main_paned.add(top_frame)

        # Frame inferior con diagrama de Gantt y cola de bloqueados
        bottom_paned = tk.PanedWindow(main_paned, orient=tk.HORIZONTAL)
        main_paned.add(bottom_paned)

        # Panel izquierdo: Diagrama de Gantt
        gantt_frame = tk.Frame(bottom_paned)
        bottom_paned.add(gantt_frame)

        # Panel derecho: Cola de bloqueados
        bloqueados_frame = tk.Frame(bottom_paned, width=300, padx=10, pady=10)
        bottom_paned.add(bloqueados_frame)

        # Configuración de la tabla de procesos
        self.tree = ttk.Treeview(top_frame, columns=("PROCESO", "T.LLEGADA", "RAFAGA TOTAL", "T.COMIENZO",
                                            "T.EJECUCIÓN", "T.ESPERA", "RAFAGA EJECUCION"), show="headings")

        headers = ["PROCESO", "T.LLEGADA", "RAFAGA TOTAL", "T.COMIENZO", "T.EJECUCIÓN", "T.ESPERA", "RAFAGA EJECUCION"]
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(top_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configuración del diagrama de Gantt
        self.fig, self.ax = plt.subplots(figsize=(10, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=gantt_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Configuración de la cola de bloqueados
        tk.Label(bloqueados_frame, text="Cola de Procesos Bloqueados", font=('Arial', 12, 'bold')).pack(pady=5)
        
        self.bloqueados_tree = ttk.Treeview(bloqueados_frame, columns=("PROCESO", "TIEMPO RESTANTE", "TIEMPO BLOQUEO"), 
                                         show="headings", height=15)
        self.bloqueados_tree.heading("PROCESO", text="PROCESO")
        self.bloqueados_tree.heading("TIEMPO RESTANTE", text="TIEMPO RESTANTE")
        self.bloqueados_tree.heading("TIEMPO BLOQUEO", text="TIEMPO BLOQUEO")
        
        self.bloqueados_tree.column("PROCESO", width=100, anchor=tk.CENTER)
        self.bloqueados_tree.column("TIEMPO RESTANTE", width=100, anchor=tk.CENTER)
        self.bloqueados_tree.column("TIEMPO BLOQUEO", width=100, anchor=tk.CENTER)
        
        scrollbar_bloq = ttk.Scrollbar(bloqueados_frame, orient="vertical", command=self.bloqueados_tree.yview)
        self.bloqueados_tree.configure(yscrollcommand=scrollbar_bloq.set)
        scrollbar_bloq.pack(side="right", fill="y")
        self.bloqueados_tree.pack(fill=tk.BOTH, expand=True)

    def actualizar_cola_bloqueados(self):
        self.bloqueados_tree.delete(*self.bloqueados_tree.get_children())
        for proceso in self.cola_bloqueados:
            tiempo_restante = proceso.rafaga_restante
            tiempo_en_bloqueo = proceso.tiempo_en_bloqueado
            tiempo_bloqueo_total = self.tiempo_bloqueo.get()
            tiempo_faltante = max(0, tiempo_bloqueo_total - tiempo_en_bloqueo)
            
            self.bloqueados_tree.insert("", "end", values=(
                proceso.alias,
                tiempo_restante,
                f"{tiempo_en_bloqueo}/{tiempo_bloqueo_total}",
            ))

    def agregar_proceso(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Proceso")
        dialog.geometry("300x200")

        tk.Label(dialog, text="Nombre del proceso:").pack()
        nombre_entry = tk.Entry(dialog)
        nombre_entry.pack()

        tk.Label(dialog, text="Tiempo de llegada:").pack()
        llegada_entry = tk.Entry(dialog)
        llegada_entry.pack()

        tk.Label(dialog, text="Ráfaga total:").pack()
        rafaga_entry = tk.Entry(dialog)
        rafaga_entry.pack()

        def guardar():
            try:
                nombre = nombre_entry.get()
                llegada = int(llegada_entry.get())
                rafaga = int(rafaga_entry.get())
                if nombre and rafaga > 0:
                    proceso = Proceso(nombre, llegada, rafaga)
                    self.procesos.append(proceso)
                    self.reingresos_contador[nombre] = 0
                    alias = nombre
                    ejecucion = Ejecucion(proceso, alias, rafaga, llegada)
                    proceso.reingresos.append(ejecucion)
                    self.ejecuciones.append(ejecucion)
                    dialog.destroy()
                    self.actualizar_tabla()
            except ValueError:
                messagebox.showerror("Error", "Datos inválidos")

        tk.Button(dialog, text="Agregar", command=guardar).pack(pady=10)

    def actualizar_tabla(self):
        self.tree.delete(*self.tree.get_children())
        for ejec in self.ejecuciones:
            # Calcular tiempo de ejecución (final - comienzo) si el proceso ha terminado
            tiempo_ejecucion = "-"
            if ejec.tiempo_comienzo != -1 and ejec.tiempo_final != -1:
                tiempo_ejecucion = ejec.tiempo_final - ejec.tiempo_comienzo
            
            self.tree.insert("", "end", values=(
                ejec.alias,
                ejec.tiempo_llegada,
                ejec.rafaga_total,
                ejec.tiempo_comienzo if ejec.tiempo_comienzo != -1 else "-",
                tiempo_ejecucion,  # Mostrar tiempo que tardó en ejecutar este fragmento
                ejec.tiempo_espera,
                f"{ejec.rafaga_ejecucion}/{ejec.rafaga_total}"
            ))

    def iniciar_simulacion(self):
        if not self.ejecuciones:
            messagebox.showwarning("Advertencia", "No hay procesos para ejecutar")
            return
        
        if self.simulation_thread and self.simulation_thread.is_alive():
            return
            
        self.ejecutando = True
        self.pausado = False
        self.tiempo_actual = 0
        self.cola_listos = deque([e for e in self.ejecuciones if e.tiempo_llegada == 0])
        self.simulation_thread = threading.Thread(target=self.simular, daemon=True)
        self.simulation_thread.start()

    def pausar_continuar(self):
        if not self.ejecutando:
            return
        self.pausado = not self.pausado

    def reiniciar(self):
        self.ejecutando = False
        self.pausado = False
        self.tiempo_actual = 0
        self.proceso_actual = None
        self.gantt_data = []
        self.cola_listos.clear()
        self.cola_bloqueados.clear()
        
        # Esperar a que el hilo de simulación termine
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join()
        
        # Reiniciar todos los procesos
        self.ejecuciones.clear()
        for p in self.procesos:
            self.reingresos_contador[p.nombre] = 0
            p.reingresos.clear()
            alias = p.nombre
            e = Ejecucion(p, alias, p.rafaga_total, p.tiempo_llegada)
            p.reingresos.append(e)
            self.ejecuciones.append(e)
        
        self.actualizar_tabla()
        self.actualizar_diagrama_gantt()
        self.actualizar_cola_bloqueados()

    def simular(self):
        quantum = self.quantum.get()
        tiempo_bloqueo = self.tiempo_bloqueo.get()

        while self.ejecutando:
            if self.pausado:
                time.sleep(0.1)
                continue

            # Verificar si han llegado nuevos procesos
            for p in self.procesos:
                if self.tiempo_actual == p.tiempo_llegada:
                    # Buscar la ejecución original del proceso
                    ejecucion = next((e for e in self.ejecuciones 
                                    if e.original == p and e.alias == p.nombre), None)
                    if ejecucion and ejecucion not in self.cola_listos and ejecucion not in self.cola_bloqueados:
                        self.cola_listos.append(ejecucion)

            # Procesar cola de bloqueados
            if self.cola_bloqueados:
                proceso_bloqueado = self.cola_bloqueados[0]
                proceso_bloqueado.tiempo_en_bloqueado += 1
                
                if proceso_bloqueado.tiempo_en_bloqueado >= tiempo_bloqueo:
                    proceso = self.cola_bloqueados.popleft()
                    self.cola_listos.append(proceso)
                    proceso.tiempo_en_bloqueado = 0

            # Asignar CPU si está libre
            if self.proceso_actual is None and self.cola_listos:
                self.proceso_actual = self.cola_listos.popleft()
                self.proceso_actual.quantum_usado = 0  # Reiniciar contador de quantum
                if self.proceso_actual.tiempo_comienzo == -1:
                    self.proceso_actual.tiempo_comienzo = self.tiempo_actual
                self.gantt_data.append({
                    'proceso': self.proceso_actual.original.nombre,
                    'inicio': self.tiempo_actual,
                    'duracion': 0
                })

            # Ejecutar proceso actual
            if self.proceso_actual:
                self.proceso_actual.rafaga_restante -= 1
                self.proceso_actual.rafaga_ejecucion += 1
                self.proceso_actual.quantum_usado += 1
                self.gantt_data[-1]['duracion'] += 1

                # Incrementar tiempo de espera para los procesos en cola de listos
                for proceso in self.cola_listos:
                    proceso.tiempo_espera += 1

                # Verificar si el proceso ha terminado
                if self.proceso_actual.rafaga_restante == 0:
                    self.proceso_actual.tiempo_final = self.tiempo_actual + 1
                    self.proceso_actual = None
                # Verificar si se ha consumido el quantum
                elif self.proceso_actual.quantum_usado >= quantum:
                    # Crear una nueva ejecución para el resto del proceso
                    proc = self.proceso_actual.original
                    restante = self.proceso_actual.rafaga_restante
                    alias_count = self.reingresos_contador[proc.nombre] + 1
                    self.reingresos_contador[proc.nombre] = alias_count
                    alias = proc.nombre + "'" * alias_count
                    nueva_ejec = Ejecucion(proc, alias, restante, proc.tiempo_llegada)
                    proc.reingresos.append(nueva_ejec)
                    self.ejecuciones.append(nueva_ejec)
                    self.cola_bloqueados.append(nueva_ejec)
                    self.proceso_actual = None

            self.actualizar_tabla()
            self.actualizar_diagrama_gantt()
            self.actualizar_cola_bloqueados()
            self.tiempo_actual += 1

            # Verificar si todos los procesos han terminado
            if all(e.rafaga_restante == 0 for e in self.ejecuciones):
                self.ejecutando = False
                self.proceso_actual = None
                self.root.after(100, lambda: messagebox.showinfo("Fin", "Todos los procesos han terminado"))
                break

            time.sleep(0.5)

    def actualizar_diagrama_gantt(self):
        self.ax.clear()
        if not self.gantt_data:
            self.canvas.draw()
            return

        procesos = sorted(set(p['proceso'] for p in self.gantt_data))
        y_ticks = range(len(procesos))
        proceso_to_y = {p: i for i, p in enumerate(procesos)}

        for bloque in self.gantt_data:
            color = next((pr.color for pr in self.procesos if pr.nombre == bloque['proceso']), '#1f77b4')
            self.ax.broken_barh([(bloque['inicio'], bloque['duracion'])], 
                            (proceso_to_y[bloque['proceso']] - 0.4, 0.8),
                            facecolors=color)

        self.ax.set_yticks(y_ticks)
        self.ax.set_yticklabels(procesos)
        self.ax.set_xlabel("Tiempo")
        self.ax.set_title("Diagrama de Gantt")
        self.ax.grid(True)

        # Añadir leyenda
        legend_elements = [Patch(facecolor=proc.color, label=proc.nombre) for proc in self.procesos]
        self.ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))

        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = RoundRobinApp(root)
    root.mainloop()