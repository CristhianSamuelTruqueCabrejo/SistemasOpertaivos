import tkinter as tk
from tkinter import ttk, messagebox
import random
import heapq
import time
import threading
from collections import defaultdict

class CorrectPriorityScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Planificador por Prioridad - Versión Corregida")
        
        # Variables de estado
        self.ready_queue = []
        self.completed_processes = []
        self.current_process = None
        self.current_time = 0
        self.is_running = False
        self.process_counter = 1
        self.simulation_speed = 1.0
        self.timeline_data = []
        
        # Configurar interfaz
        self.setup_ui()
        
        # Iniciar hilo planificador
        self.scheduler_thread = threading.Thread(target=self.scheduler_loop, daemon=True)
        self.scheduler_thread.start()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Panel de control
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        ttk.Button(control_frame, text="Agregar Proceso", command=self.add_process).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Agregar 5 Aleatorios", command=self.add_random_processes).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Mostrar Stats", command=self.show_stats).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Reiniciar", command=self.reset_system).grid(row=0, column=3, padx=5)
        ttk.Button(control_frame, text="Timeline", command=self.show_timeline).grid(row=0, column=4, padx=5)
        
        # Control de velocidad
        ttk.Label(control_frame, text="Velocidad:").grid(row=1, column=0, padx=(10,0))
        self.speed_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, value=1.0, 
                                    command=lambda v: setattr(self, 'simulation_speed', float(v)))
        self.speed_scale.grid(row=1, column=1, columnspan=4, sticky=tk.EW)
        
        # Panel de proceso actual
        current_frame = ttk.LabelFrame(main_frame, text="Proceso Actual", padding=10)
        current_frame.grid(row=1, column=0, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(current_frame, text="Proceso:").grid(row=0, column=0, sticky=tk.W)
        self.current_process_label = ttk.Label(current_frame, text="Ninguno", font=('Arial', 10, 'bold'))
        self.current_process_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(current_frame, text="Prioridad:").grid(row=1, column=0, sticky=tk.W)
        self.current_priority_label = ttk.Label(current_frame, text="-", font=('Arial', 10))
        self.current_priority_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(current_frame, text="Ráfaga:").grid(row=2, column=0, sticky=tk.W)
        self.current_burst_label = ttk.Label(current_frame, text="-")
        self.current_burst_label.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(current_frame, text="T. Restante:").grid(row=3, column=0, sticky=tk.W)
        self.remaining_time_label = ttk.Label(current_frame, text="0", font=('Arial', 10, 'bold'))
        self.remaining_time_label.grid(row=3, column=1, sticky=tk.W)
        
        # Cola de procesos
        queue_frame = ttk.LabelFrame(main_frame, text="Cola de Procesos (Prioridad)", padding=10)
        queue_frame.grid(row=2, column=0, sticky=tk.W+tk.E, pady=5)
        
        self.queue_tree = ttk.Treeview(queue_frame, columns=('nombre', 'llegada', 'rafaga', 'prioridad'), 
                                     show='headings', height=8)
        self.queue_tree.heading('nombre', text='Proceso')
        self.queue_tree.heading('llegada', text='T. Llegada')
        self.queue_tree.heading('rafaga', text='Ráfaga')
        self.queue_tree.heading('prioridad', text='Prioridad')
        
        for col in ('nombre', 'llegada', 'rafaga', 'prioridad'):
            self.queue_tree.column(col, width=90, anchor=tk.CENTER)
        
        self.queue_tree.grid(row=0, column=0, sticky=tk.EW)
        
        # Resultados
        results_frame = ttk.LabelFrame(main_frame, text="Procesos Completados", padding=10)
        results_frame.grid(row=3, column=0, sticky=tk.W+tk.E, pady=5)
        
        self.results_tree = ttk.Treeview(results_frame, 
                                       columns=('proceso', 'prioridad', 'llegada', 'rafaga', 'comienzo', 
                                               'final', 'retorno', 'espera'), 
                                       show='headings', height=10)
        
        columns = [
            ('proceso', 'Proceso', 80),
            ('prioridad', 'Prioridad', 80),
            ('llegada', 'T. Llegada', 90),
            ('rafaga', 'Ráfaga', 80),
            ('comienzo', 'T. Comienzo', 100),
            ('final', 'T. Final', 90),
            ('retorno', 'T. Retorno', 90),
            ('espera', 'T. Espera', 80)
        ]
        
        for col, text, width in columns:
            self.results_tree.heading(col, text=text)
            self.results_tree.column(col, width=width, anchor=tk.CENTER)
        
        self.results_tree.grid(row=0, column=0, sticky=tk.EW)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        # Configurar peso de columnas
        main_frame.columnconfigure(0, weight=1)
        queue_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
    
    def add_process(self, name=None, arrival=None, burst=None, priority=None):
        """Agrega un proceso manualmente o con parámetros aleatorios"""
        if name is None:
            name = f"P{self.process_counter}"
            self.process_counter += 1
            
            arrival = self.current_time + random.randint(0, 3)
            burst = random.randint(1, 10)
            priority = random.randint(1, 5)  # 1 = mayor prioridad
        
        # Usamos tupla con prioridad como primer elemento para el heap
        process = (priority, arrival, burst, name)
        heapq.heappush(self.ready_queue, process)
        self.update_queue_display()
        
        return process
    
    def add_random_processes(self):
        """Agrega varios procesos aleatorios de una vez"""
        for _ in range(5):
            self.add_process()
        messagebox.showinfo("Procesos agregados", "Se han agregado 5 procesos aleatorios a la cola")
    
    def scheduler_loop(self):
        """Bucle principal del planificador"""
        while True:
            if self.ready_queue and not self.is_running:
                # Obtener el proceso con mayor prioridad (menor número)
                priority, arrival, burst, name = heapq.heappop(self.ready_queue)
                
                # Verificar si el proceso ya llegó
                if arrival > self.current_time:
                    # Volver a poner en cola y esperar
                    heapq.heappush(self.ready_queue, (priority, arrival, burst, name))
                    time.sleep(0.1)
                    continue
                
                self.current_process = {
                    'name': name,
                    'arrival': arrival,
                    'burst': burst,
                    'priority': priority,
                    'start_time': max(self.current_time, arrival),
                    'remaining': burst
                }
                
                self.is_running = True
                self.update_current_process_display()
                
                # Ejecutar proceso
                while self.current_process['remaining'] > 0:
                    time.sleep(0.5 / self.simulation_speed)
                    self.current_process['remaining'] -= 1
                    self.current_time += 1
                    self.update_current_process_display()
                
                # Registrar proceso completado
                finish_time = self.current_time
                turnaround = finish_time - arrival
                waiting = turnaround - burst
                
                self.completed_processes.append((
                    name, priority, arrival, burst,
                    self.current_process['start_time'], finish_time,
                    turnaround, waiting
                ))
                
                # Registrar para timeline
                self.timeline_data.append((
                    name, 
                    self.current_process['start_time'], 
                    finish_time, 
                    priority
                ))
                
                # Limpiar proceso actual
                self.current_process = None
                self.is_running = False
                self.update_displays()
            
            time.sleep(0.1)
    
    def show_timeline(self):
        """Muestra el diagrama de Gantt con la ejecución"""
        if not self.timeline_data:
            messagebox.showinfo("Timeline", "No hay procesos ejecutados aún")
            return
        
        timeline_win = tk.Toplevel(self.root)
        timeline_win.title("Timeline de Ejecución")
        
        # Configurar canvas
        max_time = max(end for _, _, end, _ in self.timeline_data) or 1
        scale_factor = 30  # píxeles por unidad de tiempo
        canvas_width = max(600, max_time * scale_factor + 100)
        canvas_height = 300
        
        canvas = tk.Canvas(timeline_win, width=canvas_width, height=canvas_height, bg='white')
        canvas.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Dibujar eje de tiempo
        canvas.create_line(50, 50, canvas_width - 50, 50, width=2)
        for t in range(0, max_time + 1, max(1, max_time//10)):
            x = 50 + t * (canvas_width - 100) / max_time
            canvas.create_line(x, 45, x, 55, width=1)
            canvas.create_text(x, 70, text=str(t))
        
        # Colores por prioridad
        priority_colors = {
            1: '#FF0000',  # Rojo (máxima prioridad)
            2: '#FF6600',
            3: '#FFCC00',
            4: '#66CC00',
            5: '#0066CC'   # Azul (mínima prioridad)
        }
        
        # Dibujar barras de procesos
        y_pos = 100
        for i, (name, start, end, priority) in enumerate(self.timeline_data):
            x1 = 50 + start * (canvas_width - 100) / max_time
            x2 = 50 + end * (canvas_width - 100) / max_time
            color = priority_colors.get(priority, '#999999')
            
            canvas.create_rectangle(x1, y_pos, x2, y_pos + 30, fill=color, outline='black')
            canvas.create_text((x1 + x2)/2, y_pos + 15, text=f"{name} (P{priority})")
            canvas.create_text((x1 + x2)/2, y_pos + 50, text=f"{start}-{end}")
            
            y_pos += 60
            if y_pos > canvas_height - 50:  # Nueva columna si no hay espacio
                y_pos = 100
                canvas.create_line(x2 + 10, 40, x2 + 10, canvas_height - 20, dash=(2,2))
        
        # Leyenda
        legend_frame = ttk.Frame(timeline_win)
        legend_frame.pack(pady=5)
        
        for prio in sorted(priority_colors.keys()):
            color = priority_colors[prio]
            ttk.Label(legend_frame, text=f"P{prio}", background=color, 
                     width=4, padding=3, anchor=tk.CENTER,
                     foreground='white' if prio < 4 else 'black').pack(side=tk.LEFT, padx=5)
    
    def update_current_process_display(self):
        """Actualiza la visualización del proceso actual"""
        if self.current_process:
            proc = self.current_process
            self.current_process_label.config(text=proc['name'])
            self.current_priority_label.config(text=f"P{proc['priority']}")
            self.current_burst_label.config(text=f"{proc['burst']} (restan {proc['remaining']})")
            self.remaining_time_label.config(text=str(proc['remaining']))
        else:
            self.current_process_label.config(text="Ninguno")
            self.current_priority_label.config(text="-")
            self.current_burst_label.config(text="-")
            self.remaining_time_label.config(text="0")
    
    def update_queue_display(self):
        """Actualiza la visualización de la cola"""
        self.queue_tree.delete(*self.queue_tree.get_children())
        
        # Mostrar copia ordenada sin modificar la cola real
        temp_queue = sorted(self.ready_queue, key=lambda x: (x[0], x[1]))
        for priority, arrival, burst, name in temp_queue:
            self.queue_tree.insert('', tk.END, 
                                 values=(name, arrival, burst, f"P{priority}"),
                                 tags=('high' if priority < 3 else 'low'))
        
        # Colorear por prioridad
        self.queue_tree.tag_configure('high', background='#FFDDDD')
        self.queue_tree.tag_configure('low', background='#DDDDFF')
    
    def update_results_display(self):
        """Actualiza la tabla de resultados"""
        self.results_tree.delete(*self.results_tree.get_children())
        
        for proc in sorted(self.completed_processes, key=lambda x: x[4]):  # Ordenar por tiempo de inicio
            self.results_tree.insert('', tk.END, values=proc)
    
    def update_displays(self):
        """Actualiza todas las visualizaciones"""
        self.update_current_process_display()
        self.update_queue_display()
        self.update_results_display()
    
    def show_stats(self):
        """Muestra estadísticas de rendimiento"""
        if not self.completed_processes:
            messagebox.showinfo("Estadísticas", "No hay procesos completados aún")
            return
        
        total = len(self.completed_processes)
        avg_wait = sum(p[7] for p in self.completed_processes) / total
        avg_turnaround = sum(p[6] for p in self.completed_processes) / total
        
        # Stats por prioridad
        prio_stats = defaultdict(lambda: {'count': 0, 'wait': 0, 'turnaround': 0})
        for p in self.completed_processes:
            prio = p[1]
            prio_stats[prio]['count'] += 1
            prio_stats[prio]['wait'] += p[7]
            prio_stats[prio]['turnaround'] += p[6]
        
        stats_msg = (
            f"Procesos completados: {total}\n"
            f"Tiempo de espera promedio: {avg_wait:.2f}\n"
            f"Tiempo de retorno promedio: {avg_turnaround:.2f}\n\n"
            "Por prioridad:\n"
        )
        
        for prio in sorted(prio_stats.keys()):
            stats = prio_stats[prio]
            stats_msg += (
                f"P{prio}: {stats['count']} procesos | "
                f"Espera: {stats['wait']/stats['count']:.2f} | "
                f"Retorno: {stats['turnaround']/stats['count']:.2f}\n"
            )
        
        messagebox.showinfo("Estadísticas", stats_msg)
    
    def reset_system(self):
        """Reinicia completamente el sistema"""
        self.ready_queue = []
        self.completed_processes = []
        self.current_process = None
        self.current_time = 0
        self.is_running = False
        self.process_counter = 1
        self.timeline_data = []
        self.update_displays()
        messagebox.showinfo("Sistema Reiniciado", "Todos los procesos han sido eliminados")

if __name__ == "__main__":
    root = tk.Tk()
    app = CorrectPriorityScheduler(root)
    root.mainloop()