from field_operations import Field
from Shamirss import ShamirSecretSharing
from Lagrange import lagrange_interpolation
from Party import Party

def secure_multiplication_reorganized(players: list, prime: int, num_parties: int, degree: int):
    """
    Securely multiplies shares where each Party object contains the shares.
    
    Args:
        players: List of Party objects
        prime: Prime number for the finite field
        num_parties: Number of parties
        degree: Degree of the polynomial
    """
    # Ensure each party has at least 2 shares
    if len(players[0].shares) < 2:
        raise ValueError("Each party needs at least 2 shares for multiplication")
    
    # Step 1: Each party performs local multiplication on their first two shares
    for player in players:
        product = Field(player.shares[0] * player.shares[1], prime).value
        player.shares = [product]  # Replace shares with the computed product
    
    print("Local multiplications:")
    for player in players:
        print(f"Player {player.player_id}: {player.shares}")
    
    # Step 2: Each party secret-shares their local product
    for player in players:
        shamir = ShamirSecretSharing(prime, player.shares[0], num_parties)
        player.shares = shamir.generate_shares(degree)
    
    print("Shared local products:")
    for player in players:
        print(f"Player {player.player_id}: {player.shares}")
    
    # Step 3: Securely send shares between parties
    Party.send(players)  # Redistribute shares
    
    print("Updated party shares after redistribution:")
    for player in players:
        print(f"Player {player.player_id}: {player.shares}")
    
    # Step 4: Each party computes their share of the final product using Lagrange interpolation
    for player in players:
        lagrange_data = [(i + 1, share) for i, share in enumerate(player.shares)]
        player.shares = [lagrange_interpolation(lagrange_data, prime).value]  # Replace shares with final computed value
    
    print("Final shares after Lagrange interpolation:")
    for player in players:
        print(f"Player {player.player_id}: {player.shares}")
    
    return players  # Returns the updated Party objects

    
