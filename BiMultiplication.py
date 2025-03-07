from field_operations import Field
from Polynomials import Polynomio
from Shamirss import ShamirSecretSharing
from Lagrange import lagrange_interpolation
from party0 import Party

def secure_multiplication_reorganized(party_values, prime, num_parties, degree):
    """
    Securely multiplies shares where party_values[i] contains all the shares that party i+1 has.
    
    Args:
        party_values: List where each element represents all shares held by one party
        prime: Prime number for the finite field
        num_parties: Number of parties
        degree: Degree of the polynomial
    """
    # First, we need exactly two shares per party for multiplication
    if len(party_values[0]) < 2:
        raise ValueError("Each party needs at least 2 shares for multiplication")
    
    # Step 1: Each party performs local multiplication on their first two shares
    local_products = []
    for party_shares in party_values:
        # Multiply first two shares
        product = Field(party_shares[0] * party_shares[1], prime).value
        local_products.append(product)
    
    # print(f"Local multiplications: {local_products}")
    
    # Step 2: Each party secret-shares their local product
    party_shares = {}
    for i, product in enumerate(local_products):
        shamir = ShamirSecretSharing(prime, product, num_parties)
        party_shares[f"p_{i+1}"] = shamir.generate_shares(degree)
    
    # print(f"Shared local products: {party_shares}")
    
    # Step 3: Securely send shares between parties
    party_shares = Party.send(party_shares)
    # print(f"Updated party shares after redistribution: {party_shares}")
    
    # Step 4: Each party computes their share of the final product using Lagrange interpolation
    final_shares = []
    for fragmentos in party_shares.values():
        LagrangeParcial = [(i+1, fragmento) for i, fragmento in enumerate(fragmentos)]
        final_shares.append(lagrange_interpolation(LagrangeParcial, prime).value)
    
    return final_shares
