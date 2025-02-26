import argparse

def main():
    parser = argparse.ArgumentParser(description="Lee un archivo, muestra su contenido y permite agregar un número desde la línea de comandos.")
    parser.add_argument("-i", "--input", required=True, help="Archivo de entrada (txt)")
    parser.add_argument("-n", "--numero", type=float)
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

    # Guardar el número proporcionado por el usuario en una variable
    if args.numero is not None:
        numero = args.numero
        print(f"\nNúmero proporcionado: {numero}")
    else:
        numero = None
        print("\nNo se proporcionó ningún número.")

    # Mostrar la lista y el número por separado
    print("\nResumen final:")
    print(f"Lista de valores: {valores}")
    print(f"Número: {numero}")

if __name__ == "__main__":
    main()
