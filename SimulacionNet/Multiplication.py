from field_operations import Field
from Shamirss import ShamirSecretSharing
from Party import Party
from MultiPartyProtocol import Protocol
from Lagrange import lagrange_interpolation

def secure_multiplication_reorganized(party_values, prime, num_parties, degree):
    """
    Securely multiplies shares where party_values[i] contains all the shares that party i+1 has.
    
    Args:
        party_values: List where each element represents all shares held by one party
        prime: Prime number for the finite field
        num_parties: Number of parties
        degree: Degree of the polynomial
    """
    # Primero, necesitamos al menos dos acciones por parte para la multiplicación
    if len(party_values[0]) < 2:
        raise ValueError("Cada parte necesita al menos 2 acciones para la multiplicación")
    
    # Paso 1: Cada parte realiza la multiplicación local en sus dos primeras acciones
    local_products = []
    for party_shares in party_values:
        product = Field(party_shares[0] * party_shares[1], prime).value
        local_products.append(product)
    
    # Paso 2: Cada parte comparte secretamente su producto local
    players = []
    for i, product in enumerate(local_products):
        shamir = ShamirSecretSharing(prime, product, num_parties)
        shares = shamir.generate_shares(degree)
        players.append(Party(i + 1, prime, shares))  # Usando la clase Party actualizada
    
    # Paso 3: Enviar acciones de manera segura entre las partes usando el Protocolo
    players = Protocol.send_message(players)
    
    # Paso 4: Cada parte calcula su acción del producto final usando interpolación de Lagrange
    final_shares = []
    for player in players:
        lagrange_data = [(i + 1, share) for i, share in enumerate(player.shares)]
        final_shares.append(lagrange_interpolation(lagrange_data, prime).value)
    
    return final_shares
