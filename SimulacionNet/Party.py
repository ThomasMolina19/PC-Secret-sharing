# from field_operations import Field


# class Party:
#     def __init__(self, player_id: int, shares: list[Field]):
#         self.player_id = player_id
#         self.shares = shares

#     def __repr__(self):
#         return f"Party {self.player_id} con shares:{self.shares}"

#     @staticmethod
#     def send(players: list['Party']): 
#         """ 
#         Distribuye los fragmentos correctamente: 
#         - Cada jugador mantiene su primer fragmento.
#         - Envía los otros fragmentos a los jugadores correctos.
#         """
#         n = len(players)
        
#         # Crear una copia para evitar sobreescribir datos en el proceso
#         new_shares = [p.shares[:] for p in players]

#         for i in range(n):
#             for j in range(n):
#                 if i != j:
#                     new_shares[j][i] = players[i].shares[j]  # Cada jugador recibe el fragmento de otro jugador
        
#         # Aplicar la nueva distribución a cada jugador
#         for i in range(n):
#             players[i].shares = new_shares[i]

#         return players  # Modifica los jugadores directamente y los devuelve opcionalmente


# p1 = Party(1, [Field(2,11), Field(3,11), Field(4,11), Field(5,11)])
# p2 = Party(2, [Field(2,11), Field(75,11), Field(35,11), Field(2,11)])
# print(Party.send([p1, p2]))

from field_operations import Field

class Party:
    def __init__(self, player_id: int, values=None, field_modulus=2**19):
        """
        Initialize a Party with a player ID and optionally a list of values.
        
        Args:
            player_id: Unique identifier for the player
            values: List of values to convert to Field elements (optional)
            field_modulus: The modulus for the finite field (default: 11)
        """
        self.player_id = player_id
        
        # If values are provided, convert them to Field objects
        if values is not None:
            self.shares = [Field(value, field_modulus).value for value in values]
        else:
            self.shares = []
            
    def __repr__(self):
        return f"Party {self.player_id} con shares:{self.shares}"
    
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
    
# Example usage with the improved design
p1 = Party(1, [2, 3, 4, 5])
p2 = Party(2, [2, 75, 35, 2])
p3 = Party(3, [15,68,98,45])
print(Party.send([p1, p2, p3]))