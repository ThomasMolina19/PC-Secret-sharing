from field_operations import Field
from Shamirss import ShamirSecretSharing

def lagrange_interpolation(shares, prime):
    secret = Field(0, prime)
    num_shares = len(shares)

    #Se comienza la sumatoria
    for j in range(num_shares):
        xj, yj = shares[j]

        numerator = Field(1, prime)
        denominator = Field(1, prime)

        #Se comienza la productoria, al evaluarlo directamente en x=0 para obtener el secreto
        for i in range(num_shares):
            if i != j:
                xi, _ = shares[i]
                numerator *= Field(-xi, prime)
                denominator *= Field(xj - xi, prime)

        lj = numerator * denominator.inverse()
        secret += Field(yj, prime) * lj
    return secret

#CASO DE PRUEBA

#Secretos de cada jugador
secrets = [223, 123, 237]
prime = 11
degree = (len(secrets) - 1) // 2


shares = []
for secret in secrets:

    # Generar fragmentos para cada secreto
    polynomial = ShamirSecretSharing(prime, secret, len(secrets) + 1).generate_shares(degree)
    
    #Agregar las parejas (x, f(x)) a la lista de fragmentos, que son la evaluación de x en el polinomio aleatorio
    shares.append([(i + 1, polynomial[i]) for i in range(len(polynomial))])
    print(polynomial)

print("Shares:", shares)

# Combinar fragmentos
combined_shares = []
for i in range(len(shares[0])):
    x_value = shares[0][i][0]
    y_product = 1

    # Multiplicar los valores de y, que tengan el mismo valor de x, para obtener así la multiplicación de los valores de f(x) 
    for j in range(len(secrets)):
        y_product *= shares[j][i][1]
        
    combined_shares.append((x_value, Field(y_product, prime).value))

print("Combined Shares:", combined_shares)

# Reconstruir secretos individuales
for idx, share_set in enumerate(shares):
    secret = lagrange_interpolation(share_set, prime)
    print(f"The reconstructed secret {idx + 1} is: {secret}")

# Reconstruir el secreto combinado
combined_secret = lagrange_interpolation(combined_shares, prime)
print(f"The reconstructed combined secret is: {combined_secret}")
