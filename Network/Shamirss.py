from Polynomials import Polynomio
import Protocol
from field_operations import Field

import Lagrange

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

    def generate_shares(self, t: int) -> list[Field]:
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
            shares.append(coeficientes_polinomio.eval(Field(i, self.secret.mod)))
        
        return shares
    
    def __str__(self):
        return f"ShamirSecretSharing(secret={self.secret}, num_shares={self.num_shares})"
    
    @staticmethod
    def recuperar_secreto(shares: list["Protocol.SharedVariable"]) -> Field:
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
        ordered_shares = sorted(shares, key=lambda x: x.sender)
        return Lagrange.lagrange_interpolation(ordered_shares, required_x=0)

        
