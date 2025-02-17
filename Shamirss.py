from Polynomials import Polynomio
from field_operations import Field

class SecretShare:
    """
    Representa una parte de un secreto en el esquema de Shamir.

    Atributos:
    -----------
    indice : int
        Índice de la parte del secreto.
    valor : Field
        Valor de la parte del secreto en el campo finito.
    """
    def __init__(self, indice: int, valor: Field):
        self.indice = indice
        self.valor = valor

    def __str__(self):
        return f"({self.indice}, {self.valor})"
    
    def __eq__(self, value):
        return self.indice == value.indice and self.valor == value.valor


class ShamirSecretSharing:
    """
    Implementación del esquema de compartición de secretos de Shamir.

    Atributos:
    -----------
    prime : int
        Número primo utilizado para las operaciones en el campo finito.
    secret : Field
        Secreto a compartir.
    num_shares : int
        Número total de partes generadas.

    Métodos:
    --------
    __init__(secret: Field, num_shares: int):
        Inicializa la instancia con el número primo, el secreto y el número de partes.

    generate_shares(t: int) -> list[SecretShare]:
        Genera las partes del secreto usando un polinomio aleatorio de grado t-1, a través de evaluaciones en el campo primo.
    
    recuperar_secreto(shares: list[SecretShare], primo: int) -> Field:
        Recupera el secreto mediante interpolación de Lagrange en un campo finito.
    """
    def __init__(self, secret: Field, num_shares: int):
        self.secret = secret
        self.num_shares = num_shares

    def generate_shares(self, t: int) -> list[SecretShare]:
        """
        Genera las partes del secreto utilizando un polinomio aleatorio de grado t-1.
        
        Parámetros:
        -----------
        t : int
            Número mínimo de partes necesarias para reconstruir el secreto.
        
        Retorna:
        --------
        list[SecretShare]
            Lista de partes del secreto generadas.
        """
        shares = []
        coeficientes_polinomio = Polynomio.random(t, self.secret)
        for i in range(1, self.num_shares + 1):
            shares.append(SecretShare(indice=i, valor=coeficientes_polinomio.eval(Field(i, self.secret.mod))))
        
        print(f"Shares generados bajo el polinomio: {coeficientes_polinomio}")
        return shares
    
    def __str__(self):
        return f"ShamirSecretSharing(prime={self.prime}, secret={self.secret}, num_shares={self.num_shares})"
    
    @staticmethod
    def recuperar_secreto(shares: list[SecretShare]) -> Field:
        """
        Recupera el secreto mediante interpolación de Lagrange en un campo finito.
        
        Parámetros:
        -----------
        shares : list[SecretShare]
            Lista de partes del secreto.
        
        Retorna:
        --------
        Field
            Secreto recuperado (f(0) mod primo).
        """

        primo = shares[0].valor.mod
        secret = Field(0, primo)

        for i in range(len(shares)):
            xi, yi = shares[i].indice, shares[i].valor
            li = Field(1, primo)

            for j in range(len(shares)):
                if i == j:
                    continue
                xj = shares[j].indice
                numerador = Field(0 - xj, primo)  # (x - xj), con x=0
                denominador = Field(xi - xj, primo)  # (xi - xj)
                li = li * numerador * denominador.inverse()

            secret = secret + yi * li  # Acumulación en módulo primo

        return secret
