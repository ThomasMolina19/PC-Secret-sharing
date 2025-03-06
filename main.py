from Protocolo import secure_multiplication_reorganized
from Party import Party
from Lagrange import lagrange_interpolation

primo = 2**19 - 1 
while True:
    try:
        # Get the number of players
        cantidad_jugadores = int(input("Ingrese la cantidad de jugadores: "))
        # Keep asking for the degree until valid
        while True:
            try:
                grado = int(input("Grado del polinomio (Debe ser menor que la mitad del numero de jugadores): "))
                
                # Validate that degree is less than half the number of players
                if grado < cantidad_jugadores/2:
                    # Both inputs are valid, we can break out of both loops
                    break
                else:
                    print(f"El grado debe ser menor que {cantidad_jugadores/2}. Intente de nuevo.")
            except ValueError:
                print("Por favor ingrese un número entero para el grado.")

        # If we got here, both inputs are valid so we can break the outer loop
        break
        
    except ValueError:
        print("Por favor ingrese un número entero para la cantidad de jugadores.")

# Variables are now properly set
print(f"Configuración exitosa: {cantidad_jugadores} jugadores con polinomio de grado {grado}")

p1 = Party(primo,cantidad_jugadores).generate_party(grado)
reshared_party = Party(primo,cantidad_jugadores).send(p1)

numbers = [fragment for fragment in reshared_party.values()]
print(numbers)

def secure_product_reorganized(party_values, prime, num_parties, degree):
    """
    Securely computes the product of multiple numbers using MPC.
    
    Args:
        party_values: List where party_values[i] contains all shares that party i+1 has
        prime: Prime number for the finite field
        num_parties: Number of parties
        degree: Degree of the polynomial
    """
    if len(party_values) < 1:
        raise ValueError("At least one party is required")
    
    if len(party_values[0]) < 2:
        raise ValueError("Each party needs at least 2 shares for multiplication")
    
    # Step 1: Perform initial multiplication with first two shares
    result_shares = secure_multiplication_reorganized(party_values, prime, num_parties, degree)
    
    # Step 2: If there are more shares, continue multiplying
    if len(party_values[0]) > 2:
        # Create new party_values where each party has:
        # 1. Their share of the result from the first multiplication
        # 2. Their third share, and so on
        for share_idx in range(2, len(party_values[0])):
            next_party_values = []
            for party_idx, party_shares in enumerate(party_values):
                # Each party now has their result share and their next share
                next_party_values.append([result_shares[party_idx], party_shares[share_idx]])
            
            # Perform secure multiplication with the next set of shares
            result_shares = secure_multiplication_reorganized(next_party_values, prime, num_parties, degree)
    
    return result_shares


Resultado_encriptado = secure_product_reorganized(numbers,primo,cantidad_jugadores,grado)
Resultado_encriptado = [(i+1,fragmento) for i, fragmento in enumerate(Resultado_encriptado)]
Resultado_revelado = lagrange_interpolation(Resultado_encriptado,primo)
print(f"El resultado es:  {Resultado_revelado}")