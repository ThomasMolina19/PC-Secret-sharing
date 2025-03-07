from field_operations import Field


def send(players: list):
    # Se crea un diccionario para almacenar los fragmentos mezclados
    n = len(players)
    mixed_shares = {f"p_{i+1}": [] for i in range(n)}
    
    # Se reordena la información: cada jugador recibirá el i-ésimo fragmento
    for i in range(n):
        for player in players:
            mixed_shares[f"p_{i+1}"].append(player.shares[i])
    return mixed_shares
