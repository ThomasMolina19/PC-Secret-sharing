# Explicacion Proyecto

Este proyecto tiene como objetivo implementar un protocolo de comunicación seguro que permite a n partes calcular conjuntamente una función (en este caso, el producto de números privados) sin revelar sus datos individuales. 

Las operaciones se realizan en un campo primo finito Zp, utilizando primos de Mersenne para optimizar la eficiencia de las operaciones modulares. El protocolo se basa en el esquema de Shamir Secret Sharing, donde cada parte genera y distribuye acciones (shares) de su dato privado, y posteriormente se reconstruye el secreto (el producto final) mediante interpolación de Lagrange.

Además, se simula una red P2P para modelar la comunicación entre las partes, permitiendo la transmisión segura de las acciones. 

El software desarrollado incluirá pruebas de concepto y mediciones de tiempo de cómputo y uso de la red, lo que permitirá evaluar la eficiencia y escalabilidad del protocolo.

# Funcionamiento del programa
**Creación de Usuarios y Conexión**
- Se crean múltiples usuarios que se conectan entre sí en una red P2P simulada.
- Cada usuario tiene un identificador único y comparte su dirección IP y puerto con los demás.

**Generación de Acciones (Shares)**
- Cada usuario genera un secreto (un número en el campo primo Zp).
- Utiliza el esquema de Shamir para generar acciones (shares) del secreto.
- Las acciones se distribuyen entre los demás usuarios.

**Reconstrucción del Secreto**
- Los usuarios utilizan la interpolación de Lagrange para reconstruir el secreto a partir de las acciones recibidas.
- El secreto se reconstruye evaluando el polinomio interpolado en x=0.

**Operaciones en la Red**
- Los usuarios se comunican mediante protocolos de red.
- Cada protocolo maneja un tipo específico de mensaje (solicitud de conexión, envío de acciones, etc.).
  
# Estructura del codigo
