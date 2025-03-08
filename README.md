# Explicación del Proyecto

Este proyecto tiene como objetivo implementar un protocolo de comunicación seguro que permite a *n* partes calcular conjuntamente una función (en este caso, el producto de números privados) sin revelar sus datos individuales.

Las operaciones se realizan en un campo primo \( \mathbb{Z}_p \), utilizando primos de Mersenne para optimizar la eficiencia de las operaciones. El protocolo se basa en *Secure Multiparty Computation (MPC)* y *Secret Sharing*, donde cada parte genera y distribuye fragmentos (*shares*) de su dato privado, y posteriormente se reconstruye el secreto (el producto final) mediante interpolación de Lagrange.

Además, se utiliza una simulación local con objetos y también una red P2P para modelar la comunicación entre las partes, permitiendo la transmisión segura de las acciones.

---

## 🛠 Instalación y Dependencias de la Simulación 

Para ejecutar la simulación, solo necesitas tener **Python** instalado y contar con un archivo `.txt` que albergará los números que serán multiplicados.

---

## 🛠 Instalación y Dependencias de la Red

Para ejecutar el proyecto, necesitas tener **Python** instalado y contar con los siguientes archivos:

- Un archivo JSON (`config.json`) con las direcciones IP y los puertos de la red.
- Un certificado SSL (`cert.pem`) y una clave privada (`key.pem`) para la comunicación segura.
- Módulos de Python como `socket`, `uuid`, `ssl` y `json`.

---

## 🚀 Ejemplo de Uso de la Simulación

Ejecuta el programa con los siguientes parámetros:

```bash
python3 main.py -f "archivo.txt"
```

Para una guía más detallada sobre la ejecución del proyecto, consulta el siguiente documento dentro del repositorio:

[Guía de Ejecución](./Guia_de_Usuario.pdf))

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

- **Modelo de amenaza**: El protocolo asume que hay jugadores honestos; si un atacante controla más de *t* partes, puede reconstruir el secreto.
- **Eficiencia**: El uso de primos de Mersenne optimiza los cálculos, pero la sobrecarga de comunicación P2P puede ser alta en redes grandes.

---

## 📚 Referencias y Créditos

- [Secure Multiparty Computation (MPC)](https://g.co/kgs/gPa7VQn)

---


