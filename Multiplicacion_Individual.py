from field_operations import Field
from Shamirss import ShamirSecretSharing
from Lagrange import lagrange_interpolation

def secure_sequential_multiplication(values, prime, num_parties, degree):
    """
    Securely multiplies a list of values sequentially with degree reduction.
    
    Args:
        values: List of values to multiply
        prime: Prime number for the finite field
        num_parties: Number of parties
        degree: Degree of the polynomial for secret sharing
    """
    if len(values) < 2:
        raise ValueError("Need at least 2 values to multiply")
    
    # Start with the first value
    result = values[0]
    
    # Process each remaining value in sequence
    for i in range(1, len(values)):
        # Step 1: Multiply current result with next value
        product = Field(result * values[i], prime).value
        print(f"Intermediate product: {result} * {values[i]} = {product}")
        
        # Step 2: Secret share the product
        shamir = ShamirSecretSharing(prime, product, num_parties)
        shares = shamir.generate_shares(degree)
        print(f"Generated shares: {shares}")
        
        # Step 3: Reconstruct using Lagrange interpolation
        points = [(j+1, share) for j, share in enumerate(shares)]
        result = lagrange_interpolation(points, prime).value
        print(f"Reconstructed result: {result}")
    
    return result
