from Protocolo import secure_multiplication
from Party import Party
from Lagrange import lagrange_interpolation

cantidad_jugadores = int(input("Ingrese la cantidad de jugadores: "))
primo = 2**19 - 1 
numbers = [fragment for fragment in (Party(primo,cantidad_jugadores).generate_party(1).values())]

def secure_product(numbers, prime, num_parties):
    """
    Securely computes the product of a list of numbers using secret sharing.
    All numbers are first secret-shared, and all intermediate results remain secret-shared.
    
    Args:
        numbers: List of integers to multiply securely
        prime: Prime number for the finite field
        num_parties: Number of parties in the computation
    
    Returns:
        List of shares representing the product
    """
    if len(numbers) < 2:
        raise ValueError("At least two numbers are required for secure multiplication.")
    
    # Step 2: Start with the first number's shares
    result_shares = numbers[0]
    
    # Step 3: Iteratively multiply with the rest of the numbers
    for i in range(1, len(numbers)):
        next_shares = numbers[i]
        # Perform secure multiplication between the current result and the next number
        result_shares = secure_multiplication(result_shares, next_shares, prime, num_parties)
        # print(f"Result after multiplying with number {i+1}: {result_shares}")
    
    # Return the final product shares
    return result_shares

Resultado_encriptado = secure_product(numbers,primo,cantidad_jugadores)
Resultado_encriptado = [(i+1,fragmento) for i, fragmento in enumerate(Resultado_encriptado)]
Resultado_revelado = lagrange_interpolation(Resultado_encriptado,primo)
print(f"El resultado es:  {Resultado_revelado}")