# Explicacion Proyecto

Este proyecto tiene como objetivo implementar un protocolo de comunicación seguro que permite a n partes calcular conjuntamente una función (en este caso, el producto de números privados) sin revelar sus datos individuales. 

Las operaciones se realizan en un campo primo finito Zp, utilizando primos de Mersenne para optimizar la eficiencia de las operaciones modulares. El protocolo se basa en el esquema de Shamir Secret Sharing, donde cada parte genera y distribuye acciones (shares) de su dato privado, y posteriormente se reconstruye el secreto (el producto final) mediante interpolación de Lagrange.

Además, se simula una red P2P para modelar la comunicación entre las partes, permitiendo la transmisión segura de las acciones. 


# Funcionamiento del programa
**Creación de Usuarios y Conexión**
- Se crean múltiples usuarios que se conectan entre sí en una red P2P simulada.
- Cada usuario tiene un identificador único y comparte su dirección IP y puerto con los demás.

**Generación de Acciones (Shares)**
- Cada usuario genera un secreto (un número en el campo primo Zp).
- Utiliza el esquema de Shamir para generar acciones (shares) del secreto.
- Las acciones se distribuyen entre los demás usuarios.

**Reconstrucción del Secreto**
- Utilizando la interpolación de Lagrange para reconstruir el secreto a partir de las acciones recibidas.
- El secreto se reconstruye evaluando el polinomio interpolado en x=0.

**Operaciones en la Red**
- Los usuarios se comunican mediante protocolos de red.
- Cada protocolo maneja un tipo específico de mensaje (solicitud de conexión, envío de acciones, etc.).
  
# Estructura del codigo

## Estructura General del Programa
El programa está organizado en varios módulos y clases que trabajan juntos para implementar el protocolo de compartición de secretos. Los componentes principales son:

**Campo Finito (Zp):**
- Implementado en la clase Field.
- Realiza operaciones aritméticas (suma, resta, multiplicación, potenciación, inverso) en un campo primo finito.

**Esquema de Shamir:**
- Implementado en la clase ShamirSecretSharing.
- Genera acciones (shares) de un secreto y permite reconstruirlo mediante interpolación de Lagrange.

**Interpolación de Lagrange:**
- Implementada en la función lagrange_interpolation.
- Reconstruye el secreto a partir de las acciones generadas.

**Simulación de Red P2P:**
- Implementada en las clases MainUser, NetworkUser, y protocolos de red (NetworkProtocol, RequestConnectionProtocol, etc.).
- Simula una red entre múltiples usuarios para compartir acciones de manera segura.

**Pruebas y Ejecución:**
- Implementado en el archivo principal (main.py).
- Permite crear usuarios, conectarlos, compartir secretos y reconstruirlos.
  
## Clases Principales
  
**Field:**
- Representa un número en un campo primo finito Zp.
- Implementa operaciones aritméticas y cálculo de inversos.

**ShamirSecretSharing:**
- Implementa el esquema de Shamir.
- Genera acciones (shares) y reconstruye el secreto.

**Polynomio:**
- Representa un polinomio en el campo finito.
- Se utiliza para generar acciones en el esquema de Shamir.

**MainUser:**
- Representa un usuario en la red.
- Maneja la conexión con otros usuarios, el envío y recepción de acciones, y la reconstrucción del secreto.

**NetworkProtocol:**
- Clase base para los protocolos de red.
- Define métodos para enviar y recibir mensajes.

**SharedVariable:**
- Representa una acción (share) de un secreto.
- Contiene el valor de la acción, su índice y un identificador único.

## Protocolos de Red
**RequestConnectionProtocol:**
- Maneja las solicitudes de conexión entre usuarios.

**InputShareProtocol:**
- Maneja el envío y recepción de acciones de entrada.

**ProductShareProtocol:**
- Maneja el envío y recepción de acciones de productos (multiplicaciones).

**FinalShareProtocol:**
- Maneja el envío y recepción de acciones finales (resultado de las operaciones).

## Funciones Clave
**lagrange_interpolation:**
- Reconstruye el secreto a partir de las acciones utilizando interpolación de Lagrange.

**generate_shares:**
- Genera acciones (shares) de un secreto utilizando un polinomio aleatorio.

**recuperar_secreto:**
- Reconstruye el secreto a partir de las acciones utilizando interpolación de Lagrange.

**send_number:**
- Envía un número (secreto o acción) a los demás usuarios utilizando un protocolo específico.
