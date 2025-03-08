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
    # First, we need at least two shares per party for multiplication
    if len(party_values[0]) < 2:
        raise ValueError("Each party needs at least 2 shares for multiplication")
    
    # Step 1: Each party performs local multiplication on their first two shares
    local_products = []
    for party_shares in party_values:
        product = Field(party_shares[0] * party_shares[1], prime).value
        local_products.append(product)
    
    # Step 2: Each party secret-shares their local product
    players = []
    for i, product in enumerate(local_products):
        shamir = ShamirSecretSharing(prime, product, num_parties)
        shares = shamir.generate_shares(degree)
        players.append(Party(i + 1, prime, shares))  # Using updated Party class
    
    # Step 3: Securely send shares between parties using Protocol
    players = Protocol.send_message(players)
    
    # Step 4: Each party computes their share of the final product using Lagrange interpolation
    final_shares = []
    for player in players:
        lagrange_data = [(i + 1, share) for i, share in enumerate(player.shares)]
        final_shares.append(lagrange_interpolation(lagrange_data, prime).value)
    
    return final_shares

