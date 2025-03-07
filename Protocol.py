import uuid as UUID
from field_operations import Field
import NetworkUser
import Shamirss

class SharedVariable:
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
    def __init__(self, variable: SharedVariable, operation_index: int = 0):
        super().__init__(variable.value, variable.sender, variable.uuid)
        self.operation_index = operation_index

    def __str__(self):
        return super().__str__() + f" [{self.sender}]"

class Multiplication:
    @staticmethod
    def generate_next_multiplication(user: "NetworkUser.MainUser", multiplication_results: list[Field], input_shares: list[SharedVariable], index: int) -> Field:
        """
        Securely multiplies shares where party_values[i] contains all the shares that party i+1 has.
        
        Args:
            party_values: List where each element represents all shares held by one party
            prime: Prime number for the finite field
            num_parties: Number of parties
            degree: Degree of the polynomial
        """
        # Step 1: Each party performs local multiplication on their first two shares
        a =  input_shares[0].value  if index == 0 else multiplication_results[-1]
        b =  input_shares[1].value  if index == 0 else input_shares[index + 1].value

        product = a * b
        return product

