import uuid as UUID
from field_operations import Field
import NetworkUser
import Shamirss

class SharedVariable:
    def __init__(self, value: Field, index: int, uuid: str | None = None):
        if uuid is None:
            uuid = str(UUID.uuid4())
        self.value = value
        self.index = index
        self.uuid = uuid

    def __str__(self):
        return f"[{self.uuid} from {str(self.index)}] = {self.value}"

class MultiplicationGate():
    def __init__(self, mainUser: "NetworkUser.MainUser", index: int) -> None:
        self.mainUser: "NetworkUser.MainUser" = mainUser
        a: Field | None = mainUser.input_shares[index].value if index == 0 else mainUser.multiplication_gates[index - 1].real_value
        b: Field | None = mainUser.input_shares[index + 1].value
        if a is None or b is None:
            raise Exception(f"No se puede multiplicar sin el valor de: a={a} o b={b}")
        self.variables: tuple[Field, Field] = (a, b)
        self.shares: list[SharedVariable] = []
        self.real_value: Field | None = None
        self.index = index

    def addShare(self, variable: "SharedVariable"):
        self.shares.append(variable)
        if (len(self.shares) > self.mainUser.t):
            self.mainUser.log("Shares: " + ", ".join([str(var) for var in self.shares]))
            self.real_value = Shamirss.ShamirSecretSharing.recuperar_secreto(self.shares)

    def __str__(self) -> str:
        return f"MultiplicationGate({self.index}) = {self.real_value} from: " + ", ".join([str(var) for var in self.variables])