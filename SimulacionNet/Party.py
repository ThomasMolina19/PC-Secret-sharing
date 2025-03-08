from field_operations import Field

class Party:
    def __init__(self, player_id: int, prime, values=None):
        """
        Inicializa una Party con un ID de jugador y opcionalmente una lista de valores.
        
        Args:
            player_id: Identificador único para el jugador
            values: Lista de valores para convertir a elementos del campo (opcional)
            field_modulus: El módulo para el campo finito (por defecto: 11)
        """
        self.player_id = player_id
            
        # Si se proporcionan valores, convertirlos a objetos Field
        if values is not None:
            self.shares = [Field(value, prime).value for value in values]
        else:
            self.shares = []    
            
    def __repr__(self):
        return f"Party {self.player_id} con shares: {self.shares}"

    
    @staticmethod
    def send(players: list['Party']):
        """
        Distribuye los fragmentos correctamente:
        - Cada jugador mantiene su primer fragmento.
        - Envía los otros fragmentos a los jugadores correctos.
        """
        n = len(players)
    
        # Crear una copia para evitar sobreescribir datos en el proceso
        new_shares = [p.shares[:] for p in players]
        for i in range(n):
            for j in range(n):
                if i != j:
                    new_shares[j][i] = players[i].shares[j]  # Cada jugador recibe el fragmento de otro jugador
    
        # Aplicar la nueva distribución a cada jugador
        for i in range(n):
            players[i].shares = new_shares[i]
        return players  # Modifica los jugadores directamente y los devuelve opcionalmente
    