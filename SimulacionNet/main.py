import argparse
from Party import Party
from MultiPartyProtocol import Protocol


def leer_archivo(input_file):
    valores = []
    try:
        with open(input_file, "r") as archivo:
            for linea in archivo:
                elementos = linea.strip().split()
                for elem in elementos:
                    try:
                        # Convertir cada elemento a entero
                        valores.append(int(elem))
                    except ValueError:
                        print(f"Advertencia: El elemento '{elem}' no se puede convertir a entero y se omitirá.")
    except FileNotFoundError:
        print(f"Error: El archivo '{input_file}' no existe.")
        return None
    return valores

def main():
    parser = argparse.ArgumentParser(
        description="Lee un archivo, muestra su contenido y permite agregar un número desde la línea de comandos."
    )
    parser.add_argument("-i", "--input", required=True, help="Archivo de entrada (txt)")
    parser.add_argument("-n", "--numero", type=int, help="Número para agregar a la lista")
    args = parser.parse_args()

    # Leer el archivo y guardar los valores en una lista como enteros
    valores = leer_archivo(args.input)
    if valores is None:
        return

    # Mostrar los valores leídos del archivo (ya convertidos a enteros)
    print("\nValores leídos del archivo (enteros):")
    print(valores)

    # Agregar el número proporcionado por el usuario (si existe)
    if args.numero is not None:
        p = args.numero
        print(f"\nEl campo a trabajar es Z_{p}\n")
    else:
        print("\nNo se proporcionó un número. Usaremos un valor predeterminado de campo.")
        p = 7  # Valor predeterminado del campo primo (si no se pasa como argumento)

    # Crear una instancia de la clase Protocol
    protocol = Protocol(p, len(valores))

    # Ejecutar el protocolo con los valores leídos
    mixed_shares = protocol.run_protocol(valores)
    print(mixed_shares)


if __name__ == "__main__":
    main()


