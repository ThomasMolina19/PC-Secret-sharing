from field_operations import Field
import Protocol

def lagrange_interpolation(shares: list["Protocol.SharedVariable"], required_x = 0) -> Field:
        primo = shares[0].value.mod
        secret = Field(0, primo)

        for i in range(len(shares)):
            xi, yi = shares[i].index, shares[i].value
            li = Field(1, primo)

            for j in range(len(shares)):
                if i == j:
                    continue
                xj = shares[j].index
                numerador = Field(required_x - xj, primo)  # (x - xj)
                denominador = Field(xi - xj, primo)  # (xi - xj)
                li = li * numerador * denominador.inverse()

            secret = secret + yi * li  # Acumulación en módulo primo
        return secret