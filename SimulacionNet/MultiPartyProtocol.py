from field_operations import Field
from Shamirss import ShamirSecretSharing
from Party import Party
from Multiplication import secure_multiplication_reorganized
from Lagrange import lagrange_interpolation
class Protocol:
    def __init__(self, field: int, number_players: int):
        self.field = field
        self.number_players = number_players

    @staticmethod
    def send_message(players: list['Party']): 
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

    def run_protocol(self, valores: list[int]):
        n = self.number_players
        secrets = valores.copy()  # Usamos una copia para no modificar la lista original
        t = n // 2

        players = []
        for i in range(1, n + 1):
            # Se extrae el secreto correspondiente al jugador i
            secret = secrets[i - 1]
            
            # Se generan los fragmentos usando Shamir
            shamir = ShamirSecretSharing(self.field, secret, n)
            shares = shamir.generate_shares(t)
            print(f"Shares generados por el jugador {i}:")
            print(f"{shares}\n")
            
            # Se crea un objeto Party y se añade a la lista de jugadores
            players.append(Party(i, shares))

        print("Fragmentos originales de los jugadores:")
        for p in players:
            print(p)
        
        # Llamamos a send_message para distribuir los fragmentos
        self.send_message(players)

        print("\nFragmentos después de la reparticiónl:")
        for p in players:
            print(p)

        a=secure_multiplication_reorganized(players, self.field, self.number_players, t)
        
        print("Multiplicación segura de los fragmentos:")
        print(a)

        return players  # Devuelve los jugadores con los fragmentos redistribuidos
        
    
