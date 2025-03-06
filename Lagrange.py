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
