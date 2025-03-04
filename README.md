# Explicacion Proyecto

Este proyecto tiene como objetivo implementar un protocolo de comunicación seguro que permite a n partes calcular conjuntamente una función (en este caso, el producto de números privados) sin revelar sus datos individuales. 

Las operaciones se realizan en un campo primo finito Zp, utilizando primos de Mersenne para optimizar la eficiencia de las operaciones modulares. El protocolo se basa en el esquema de Shamir Secret Sharing, donde cada parte genera y distribuye acciones (shares) de su dato privado, y posteriormente se reconstruye el secreto (el producto final) mediante interpolación de Lagrange.

Además, se simula una red P2P para modelar la comunicación entre las partes, permitiendo la transmisión segura de las acciones. 

El software desarrollado incluirá pruebas de concepto y mediciones de tiempo de cómputo y uso de la red, lo que permitirá evaluar la eficiencia y escalabilidad del protocolo.

# Funcionamiento del programa

# Estructura del codigo
