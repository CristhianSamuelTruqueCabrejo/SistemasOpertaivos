import tkinter as tk
from tkinter import ttk, messagebox
import random
import heapq
import time
import threading
from collections import defaultdict

class FinalPriorityScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Planificador por Prioridad Completo")
        
        # Variables de estado
        self.ready_queue = []
        self.blocked_queue = []
        self.completed_processes = []
        self.current_process = None
        self.current_time = 0
        self.process_counter = 1
        self.simulation_speed = 1.0
        self.timeline_data = []
        self.running = True
        self.blocked_versions = defaultdict(int)
        self.process_history = []
        
        # Configurar interfaz
        self.setup_ui()
        
        # Iniciar hilo planificador
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Panel de control
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=3, pady=5, sticky=tk.W)
        
        ttk.Button(control_frame, text="Agregar Proceso", command=self.add_process).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="+5 Aleatorios", command=self.add_random_processes).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Bloquear Actual", command=self.block_current_process).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Estadísticas", command=self.show_stats).grid(row=0, column=3, padx=5)
        ttk.Button(control_frame, text="Reiniciar", command=self.reset_system).grid(row=0, column=4, padx=5)
        ttk.Button(control_frame, text="Timeline", command=self.show_timeline).grid(row=0, column=5, padx=5)
        
        # Control de velocidad
        ttk.Label(control_frame, text="Velocidad:").grid(row=1, column=0, padx=(10,0))
        self.speed_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, value=1.0, 
                                    command=lambda v: setattr(self, 'simulation_speed', float(v)))
        self.speed_scale.grid(row=1, column=1, columnspan=5, sticky=tk.EW)
        
        # Panel de proceso actual
        current_frame = ttk.LabelFrame(main_frame, text="Proceso en Ejecución", padding=10)
        current_frame.grid(row=1, column=0, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(current_frame, text="Proceso:").grid(row=0, column=0, sticky=tk.W)
        self.current_name = ttk.Label(current_frame, text="Ninguno", font=('Arial', 10, 'bold'))
        self.current_name.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(current_frame, text="Prioridad:").grid(row=1, column=0, sticky=tk.W)
        self.current_priority = ttk.Label(current_frame, text="-")
        self.current_priority.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(current_frame, text="Ráfaga:").grid(row=2, column=0, sticky=tk.W)
        self.current_burst = ttk.Label(current_frame, text="-")
        self.current_burst.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(current_frame, text="Restante:").grid(row=3, column=0, sticky=tk.W)
        self.current_remaining = ttk.Label(current_frame, text="0")
        self.current_remaining.grid(row=3, column=1, sticky=tk.W)
        
        # Cola de listos
        ready_frame = ttk.LabelFrame(main_frame, text="Cola de Listos (Prioridad)", padding=10)
        ready_frame.grid(row=2, column=0, sticky=tk.W+tk.E, pady=5)
        
        self.ready_tree = ttk.Treeview(ready_frame, columns=('nombre', 'llegada', 'rafaga', 'prioridad'), 
                                     show='headings', height=6)
        self.ready_tree.heading('nombre', text='Proceso')
        self.ready_tree.heading('llegada', text='T. Llegada')
        self.ready_tree.heading('rafaga', text='Ráfaga')
        self.ready_tree.heading('prioridad', text='Prioridad')
        
        for col in ('nombre', 'llegada', 'rafaga', 'prioridad'):
            self.ready_tree.column(col, width=90, anchor=tk.CENTER)
        
        self.ready_tree.grid(row=0, column=0, sticky=tk.EW)
        
        # Cola de bloqueados
        blocked_frame = ttk.LabelFrame(main_frame, text="Cola de Bloqueados", padding=10)
        blocked_frame.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
        
        self.blocked_tree = ttk.Treeview(blocked_frame, columns=('nombre', 'prioridad', 'restante'), 
                                       show='headings', height=6)
        self.blocked_tree.heading('nombre', text='Proceso')
        self.blocked_tree.heading('prioridad', text='Prioridad')
        self.blocked_tree.heading('restante', text='T. Bloqueo')
        
        for col in ('nombre', 'prioridad', 'restante'):
            self.blocked_tree.column(col, width=100, anchor=tk.CENTER)
        
        self.blocked_tree.grid(row=0, column=0, sticky=tk.EW)
        
        # Procesos completados
        completed_frame = ttk.LabelFrame(main_frame, text="Procesos Completados", padding=10)
        completed_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        self.completed_tree = ttk.Treeview(completed_frame, 
                                         columns=('proceso', 'llegada', 'rafaga', 'comienzo', 'final', 
                                                 'retorno', 'espera', 'Prioridad', 'rafaga_ejec'), 
                                         show='headings', height=8)
        
        columns = [
            ('proceso', 'Proceso', 80),
            ('llegada', 'T. Llegada', 90),
            ('rafaga', 'Ráfaga Total', 90),
            ('comienzo', 'T. Comienzo', 90),
            ('final', 'T. Final', 80),
            ('retorno', 'T. Retorno', 90),
            ('espera', 'T. Espera', 80),
            ('Prioridad', 'Prioridad', 80),
            ('rafaga_ejec', 'Ráfaga Ejec', 90)
        ]
        
        for col, text, width in columns:
            self.completed_tree.heading(col, text=text)
            self.completed_tree.column(col, width=width, anchor=tk.CENTER)
        
        self.completed_tree.grid(row=0, column=0, sticky=tk.EW)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(completed_frame, orient=tk.VERTICAL, command=self.completed_tree.yview)
        self.completed_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        # Configurar pesos
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        ready_frame.columnconfigure(0, weight=1)
        blocked_frame.columnconfigure(0, weight=1)
        completed_frame.columnconfigure(0, weight=1)
    
    def add_process(self, name=None, arrival=None, burst=None, priority=None):
        """Agrega un nuevo proceso a la cola de listos"""
        if name is None:
            name = f"P{self.process_counter}"
            self.process_counter += 1
            arrival = self.current_time
            burst = random.randint(3, 15)
            priority = random.randint(1, 5)  # 1 = máxima prioridad
        
        process = {
            'name': name,
            'original_name': name,
            'arrival': 0,
            'burst': burst,
            'remaining': burst,
            'priority': priority,
            'start_time': None,
            'block_count': priority,
            'executed': 0,
            'state': 'ready',
            'history': []
        }
        
        heapq.heappush(self.ready_queue, (priority, arrival, len(self.ready_queue), process))
        self.update_ready_queue()
        
        # Verificar expropiación
        if self.current_process and priority < self.current_process['priority']:
            self.preempt_current()
        
        return process
    
    def add_random_processes(self):
        """Agrega varios procesos aleatorios"""
        for _ in range(5):
            self.add_process()
    
    def block_current_process(self):
        """Bloquea el proceso actual según las reglas especificadas"""
        if not self.current_process:
            messagebox.showwarning("Error", "No hay proceso en ejecución")
            return
        
        current = self.current_process
        original_name = current['original_name']
        executed = current['burst'] - current['remaining']
        block_time = random.randint(2, 5)
        
        # 1. Registrar el proceso actual como completado (versión actual)
        completed_process = {
            'name': current['name'],
            'original_name': original_name,
            'arrival': current['arrival'],
            'burst': current['burst'],
            'start_time': current['start_time'],
            'end_time': self.current_time,
            'executed': executed,
            'block_count': current['priority'],
            'block_time': current['burst'] - executed  # Tiempo de bloqueo = ráfaga total - ráfaga ejecutada
        }
        
        # Calcular métricas
        turnaround = completed_process['end_time'] - completed_process['arrival']
        waiting = turnaround - completed_process['executed']
        
        completed_process.update({
            'turnaround': turnaround,
            'waiting': waiting
        })
        
        self.completed_processes.append(completed_process)
        self.process_history.append(('completed', completed_process))
        self.update_completed_queue()
        
        # 2. Crear nueva versión bloqueada (Pn')
        self.blocked_versions[original_name] += 1
        blocked_name = f"{original_name}{''.join(['´']*self.blocked_versions[original_name])}"
        
        blocked_process = {
            'name': blocked_name,
            'original_name': original_name,
            'arrival': current['arrival'],
            'burst': current['remaining'],
            'remaining': current['remaining'],
            'priority': current['priority'],
            'start_time': None,
            'block_count': current['priority'] + 1,
            'executed': 0,
            'state': 'blocked',
            'blocked_until': self.current_time + block_time,
            'history': current['history'] + [('blocked', self.current_time)]
        }
        
        self.blocked_queue.append(blocked_process)
        self.process_history.append(('blocked', blocked_process))
        self.current_process = None
        
        self.update_blocked_queue()
        self.update_current_display()
        
        messagebox.showinfo("Bloqueado", 
                          f"Proceso {completed_process['name']} completado parcialmente\n"
                          f"Ráfaga ejecutada: {executed}/{current['burst']}\n"
                          f"Versión bloqueada {blocked_name} creada por {block_time} unidades")
    
    def preempt_current(self):
        """Expropia el proceso actual"""
        if not self.current_process:
            return
        
        current = self.current_process
        executed = current['burst'] - current['remaining']
        current['executed'] = executed
        
        # Registrar el tiempo de ejecución hasta ahora
        if current['start_time'] is not None:
            current['history'].append(('executed', current['start_time'], self.current_time))
        
        # Volver a poner en cola de listos
        heapq.heappush(self.ready_queue, 
                      (current['priority'], 
                       current['arrival'], 
                       len(self.ready_queue),
                       current))
        
        self.current_process = None
        self.update_ready_queue()
        self.update_current_display()
    
    def unblock_processes(self):
        """Desbloquea procesos cuando la cola de listos está vacía"""
        if not self.ready_queue and self.blocked_queue:
            for process in list(self.blocked_queue):
                if self.current_time >= process['blocked_until']:
                    self.blocked_queue.remove(process)
                    process['state'] = 'ready'
                    process['start_time'] = None
                    heapq.heappush(self.ready_queue, 
                                 (process['priority'], 
                                  process['arrival'], 
                                  len(self.ready_queue),
                                  process))
                    self.process_history.append(('unblocked', process))
            
            self.update_blocked_queue()
            self.update_ready_queue()
    
    def run_scheduler(self):
        """Bucle principal del planificador"""
        while self.running:
            # Desbloquear procesos si es posible
            self.unblock_processes()
            
            # Seleccionar siguiente proceso si no hay uno en ejecución
            if not self.current_process and self.ready_queue:
                _, _, _, process = heapq.heappop(self.ready_queue)
                
                if process['arrival'] <= self.current_time:
                    process['start_time'] = self.current_time
                    self.current_process = process
                    self.process_history.append(('started', process))
                    self.update_ready_queue()
                    self.update_current_display()
                else:
                    heapq.heappush(self.ready_queue, 
                                 (process['priority'], 
                                  process['arrival'], 
                                  len(self.ready_queue),
                                  process))
            
            # Ejecutar proceso actual
            if self.current_process:
                self.current_process['remaining'] -= 1
                self.current_process['executed'] += 1
                self.current_time += 1
                self.update_current_display()
                
                # Verificar si ha terminado
                if self.current_process['remaining'] <= 0:
                    self.complete_current_process()
                
                # Verificar expropiación
                """elif self.ready_queue and self.ready_queue[0][0] < self.current_process['priority']:
                    self.preempt_current()"""
            
            time.sleep(0.5 / self.simulation_speed)
    
    def complete_current_process(self):
        """Marca el proceso actual como completado"""
        process = self.current_process
        executed = process['executed']
        
        completed_process = {
            'name': process['name'],
            'original_name': process['original_name'],
            'arrival': process['arrival'],
            'burst': process['burst'],
            'start_time': process['start_time'],
            'end_time': self.current_time,
            'executed': executed,
            'block_count': process['block_count'],
            'block_time': process['burst'] - executed  # Tiempo de bloqueo = ráfaga total - ráfaga ejecutada
        }
        
        # Calcular métricas
        turnaround = completed_process['end_time'] - completed_process['arrival']
        waiting = turnaround - completed_process['executed']
        
        completed_process.update({
            'turnaround': turnaround,
            'waiting': waiting
        })
        
        self.completed_processes.append(completed_process)
        self.process_history.append(('completed', completed_process))
        self.current_process = None
        
        self.update_completed_queue()
        self.update_current_display()
    
    def update_current_display(self):
        """Actualiza la visualización del proceso actual"""
        if self.current_process:
            p = self.current_process
            self.current_name.config(text=p['name'])
            self.current_priority.config(text=f"P{p['priority']}")
            self.current_burst.config(text=str(p['burst']))
            self.current_remaining.config(text=str(p['remaining']))
        else:
            self.current_name.config(text="Ninguno")
            self.current_priority.config(text="-")
            self.current_burst.config(text="-")
            self.current_remaining.config(text="0")
    
    def update_ready_queue(self):
        """Actualiza la visualización de la cola de listos"""
        self.ready_tree.delete(*self.ready_tree.get_children())
        
        for _, _, _, process in sorted(self.ready_queue, key=lambda x: (x[0], x[1])):
            self.ready_tree.insert('', tk.END,
                                 values=(process['name'],
                                        process['arrival'],
                                        process['burst'],
                                        f"P{process['priority']}"))
    
    def update_blocked_queue(self):
        """Actualiza la visualización de la cola de bloqueados"""
        self.blocked_tree.delete(*self.blocked_tree.get_children())
        
        for process in self.blocked_queue:
            remaining = max(0, process['blocked_until'] - self.current_time)
            self.blocked_tree.insert('', tk.END,
                                   values=(process['name'],
                                          f"P{process['priority']}",
                                          remaining))
    
    def update_completed_queue(self):
        """Actualiza la visualización de procesos completados"""
        self.completed_tree.delete(*self.completed_tree.get_children())
        
        for p in sorted(self.completed_processes, key=lambda x: x['end_time']):
            self.completed_tree.insert('', tk.END,
                                     values=(p['name'],
                                            p['arrival'],
                                            p['burst'],
                                            p['start_time'],
                                            p['end_time'],
                                            p['turnaround'],
                                            p['waiting'],
                                            p['block_count'],
                                            p['executed']))
    
    def show_timeline(self):
        """Muestra el diagrama de Gantt"""
        if not self.process_history:
            messagebox.showinfo("Timeline", "No hay datos para mostrar")
            return
        
        # Calcular tiempo máximo
        max_time = max(
            max(p['end_time'] for _, p in self.process_history if _ == 'completed'),
            self.current_time
        ) if self.process_history else 1
        
        timeline_win = tk.Toplevel(self.root)
        timeline_win.title("Timeline de Ejecución")
        
        canvas_width = min(800, max(600, max_time * 30 + 100))
        canvas_height = 400
        
        canvas = tk.Canvas(timeline_win, width=canvas_width, height=canvas_height, bg='white')
        canvas.pack(pady=10, expand=True, fill=tk.BOTH)
        
        # Dibujar eje de tiempo
        canvas.create_line(50, 50, canvas_width - 50, 50, width=2)
        for t in range(0, max_time + 1, max(1, max_time//10)):
            x = 50 + t * (canvas_width - 100) / max_time
            canvas.create_line(x, 45, x, 55, width=1)
            canvas.create_text(x, 70, text=str(t))
        
        # Colores por prioridad
        colors = {
            1: '#FF0000', 2: '#FF6600', 3: '#FFCC00',
            4: '#66CC00', 5: '#0066CC'
        }
        
        # Organizar procesos por fila (por nombre original)
        rows = {}
        y_pos = 100
        for original_name in set(p['original_name'] for _, p in self.process_history if 'original_name' in p):
            rows[original_name] = y_pos
            y_pos += 40
        
        # Dibujar barras para cada evento
        for event_type, event_data in self.process_history:
            if event_type == 'completed':
                p = event_data
                x1 = 50 + p['start_time'] * (canvas_width - 100) / max_time
                x2 = 50 + p['end_time'] * (canvas_width - 100) / max_time
                color = colors.get(
                    next((proc['priority'] for proc in self.completed_processes 
                         if proc['name'] == p['name']), 5))
                
                canvas.create_rectangle(x1, rows[p['original_name']] - 15, x2, rows[p['original_name']] + 15, 
                                      fill=color, outline='black')
                canvas.create_text((x1 + x2)/2, rows[p['original_name']], text=p['name'])
                canvas.create_text((x1 + x2)/2, rows[p['original_name']] + 30, 
                                 text=f"{p['start_time']}-{p['end_time']} (Ejec: {p['executed']})")
            
            elif event_type == 'blocked':
                p = event_data
                x1 = 50 + p['history'][-1][2] * (canvas_width - 100) / max_time
                x2 = 50 + p['blocked_until'] * (canvas_width - 100) / max_time
                canvas.create_rectangle(x1, rows[p['original_name']] - 15, x2, rows[p['original_name']] + 15, 
                                      fill='#666666', outline='black')
                canvas.create_text((x1 + x2)/2, rows[p['original_name']], text=p['name'], fill='white')
        
        # Leyenda
        legend = ttk.Frame(timeline_win)
        legend.pack()
        
        for prio in sorted(colors.keys()):
            ttk.Label(legend, text=f"P{prio}", background=colors[prio],
                     width=4, padding=3, anchor=tk.CENTER,
                     foreground='white' if prio < 3 else 'black').pack(side=tk.LEFT, padx=5)
        
        ttk.Label(legend, text="Bloqueado", background='#666666',
                 width=8, padding=3, anchor=tk.CENTER,
                 foreground='white').pack(side=tk.LEFT, padx=5)
    
    def show_stats(self):
        """Muestra estadísticas de rendimiento"""
        if not self.completed_processes:
            messagebox.showinfo("Estadísticas", "No hay procesos completados")
            return
        
        total = len(self.completed_processes)
        avg_turnaround = sum(p['turnaround'] for p in self.completed_processes) / total
        avg_waiting = sum(p['waiting'] for p in self.completed_processes) / total
        total_blocks = sum(p['block_count'] for p in self.completed_processes)
        total_block_time = sum(p['block_time'] for p in self.completed_processes)
        
        # Estadísticas por prioridad
        stats = defaultdict(lambda: {'count': 0, 'turnaround': 0, 'waiting': 0, 'blocks': 0, 'block_time': 0})
        for p in self.completed_processes:
            prio = next((proc['priority'] for proc in self.completed_processes 
                        if proc['name'] == p['name']), 5)
            stats[prio]['count'] += 1
            stats[prio]['turnaround'] += p['turnaround']
            stats[prio]['waiting'] += p['waiting']
            stats[prio]['blocks'] += p['block_count']
            stats[prio]['block_time'] += p['block_time']
        
        msg = (
            f"Procesos completados: {total}\n"
            f"Tiempo de retorno promedio: {avg_turnaround:.2f}\n"
            f"Tiempo de espera promedio: {avg_waiting:.2f}\n"
            f"Total de Prioridad: {total_blocks}\n"
            f"Tiempo total de bloqueo: {total_block_time}\n\n"
            "Estadísticas por prioridad:\n"
        )
        
        for prio in sorted(stats.keys()):
            s = stats[prio]
            msg += (
                f"P{prio}: {s['count']} procs | "
                f"Retorno: {s['turnaround']/s['count']:.2f} | "
                f"Espera: {s['waiting']/s['count']:.2f} | "
                f"Prioridad: {s['blocks']} | "
                f"T. Bloqueo: {s['block_time']}\n"
            )
        
        messagebox.showinfo("Estadísticas", msg)
    
    def reset_system(self):
        """Reinicia el sistema"""
        self.ready_queue = []
        self.blocked_queue = []
        self.completed_processes = []
        self.current_process = None
        self.current_time = 0
        self.process_counter = 1
        self.blocked_versions = defaultdict(int)
        self.process_history = []
        
        self.update_current_display()
        self.update_ready_queue()
        self.update_blocked_queue()
        self.update_completed_queue()
        
        messagebox.showinfo("Reinicio", "Sistema reiniciado correctamente")
    
    def on_close(self):
        """Maneja el cierre de la ventana"""
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinalPriorityScheduler(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()