from field_operations import Field
from Polynomials import Polynomio
from Shamirss import ShamirSecretSharing

class Party:

    def __init__(self, field, number_players):
        self.field = field
        self.number_players = number_players
        

    @staticmethod
    def generate_party(number_players: int, field: int):
        # Número de jugadores
        n = number_players  # Puedes cambiar este valor según el número de jugadores

        # Crear el diccionario
        party = {}

        # Llenar el diccionario con jugadores p_1, p_2, ..., p_n
        for i in range(1, n + 1):
            numero_jugador = input(f"Ingresa el numero del P{i}: ")  # El usuario ingresa el nombre del jugador
            p_i=ShamirSecretSharing(field, numero_jugador, n)
            party[f"p_{i}"] = p_i  # Asignamos el nombre al jugador p_i

        # Mostrar el diccionario
        print(party)


    
p1 = ShamirSecretSharing(11, 7, 5)

print(p1.generate_shares(2))
