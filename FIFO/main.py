import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import time
from collections import deque

class FIFOSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Planificador FIFO Corregido")
        
        # Variables de estado
        self.process_queue = deque()
        self.completed_processes = []
        self.current_process = None
        self.current_time = 0
        self.is_running = False
        self.process_counter = 1
        self.simulation_speed = 1.0  # Factor de velocidad de simulación
        
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
        
        ttk.Button(control_frame, text="Agregar Proceso", command=self.add_random_process).grid(row=0, column=0, padx=5)
        
        # Control de velocidad
        ttk.Label(control_frame, text="Velocidad:").grid(row=0, column=3, padx=(10,0))
        self.speed_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, value=1.0, 
                                    command=lambda v: setattr(self, 'simulation_speed', float(v)))
        self.speed_scale.grid(row=0, column=4, padx=5)
        
        # Panel de proceso actual
        current_frame = ttk.LabelFrame(main_frame, text="Proceso Actual", padding=10)
        current_frame.grid(row=1, column=0, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(current_frame, text="Proceso:").grid(row=0, column=0, sticky=tk.W)
        self.current_process_label = ttk.Label(current_frame, text="Ninguno")
        self.current_process_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(current_frame, text="Tiempo Restante:").grid(row=1, column=0, sticky=tk.W)
        self.remaining_time_label = ttk.Label(current_frame, text="0")
        self.remaining_time_label.grid(row=1, column=1, sticky=tk.W)
        
        # Cola de procesos
        queue_frame = ttk.LabelFrame(main_frame, text="Cola de Procesos", padding=10)
        queue_frame.grid(row=2, column=0, sticky=tk.W+tk.E, pady=5)
        
        self.queue_tree = ttk.Treeview(queue_frame, columns=('nombre', 'llegada', 'rafaga'), 
                                     show='headings', height=6)
        self.queue_tree.heading('nombre', text='Proceso')
        self.queue_tree.heading('llegada', text='T. Llegada')
        self.queue_tree.heading('rafaga', text='Ráfaga')
        self.queue_tree.column('nombre', width=80, anchor=tk.CENTER)
        self.queue_tree.column('llegada', width=80, anchor=tk.CENTER)
        self.queue_tree.column('rafaga', width=80, anchor=tk.CENTER)
        self.queue_tree.grid(row=0, column=0)
        
        # Resultados
        results_frame = ttk.LabelFrame(main_frame, text="Procesos Completados", padding=10)
        results_frame.grid(row=3, column=0, sticky=tk.W+tk.E, pady=5)
        
        self.results_tree = ttk.Treeview(results_frame, 
                                       columns=('proceso', 'llegada', 'rafaga', 'comienzo', 
                                               'final', 'retorno', 'espera'), 
                                       show='headings', height=8)
        columns = {
            'proceso': ('Proceso', 70),
            'llegada': ('T. Llegada', 80),
            'rafaga': ('Ráfaga', 70),
            'comienzo': ('T. Comienzo', 90),
            'final': ('T. Final', 80),
            'retorno': ('T. Retorno', 90),
            'espera': ('T. Espera', 80)
        }
        
        for col, (text, width) in columns.items():
            self.results_tree.heading(col, text=text)
            self.results_tree.column(col, width=width, anchor=tk.CENTER)
        
        self.results_tree.grid(row=0, column=0)
        
        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
    
    def add_random_process(self):
        """Agrega un nuevo proceso con parámetros aleatorios"""
        process_name = f"P{self.process_counter}"
        self.process_counter += 1
        
        # Generar tiempo de llegada (asegurando que sea mayor o igual que el anterior)
        if not self.process_queue:
            arrival_time = random.randint(0, 10)
        else:
            last_arrival = self.process_queue[-1][1]
            arrival_time = last_arrival + random.randint(0, 3)
        
        burst_time = random.randint(1, 10)
        self.process_queue.append((process_name, arrival_time, burst_time))
        self.update_queue_display()
    
    def scheduler_loop(self):
        """Bucle principal del planificador FIFO"""
        while True:
            if self.process_queue and not self.is_running:
                self.current_process = self.process_queue.popleft()
                self.is_running = True
                
                # Calcular tiempo de comienzo (máximo entre tiempo actual y llegada del proceso)
                start_time = max(self.current_time, self.current_process[1])
                
                # Simular ejecución del proceso
                remaining_time = self.current_process[2]
                while remaining_time > 0:
                    time.sleep(0.5 / self.simulation_speed)  # Ajustar velocidad
                    remaining_time -= 1
                    self.current_time = start_time + (self.current_process[2] - remaining_time)
                    self.update_current_process_display(remaining_time)
                
                # Calcular métricas
                finish_time = start_time + self.current_process[2]
                turnaround_time = finish_time - self.current_process[1]
                waiting_time = turnaround_time - self.current_process[2]
                
                # Registrar proceso completado
                self.completed_processes.append((
                    self.current_process[0],  # nombre
                    self.current_process[1],  # llegada
                    self.current_process[2],  # ráfaga
                    start_time,             # comienzo
                    finish_time,            # final
                    turnaround_time,        # retorno
                    waiting_time             # espera
                ))
                
                # Preparar para siguiente proceso
                self.current_time = finish_time
                self.is_running = False
                self.current_process = None
                self.update_displays()
            
            time.sleep(0.1)
    
    def update_current_process_display(self, remaining_time):
        """Actualiza la visualización del proceso en ejecución"""
        self.root.after(0, lambda: [
            self.current_process_label.config(text=self.current_process[0]),
            self.remaining_time_label.config(text=str(remaining_time))
        ])
    
    def update_queue_display(self):
        """Actualiza la visualización de la cola de procesos"""
        self.root.after(0, lambda: [
            self.queue_tree.delete(item) for item in self.queue_tree.get_children()
        ])
        
        for process in self.process_queue:
            self.root.after(0, lambda p=process: self.queue_tree.insert(
                '', tk.END, values=(p[0], p[1], p[2])
            ))
    
    def update_results_display(self):
        """Actualiza la tabla de resultados"""
        self.root.after(0, lambda: [
            self.results_tree.delete(item) for item in self.results_tree.get_children()
        ])
        
        for process in sorted(self.completed_processes, key=lambda x: x[3]):  # Ordenar por tiempo de comienzo
            self.root.after(0, lambda p=process: self.results_tree.insert(
                '', tk.END, values=p
            ))
    
    def update_displays(self):
        """Actualiza todas las visualizaciones"""
        self.update_current_process_display(0)
        self.update_queue_display()
        self.update_results_display()
    
    def show_stats(self):
        """Muestra estadísticas de rendimiento"""
        if not self.completed_processes:
            messagebox.showinfo("Estadísticas", "No hay procesos completados aún")
            return
        
        total_processes = len(self.completed_processes)
        avg_turnaround = sum(p[5] for p in self.completed_processes) / total_processes
        avg_waiting = sum(p[6] for p in self.completed_processes) / total_processes
        
        stats_message = (
            f"Procesos completados: {total_processes}\n"
            f"Tiempo de retorno promedio: {avg_turnaround:.2f}\n"
            f"Tiempo de espera promedio: {avg_waiting:.2f}\n\n"
            f"Tiempo total del sistema: {self.current_time}"
        )
        
        messagebox.showinfo("Estadísticas del Sistema", stats_message)
    
    def reset_system(self):
        """Reinicia el sistema a su estado inicial"""
        self.process_queue.clear()
        self.completed_processes.clear()
        self.current_process = None
        self.current_time = 0
        self.is_running = False
        self.process_counter = 1
        self.update_displays()
        messagebox.showinfo("Sistema Reiniciado", "Todos los procesos han sido eliminados")

if __name__ == "__main__":
    root = tk.Tk()
    app = FIFOSchedulerApp(root)
    root.mainloop()