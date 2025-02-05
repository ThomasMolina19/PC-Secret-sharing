import random
from field_operations import Field

class Polynomio:
    """
    Clase que representa un polinomio.

    Atributos:
    ----------
    coefs : list[int]
        Lista de coeficientes del polinomio.

    Métodos:
    --------
    __init__(coefs: list[int]):
        Inicializa el polinomio con una lista de coeficientes.
    
    random(t: int, secret: int) -> 'Polynomio':
        Genera un polinomio aleatorio de grado t, con el valor 'secret' en la posición 0.
    
    eval(x: int) -> int:
        Evalúa el polinomio en el valor x.
    
    __str__() -> str:
        Devuelve una representación en cadena del polinomio.
    """
    def __init__(self, coefs: list[Field]):
        self.coefs = coefs

    '''
    Genera un polinomio aleatorio de grado degree, con el valor x en la posición 0
    De esta forma, el polinomio es de la forma p(x) = x + a_1x + a_2x^2 + ... + a_nx^n
    '''
    @staticmethod
    def random(t: int, secret: Field) -> 'Polynomio':
        coefs = [Field.random(secret.mod) for _ in range(t + 1)]
        coefs[0] = secret
        return Polynomio(coefs)

    def eval(self, x: Field) -> Field:
        mod = self.coefs[0].mod

        result = Field(0, mod)
        x_power = Field(1, mod)
        for coef in self.coefs:
            result += coef * x_power
            x_power *= x
        return result

    def __str__(self):
        terms = []
        for i, coef in enumerate(self.coefs):
            terms.append(f"{coef}x^{i}")
        return " + ".join(terms)