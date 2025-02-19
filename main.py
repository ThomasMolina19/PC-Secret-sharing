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


    combined_shares = []

    for secret in party:
        y_product = 1
        for i in range(len(party)):
            y_product *= party[secret][i]
        print(y_product)
        combined_shares.append(Field(y_product,prime).value)
    combined_shares = [ShamirSecretSharing(prime,i,number_players).generate_shares(number_players-1) for i in combined_shares ]

    print(combined_shares)

    final_shares= []
    for j in range(len(combined_shares)):
        y_sum = 0
        for i in range(len(combined_shares)):
            y_sum += combined_shares[i][j]
        # print(y_sum)
        final_shares.append((j+1,Field(y_sum,prime).value))
    print(final_shares)
    print(lagrange_interpolation(final_shares,prime))


final_secret = lagrange_interpolation(final_shares, prime)
print(final_secret)
