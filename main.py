from field_operations import Field
from Polynomials import Polynomio
from Shamirss import ShamirSecretSharing
from Lagrange import lagrange_interpolation

if __name__ == "__main__":
    secrets = []
    prime = 11

    #Secretos de cada jugador
    print(f"Ingrese el secreto de cada jugador, y presione 's' para terminar de ingresar secretos. Se trabajará sobre Zp, p= {prime}: ")
    while True:
        try:
            secret = input("Ingrese el número secreto (mod p): ")
            if secret == "s" and len(secrets) > 0:
                break
            elif secret == "s" and len(secrets) == 0:
                print("Ingrese al menos un secreto.")
            else:
                secret = int(secret)
                secrets.append(Field(secret,prime).value)
        except:
            print("Ingrese un número válido.")
    
    polynomial_degree = (len(secrets) - 1) // 2
    
    shares = []
    for secret in secrets:
        # Generar fragmentos para cada secreto
        polynomial = ShamirSecretSharing(prime, secret, len(secrets)).generate_shares(polynomial_degree)
        
        #Agregar las parejas (x, f(x)) a la lista de fragmentos, que son la evaluación de x en el polinomio aleatorio
        shares.append([(i + 1, polynomial[i]) for i in range(len(polynomial))])
        print(polynomial)
    
    print("Fragmentos:", shares)
    
    # Combinar fragmentos
    combined_shares = []
    for i in range(len(shares[0])):
        x_value = shares[0][i][0]
        y_product = 1
    
        # Multiplicar los valores de y, que tengan el mismo valor de x, para obtener así la multiplicación de los valores de f(x) 
        for j in range(len(secrets)):
            y_product *= shares[j][i][1]
            
        combined_shares.append((x_value, Field(y_product, prime).value))
    
    print("Fragmentos combinados:", combined_shares)
    
    # Reconstruir secretos individuales
    for idx, share_set in enumerate(shares):
        secret = lagrange_interpolation(share_set, prime)
        print(f"El secreto reconstruido {idx + 1} es: {secret}")
    
    # Reconstruir el secreto combinado
    combined_secret = lagrange_interpolation(combined_shares, prime)
    print(f"El secreto reconstruido combinado es: {combined_secret}")

