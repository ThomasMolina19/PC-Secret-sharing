import random

q = 11  # Field size
n = 3  # Number of parties

# Example secrets
secrets = [3,4,5]

# Evaluation points (1 to n)
points = list(range(1, n + 1))

# Generate random polynomials for each secret (degree n - 1)
polynomials = {}
for i in range(n):
    coefficients = [secrets[i]] + [random.randint(0, q - 1) for _ in range(n - 1)]
    polynomials[i] = coefficients

# Evaluate each polynomial at the evaluation points
shares = {i: [] for i in points}
for i in range(n):
    for x in points:
        poly_val = sum(polynomials[i][j] * (x ** j) for j in range(n)) % q
        shares[x].append(poly_val)

# Each party multiplies their shares locally
local_products = {i: 1 for i in points}
for i in points:
    for share in shares[i]:
        local_products[i] = (local_products[i] * share) % q

# Degree reduction: Reshare the local product shares using polynomials of degree n - 1
reshare_polynomials = {}
for i in points:
    coefficients = [local_products[i]] + [random.randint(0, q - 1) for _ in range(n - 1)]
    reshare_polynomials[i] = coefficients

# Evaluate the reshared polynomials at the evaluation points
final_shares = {i: 0 for i in points}
for i in points:
    for x in points:
        poly_val = sum(reshare_polynomials[i][j] * (x ** j) for j in range(n)) % q
        final_shares[x] = (final_shares[x] + poly_val) % q

# Modular inverse function
def mod_inverse(a, m):
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

# Lagrange interpolation at x = 0
def lagrange_interpolation(x_values, y_values, x_at, q):
    result = 0
    n = len(x_values)
    for i in range(n):
        xi, yi = x_values[i], y_values[i]
        term = yi
        for j in range(n):
            if i != j:
                xj = x_values[j]
                num = (x_at - xj) % q
                denom = (xi - xj) % q
                denom_inv = mod_inverse(denom, q)
                term = (term * num * denom_inv) % q
        result = (result + term) % q
    return result

# Reconstruct the product
result = lagrange_interpolation(points, list(final_shares.values()), 0, q)

print("Final Result (Product of secrets):", result)
expected_product = 1
for secret in secrets:
    expected_product = (expected_product * secret) % q
print("Expected result:", expected_product)