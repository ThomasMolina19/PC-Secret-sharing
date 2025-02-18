def leer_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
            return [linea.strip() for linea in lineas]  # Guarda cada línea en una lista
    except FileNotFoundError:
        print(f"El archivo {nombre_archivo} no fue encontrado.")
        return []
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")
        return []

def main():
    nombre_archivo = input("Por favor, ingresa el nombre del archivo: ")
    lineas = leer_archivo(nombre_archivo)

    if lineas:
        print("Líneas del archivo:")
        for linea in lineas:
            print(linea)
    else:
        print("El archivo está vacío o no se pudo leer.")

if __name__ == "__main__":
    main()

