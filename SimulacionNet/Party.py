from field_operations import Field


class Party:
    def __init__(self, player_id: int, shares: list[Field]):
        self.player_id = player_id
        self.shares = shares

    def __repr__(self):
        return f"Party {self.player_id} con shares: {self.shares}"

    @staticmethod
    def send(players: list['Party']):
        # Se crea un diccionario para almacenar los fragmentos mezclados
        n = len(players)
        mixed_shares = {f"p_{i+1}": [] for i in range(n)}
        
        # Se reordena la información: cada jugador recibirá el i-ésimo fragmento
        for i in range(n):
            for player in players:
                mixed_shares[f"p_{i+1}"].append(player.shares[i])
        return mixed_shares
