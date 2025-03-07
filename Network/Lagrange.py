from field_operations import Field
import Protocol

def lagrange_interpolation(shares: list["Protocol.SharedVariable"], required_x = 0) -> Field:
        """
        Interpolación de Lagrange para recuperar el secreto a partir de los shares.

        Obtiene el x-ésimo valor de la interpolación de Lagrange a partir de los shares.
        Supone que los shares está ordenados de 1 a n.

        :param shares: Lista de shares.
        :param required_x: Valor de x para el que se quiere recuperar el secreto.
        :return: El secreto recuperado.
        """
        primo = shares[0].value.mod
        secret = Field(0, primo)

        for i in range(len(shares)):
            xi, yi = i + 1, shares[i].value
            li = Field(1, primo)

            for j in range(len(shares)):
                if i == j:
                    continue
                xj = j + 1
                numerador = Field(required_x - xj, primo)  # (x - xj)
                denominador = Field(xi - xj, primo)  # (xi - xj)
                li = li * numerador * denominador.inverse()

            secret = secret + yi * li  # Acumulación en módulo primo
        return secret