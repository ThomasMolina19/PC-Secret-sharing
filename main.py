from field_operations import Field
from Polynomials import Polynomio
from Shamirss import ShamirSecretSharing


# a=Field(3, 7)
# b=Field(9, 7)
# c=a+b
# print(c)
# print(b)

# j = 11  # Elegimos un primo, por ejemplo, 7, para trabajar en Z7

# # Creamos un polinomio aleatorio de grado 3 en Z7
# polinomio = Polynomio.random(t=3, p=j)
# print("Polinomio en Z7:")
# print(polinomio)

# # Evaluamos el polinomio en x=2
# x = 2
# resultado = polinomio.eval(x)
# print(f"El polinomio evaluado en x={x} es {resultado}")

p1 = ShamirSecretSharing(11, 7, 5)

print(p1.generate_shares(2))

