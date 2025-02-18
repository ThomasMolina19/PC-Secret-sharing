import random

class Field:
    """
    Representa un campo finito \(\mathbb{Z}_m\), donde los cálculos se realizan módulo un número \(m\).
    """
    
    def __init__(self, value: int, mod: int):
        """
        Inicializa una instancia de la clase Field.

        Parameters:
        value (int): El valor en el campo.
        mod (int): El módulo del campo.
        """
        self.value = value % mod  # Asegura que el valor esté en el rango [0, mod-1]
        self.mod = mod  # Establece el módulo del campo

    def __add__(self, other):
        """
        Suma dos instancias de Field. El resultado es otro Field con el valor de la suma módulo el módulo del campo.

        Parameters:
        other (Field): El otro campo con el cual sumar.

        Returns:
        Field: Una nueva instancia de Field con el resultado de la suma.
        
        Raises:
        TypeError: Si el objeto con el que se intenta sumar no es una instancia de Field.
        """
        if isinstance(other, Field):
            return Field(self.value + other.value, self.mod)
        raise TypeError("No se puede sumar un campo con algo que no sea un campo")

    def __sub__(self, other):
        """
        Resta dos instancias de Field. El resultado es otro Field con el valor de la resta módulo el módulo del campo.

        Parameters:
        other (Field): El otro campo con el cual restar.

        Returns:
        Field: Una nueva instancia de Field con el resultado de la resta.

        Raises:
        TypeError: Si el objeto con el que se intenta restar no es una instancia de Field.
        """
        if isinstance(other, Field):
            return Field(self.value - other.value, self.mod)
        raise TypeError("No se puede restar un campo con algo que no sea un campo")

    def __mul__(self, other):
        """
        Multiplica dos instancias de Field. El resultado es otro Field con el valor de la multiplicación módulo el módulo del campo.

        Parameters:
        other (Field): El otro campo con el cual multiplicar.

        Returns:
        Field: Una nueva instancia de Field con el resultado de la multiplicación.

        Raises:
        TypeError: Si el objeto con el que se intenta multiplicar no es una instancia de Field.
        """
        if isinstance(other, Field):
            return Field(self.value * other.value, self.mod)
        raise TypeError("No se puede multiplicar un campo con algo que no sea un campo")

    def __pow__(self, other):
        """
        Eleva una instancia de Field a la potencia de otro Field. El resultado es otro Field con el valor de la potenciación módulo el módulo del campo.

        Parameters:
        other (Field): El otro campo con el cual elevar a la potencia.

        Returns:
        Field: Una nueva instancia de Field con el resultado de la potenciación.

        Raises:
        TypeError: Si el objeto con el que se intenta elevar no es una instancia de Field.
        """
        if isinstance(other, Field):
            return Field(pow(self.value, other.value, self.mod), self.mod)
        raise TypeError("No se puede elevar un campo con algo que no sea un campo")

    def __eq__(self, other):
        """
        Compara dos instancias de Field para ver si son iguales.

        Parameters:
        other (Field): El otro campo a comparar.

        Returns:
        bool: True si los campos son iguales (tienen el mismo valor y módulo), False de lo contrario.
        """
        if isinstance(other, Field):
            return self.value == other.value and self.mod == other.mod
        return False

    def inverse(self):
        """
        Calcula el inverso multiplicativo de un campo dentro de su módulo. Utiliza el algoritmo de Euclides extendido.

        Returns:
        Field: Una nueva instancia de Field con el inverso multiplicativo del campo.
        """
        return Field(pow(self.value, self.mod - 2, self.mod), self.mod)

    def __str__(self):
        """
        Representación en cadena de la instancia de Field. Muestra el valor y el módulo.

        Returns:
        str: Representación en cadena de la instancia de Field.
        """
        return str(self.value) + " (mod " + str(self.mod) + ")"

    @staticmethod
    def random(mod: int):
        """
        Genera un número aleatorio en el campo \(\mathbb{Z}_m\).

        Parameters:
        mod (int): El módulo del campo.

        Returns:
        Field: Una nueva instancia de Field con un valor aleatorio en el rango [0, mod-1].
        """
        return Field(random.randint(0, mod - 1), mod)

