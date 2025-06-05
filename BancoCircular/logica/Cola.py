import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import time
from queue import Queue

class Nodo:
    def __init__(self, dato, es_cajero=False):
        self.dato = dato
        self.es_cajero = es_cajero
        self.siguiente = None

class ColaBancoCircular:
    def __init__(self):
        self.cabeza = None
        self.cajero = None
        self.clientes_atendidos = 0
        self.clientes_en_cola = 0
        self.inicializar_cajero()
        
    def inicializar_cajero(self):
        self.cajero = Nodo("CAJERO #1", es_cajero=True)
        self.cabeza = self.cajero
        self.cajero.siguiente = self.cajero
    
    def agregar_cliente(self, id_cliente, transacciones=None):
        if transacciones is None:
            transacciones = random.randint(1, 15)  # 1-15 transacciones aleatorias
        
        nuevo_cliente = Nodo(f"ID: {id_cliente} - Transacciones: {transacciones}")
        
        if self.cabeza == self.cajero and self.cajero.siguiente == self.cajero:
            self.cajero.siguiente = nuevo_cliente
            nuevo_cliente.siguiente = self.cajero
        else:
            actual = self.cajero
            while actual.siguiente != self.cajero:
                actual = actual.siguiente
            actual.siguiente = nuevo_cliente
            nuevo_cliente.siguiente = self.cajero
        
        self.clientes_en_cola += 1
        return f"Cliente ID:{id_cliente} agregado con {transacciones} transacciones"
    
    def atender_cliente(self):
        if self.cajero.siguiente == self.cajero:
            return None, "No hay clientes en la cola"
        
        cliente_actual = self.cajero.siguiente
        transacciones = int(cliente_actual.dato.split(":")[-1])
        atendidas = min(transacciones, 5)
        nuevas_transacciones = transacciones - atendidas
        
        if nuevas_transacciones > 0:
            cliente_actual.dato = f"{cliente_actual.dato.split(':')[0]}:{cliente_actual.dato.split(':')[1]}: {nuevas_transacciones}"
            self.mover_al_final(cliente_actual)
            mensaje = f"Atendido ID: {cliente_actual.dato.split(':')[1].strip()} - {atendidas} transacciones (vuelve a cola)"
        else:
            self.eliminar_cliente(cliente_actual)
            self.clientes_atendidos += 1
            self.clientes_en_cola -= 1
            mensaje = f"Atendido ID: {cliente_actual.dato.split(':')[1].strip()} - {atendidas} transacciones (completado)"
        
        return cliente_actual, mensaje
    
    def mover_al_final(self, cliente):
        if cliente.siguiente == self.cajero:
            return
        
        anterior = self.cajero
        while anterior.siguiente != cliente:
            anterior = anterior.siguiente
        
        anterior.siguiente = cliente.siguiente
        ultimo = self.cajero
        while ultimo.siguiente != self.cajero:
            ultimo = ultimo.siguiente
        ultimo.siguiente = cliente
        cliente.siguiente = self.cajero
    
    def eliminar_cliente(self, cliente):
        if self.cajero.siguiente == cliente:
            self.cajero.siguiente = cliente.siguiente
    
    def obtener_cola(self):
        cola = []
        if self.cajero.siguiente == self.cajero:
            return cola
        
        actual = self.cajero.siguiente
        while actual != self.cajero:
            cola.append(actual.dato)
            actual = actual.siguiente
        return cola

class BancoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Banco Automatizado")
        self.root.geometry("750x600")
        
        self.cola = ColaBancoCircular()
        self.id_cliente = 1
        self.event_queue = Queue()
        self.running = True
        
        # Frame para controles
        frame_controles = ttk.LabelFrame(root, text="Controles", padding=10)
        frame_controles.pack(pady=10, padx=10, fill=tk.X)
        
        self.start_btn = ttk.Button(frame_controles, text="Iniciar Simulación", command=self.iniciar_simulacion)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(frame_controles, text="Detener Simulación", command=self.detener_simulacion, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame para estadísticas
        frame_stats = ttk.LabelFrame(root, text="Estadísticas", padding=10)
        frame_stats.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Label(frame_stats, text="Clientes en cola:").pack(side=tk.LEFT, padx=5)
        self.lbl_en_cola = ttk.Label(frame_stats, text="0")
        self.lbl_en_cola.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_stats, text="Clientes atendidos:").pack(side=tk.LEFT, padx=5)
        self.lbl_atendidos = ttk.Label(frame_stats, text="0")
        self.lbl_atendidos.pack(side=tk.LEFT, padx=5)
        
        # Frame para mensajes
        frame_mensajes = ttk.LabelFrame(root, text="Registro de Eventos", padding=10)
        frame_mensajes.pack(pady=10, padx=10, fill=tk.X)
        
        self.mensaje_text = tk.Text(frame_mensajes, height=5, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame_mensajes, orient=tk.VERTICAL, command=self.mensaje_text.yview)
        self.mensaje_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.mensaje_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame para mostrar la cola
        frame_cola = ttk.LabelFrame(root, text="Cola del Banco", padding=10)
        frame_cola.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.cola_tree = ttk.Treeview(frame_cola, columns=('item',), show='headings')
        self.cola_tree.heading('item', text='Elemento en la cola')
        self.cola_tree.column('item', width=700)
        
        scrollbar_cola = ttk.Scrollbar(frame_cola, orient=tk.VERTICAL, command=self.cola_tree.yview)
        self.cola_tree.configure(yscrollcommand=scrollbar_cola.set)
        
        scrollbar_cola.pack(side=tk.RIGHT, fill=tk.Y)
        self.cola_tree.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar cajero al inicio
        self.actualizar_cola()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.process_queue()
    
    def iniciar_simulacion(self):
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Thread para llegada de clientes
        threading.Thread(target=self.llegada_clientes, daemon=True).start()
        
        # Thread para atención de clientes
        threading.Thread(target=self.atencion_clientes, daemon=True).start()
    
    def detener_simulacion(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def llegada_clientes(self):
        while self.running:
            time.sleep(2)  # Cada 4 segundos
            if not self.running:
                break
                
            mensaje = self.cola.agregar_cliente(self.id_cliente)
            self.event_queue.put(("nuevo_cliente", mensaje))
            self.id_cliente += 1
    
    def atencion_clientes(self):
        while self.running:
            time.sleep(5)  # Cada 5 segundos
            if not self.running:
                break
                
            cliente, mensaje = self.cola.atender_cliente()
            self.event_queue.put(("atencion", mensaje))
    
    def process_queue(self):
        while not self.event_queue.empty():
            event_type, message = self.event_queue.get()
            
            if event_type == "nuevo_cliente":
                self.mensaje_text.insert(tk.END, f"Nuevo cliente: {message}\n")
            elif event_type == "atencion":
                self.mensaje_text.insert(tk.END, f"Atención: {message}\n")
            
            self.mensaje_text.see(tk.END)
            self.actualizar_cola()
            self.actualizar_estadisticas()
        
        self.root.after(100, self.process_queue)
    
    def actualizar_cola(self):
        for item in self.cola_tree.get_children():
            self.cola_tree.delete(item)
        
        self.cola_tree.insert('', tk.END, values=("=== CAJERO PRINCIPAL ===",))
        
        for cliente in self.cola.obtener_cola():
            self.cola_tree.insert('', tk.END, values=(cliente,))
    
    def actualizar_estadisticas(self):
        self.lbl_en_cola.config(text=str(self.cola.clientes_en_cola))
        self.lbl_atendidos.config(text=str(self.cola.clientes_atendidos))
    
    def on_close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BancoApp(root)
    root.mainloop()