import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton, 
                             QGroupBox, QTextEdit, QComboBox, QSpinBox, QGraphicsView,
                             QGraphicsScene, QGraphicsRectItem)
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QColor, QBrush, QPen, QPainter

class Proceso:
    def __init__(self, id, tiempo_llegada, rafaga, prioridad_cola, prioridad_proceso=None):
        self.id = id
        self.tiempo_llegada = tiempo_llegada
        self.rafaga = rafaga
        self.rafaga_restante = rafaga
        self.prioridad_cola = prioridad_cola  # Prioridad general (1-3)
        self.prioridad_proceso = prioridad_proceso if prioridad_proceso is not None else random.randint(1, 5)  # Prioridad específica para cola 3 (1-5, 1 es más alta)
        self.tiempo_comienzo = -1
        self.tiempo_final = -1
        self.tiempo_espera = 0
        self.tiempo_retorno = 0
        self.tiempo_en_cola_actual = 0
        self.envejecimiento = 0
        self.color = self.generar_color()
        
    def generar_color(self):
        # Generar un color único basado en el ID del proceso
        random.seed(self.id)
        return QColor(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        
    def __str__(self):
        if self.prioridad_cola == 3:
            return f"Proceso {self.id} (Cola:{self.prioridad_cola}, Prio:{self.prioridad_proceso}): Llegada={self.tiempo_llegada}, Rafaga={self.rafaga}, Restante={self.rafaga_restante}"
        else:
            return f"Proceso {self.id} (Cola:{self.prioridad_cola}): Llegada={self.tiempo_llegada}, Rafaga={self.rafaga}, Restante={self.rafaga_restante}"

class SimuladorMulticolas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Multicolas con Prioridades Detalladas")
        self.setGeometry(100, 100, 1400, 900)
        
        # Variables de simulación
        self.tiempo_actual = 0
        self.procesos = []
        self.colas = {
            1: [],  # Round Robin (q=2)
            2: [],  # FIFO
            3: [],  # Prioridades (se ordenan por prioridad_proceso)
        }
        self.proceso_en_ejecucion = None
        self.quantum = 2
        self.quantum_restante = self.quantum
        self.gantt = []
        self.procesos_terminados = []
        self.id_proceso = 1
        self.paused = True
        self.max_tiempo_visualizado = 20  # Tiempo máximo inicial en el diagrama de Gantt
        
        # Configurar interfaz
        self.initUI()
        
    def initUI(self):
        # Layout principal
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Panel de control
        control_panel = QGroupBox("Control")
        control_layout = QVBoxLayout()
        
        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_pausar = QPushButton("Pausar")
        self.btn_reiniciar = QPushButton("Reiniciar")
        self.btn_agregar = QPushButton("Agregar Proceso")
        self.btn_agregar_aleatorio = QPushButton("Agregar 5 procesos aleatorios")
        
        self.spin_rafaga = QSpinBox()
        self.spin_rafaga.setRange(1, 20)
        self.spin_prioridad_cola = QSpinBox()
        self.spin_prioridad_cola.setRange(1, 3)
        self.spin_prioridad_proceso = QSpinBox()
        self.spin_prioridad_proceso.setRange(1, 5)
        
        control_layout.addWidget(QLabel("Ráfaga:"))
        control_layout.addWidget(self.spin_rafaga)
        control_layout.addWidget(QLabel("Prioridad Cola (1-3):"))
        control_layout.addWidget(self.spin_prioridad_cola)
        control_layout.addWidget(QLabel("Prioridad Proceso (1-5, solo cola 3):"))
        control_layout.addWidget(self.spin_prioridad_proceso)
        control_layout.addWidget(self.btn_agregar)
        control_layout.addWidget(self.btn_agregar_aleatorio)
        control_layout.addWidget(self.btn_iniciar)
        control_layout.addWidget(self.btn_pausar)
        control_layout.addWidget(self.btn_reiniciar)
        control_layout.addStretch()
        
        control_panel.setLayout(control_layout)
        
        # Panel de visualización
        vis_panel = QWidget()
        vis_layout = QVBoxLayout()
        
        # Diagrama de Gantt
        gantt_group = QGroupBox("Diagrama de Gantt")
        gantt_layout = QVBoxLayout()
        
        self.gantt_scene = QGraphicsScene()
        self.gantt_view = QGraphicsView(self.gantt_scene)
        self.gantt_view.setRenderHint(QPainter.Antialiasing)
        self.gantt_view.setMinimumHeight(200)
        
        self.gantt_leyenda = QGraphicsScene()
        self.gantt_leyenda_view = QGraphicsView(self.gantt_leyenda)
        self.gantt_leyenda_view.setMaximumHeight(50)
        self.gantt_leyenda_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        gantt_layout.addWidget(self.gantt_view)
        gantt_layout.addWidget(QLabel("Leyenda:"))
        gantt_layout.addWidget(self.gantt_leyenda_view)
        gantt_group.setLayout(gantt_layout)
        
        # Tabla de procesos
        self.tabla_procesos = QTableWidget()
        self.tabla_procesos.setColumnCount(9)
        self.tabla_procesos.setHorizontalHeaderLabels(["Proceso", "Cola", "Prio", "Llegada", "Ráfaga", 
                                                     "Comienzo", "Final", "Retorno", "Espera"])
        
        # Visualización de colas
        self.cola_rr = QTextEdit()
        self.cola_rr.setReadOnly(True)
        self.cola_fifo = QTextEdit()
        self.cola_fifo.setReadOnly(True)
        self.cola_prioridades = QTextEdit()
        self.cola_prioridades.setReadOnly(True)
        
        colas_group = QGroupBox("Colas")
        colas_layout = QHBoxLayout()
        colas_layout.addWidget(QLabel("Round Robin (1):"))
        colas_layout.addWidget(self.cola_rr)
        colas_layout.addWidget(QLabel("FIFO (2):"))
        colas_layout.addWidget(self.cola_fifo)
        colas_layout.addWidget(QLabel("Prioridades (3):"))
        colas_layout.addWidget(self.cola_prioridades)
        colas_group.setLayout(colas_layout)
        
        vis_layout.addWidget(gantt_group)
        vis_layout.addWidget(QLabel("Procesos terminados:"))
        vis_layout.addWidget(self.tabla_procesos)
        vis_layout.addWidget(colas_group)
        
        vis_panel.setLayout(vis_layout)
        
        # Agregar paneles al layout principal
        main_layout.addWidget(control_panel, stretch=1)
        main_layout.addWidget(vis_panel, stretch=4)
        main_widget.setLayout(main_layout)
        
        self.setCentralWidget(main_widget)
        
        # Conectar señales
        self.btn_iniciar.clicked.connect(self.iniciar_simulacion)
        self.btn_pausar.clicked.connect(self.pausar_simulacion)
        self.btn_reiniciar.clicked.connect(self.reiniciar_simulacion)
        self.btn_agregar.clicked.connect(self.agregar_proceso_manual)
        self.btn_agregar_aleatorio.clicked.connect(lambda: self.agregar_proceso_aleatorio(5))
        
        # Timer para la simulación
        self.timer = QTimer()
        self.timer.timeout.connect(self.avanzar_tiempo)
        
        # Configurar el diagrama de Gantt
        self.dibujar_gantt()
        self.dibujar_leyenda()
        
    def agregar_proceso_aleatorio(self, cantidad):
        for _ in range(cantidad):
            tiempo_llegada = random.randint(0, 10)
            rafaga = random.randint(1, 10)
            prioridad_cola = random.randint(1, 3)
            prioridad_proceso = random.randint(1, 5) if prioridad_cola == 3 else None
            self.procesos.append(Proceso(self.id_proceso, tiempo_llegada, rafaga, prioridad_cola, prioridad_proceso))
            self.id_proceso += 1
        self.actualizar_colas()
        self.dibujar_leyenda()
    
    def agregar_proceso_manual(self):
        rafaga = self.spin_rafaga.value()
        prioridad_cola = self.spin_prioridad_cola.value()
        prioridad_proceso = self.spin_prioridad_proceso.value() if prioridad_cola == 3 else None
        proceso = Proceso(self.id_proceso, self.tiempo_actual, rafaga, prioridad_cola, prioridad_proceso)
        self.procesos.append(proceso)
        self.id_proceso += 1
        self.actualizar_colas()
        self.dibujar_leyenda()
        
    def iniciar_simulacion(self):
        self.paused = False
        self.timer.start(500)  # Avanzar cada 500ms
    
    def pausar_simulacion(self):
        self.paused = True
        self.timer.stop()
    
    def reiniciar_simulacion(self):
        self.pausar_simulacion()
        self.tiempo_actual = 0
        self.procesos = []
        self.colas = {1: [], 2: [], 3: []}
        self.proceso_en_ejecucion = None
        self.quantum_restante = self.quantum
        self.gantt = []
        self.procesos_terminados = []
        self.id_proceso = 1
        self.agregar_proceso_aleatorio(5)
        self.actualizar_ui()
    
    def avanzar_tiempo(self):
        if self.paused:
            return
            
        self.tiempo_actual += 1
        
        # Ajustar el rango del diagrama de Gantt si es necesario
        if self.tiempo_actual > self.max_tiempo_visualizado:
            self.max_tiempo_visualizado = self.tiempo_actual + 5
            self.dibujar_gantt()
        
        # Agregar procesos que han llegado a sus colas correspondientes
        nuevos_procesos = [p for p in self.procesos if p.tiempo_llegada == self.tiempo_actual]
        for proceso in nuevos_procesos:
            self.colas[proceso.prioridad_cola].append(proceso)
        
        # Ordenar cola de prioridades (3) por prioridad_proceso (1 es más alta)
        self.colas[3].sort(key=lambda x: x.prioridad_proceso)
        
        # Verificar si hay un proceso en ejecución
        if self.proceso_en_ejecucion is None:
            self.elegir_proximo_proceso()
        else:
            # Verificar si llegó un proceso de mayor prioridad
            prioridad_actual = self.proceso_en_ejecucion.prioridad_cola
            colas_superiores = [p for p in self.colas.keys() if p < prioridad_actual]
            for prioridad in colas_superiores:
                if self.colas[prioridad]:
                    # Expulsar el proceso actual
                    self.colas[prioridad_actual].insert(0, self.proceso_en_ejecucion)
                    self.proceso_en_ejecucion = None
                    self.quantum_restante = self.quantum
                    self.elegir_proximo_proceso()
                    break
            
            if self.proceso_en_ejecucion:
                # Ejecutar el proceso actual
                self.proceso_en_ejecucion.rafaga_restante -= 1
                self.quantum_restante -= 1
                
                # Registrar en el diagrama de Gantt
                self.actualizar_gantt()
                
                # Verificar si el proceso ha terminado
                if self.proceso_en_ejecucion.rafaga_restante == 0:
                    self.proceso_en_ejecucion.tiempo_final = self.tiempo_actual
                    self.proceso_en_ejecucion.tiempo_retorno = self.proceso_en_ejecucion.tiempo_final - self.proceso_en_ejecucion.tiempo_llegada
                    self.proceso_en_ejecucion.tiempo_espera = self.proceso_en_ejecucion.tiempo_retorno - self.proceso_en_ejecucion.rafaga
                    self.procesos_terminados.append(self.proceso_en_ejecucion)
                    self.proceso_en_ejecucion = None
                    self.quantum_restante = self.quantum
                    # Elegir inmediatamente el siguiente proceso en el mismo tiempo
                    self.elegir_proximo_proceso()
                # Verificar si se acabó el quantum (solo para Round Robin)
                elif self.quantum_restante == 0 and prioridad_actual == 1:
                    self.colas[prioridad_actual].append(self.proceso_en_ejecucion)
                    self.proceso_en_ejecucion = None
                    self.quantum_restante = self.quantum
                    # Elegir inmediatamente el siguiente proceso en el mismo tiempo
                    self.elegir_proximo_proceso()
        
        # Aplicar envejecimiento
        self.aplicar_envejecimiento()
        
        # Actualizar la interfaz
        self.actualizar_ui()
    
    def actualizar_gantt(self):
        if not self.gantt or self.gantt[-1][0] != self.proceso_en_ejecucion.id or self.gantt[-1][2] != self.tiempo_actual - 1:
            # Nuevo segmento en el diagrama de Gantt
            self.gantt.append((self.proceso_en_ejecucion.id, self.tiempo_actual - 1, self.tiempo_actual))
        else:
            # Extender el segmento actual
            self.gantt[-1] = (self.gantt[-1][0], self.gantt[-1][1], self.tiempo_actual)
        
        self.dibujar_gantt()
    
    def dibujar_gantt(self):
        self.gantt_scene.clear()
        
        # Dibujar ejes
        self.gantt_scene.addLine(50, 30, 50, 180, QPen(Qt.black))
        self.gantt_scene.addLine(50, 180, 50 + self.max_tiempo_visualizado * 30, 180, QPen(Qt.black))
        
        # Dibujar marcas de tiempo
        for t in range(0, self.max_tiempo_visualizado + 1):
            x = 50 + t * 30
            self.gantt_scene.addLine(x, 175, x, 180, QPen(Qt.black))
            texto = self.gantt_scene.addText(str(t))
            texto.setPos(x - 10, 182)
        
        # Dibujar barras de procesos
        procesos_gantt = {}
        for entry in self.gantt:
            pid, inicio, fin = entry
            if pid not in procesos_gantt:
                procesos_gantt[pid] = []
            procesos_gantt[pid].append((inicio, fin))
        
        # Encontrar todos los procesos que han aparecido en el Gantt
        all_pids = list(procesos_gantt.keys())
        all_pids.sort()
        
        # Asignar posición vertical a cada proceso
        pos_y = {pid: 60 + i * 30 for i, pid in enumerate(all_pids)}
        
        # Dibujar las barras para cada proceso
        for pid in all_pids:
            proceso = next((p for p in self.procesos + self.procesos_terminados if p.id == pid), None)
            if proceso:
                color = proceso.color
                for inicio, fin in procesos_gantt[pid]:
                    x1 = 50 + inicio * 30
                    x2 = 50 + fin * 30
                    rect = QRectF(x1, pos_y[pid] - 10, x2 - x1, 20)
                    barra = self.gantt_scene.addRect(rect, QPen(Qt.black), QBrush(color))
                    # Mostrar ID del proceso en la barra si hay espacio
                    if x2 - x1 > 20:
                        texto = self.gantt_scene.addText(f"P{pid}")
                        texto.setPos(x1 + 5, pos_y[pid] - 10)
        
        # Dibujar línea de tiempo actual
        x_actual = 50 + self.tiempo_actual * 30
        self.gantt_scene.addLine(x_actual, 30, x_actual, 180, QPen(Qt.red, 2))
    
    def dibujar_leyenda(self):
        self.gantt_leyenda.clear()
        
        # Obtener todos los procesos únicos
        procesos_unicos = {}
        for p in self.procesos + self.procesos_terminados:
            if p.id not in procesos_unicos:
                procesos_unicos[p.id] = p
        
        # Ordenar por ID
        pids = sorted(procesos_unicos.keys())
        
        # Dibujar leyenda
        x_pos = 10
        for pid in pids:
            p = procesos_unicos[pid]
            # Cuadro de color
            rect = self.gantt_leyenda.addRect(x_pos, 10, 20, 20, QPen(Qt.black), QBrush(p.color))
            # Texto
            if p.prioridad_cola == 3:
                texto = self.gantt_leyenda.addText(f"P{pid} (Cola:{p.prioridad_cola}, Prio:{p.prioridad_proceso})")
            else:
                texto = self.gantt_leyenda.addText(f"P{pid} (Cola:{p.prioridad_cola})")
            texto.setPos(x_pos + 25, 10)
            x_pos += 180  # Espacio entre elementos de leyenda
    
    def elegir_proximo_proceso(self):
        for prioridad in sorted(self.colas.keys()):
            if self.colas[prioridad]:
                if prioridad == 3:
                    # Para la cola de prioridades, seleccionar el de mayor prioridad_proceso (menor número)
                    self.colas[prioridad].sort(key=lambda x: x.prioridad_proceso)
                self.proceso_en_ejecucion = self.colas[prioridad].pop(0)
                if self.proceso_en_ejecucion.tiempo_comienzo == -1:
                    self.proceso_en_ejecucion.tiempo_comienzo = self.tiempo_actual
                self.quantum_restante = self.quantum if prioridad == 1 else float('inf')
                break
    
    def aplicar_envejecimiento(self):
        for prioridad in [2, 3]:  # Solo FIFO y Prioridades pueden envejecer
            for proceso in self.colas[prioridad]:
                proceso.tiempo_en_cola_actual += 1
                if proceso.tiempo_en_cola_actual >= 3 * proceso.rafaga:
                    nueva_prioridad = max(1, prioridad - 1)
                    self.colas[prioridad].remove(proceso)
                    self.colas[nueva_prioridad].append(proceso)
                    proceso.prioridad_cola = nueva_prioridad
                    proceso.tiempo_en_cola_actual = 0
                    # Si pasa a la cola Round Robin, ya no necesita prioridad_proceso
                    if nueva_prioridad == 1:
                        proceso.prioridad_proceso = None
    
    def actualizar_colas(self):
        # Limpiar colas
        for cola in self.colas.values():
            cola.clear()
        
        # Agregar procesos a sus colas correspondientes
        for proceso in self.procesos:
            if proceso.tiempo_llegada <= self.tiempo_actual and proceso not in self.procesos_terminados and proceso != self.proceso_en_ejecucion:
                self.colas[proceso.prioridad_cola].append(proceso)
        
        # Ordenar cola de prioridades
        self.colas[3].sort(key=lambda x: x.prioridad_proceso)
    
    def actualizar_ui(self):
        # Actualizar visualización de colas
        self.cola_rr.setText("\n".join(str(p) for p in self.colas[1]))
        self.cola_fifo.setText("\n".join(str(p) for p in self.colas[2]))
        self.cola_prioridades.setText("\n".join(str(p) for p in self.colas[3]))
        
        # Actualizar tabla de procesos terminados
        self.tabla_procesos.setRowCount(len(self.procesos_terminados))
        for i, proceso in enumerate(self.procesos_terminados):
            self.tabla_procesos.setItem(i, 0, QTableWidgetItem(str(proceso.id)))
            self.tabla_procesos.setItem(i, 1, QTableWidgetItem(str(proceso.prioridad_cola)))
            prio_str = str(proceso.prioridad_proceso) if proceso.prioridad_cola == 3 else "N/A"
            self.tabla_procesos.setItem(i, 2, QTableWidgetItem(prio_str))
            self.tabla_procesos.setItem(i, 3, QTableWidgetItem(str(proceso.tiempo_llegada)))
            self.tabla_procesos.setItem(i, 4, QTableWidgetItem(str(proceso.rafaga)))
            self.tabla_procesos.setItem(i, 5, QTableWidgetItem(str(proceso.tiempo_comienzo)))
            self.tabla_procesos.setItem(i, 6, QTableWidgetItem(str(proceso.tiempo_final)))
            self.tabla_procesos.setItem(i, 7, QTableWidgetItem(str(proceso.tiempo_retorno)))
            self.tabla_procesos.setItem(i, 8, QTableWidgetItem(str(proceso.tiempo_espera)))
        
        # Mostrar proceso en ejecución
        if self.proceso_en_ejecucion:
            status = f"Ejecutando: {self.proceso_en_ejecucion} - Tiempo: {self.tiempo_actual}"
        else:
            status = f"Tiempo: {self.tiempo_actual} - No hay proceso en ejecución"
        self.statusBar().showMessage(status)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    simulador = SimuladorMulticolas()
    simulador.show()
    sys.exit(app.exec_())