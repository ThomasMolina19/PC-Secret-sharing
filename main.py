from field_operations import Field
from Polynomials import Polynomio
from Shamirss import ShamirSecretSharing


p1 = ShamirSecretSharing(11, 7, 5)

print(p1.generate_shares(2))

