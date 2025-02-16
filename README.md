# Proyecto Secreto Compartido

Este proyecto busca implementar un protocolo de comunicación que permite que n partes
calculen juntos una función usando datos privados sin revelar a las otras partes sus datos.

 Los detalles del protocolo los pueden encontrar por ejemplo en la sección 3.3 del libro
Kramer, Damgaard, Nielsen. Secure Multiparty Computation and Secret Sharing. 2015.

Para este proyecto se propone hacer el protocolo central que permite computar el producto entre n números privados. 

El protocolo asume que se ha establecido una red P2P, aunque en un primer acercamiento, podemos simular la red, y solo implementar los algoritmos que debe llevar a cabo cada parte. 

En una segunda fase de desarrollo se puede usar una librería de SSL para establecer conexiones seguras entre las partes.

Las operaciones se llevan a cabo en un campo primo $Z_p$, y se recomienda usar un primo de Mersenne, para que las operaciones sean más eficientes. 

Sobre dicho campo es necesario implementar interpolación usando polinomios de Lagrange.

El software debe permitir hacer una prueba de concepto, así como mediciones de tiempo de cómputo y de uso de la red.
