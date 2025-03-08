from BiMultiplication import secure_multiplication_reorganized
from Lagrange import lagrange_interpolation
import argparse
from Party import Party
from MultiPartyProtocol import Protocol

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
                if grado < cantidad_jugadores / 2:
                    break  # Valid degree, exit loop
                else:
                    print(f"El grado debe ser menor que {cantidad_jugadores/2}. Intente de nuevo.")
            except ValueError:
                print("Por favor ingrese un número entero para el grado.")
        
        print(f"Configuración exitosa: {cantidad_jugadores} jugadores con polinomio de grado {grado}")

        # Use Protocol to create and distribute shares
        protocolo = Protocol(primo, cantidad_jugadores)
        parties = protocolo.run_protocol(caso, grado)  # `run_protocol` returns the Party objects

        # Extract shares from parties for secure multiplication
        numbers = [party for party in parties]

        # Perform secure multi-party multiplication
        resultado_encriptado = secure_product_reorganized(numbers, primo, cantidad_jugadores, grado)

        # Prepare shares for interpolation
        resultado_encriptado = [(i + 1, fragmento) for i, fragmento in enumerate(resultado_encriptado)]
        resultado_revelado = lagrange_interpolation(resultado_encriptado, primo)

        print(f"El resultado es: {resultado_revelado}")

if __name__ == "__main__":
    main()
