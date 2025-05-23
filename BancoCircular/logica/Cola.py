import tkinter as tk
from tkinter import ttk, messagebox

class Cliente:
    def __init__(self, nombre, transacciones):
        self.nombre = nombre
        self.transacciones = transacciones
        self.siguiente = None

class ColaBancoCircular:
    def __init__(self):
        self.cabeza = None
        self.tamano = 0
    
    def agregar_cliente(self, nombre, transacciones):
        nuevo_cliente = Cliente(nombre, transacciones)
        
        if not self.cabeza:
            self.cabeza = nuevo_cliente
            nuevo_cliente.siguiente = self.cabeza
        else:
            actual = self.cabeza
            while actual.siguiente != self.cabeza:
                actual = actual.siguiente
            actual.siguiente = nuevo_cliente
            nuevo_cliente.siguiente = self.cabeza
        
        self.tamano += 1
        return f"Cliente {nombre} agregado con {transacciones} transacciones"
    
    def atender_cliente(self):
        if not self.cabeza:
            return None, "No hay clientes en la cola"
        
        cliente = self.cabeza
        atendidas = min(cliente.transacciones, 5)
        cliente.transacciones -= atendidas
        
        if cliente.transacciones > 0:
            # Mover al final de la cola
            self.cabeza = cliente.siguiente
            mensaje = f"{cliente.nombre}: Atendidas {atendidas} transacciones (vuelve a la cola)"
        else:
            # Eliminar de la cola
            self.eliminar_cliente(cliente)
            mensaje = f"{cliente.nombre}: Atendidas {atendidas} transacciones (completado)"
        
        return cliente, mensaje
    
    def eliminar_cliente(self, cliente):
        if self.tamano == 1:
            self.cabeza = None
        else:
            anterior = self.cabeza
            while anterior.siguiente != cliente:
                anterior = anterior.siguiente
            anterior.siguiente = cliente.siguiente
            if cliente == self.cabeza:
                self.cabeza = cliente.siguiente
        
        self.tamano -= 1
    
    def obtener_cola(self):
        if not self.cabeza:
            return []
        
        cola = []
        actual = self.cabeza
        while True:
            cola.append(f"{actual.nombre} ({actual.transacciones} trans.)")
            actual = actual.siguiente
            if actual == self.cabeza:
                break
        return cola

class BancoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación de Cola de Banco")
        self.root.geometry("600x500")
        
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
        
        agregar_btn = ttk.Button(frame_agregar, text="Agregar a la cola", command=self.agregar_cliente)
        agregar_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Frame para atender clientes
        frame_atender = ttk.LabelFrame(root, text="Atender Clientes", padding=10)
        frame_atender.pack(pady=10, padx=10, fill=tk.X)
        
        atender_btn = ttk.Button(frame_atender, text="Atender Siguiente Cliente", command=self.atender_cliente)
        atender_btn.pack(pady=5)
        
        self.mensaje_atencion = tk.StringVar()
        ttk.Label(frame_atender, textvariable=self.mensaje_atencion, wraplength=550).pack(pady=5)
        
        # Frame para mostrar la cola
        frame_cola = ttk.LabelFrame(root, text="Clientes en Cola", padding=10)
        frame_cola.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.cola_tree = ttk.Treeview(frame_cola, columns=('nombre', 'transacciones'), show='headings')
        self.cola_tree.heading('nombre', text='Nombre')
        self.cola_tree.heading('transacciones', text='Transacciones Pendientes')
        self.cola_tree.column('nombre', width=300)
        self.cola_tree.column('transacciones', width=200)
        self.cola_tree.pack(fill=tk.BOTH, expand=True)
        
        # Inicializar con algunos clientes

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
        messagebox.showinfo("Cliente agregado", mensaje)
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
        
        # Agregar los clientes actuales
        if self.cola.cabeza:
            actual = self.cola.cabeza
            while True:
                self.cola_tree.insert('', tk.END, values=(actual.nombre, actual.transacciones))
                actual = actual.siguiente
                if actual == self.cola.cabeza:
                    break

if __name__ == "__main__":
    root = tk.Tk()
    app = BancoApp(root)
    root.mainloop()