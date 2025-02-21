from field_operations import Field
from Polynomials import Polynomio
from Shamirss import ShamirSecretSharing
from Lagrange import lagrange_interpolation
from Party import Party

if __name__ == "__main__":

    number_players = 3
    prime = 11
    party = (Party(prime, number_players)).generate_party()
    party = Party.send(party) #Combinar los fragmentos de los secretos
    print(party)

    combined_shares = []

    for j, secret in enumerate(party):
        y_product = 1
        for i in range(len(party)):
            y_product *= party[secret][i]
        print(y_product)
        combined_shares.append((j+1,Field(y_product,prime).value))
    print(combined_shares)

final_secret = lagrange_interpolation(combined_shares, prime)
print(final_secret)
