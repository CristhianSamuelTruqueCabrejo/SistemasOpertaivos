class Proceso:
    def __init__(self, id_proceso, nombre,  tiempoLlegada, rafaga, tiempoComienzo):
        self.id_proceso = id_proceso
        self.nombre = nombre
        self.tiempoLlegada = tiempoLlegada
        self.rafaga = rafaga
        self.tiempoComienzo = tiempoComienzo
        self.tiempoFinal = self.rafaga + self.tiempoComienzo
        self.tiempoRetorno = self.tiempoFinal - self.tiempoLlegada
        self.tiempoEspera = self.tiempoRetorno - self.rafaga

    