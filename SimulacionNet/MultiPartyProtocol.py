from Shamirss import ShamirSecretSharing
from Party import Party

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
        n = len(players)  # Número de jugadores
        
        # Crear una copia de los fragmentos de cada jugador para evitar sobreescribir datos en el proceso
        new_shares = [p.shares[:] for p in players]

        # Distribuir los fragmentos entre los jugadores
        for i in range(n):
            for j in range(n):
                if i != j:
                    new_shares[j][i] = players[i].shares[j]  # Cada jugador recibe el fragmento de otro jugador
        
        # Aplicar la nueva distribución de fragmentos a cada jugador
        for i in range(n):
            players[i].shares = new_shares[i]

        return players

    def run_protocol(self, valores: list[int], t):
        n = self.number_players 
        secrets = valores.copy() 

        players = [] 
        for i in range(1, n + 1):
            # Se extrae el secreto correspondiente al jugador i
            secret = secrets[i - 1]
            
            # Se generan los fragmentos usando el esquema de Shamir
            shamir = ShamirSecretSharing(self.field, secret, n)
            shares = shamir.generate_shares(t) 
            print(f"Shares generados por el jugador {i}:")
            print(f"{shares}\n")
            
            # Se crea un objeto Party (jugador) y se añade a la lista de jugadores
            players.append(Party(i, self.field, shares))

        print("Fragmentos originales de los jugadores:")
        for p in players:
            print(p)
        
        # Llamamos a send_message para distribuir los fragmentos entre los jugadores
        self.send_message(players)

        print("\nFragmentos después de la repartición:")
        for p in players:
            print(p)

        players_shares = [p.shares for p in players]  # Obtener los fragmentos de cada jugador

        return players_shares
