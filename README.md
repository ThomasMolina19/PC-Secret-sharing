# Explicacion Proyecto

Este proyecto tiene como objetivo implementar un protocolo de comunicación seguro que permite a n partes calcular conjuntamente una función (en este caso, el producto de números privados) sin revelar sus datos individuales. 

Las operaciones se realizan en un campo primo finito Zp, utilizando primos de Mersenne para optimizar la eficiencia de las operaciones modulares. El protocolo se basa en el esquema de Shamir Secret Sharing, donde cada parte genera y distribuye acciones (shares) de su dato privado, y posteriormente se reconstruye el secreto (el producto final) mediante interpolación de Lagrange.

Además, se utiliza una red P2P para modelar la comunicación entre las partes, permitiendo la transmisión segura de las acciones. 

# Estructura del código
El código está organizado en varios módulos y clases que trabajan juntos para implementar el protocolo de compartición de secretos y la multiplicación segura. Aquí hay una descripción de los componentes principales:

**Field:**
- Representa un campo finito Zp, donde los cálculos se realizan módulo un número p.
- Implementa operaciones básicas como suma, resta, multiplicación, potenciación y cálculo del inverso multiplicativo.

**Polynomio:**
- Representa un polinomio con coeficientes en un campo finito.
- Permite generar polinomios aleatorios y evaluarlos en un punto específico.

**ShamirSecretSharing:**
- Implementa el esquema de compartición de secretos de Shamir.
- Genera "shares" (partes del secreto) utilizando un polinomio aleatorio.
- Reconstruye el secreto a partir de las partes utilizando la interpolación de Lagrange.

**Party:**
- Representa a una "parte" o "jugador" en el protocolo.
- Almacena el ID del jugador y sus "shares" (fragmentos del secreto).
- Proporciona un método para redistribuir los "shares" entre los jugadores.

**Protocol:**
- Es la clase principal que ejecuta el protocolo de compartición de secretos y la multiplicación segura.
- Utiliza ShamirSecretSharing para generar los "shares" y secure_multiplication_reorganized para realizar la multiplicación segura.

**secure_multiplication_reorganized:**

- Implementa la multiplicación segura entre las partes.
- Cada parte realiza una multiplicación local de sus "shares" y luego comparte el resultado con las otras partes.
- Utiliza la interpolación de Lagrange para reconstruir el resultado final.

**lagrange_interpolation:**
- Implementa la interpolación de Lagrange para reconstruir el secreto a partir de los "shares".

**main.py:**
- Es el punto de entrada del programa.
- Lee un archivo de entrada con valores, los convierte en enteros y ejecuta el protocolo de compartición de secretos y multiplicación segura.

# Funcionamiento del programa
El programa sigue estos pasos generales:

**Lectura del archivo de entrada:**

- El programa lee un archivo de texto que contiene valores numéricos.
- Estos valores se convierten en enteros y se utilizan como los secretos iniciales.

**Inicialización del protocolo:**

- Se crea una instancia de la clase Protocol con un campo primo y el número de jugadores.
- Los valores leídos del archivo se utilizan como los secretos de cada jugador.

**Generación de "shares":**
- Cada jugador genera "shares" de su secreto utilizando el esquema de Shamir Secret Sharing.
- Estos "shares" se distribuyen entre los otros jugadores.

**Multiplicación segura:**
- Cada jugador realiza una multiplicación local de sus "shares".
- Luego, comparte el resultado de la multiplicación con los otros jugadores.
- Finalmente, se utiliza la interpolación de Lagrange para reconstruir el resultado final.

**Reconstrucción del secreto:**
- El programa reconstruye el secreto a partir de los "shares" utilizando la interpolación de Lagrange.

# Flujo de ejecución
**Lectura del archivo:**
- El programa lee un archivo de texto que contiene valores numéricos.
- Estos valores se convierten en enteros y se almacenan en una lista.

**Inicialización del protocolo:**
- Se crea una instancia de la clase Protocol con un campo primo y el número de jugadores.
- Los valores leídos del archivo se utilizan como los secretos de cada jugador.

**Generación de "shares":**
- Cada jugador genera "shares" de su secreto utilizando el esquema de Shamir Secret Sharing.
- Estos "shares" se distribuyen entre los otros jugadores.

**Multiplicación segura:**
- Cada jugador realiza una multiplicación local de sus "shares".
- Luego, comparte el resultado de la multiplicación con los otros jugadores.
- Finalmente, se utiliza la interpolación de Lagrange para reconstruir el resultado final.

**Reconstrucción del secreto:**
- El programa reconstruye el secreto a partir de los "shares" utilizando la interpolación de Lagrange.

# Detalles clave
**Seguridad:**
- El programa utiliza el esquema de Shamir Secret Sharing para garantizar que solo un subconjunto específico de partes puede reconstruir el secreto.
- La multiplicación segura se realiza de manera distribuida, lo que garantiza que ningún jugador tenga acceso completo al secreto.

**Concurrencia:**

El programa no utiliza hilos o concurrencia explícita, pero está diseñado para ser ejecutado en un entorno distribuido donde cada jugador es una entidad independiente.

**Interfaz de consola:**
- El programa incluye una interfaz de consola para interactuar con el sistema.

- Permite leer un archivo de entrada, ejecutar el protocolo y mostrar los resultados.
