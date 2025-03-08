# Explicación del Proyecto

Este proyecto tiene como objetivo implementar un protocolo de comunicación seguro que permite a *n* partes calcular conjuntamente una función (en este caso, el producto de números privados) sin revelar sus datos individuales.

Las operaciones se realizan en un campo primo \(Z_p\), utilizando primos de Mersenne para optimizar la eficiencia de las operaciones. El protocolo se basa en *Secure Multiparty Computation (MPC)* y *Secret Sharing*, donde cada parte genera y distribuye fragmentos (*shares*) de su dato privado, y posteriormente se reconstruye el secreto (el producto final) mediante interpolación de Lagrange.

Además, se utiliza una simulacion local con objetos y tambien una red P2P para modelar la comunicación entre las partes, permitiendo la transmisión segura de las acciones.

---

## 🛠 Instalación y Dependencias de la Simulacion 

Para ejecutar la simulacion, solo necesitas tener **Python** instalado y contar con un archivo .txt que albergara los numeros que seran multiplicados

---


## 🛠 Instalación y Dependencias de la Red

Para ejecutar el proyecto, necesitas tener **Python** instalado y contar con los siguientes archivos:

- Un archivo JSON (`config.json`) con las direcciones IP y los puertos de la red.
- Un certificado SSL (cert.pem) y una clave privada (key.pem) para la comunicacíon segura.
- Modulos de python como socket, uuid, ssl y json. 

---

## 🚀 Ejemplo de Uso de la simulacion

Ejecuta el programa con los siguientes parámetros:

```bash
python3 main.py -f ”archivo.txt”
```

---

## 🔍 Explicación Técnica

### **Shamir Secret Sharing**
Este protocolo divide un secreto en múltiples fragmentos (*shares*) y distribuye cada uno a diferentes jugadores. Solo un subconjunto suficiente de ellos puede reconstruir el secreto original.

### **Interpolación de Lagrange**
Se usa para reconstruir un polinomio a partir de sus puntos conocidos, permitiendo recuperar el secreto después de las operaciones.

### **Comunicación P2P**
Cada jugador intercambia mensajes con los demás a través de una red P2P, asegurando que las operaciones sean seguras y descentralizadas.

---

## ⚠️ Seguridad y Limitaciones

- **Modelo de amenaza**: El protocolo asume que hay jugadores son honestos; si un atacante controla más de *t* partes, puede reconstruir el secreto.
- **Eficiencia**: El uso de primos de Mersenne optimiza los cálculos, pero la sobrecarga de comunicación P2P puede ser alta en redes grandes.

---

## 📚 Referencias y Créditos

- [Secure Multiparty Computation (MPC)](https://g.co/kgs/gPa7VQn)

---

