from field_operations import Field
from Polynomials import Polynomio
from Shamirss import ShamirSecretSharing
from Lagrange import lagrange_interpolation
from Party import Party

def secure_multiplication(shares_a, shares_b, prime, num_parties):

    # Step 2: Generate secret shares for each party
    party_shares = {f"p_{i}": [shares_a[i-1],shares_b[i-1]] for i in range(1, num_parties + 1)}
    # print(party_shares)

    # Step 3: Local multiplication of shares
    local_products = [Field(share[0] * share[1], prime).value for share in party_shares.values()]
    # print(f"Local multiplications: {local_products}")

    # Step 4: Secret sharing of the multiplication result
    for i, partial_product in enumerate(local_products):
        shamir = ShamirSecretSharing(prime, partial_product, num_parties)
        party_shares[f"p_{i+1}"] = shamir.generate_shares(1)
    # print(party_shares)
    
    # Step 5: Securely send shares between parties
    party_shares = Party.send(party_shares)
    # print(f"Updated party shares after redistribution: {party_shares}")

    ProductoFragmentado = []
    for fragmentos in (party_shares.values()):
        LagrangeParcial = [(i+1,fragmento) for i, fragmento in enumerate(fragmentos)]
        ProductoFragmentado.append(lagrange_interpolation(LagrangeParcial,prime).value)

    return ProductoFragmentado

