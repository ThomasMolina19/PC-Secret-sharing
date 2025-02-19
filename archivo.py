import argparse

def main():
    parser = argparse.ArgumentParser(description="Lee un archivo, muestra su contenido y permite agregar un número desde la línea de comandos.")
    parser.add_argument("-i", "--input", required=True, help="Archivo de entrada (txt)")
    parser.add_argument("-n", "--numero", type=float, help="Número para agregar a la lista")
    args = parser.parse_args()

    # Leer el archivo y guardar los valores en una lista
    valores = []
    try:
        with open(args.input, "r") as archivo:
            for linea in archivo:
                elementos = linea.strip().split()
                valores.extend(elementos)
    except FileNotFoundError:
        print(f"Error: El archivo '{args.input}' no existe.")
        return

    # Mostrar los valores leídos del archivo
    print("\nValores leídos del archivo:")
    print(valores)

    # Agregar el número proporcionado por el usuario (si existe)
    if args.numero is not None:
        valores.append(str(args.numero))  # Convertir el número a cadena para consistencia
        print(f"\nNúmero '{args.numero}' agregado a la lista.")

    # Mostrar la lista final
    print("\nLista final de valores:")
    print(valores)

if __name__ == "__main__":
    main()
