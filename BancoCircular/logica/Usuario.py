import Transaccion
class Usuario:
    def __init__(self):
        self.transacciones = []
        self.cantTransacciones = len(self.transacciones) + 1

    def agregarTransaccion(self, transaccion : Transaccion):
        self.transacciones.append(transaccion)

daniel = Usuario()

daniel.agregarTransaccion(1000)

print(daniel.transacciones)
