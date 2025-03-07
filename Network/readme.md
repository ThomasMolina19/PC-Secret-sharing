# Ejecutar localmente

Clona el repositorio

```bash
  git clone https://github.com/ThomasMolina19/PC-Secret-sharing.git
```

Dirigete al directorio de la red del proyecto

```bash
  cd PC-Secret-sharing/Network
```


## Uso por consola:
Ejecuta el archivo main.py
```bash
python main.py --ip "127.0.0.1" --port "5000"
```
Los argumentos --ip y --port son completamente opcionales. Si no se indican, se le pedira al momento de la ejecución. Además, está la opción de dejarlo en blanco para que el sistema le proporcione una ip y puerto adecuado.

Una vez en la consola dispone de los siguientes comandos:
#### Connect
Usado para conectarse con otros equipos ejecutando el archivo
```bash
connect <IP> <PUERTO>
```

#### Message
Usado para enviar un mensaje en texto plano a todos los equipos conectados
```bash
message <MENSAJE>
```

#### Status
Proporciona información util sobre los usuarios conectados, partes de los secretos que se conocen, las partes de cada etapa de la multipliación y los resultados finales de las mismas
```bash
status
```

#### Number
Usado para indicar el número secreto a multiplicar
```bash
number <NUMERO>
````

#### Multiply
Una vez se hayan enviado todos los números, cada usuario deberá enviar su parte de la multiplicación
```bash
multiply
````
Nota: La multiplicación toma tiempo, se recomienda esperar a que se reciban los shares finales, antes de ejecutar otro comando en la consola

#### Reconstruct
Cuando se hayan obtenido todos los shares finales, se usa reconstruct para obtener a través de interpolación de Lagrange el resultado de la multiplicación
```bash
reconstruct
````

#### Exit
Para cerrar el programa
```bash
exit
```

## Uso por archivo JSON
Ejecuta el archivo main.py mandando cómo argumento el archivo JSON
```bash
main.py --file "ruta/del/archivo/json" --ip "127.0.0.1" --port 5000
```
Al igual que por consola, la ip y el puerto son opcionales. \
El archivo json es de la siguiente forma
```json
        {
            "host": {
                "ip": "ip del host",
                "port": "puerto del host",
                "uuid": "uuid del host"
            },
            "users": [
                {
                    "ip": "ip del usuario",
                    "port": "puerto del usuario",
                    "uuid": "uuid del usuario",
                    "numbers": [ "número 1" ]
                }
            ]
        }
```

Cuando se ejecuta a partir del archivo, el proceso es automatico, dando al final el resultado de la multiplicación. \
Si hay usuarios usando la consola, cómo el archivo, los que estén usando el archivo, esperaran indefinidamente hasta recibir todo lo necesario.