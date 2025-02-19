from Polynomials import Polynomio
from field_operations import Field

class ShamirSecretSharing:
    """
    Clase para implementar el esquema de compartición de secretos de Shamir.

    Atributos:
    -----------
    prime : int
        Un número primo utilizado para las operaciones en el campo finito.
    secret : int
        El secreto que se desea compartir.
    num_shares : int
        El número total de partes (shares) que se generarán.

    Métodos:
    --------
    __init__(self, prime, secret, num_shares):
        Inicializa una instancia de la clase con el número primo, el secreto y el número de partes.

    generate_shares(self, t):
        Genera las partes del secreto utilizando un polinomio aleatorio de grado t-1.
        
        Parámetros:
        -----------
        t : int
            El número mínimo de partes necesarias para reconstruir el secreto.
        
        Retorna:
        --------
        list
            Una lista de partes del secreto.
    """
    def __init__(self, prime, secret, num_shares):
        self.prime = prime
        self.secret = secret
        self.num_shares = num_shares

    def generate_shares(self, t):
        if t < self.num_shares:
            s_i = []
            coeficientes_polinomio = Polynomio.random(t, self.secret, self.prime)
            for i in range(1, self.num_shares + 1):
                s_i.append(coeficientes_polinomio.eval(i))
            print(coeficientes_polinomio)
            for i in range(0, self.num_shares):
                s_i[i]=Field(int(s_i[i]), self.prime).value
            return s_i
        else:
            raise ValueError("El valor de t debe ser menor o igual que el número total de partes")

