from BiMultiplication import secure_multiplication_reorganized
from Party import Party
from Lagrange import lagrange_interpolation
import argparse

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

def leer_archivo(input_file):
    valores = []
    try:
        with open(input_file, "r") as archivo:
            for linea in archivo:
                lista_linea = []
                elementos = linea.strip().split()
                for elem in elementos:
                    try:
                        # Convertir cada elemento a entero
                        lista_linea.append(int(elem))
                    except ValueError:
                        print(f"Advertencia: El elemento '{elem}' no se puede convertir a entero y se omitirá.")
                valores.append(lista_linea)
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no existe.")
        return None
    return valores

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Multiplicación segura de números usando MPC."
    )
    parser.add_argument("-f", "--file", required=True, help="Archivo con los números a multiplicar")
    parser.add_argument("-p", "--prime", type=int, required=True, help="Número primo para el campo Z_p")
    
    args = parser.parse_args()
    
    # Read prime number from command line arguments
    primo = args.prime
    print(f"Usando el campo Z_{primo}")
    
    # Read numbers from file
    numeros = leer_archivo(args.file)
    if numeros is None:
        return
    
    print(f"Números leídos del archivo: {numeros}")

    for i, caso in enumerate(numeros):
        print(f"Caso {i+1}")
        cantidad_jugadores = len(caso)
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
        
        # Variables are now properly set
        print(f"Configuración exitosa: {cantidad_jugadores} jugadores con polinomio de grado {grado}")

        p1 = Party(primo,cantidad_jugadores).generate_party(caso, grado)
        reshared_party = Party(primo,cantidad_jugadores).send(p1)
        numbers = [fragment for fragment in reshared_party.values()]

        Resultado_encriptado = secure_product_reorganized(numbers,primo,cantidad_jugadores,grado)
        Resultado_encriptado = [(i+1,fragmento) for i, fragmento in enumerate(Resultado_encriptado)]
        Resultado_revelado = lagrange_interpolation(Resultado_encriptado,primo)
        print(f"El resultado es:  {Resultado_revelado}")

if __name__ == "__main__":
    main()