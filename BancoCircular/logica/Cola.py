import tkinter as tk
from tkinter import ttk, messagebox

class Nodo:
    def __init__(self, dato, es_cajero=False):
        self.dato = dato
        self.es_cajero = es_cajero
        self.siguiente = None

class ColaBancoCircular:
    def __init__(self):
        self.cabeza = None
        self.cajero = None  # Referencia al nodo del cajero
        self.inicializar_cajero()
    
    def inicializar_cajero(self):
        """Crea el nodo del cajero al iniciar la cola"""
        self.cajero = Nodo("CAJERO PRINCIPAL", es_cajero=True)
        self.cabeza = self.cajero
        self.cajero.siguiente = self.cajero  # Apunta a sí mismo inicialmente
    
    def agregar_cliente(self, nombre, transacciones):
        nuevo_cliente = Nodo(f"Cliente: {nombre} - Transacciones: {transacciones}")
        
        if self.cabeza == self.cajero and self.cajero.siguiente == self.cajero:
            # Primer cliente después del cajero
            self.cajero.siguiente = nuevo_cliente
            nuevo_cliente.siguiente = self.cajero
        else:
            # Agregar al final de la cola
            actual = self.cajero
            while actual.siguiente != self.cajero:
                actual = actual.siguiente
            actual.siguiente = nuevo_cliente
            nuevo_cliente.siguiente = self.cajero
        
        return f"Cliente {nombre} agregado a la cola"
    
    def atender_cliente(self):
        if self.cajero.siguiente == self.cajero:
            return None, "No hay clientes en la cola"
        
        cliente_actual = self.cajero.siguiente
        transacciones = int(cliente_actual.dato.split(":")[-1])
        atendidas = min(transacciones, 5)
        nuevas_transacciones = transacciones - atendidas
        
        if nuevas_transacciones > 0:
            # Actualizar transacciones pendientes
            cliente_actual.dato = f"{cliente_actual.dato.split(':')[0]}: {nuevas_transacciones}"
            # Mover al final de la cola
            self.mover_al_final(cliente_actual)
            mensaje = f"Atendidas {atendidas} transacciones. Cliente vuelve a la cola"
        else:
            # Eliminar de la cola
            self.eliminar_cliente(cliente_actual)
            mensaje = f"Atendidas {atendidas} transacciones. Cliente atendido completamente"
        
        return cliente_actual, mensaje
    
    def mover_al_final(self, cliente):
        if cliente.siguiente == self.cajero:
            return  # Ya está al final
        
        # Buscar el nodo anterior al cliente
        anterior = self.cajero
        while anterior.siguiente != cliente:
            anterior = anterior.siguiente
        
        # Reconectar nodos
        anterior.siguiente = cliente.siguiente
        # Mover cliente al final
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
        self.root.title("Sistema de Banco con Cajero Principal")
        self.root.geometry("700x550")
        
        self.cola = ColaBancoCircular()
        
        # Frame para agregar clientes
        frame_agregar = ttk.LabelFrame(root, text="Agregar Cliente", padding=10)
        frame_agregar.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Label(frame_agregar, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.nombre_entry = ttk.Entry(frame_agregar, width=25)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_agregar, text="Transacciones:").grid(row=1, column=0, padx=5, pady=5)
        self.transacciones_entry = ttk.Entry(frame_agregar, width=25)
        self.transacciones_entry.grid(row=1, column=1, padx=5, pady=5)
        
        agregar_btn = ttk.Button(frame_agregar, text="Agregar Cliente", command=self.agregar_cliente)
        agregar_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Frame para atender clientes
        frame_atender = ttk.LabelFrame(root, text="Atender Clientes", padding=10)
        frame_atender.pack(pady=10, padx=10, fill=tk.X)
        
        atender_btn = ttk.Button(frame_atender, text="Atender Siguiente Cliente", command=self.atender_cliente)
        atender_btn.pack(pady=5)
        
        self.mensaje_atencion = tk.StringVar()
        ttk.Label(frame_atender, textvariable=self.mensaje_atencion, wraplength=650).pack(pady=5)
        
        # Frame para mostrar la cola
        frame_cola = ttk.LabelFrame(root, text="Cola del Banco (Cajero Principal siempre al inicio)", padding=10)
        frame_cola.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.cola_tree = ttk.Treeview(frame_cola, columns=('item',), show='headings')
        self.cola_tree.heading('item', text='Elemento en la cola')
        self.cola_tree.column('item', width=650)
        self.cola_tree.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar cajero al inicio
        self.actualizar_cola()
    
    def agregar_cliente(self):
        nombre = self.nombre_entry.get()
        transacciones = self.transacciones_entry.get()
        
        if not nombre or not transacciones:
            messagebox.showerror("Error", "Debe ingresar nombre y número de transacciones")
            return
        
        try:
            transacciones = int(transacciones)
            if transacciones <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Las transacciones deben ser un número entero positivo")
            return
        
        mensaje = self.cola.agregar_cliente(nombre, transacciones)
        messagebox.showinfo("Información", mensaje)
        self.nombre_entry.delete(0, tk.END)
        self.transacciones_entry.delete(0, tk.END)
        self.actualizar_cola()
    
    def atender_cliente(self):
        cliente, mensaje = self.cola.atender_cliente()
        self.mensaje_atencion.set(mensaje)
        self.actualizar_cola()
    
    def actualizar_cola(self):
        # Limpiar el Treeview
        for item in self.cola_tree.get_children():
            self.cola_tree.delete(item)
        
        # Mostrar siempre el cajero primero
        self.cola_tree.insert('', tk.END, values=("=== CAJERO PRINCIPAL ===",))
        
        # Mostrar clientes en cola
        for cliente in self.cola.obtener_cola():
            self.cola_tree.insert('', tk.END, values=(cliente,))

if __name__ == "__main__":
    root = tk.Tk()
    app = BancoApp(root)
    root.mainloop()