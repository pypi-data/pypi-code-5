"""
My personal mixed bag library

jmrod4 2014-05-10

Shell command to execute the tests:
import doctest; doctest.testmod()
"""



def convertir_temperatura(temp, orig, dest):
    """ (number, str, str) -> float
    Devuelve la temperatura t convertida desde unidades orig a unidades dest
    Unidades: "Kelvin", "Celsius", "Fahrenheit", "Rankine", "Delisle",
              "Reaumur", "Romer", "Newton"

    >>> convertir_temperatura(313.15, "Kelvin", "Celsius")
    40.0
    >>> convertir_temperatura(40, "Celsius", "Fahrenheit")
    104.0
    >>> convertir_temperatura(104, "Fahrenheit", "Rankine")
    563.6700000000001
    >>> convertir_temperatura(563.67, "Rankine", "Delisle")
    90.00000000000004
    >>> convertir_temperatura(90, "Delisle", "Reaumur")
    32.0
    >>> convertir_temperatura(32, "Reaumur", "Romer")
    28.5
    >>> convertir_temperatura(28.5, "Romer", "Newton")
    13.2
    >>> convertir_temperatura(13.2, "Newton", "Kelvin")
    313.15
    """
    # convertir la unidad origen a celsius
    if orig == "Kelvin":
        celsius = temp - 273.15 
    elif orig == "Celsius":
        celsius = temp
    elif orig == "Fahrenheit":
        celsius = (temp - 32)*5/9
    elif orig == "Rankine":
        celsius = (temp - 491.67)*5/9
    elif orig == "Delisle":
        celsius = 100 - temp*2/3
    elif orig == "Reaumur":
        celsius = temp*5/4
    elif orig == "Romer":
        celsius = (temp - 7.5)*40/21       
    elif orig == "Newton":
        celsius = temp*100/33
    else:
        raise RuntimeError("Escala de temperatura origen desconocida")

    # convertir celsius a la unidad de destino
    if dest == "Kelvin":
        res = celsius + 273.15
    elif dest == "Celsius":
        res = celsius
    elif dest == "Fahrenheit":
        res = celsius*9/5 + 32
    elif dest == "Rankine":
        res = celsius*9/5 + 491.67
    elif dest == "Delisle":
        res = (100 - celsius)*3/2
    elif dest == "Reaumur":
        res = celsius*4/5
    elif dest == "Romer":
        res = celsius*21/40 + 7.5
    elif dest == "Newton":
        res = celsius*33/100
    else:
        raise RuntimeError("Escala de temperatura destino desconocida")
    
    return(res)


import sys

def print_flat_list(the_list, indent=False, level=0, file=sys.stdout):
    """Prints the_list to a file, flattening nested lists and indenting
    as specified

    indent: to indent or not to indent, default False
    level: number of tab stops to use for indenting the root list, default 0
    file: a file object open for writing, default stdout"""
    for item in the_list:
        if isinstance(item, list):
            print_flat_list(item, indent, level+1, file)
        else:
            if indent:
                print('\t'*level, end='', file=file)
            print(item, file=file)
