import uuid as UUID
from field_operations import Field
import NetworkUser

class SharedVariable:
    """
    Clase que representa a una variable distribuida por la red.
    Almacena el valor de la variable, el UUID del emisor y un identificador único que la representa en la red.

    Args:
        value (Field): Valor de la variable.
        sender (str): UUID del emisor.
        uuid (str, optional): Identificador único de la variable. Defaults to None.
    """
    def __init__(self, value: Field, sender: str, uuid: str | None = None):
        if uuid is None:
            uuid = str(UUID.uuid4())
        self.value = value
        self.sender = sender
        self.uuid = uuid

    def __str__(self):
        return f"{self.value}"
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, SharedVariable):
            return False
        return self.value == value.value and self.sender == value.sender
    
class MultiplicationVariable(SharedVariable):
    """
    Clase que representa a una variable distribuida por la red que ha sido multiplicada.
    Almacena el valor de la variable, el UUID del emisor, un identificador único que la representa en la red y el índice de la operación.
    """
    def __init__(self, variable: SharedVariable, operation_index: int = 0):
        super().__init__(variable.value, variable.sender, variable.uuid)
        self.operation_index = operation_index

    def __str__(self):
        return super().__str__() + f" [{self.sender}]"

class Multiplication:
    @staticmethod
    def generate_next_multiplication(user: "NetworkUser.MainUser", multiplication_results: list[Field], input_shares: list[SharedVariable], index: int) -> Field:
        """
        Genera la siguiente multiplicación en la cadena de operaciones.

        Si es la primera multiplicación, se toman los dos primeros valores de input_shares.
        En caso contrario, se toma el resultado de la multiplicación previa y el siguiente valor de input_shares.

        Args:
            user (NetworkUser.MainUser): Usuario que realiza la operación.
            multiplication_results (list[Field]): Resultados de las multiplicaciones previas.
            input_shares (list[SharedVariable]): Variables de entrada.
            index (int): Índice de la operación.
        """
        # Step 1: Each party performs local multiplication on their first two shares
        a =  input_shares[0].value  if index == 0 else multiplication_results[-1]
        b =  input_shares[1].value  if index == 0 else input_shares[index + 1].value

        product = a * b
        return product

