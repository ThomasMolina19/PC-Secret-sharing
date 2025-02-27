import uuid as UUID

from field_operations import Field

class SharedVariable:
    def __init__(self, value: Field, sender: str, uuid: str | None = None):
        if uuid is None:
            uuid = str(UUID.uuid4())
        self.value = value
        self.sender = sender
        self.uuid = uuid

    @property
    def polynomial(self):
        pass

    def __str__(self):
        return f"[{self.uuid} from {self.sender}] = {self.value}"

class MultiplicationVariable(SharedVariable):
    def __init__(self, value: Field, sender: str, indice: int):
        super().__init__(value, sender, None)
        self.indice = indice