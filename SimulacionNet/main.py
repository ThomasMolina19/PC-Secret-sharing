from Multiplication import secure_multiplication_reorganized
from Lagrange import lagrange_interpolation
import argparse
from MultiPartyProtocol import Protocol

def secure_product_reorganized(party_values, prime, num_parties, degree):
    """
    Calcula de manera segura el producto de múltiples números usando MPC.
    
    Args:
        party_values: Lista donde party_values[i] contiene todas las acciones que la parte i+1 tiene
        prime: Número primo para el campo finito
        num_parties: Número de partes
        degree: Grado de los polinomios
    """
    if len(party_values) < 1:
        raise ValueError("Se requiere al menos una parte")
    
    if len(party_values[0]) < 2:
        raise ValueError("Cada parte necesita al menos 2 acciones para la multiplicación")
    
    # Paso 1: Realizar la multiplicación inicial con las dos primeras acciones
    result_shares = secure_multiplication_reorganized(party_values, prime, num_parties, degree)
    
    # Paso 2: Si hay más acciones, continuar multiplicando
    if len(party_values[0]) > 2:
        # Crear nuevos party_values donde cada parte tiene:
        # 1. Su acción del resultado de la primera multiplicación
        # 2. Su tercera acción, y así sucesivamente
        for share_idx in range(2, len(party_values[0])):
            next_party_values = []
            for party_idx, party_shares in enumerate(party_values):
                # Cada parte ahora tiene su acción de resultado y su siguiente acción
                next_party_values.append([result_shares[party_idx], party_shares[share_idx]])
            
            # Realizar la multiplicación segura con el siguiente conjunto de acciones
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
    # Configurar el análisis de argumentos de la línea de comandos
    parser = argparse.ArgumentParser(
        description="Multiplicación segura de números usando MPC."
    )
    parser.add_argument("-f", "--file", required=True, help="Archivo con los números a multiplicar")
    
    args = parser.parse_args()
    
    # Leer el número primo de los argumentos de la línea de comandos
    primo = 2**31 - 1 
    print(f"Usando el campo Z_{primo}")
    
    # Leer números del archivo
    numeros = leer_archivo(args.file)
    if numeros == None:
        return
    
    print(f"Números leídos del archivo: {numeros}")

    for i, caso in enumerate(numeros):
        print(f"Caso {i+1}")
        cantidad_jugadores = len(caso)

        while True:
            try:
                grado = int(input("Grado del polinomio (Debe ser menor que la mitad del numero de jugadores): "))
                if grado < cantidad_jugadores / 2:
                    break  # Grado polinomio válido, salir del bucle
                else:
                    print(f"El grado debe ser menor que {cantidad_jugadores/2}. Intente de nuevo.")
            except ValueError:
                print("Por favor ingrese un número entero para el grado.")
        
        print(f"Configuración exitosa: {cantidad_jugadores} jugadores con polinomio de grado {grado}")

        # Usar el Protocolo para crear y distribuir acciones
        protocolo = Protocol(primo, cantidad_jugadores)
        # `run_protocol` devuelve los objetos Party que contienen las acciones de cada jugador
        parties = protocolo.run_protocol(caso, grado)

        # Extraer acciones de las partes para la multiplicación segura
        numbers = [party for party in parties]

        # Realizar la multiplicación segura de las acciones y asociar cada fragmento del resultado con su índice de jugador
        resultado_encriptado = secure_product_reorganized(numbers, primo, cantidad_jugadores, grado)
        resultado_encriptado = [(i + 1, fragmento) for i, fragmento in enumerate(resultado_encriptado)]
        
        # Usar la interpolación de Lagrange para revelar el resultado final
        resultado_revelado = lagrange_interpolation(resultado_encriptado, primo)

        # Imprimir el resultado final
        print(f"El resultado es: {resultado_revelado}")

if __name__ == "__main__":
    main()