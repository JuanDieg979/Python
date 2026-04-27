"""
╔══════════════════════════════════════════════════════════════════════╗
║          ANALIZADOR LÉXICO - LENGUAJE FLYNNS                         ║
║          Extensión de archivos fuente: .isos                         ║
║          Autor: Juan Nava, Fernando Cisneros y Greko Fuentes         ║
║          Versión: 1.0                                                ║
╚══════════════════════════════════════════════════════════════════════╝

DESCRIPCIÓN:
    Este módulo implementa el analizador léxico del lenguaje de
    programación FLYNNS. Su función es leer un archivo fuente con
    extensión .isos y producir:
        - progfte.dep : programa fuente depurado (sin comentarios ni
                        espacios redundantes)
        - progfte.tok : lista completa de tokens reconocidos
        - progfte.tab : tabla de símbolos (identificadores y constantes)

    En caso de encontrar errores léxicos, los reporta indicando la
    línea donde ocurrieron.

USO:
    python flynns.py <archivo_fuente.isos>

EJEMPLO:
    python flynns.py progfte.isos
"""

import sys          # Para leer argumentos de la línea de comandos
import os           # Para manejo de rutas y carpetas

# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 1: DEFINICIÓN DE TOKENS
# ─────────────────────────────────────────────────────────────────────
#
# Cada token se representa como una cadena constante.
# La estructura de un token es: (NOMBRE_TOKEN, atributo)
# donde el atributo es el lexema encontrado en el programa fuente.

# ── Palabras reservadas del lenguaje ──────────────────────────────────
# Estas palabras tienen significado especial y NO pueden usarse
# como nombres de variables o funciones.

TOKEN_PROG    = "PROG"      # pf2025  → indica inicio del programa
TOKEN_DECL    = "DECL"      # decl    → inicio de declaraciones
TOKEN_INICIO  = "INICIO"    # inicio  → inicio del cuerpo del programa
TOKEN_FIN     = "FIN"       # fin     → fin del cuerpo del programa
TOKEN_END     = "FIN_BLOQUE"  # fin     → fin de estructuras (si, mientras)
TOKEN_IF      = "SI"          # si      → condicional
TOKEN_THEN    = "ENTONCES"    # entonces→ rama verdadera del si
TOKEN_ELSE    = "SINO"        # sino    → rama falsa del si
TOKEN_AND     = "Y"           # y       → operador lógico Y
TOKEN_OR      = "O"           # o       → operador lógico O
TOKEN_NOT     = "NO"          # no      → operador lógico negación
TOKEN_TRUE    = "VERDADERO"   # verdadero → constante booleana verdadero
TOKEN_FALSE   = "FALSO"       # falso     → constante booleana falso

# ── Instrucciones de entrada / salida ────────────────────────────────
TOKEN_IMPDIG  = "IMPDIG"    # impdig   → imprime un entero
TOKEN_IMPCAD  = "IMPCAD"    # impcad   → imprime una cadena
TOKEN_IMPBOOL = "IMPBOOL"   # impBool  → imprime un booleano
TOKEN_LEERDIG = "LEERDIG"   # leerdig  → lee un entero por teclado
TOKEN_LEERCAD = "LEERCAD"   # leercad  → lee una cadena por teclado
TOKEN_LEERBOOL= "LEERBOOL"  # leerBool → lee un booleano por teclado

# ── Tipos de datos ────────────────────────────────────────────────────
# Los tres tipos básicos del lenguaje comparten el mismo token TIPO.
# El atributo del token indica cuál tipo es (Ent, cad, Bool).
TOKEN_TIPO    = "TIPO"      # Ent | cad | Bool

# ── Identificadores y constantes ─────────────────────────────────────
TOKEN_ID      = "ID"        # nombre de variable o programa
TOKEN_CENT    = "CENT"      # constante entera no negativa (ej: 0, 42)
TOKEN_CADENA  = "CADENA"    # literal de cadena entre comillas "..."

# ── Operadores aritméticos ────────────────────────────────────────────
TOKEN_MAS     = "MAS"       # +
TOKEN_MENOS   = "MENOS"     # -
TOKEN_MUL     = "MUL"       # *
TOKEN_DIV     = "DIV"       # /

# ── Operadores relacionales ───────────────────────────────────────────
TOKEN_IGUAL   = "IGUAL"        # =   (asignación o comparación simple)
TOKEN_EQEQ    = "IGUALIGUAL"  # ==  (igualdad lógica, doble igual)
TOKEN_NEQ     = "DISTINTO"    # !=  (desigualdad)
TOKEN_MAYOR   = "MAYOR"     # >
TOKEN_MENOR   = "MENOR"     # <
TOKEN_MAYOREQ = "MAYOREQ"   # >=
TOKEN_MENOREQ = "MENOREQ"   # <=

# ── Operador de asignación ────────────────────────────────────────────
TOKEN_ASIG    = "ASIG"      # :=

# ── Signos de puntuación ─────────────────────────────────────────────
TOKEN_PC      = "PC"        # ;  (punto y coma)
TOKEN_COMA    = "COMA"      # ,
TOKEN_PAREN   = "PAREN"     # (  (paréntesis de apertura)
TOKEN_TESIS   = "TESIS"     # )  (paréntesis de cierre)

# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 2: TABLA DE PALABRAS RESERVADAS
# ─────────────────────────────────────────────────────────────────────
#
# Diccionario que mapea cada lexema reservado a su token.
# IMPORTANTE: el lenguaje distingue mayúsculas y minúsculas.
# Por tanto "inicio" ≠ "Inicio" ≠ "INICIO".

PALABRAS_RESERVADAS = {
    # Estructura del programa
    "pf2025"    : TOKEN_PROG,
    "decl"      : TOKEN_DECL,
    "inicio"    : TOKEN_INICIO,
    "fin"       : TOKEN_FIN,
    # Control de flujo
    "finsi"     : TOKEN_END,      # fin del bloque si
    "si"        : TOKEN_IF,       # condicional
    "entonces"  : TOKEN_THEN,     # rama verdadera
    "sino"      : TOKEN_ELSE,     # rama falsa
    # Operadores lógicos
    "y"         : TOKEN_AND,      # operador lógico Y
    "o"         : TOKEN_OR,       # operador lógico O
    "no"        : TOKEN_NOT,      # operador lógico negación
    # Constantes booleanas
    "verdadero" : TOKEN_TRUE,
    "falso"     : TOKEN_FALSE,
    # Instrucciones de E/S
    "impdig"   : TOKEN_IMPDIG,
    "impcad"   : TOKEN_IMPCAD,
    "impBool"  : TOKEN_IMPBOOL,
    "leerdig"  : TOKEN_LEERDIG,
    "leercad"  : TOKEN_LEERCAD,
    "leerBool" : TOKEN_LEERBOOL,
    # Tipos de datos (comparten token TIPO)
    "Ent"      : TOKEN_TIPO,
    "cad"      : TOKEN_TIPO,
    "Bool"     : TOKEN_TIPO,
}

# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 3: CLASE TOKEN
# ─────────────────────────────────────────────────────────────────────

class Token:
    """
    Representa una unidad léxica reconocida en el programa fuente.

    Atributos:
        tipo    (str) : nombre del token (ej: "ID", "CENT", "MAS")
        lexema  (str) : cadena exacta encontrada en el fuente
        linea   (int) : número de línea donde se encontró el token
    """

    def __init__(self, tipo, lexema, linea):
        self.tipo   = tipo
        self.lexema = lexema
        self.linea  = linea

    def __str__(self):
        # Formato de salida: <TIPO, 'lexema', línea N>
        return f"<{self.tipo}, '{self.lexema}', línea {self.linea}>"


# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 4: CLASE ANALIZADOR LÉXICO
# ─────────────────────────────────────────────────────────────────────

class AnalizadorLexico:
    """
    Implementa el autómata finito determinista (AFD) que reconoce
    todos los tokens del lenguaje FLYNNS.

    El análisis se realiza carácter a carácter sobre el texto fuente.
    El método principal es `analizar()`, que devuelve la lista
    completa de tokens reconocidos.

    Atributos internos:
        fuente       (str)  : texto completo del programa fuente
        posicion     (int)  : índice del carácter actual
        linea_actual (int)  : número de línea actual (empieza en 1)
        tokens       (list) : lista de tokens reconocidos
        errores      (list) : lista de errores léxicos encontrados
        texto_dep    (str)  : texto depurado (sin comentarios)
        tabla_sim    (dict) : tabla de símbolos {nombre: info}
    """

    def __init__(self, fuente):
        self.fuente       = fuente
        self.posicion     = 0
        self.linea_actual = 1
        self.tokens       = []
        self.errores      = []
        self.texto_dep    = ""
        self.tabla_sim    = {}

    # ── Métodos auxiliares de navegación ─────────────────────────────

    def caracter_actual(self):
        """Devuelve el carácter en la posición actual sin avanzar."""
        if self.posicion < len(self.fuente):
            return self.fuente[self.posicion]
        return None  # Fin de archivo

    def siguiente_caracter(self):
        """Devuelve el siguiente carácter sin avanzar la posición."""
        if self.posicion + 1 < len(self.fuente):
            return self.fuente[self.posicion + 1]
        return None

    def avanzar(self):
        """
        Avanza la posición al siguiente carácter.
        Si el carácter actual es salto de línea, incrementa el
        contador de líneas.
        """
        caracter = self.fuente[self.posicion]
        if caracter == '\n':
            self.linea_actual += 1
        self.posicion += 1

    def fin_de_archivo(self):
        """Devuelve True si ya se procesó todo el archivo."""
        return self.posicion >= len(self.fuente)

    # ── Métodos de clasificación de caracteres ────────────────────────
    # Estos métodos corresponden a las transiciones del AFD.

    def es_letra(self, c):
        """
        Devuelve True si el carácter es una letra (a-z, A-Z).
        Expresión regular: [a-zA-Z]
        """
        return c is not None and c.isalpha()

    def es_digito(self, c):
        """
        Devuelve True si el carácter es un dígito (0-9).
        Expresión regular: [0-9]
        """
        return c is not None and c.isdigit()

    def es_alfanumerico(self, c):
        """
        Devuelve True si el carácter es letra o dígito.
        Expresión regular: [a-zA-Z0-9]
        """
        return self.es_letra(c) or self.es_digito(c)

    def es_espacio(self, c):
        """
        Devuelve True si el carácter es espacio en blanco,
        tabulador, salto de línea o retorno de carro.
        Estos caracteres se ignoran (no generan token).
        """
        return c is not None and c in ' \t\n\r'

    # ── Métodos de reconocimiento (sub-autómatas) ─────────────────────

    def saltar_espacios(self):
        """
        AFD para espacios en blanco.
        Consume todos los espacios, tabs y saltos de línea
        consecutivos sin generar ningún token.
        """
        while not self.fin_de_archivo() and self.es_espacio(self.caracter_actual()):
            self.avanzar()

    def saltar_comentario(self):
        """
        AFD para comentarios de bloque: /* ... */
        Consume todo el contenido entre /* y */ sin generar token.
        Si el comentario no se cierra, reporta error léxico.

        Expresión regular: /\*([^*]|\*[^/])*\*/

        Estados:
            q0: inicio, se detectó '/'
            q1: se detectó '/*', dentro del comentario
            q2: se detectó '*' dentro del comentario
            q3: estado de aceptación, se detectó '*/'
        """
        linea_inicio = self.linea_actual
        self.avanzar()  # consume '/'
        self.avanzar()  # consume '*'

        # q1: buscamos el cierre */
        while not self.fin_de_archivo():
            caracter = self.caracter_actual()

            if caracter == '*':        # posible cierre
                self.avanzar()
                if not self.fin_de_archivo() and self.caracter_actual() == '/':
                    self.avanzar()     # q3: comentario cerrado
                    return             # éxito, salimos
                # si no es '/', seguimos en q1
            else:
                self.avanzar()         # consumimos y seguimos en q1

        # Si llegamos aquí, el archivo terminó sin cerrar el comentario
        self.errores.append(
            f"ERROR LÉXICO en línea {linea_inicio}: "
            f"comentario abierto con '/*' nunca fue cerrado con '*/'"
        )

    def leer_identificador_o_reservada(self):
        """
        AFD para identificadores y palabras reservadas.
        Expresión regular: letra(letra|digito)*

        Estados:
            q0 → q1 : se lee una letra (inicio del identificador)
            q1 → q1 : se lee letra o dígito (continuación)
            q1      : estado de aceptación

        Después de reconocer la cadena completa, se consulta la tabla
        de palabras reservadas para decidir si es reservada o ID.
        """
        lexema = ""

        # q0 → q1: primer carácter obligatorio es letra
        while not self.fin_de_archivo() and self.es_alfanumerico(self.caracter_actual()):
            lexema += self.caracter_actual()
            self.avanzar()

        # Consultar tabla de palabras reservadas
        if lexema in PALABRAS_RESERVADAS:
            tipo_token = PALABRAS_RESERVADAS[lexema]
            return Token(tipo_token, lexema, self.linea_actual)
        else:
            # Es un identificador → se agrega a tabla de símbolos
            self._agregar_identificador(lexema)
            return Token(TOKEN_ID, lexema, self.linea_actual)

    def leer_numero_entero(self):
        """
        AFD para constantes enteras no negativas.
        Expresión regular: digito+

        Estados:
            q0 → q1 : se lee un dígito
            q1 → q1 : se sigue leyendo dígitos
            q1      : estado de aceptación
        """
        lexema = ""

        while not self.fin_de_archivo() and self.es_digito(self.caracter_actual()):
            lexema += self.caracter_actual()
            self.avanzar()

        # Agregar constante a tabla de símbolos
        self._agregar_constante(lexema)
        return Token(TOKEN_CENT, lexema, self.linea_actual)

    def leer_cadena_literal(self):
        """
        AFD para literales de cadena: "contenido"
        Expresión regular: "([^"\n])*"

        Estados:
            q0 → q1 : se lee '"' de apertura
            q1 → q1 : se lee cualquier carácter excepto '"' y '\n'
            q1 → q2 : se lee '"' de cierre (aceptación)

        Si se llega al fin de línea o fin de archivo sin cerrar
        la cadena, se reporta error léxico.
        """
        linea_inicio = self.linea_actual
        lexema = '"'
        self.avanzar()  # consume '"' inicial → q1

        while not self.fin_de_archivo():
            caracter = self.caracter_actual()

            if caracter == '"':        # q1 → q2: cierre de cadena
                lexema += '"'
                self.avanzar()
                return Token(TOKEN_CADENA, lexema, linea_inicio)
            elif caracter == '\n':     # error: cadena no cerrada en la línea
                break
            else:
                lexema += caracter
                self.avanzar()

        self.errores.append(
            f"ERROR LÉXICO en línea {linea_inicio}: "
            f"literal de cadena no cerrada, falta '\"' de cierre"
        )
        return None

    def leer_dos_puntos(self):
        """
        AFD para el operador de asignación ':='
        y el carácter ':' solitario (error).

        Estados:
            q0 → q1 : se lee ':'
            q1 → q2 : se lee '=' → token ASIG ':=' (aceptación)
            q1      : error si el siguiente no es '='
        """
        linea = self.linea_actual
        self.avanzar()  # consume ':' → q1

        if not self.fin_de_archivo() and self.caracter_actual() == '=':
            self.avanzar()  # consume '=' → q2
            return Token(TOKEN_ASIG, ":=", linea)
        else:
            self.errores.append(
                f"ERROR LÉXICO en línea {linea}: "
                f"se esperaba ':=' pero se encontró ':' solitario"
            )
            return None

    def leer_mayor(self):
        """
        AFD para '>' y '>='
        q0 → q1: se lee '>'
        q1 → q2: se lee '=' → MAYOREQ
        q1     : aceptación → MAYOR
        """
        linea = self.linea_actual
        self.avanzar()  # consume '>'
        if not self.fin_de_archivo() and self.caracter_actual() == '=':
            self.avanzar()
            return Token(TOKEN_MAYOREQ, ">=", linea)
        return Token(TOKEN_MAYOR, ">", linea)

    def leer_menor(self):
        """
        AFD para '<' y '<='
        q0 → q1: se lee '<'
        q1 → q2: se lee '=' → MENOREQ
        q1     : aceptación → MENOR
        """
        linea = self.linea_actual
        self.avanzar()  # consume '<'
        if not self.fin_de_archivo() and self.caracter_actual() == '=':
            self.avanzar()
            return Token(TOKEN_MENOREQ, "<=", linea)
        return Token(TOKEN_MENOR, "<", linea)

    def leer_igual(self):
        """
        AFD para '=' y '=='
        q0 → q1: se lee '='
        q1 → q2: se lee '=' → IGUALIGUAL (igualdad lógica ==)
        q1     : aceptación → IGUAL (asignación simple =)
        """
        linea = self.linea_actual
        self.avanzar()  # consume primer '='
        if not self.fin_de_archivo() and self.caracter_actual() == '=':
            self.avanzar()
            return Token(TOKEN_EQEQ, "==", linea)
        return Token(TOKEN_IGUAL, "=", linea)

    def leer_distinto(self):
        """
        AFD para '!='
        q0 → q1: se lee '!'
        q1 → q2: se lee '=' → DISTINTO (aceptación)
        q1     : error, '!' solitario no es válido en flynns
        """
        linea = self.linea_actual
        self.avanzar()  # consume '!'
        if not self.fin_de_archivo() and self.caracter_actual() == '=':
            self.avanzar()
            return Token(TOKEN_NEQ, "!=", linea)
        else:
            self.errores.append(
                f"ERROR LÉXICO en línea {linea}: "
                f"carácter '!' no válido, ¿quiso escribir '!='?"
            )
            return None

    # ── Método principal del AFD ──────────────────────────────────────

    def analizar(self):
        """
        Método principal del analizador léxico.
        Recorre el texto fuente carácter a carácter aplicando
        el AFD correspondiente según el carácter actual.

        Devuelve:
            lista de objetos Token reconocidos.
        """
        lineas_depuradas = []   # para construir el archivo .dep
        linea_dep_actual = ""   # línea actual del texto depurado

        while not self.fin_de_archivo():
            caracter = self.caracter_actual()

            # ── Estado inicial del AFD principal ──────────────────────

            # CASO 1: Espacio en blanco → ignorar, no generar token
            if self.es_espacio(caracter):
                if caracter == '\n':
                    lineas_depuradas.append(linea_dep_actual)
                    linea_dep_actual = ""
                else:
                    linea_dep_actual += caracter
                self.avanzar()

            # CASO 2: Comentario de bloque /* ... */
            elif caracter == '/' and self.siguiente_caracter() == '*':
                # El comentario se elimina por completo (sin token)
                self.saltar_comentario()

            # CASO 3: Identificador o palabra reservada
            # AFD: letra → (letra|digito)*
            elif self.es_letra(caracter):
                tok = self.leer_identificador_o_reservada()
                self.tokens.append(tok)
                linea_dep_actual += tok.lexema + " "

            # CASO 4: Constante entera
            # AFD: digito → digito*
            elif self.es_digito(caracter):
                tok = self.leer_numero_entero()
                self.tokens.append(tok)
                linea_dep_actual += tok.lexema + " "

            # CASO 5: Literal de cadena
            elif caracter == '"':
                tok = self.leer_cadena_literal()
                if tok:
                    self.tokens.append(tok)
                    linea_dep_actual += tok.lexema + " "

            # CASO 6: Asignación ':='
            elif caracter == ':':
                tok = self.leer_dos_puntos()
                if tok:
                    self.tokens.append(tok)
                    linea_dep_actual += tok.lexema + " "

            # CASO 7: Operadores relacionales y aritméticos
            elif caracter == '>':
                tok = self.leer_mayor()
                self.tokens.append(tok)
                linea_dep_actual += tok.lexema + " "

            elif caracter == '<':
                tok = self.leer_menor()
                self.tokens.append(tok)
                linea_dep_actual += tok.lexema + " "

            elif caracter == '=':
                tok = self.leer_igual()
                self.tokens.append(tok)
                linea_dep_actual += tok.lexema + " "

            elif caracter == '!':
                tok = self.leer_distinto()
                if tok:
                    self.tokens.append(tok)
                    linea_dep_actual += tok.lexema + " "

            # CASO 8: Operadores aritméticos simples
            elif caracter == '+':
                self.tokens.append(Token(TOKEN_MAS, "+", self.linea_actual))
                linea_dep_actual += "+ "
                self.avanzar()

            elif caracter == '-':
                self.tokens.append(Token(TOKEN_MENOS, "-", self.linea_actual))
                linea_dep_actual += "- "
                self.avanzar()

            elif caracter == '*':
                self.tokens.append(Token(TOKEN_MUL, "*", self.linea_actual))
                linea_dep_actual += "* "
                self.avanzar()

            elif caracter == '/':
                # '/' que no va seguido de '*' es operador de división
                self.tokens.append(Token(TOKEN_DIV, "/", self.linea_actual))
                linea_dep_actual += "/ "
                self.avanzar()

            # CASO 9: Signos de puntuación
            elif caracter == ';':
                self.tokens.append(Token(TOKEN_PC, ";", self.linea_actual))
                linea_dep_actual += "; "
                self.avanzar()

            elif caracter == ',':
                self.tokens.append(Token(TOKEN_COMA, ",", self.linea_actual))
                linea_dep_actual += ", "
                self.avanzar()

            elif caracter == '(':
                self.tokens.append(Token(TOKEN_PAREN, "(", self.linea_actual))
                linea_dep_actual += "( "
                self.avanzar()

            elif caracter == ')':
                self.tokens.append(Token(TOKEN_TESIS, ")", self.linea_actual))
                linea_dep_actual += ") "
                self.avanzar()

            # CASO 10: Carácter no reconocido → Error léxico
            else:
                self.errores.append(
                    f"ERROR LÉXICO en línea {self.linea_actual}: "
                    f"carácter no reconocido '{caracter}'"
                )
                self.avanzar()

        # Guardar última línea depurada
        if linea_dep_actual.strip():
            lineas_depuradas.append(linea_dep_actual)

        # Construir texto depurado completo
        self.texto_dep = "\n".join(
            linea for linea in lineas_depuradas if linea.strip()
        )

        return self.tokens

    # ── Métodos para la tabla de símbolos ─────────────────────────────

    def _agregar_identificador(self, nombre):
        """
        Agrega un identificador a la tabla de símbolos si no existe.
        La entrada almacena: nombre, categoría y número de línea
        de la primera aparición.
        """
        if nombre not in self.tabla_sim:
            self.tabla_sim[nombre] = {
                "nombre"    : nombre,
                "categoria" : "identificador",
                "tipo"      : "desconocido",    # se determina en análisis semántico
                "linea"     : self.linea_actual,
            }

    def _agregar_constante(self, valor):
        """
        Agrega una constante entera a la tabla de símbolos.
        La clave es el valor mismo (ej: "42").
        """
        clave = f"CONST_{valor}"
        if clave not in self.tabla_sim:
            self.tabla_sim[clave] = {
                "nombre"    : valor,
                "categoria" : "constante_entera",
                "tipo"      : "Ent",
                "linea"     : self.linea_actual,
            }


# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 5: GENERACIÓN DE FICHEROS DE SALIDA
# ─────────────────────────────────────────────────────────────────────

def generar_archivo_depurado(ruta_salida, texto_depurado):
    """
    Genera el fichero progfte.dep que contiene el programa fuente
    depurado: sin comentarios, sin espacios redundantes.

    Parámetro:
        ruta_salida    (str) : ruta completa del archivo a crear
        texto_depurado (str) : contenido depurado generado por el AFD
    """
    with open(ruta_salida, 'w', encoding='utf-8') as archivo:
        archivo.write("═" * 65 + "\n")
        archivo.write("  PROGRAMA FUENTE DEPURADO - LENGUAJE FLYNNS\n")
        archivo.write("  (sin comentarios, espacios en blanco eliminados)\n")
        archivo.write("═" * 65 + "\n\n")
        archivo.write(texto_depurado)
        archivo.write("\n")
    print(f"  → Archivo depurado generado: {ruta_salida}")


def generar_archivo_tokens(ruta_salida, lista_tokens, lista_errores):
    """
    Genera el fichero progfte.tok que contiene:
        - La lista completa de tokens reconocidos con su línea
        - Los errores léxicos encontrados (si los hay)

    Formato de cada token:
        Línea NNN | TOKEN       | 'lexema'
    """
    with open(ruta_salida, 'w', encoding='utf-8') as archivo:
        archivo.write("═" * 65 + "\n")
        archivo.write("  TABLA DE TOKENS - LENGUAJE FLYNNS\n")
        archivo.write("═" * 65 + "\n")
        archivo.write(f"  Total de tokens reconocidos: {len(lista_tokens)}\n")
        archivo.write("═" * 65 + "\n\n")

        # Encabezado de la tabla
        archivo.write(f"{'LÍNEA':<10} {'TOKEN':<15} {'LEXEMA'}\n")
        archivo.write("-" * 50 + "\n")

        for tok in lista_tokens:
            archivo.write(
                f"{str(tok.linea):<10} {tok.tipo:<15} '{tok.lexema}'\n"
            )

        # Sección de errores
        archivo.write("\n" + "═" * 65 + "\n")
        if lista_errores:
            archivo.write(f"  ERRORES LÉXICOS ENCONTRADOS: {len(lista_errores)}\n")
            archivo.write("═" * 65 + "\n")
            for error in lista_errores:
                archivo.write(f"  {error}\n")
        else:
            archivo.write("  SIN ERRORES LÉXICOS\n")
        archivo.write("═" * 65 + "\n")

    print(f"  → Tabla de tokens generada:  {ruta_salida}")


def generar_tabla_simbolos(ruta_salida, tabla):
    """
    Genera el fichero progfte.tab que contiene la tabla de símbolos.
    Incluye todos los identificadores y constantes encontrados.

    Formato:
        Nombre | Categoría | Tipo | Primera línea
    """
    with open(ruta_salida, 'w', encoding='utf-8') as archivo:
        archivo.write("═" * 65 + "\n")
        archivo.write("  TABLA DE SÍMBOLOS - LENGUAJE FLYNNS\n")
        archivo.write("═" * 65 + "\n")
        archivo.write(f"  Total de entradas: {len(tabla)}\n")
        archivo.write("═" * 65 + "\n\n")

        # Encabezado
        archivo.write(
            f"{'NOMBRE':<20} {'CATEGORÍA':<22} {'TIPO':<15} {'LÍNEA'}\n"
        )
        archivo.write("-" * 65 + "\n")

        for clave, info in sorted(tabla.items()):
            archivo.write(
                f"{info['nombre']:<20} "
                f"{info['categoria']:<22} "
                f"{info['tipo']:<15} "
                f"{info['linea']}\n"
            )

        archivo.write("\n" + "═" * 65 + "\n")
        archivo.write("  NOTA: El tipo de los identificadores se determinará\n")
        archivo.write("        en la fase de análisis semántico.\n")
        archivo.write("═" * 65 + "\n")

    print(f"  → Tabla de símbolos generada: {ruta_salida}")


# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 6: FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────

def principal():
    """
    Punto de entrada del analizador léxico FLYNNS.

    Flujo:
        1. Verifica que se pasó un archivo fuente como argumento.
        2. Verifica que el archivo tiene extensión .isos
        3. Lee el contenido del archivo fuente.
        4. Crea el analizador y ejecuta el análisis.
        5. Genera los tres ficheros de salida.
        6. Muestra en pantalla un resumen del análisis.
    """
    print("\n" + "═" * 65)
    print("       ANALIZADOR LÉXICO - LENGUAJE FLYNNS v1.0")
    print("═" * 65)

    # Paso 1: Verificar argumento
    if len(sys.argv) < 2:
        print("\n  USO CORRECTO:")
        print("      python flynns.py <archivo_fuente.isos>\n")
        print("  EJEMPLO:")
        print("      python flynns.py progfte.isos\n")
        sys.exit(1)

    ruta_fuente = sys.argv[1]

    # Paso 2: Verificar extensión
    if not ruta_fuente.endswith('.isos'):
        print(f"\n  ADVERTENCIA: El archivo '{ruta_fuente}' no tiene")
        print(f"  extensión '.isos'. Se procesará de todas formas.\n")

    # Paso 3: Leer archivo fuente
    if not os.path.exists(ruta_fuente):
        print(f"\n  ERROR: No se encontró el archivo '{ruta_fuente}'\n")
        sys.exit(1)

    with open(ruta_fuente, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()

    print(f"\n  Archivo fuente: {ruta_fuente}")
    print(f"  Tamaño: {len(contenido)} caracteres")

    # Paso 4: Ejecutar análisis léxico
    print("\n  Ejecutando análisis léxico...")
    analizador = AnalizadorLexico(contenido)
    tokens = analizador.analizar()

    # Paso 5: Crear carpeta de salidas si no existe
    carpeta_salida = "salidas"
    os.makedirs(carpeta_salida, exist_ok=True)

    # Paso 6: Generar los tres ficheros de salida
    print("\n  Generando ficheros de salida:")
    generar_archivo_depurado(
        os.path.join(carpeta_salida, "progfte.dep"),
        analizador.texto_dep
    )
    generar_archivo_tokens(
        os.path.join(carpeta_salida, "progfte.tok"),
        tokens,
        analizador.errores
    )
    generar_tabla_simbolos(
        os.path.join(carpeta_salida, "progfte.tab"),
        analizador.tabla_sim
    )

    # Paso 7: Mostrar resumen en pantalla
    print("\n" + "═" * 65)
    print("  RESUMEN DEL ANÁLISIS")
    print("═" * 65)
    print(f"  Tokens reconocidos : {len(tokens)}")
    print(f"  Errores léxicos    : {len(analizador.errores)}")
    print(f"  Símbolos en tabla  : {len(analizador.tabla_sim)}")

    if analizador.errores:
        print("\n  ── ERRORES ENCONTRADOS ──────────────────────────────")
        for error in analizador.errores:
            print(f"  {error}")
        print("\n  Análisis terminado CON ERRORES.")
    else:
        print("\n  Análisis completado SIN ERRORES LÉXICOS.")

    print("═" * 65 + "\n")


# ─────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    principal()
