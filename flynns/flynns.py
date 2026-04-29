"""
╔══════════════════════════════════════════════════════════════════════╗
║          ANALIZADOR LÉXICO - LENGUAJE FLYNNS                         ║
║          Extensión de archivos fuente: .isos                         ║
║          Autor: Juan Nava, Fernando Cisneros y Greko Fuentes         ║
║          Versión: 2.0                                                ║
╚══════════════════════════════════════════════════════════════════════╝

DESCRIPCIÓN:
    Este módulo implementa el analizador léxico del lenguaje FLYNNS.
    Genera:
        - progfte.dep : programa depurado en UNA SOLA LÍNEA
        - progfte.tok : lista de lexemas con referencia numérica
        - progfte.tab : tabla de símbolos con No, Lexema, Token, Ref, Línea

TABLA DE REFERENCIAS NUMÉRICAS:
    100 - 199  Palabras reservadas (estructura del programa)
    200 - 299  Tipos, constantes booleanas e instrucciones E/S
    300 - 399  Identificadores (ID) — numerados dinámicamente
    400 - 499  Constantes enteras (CENT) — numeradas dinámicamente
    500 - 599  Operadores aritméticos
    600 - 699  Operadores relacionales y asignación
    700 - 799  Operadores lógicos
    800 - 899  Símbolos de puntuación
    900        Error léxico
"""

import sys
import os

# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 1: DEFINICIÓN DE TOKENS CON REFERENCIA NUMÉRICA
# ─────────────────────────────────────────────────────────────────────
# Cada token es una tupla: (NOMBRE, REFERENCIA_NUMERICA)

# Palabras reservadas — rango 100
TOKEN_PROG    = ("PROG",       100)
TOKEN_DECL    = ("DECL",       101)
TOKEN_INICIO  = ("INICIO",     102)
TOKEN_FIN     = ("FIN",        103)
TOKEN_END     = ("FIN_BLOQUE", 104)
TOKEN_IF      = ("SI",         105)
TOKEN_THEN    = ("ENTONCES",   106)
TOKEN_ELSE    = ("SINO",       107)

# Tipos, booleanos e instrucciones E/S — rango 200
TOKEN_TIPO    = ("TIPO",       200)
TOKEN_TRUE    = ("VERDADERO",  201)
TOKEN_FALSE   = ("FALSO",      202)
TOKEN_IMPDIG  = ("IMPDIG",     210)
TOKEN_IMPCAD  = ("IMPCAD",     211)
TOKEN_IMPBOOL = ("IMPBOOL",    212)
TOKEN_LEERDIG = ("LEERDIG",    213)
TOKEN_LEERCAD = ("LEERCAD",    214)
TOKEN_LEERBOOL= ("LEERBOOL",   215)

# Identificadores y constantes — rango 300 y 400 (dinámicos)
TOKEN_ID      = ("ID",         300)  # base; ref real asignada dinámicamente
TOKEN_CENT    = ("CENT",       400)  # base; ref real asignada dinámicamente
TOKEN_CADENA  = ("CADENA",     401)

# Operadores aritméticos — rango 500
TOKEN_MAS     = ("MAS",        500)
TOKEN_MENOS   = ("MENOS",      501)
TOKEN_MUL     = ("MUL",        502)
TOKEN_DIV     = ("DIV",        503)

# Operadores relacionales y asignación — rango 600
TOKEN_ASIG    = ("ASIG",       600)
TOKEN_IGUAL   = ("IGUAL",      601)
TOKEN_EQEQ    = ("IGUALIGUAL", 602)
TOKEN_NEQ     = ("DISTINTO",   603)
TOKEN_MAYOR   = ("MAYOR",      604)
TOKEN_MENOR   = ("MENOR",      605)
TOKEN_MAYOREQ = ("MAYOREQ",    606)
TOKEN_MENOREQ = ("MENOREQ",    607)

# Operadores lógicos — rango 700
TOKEN_AND     = ("Y",          700)
TOKEN_OR      = ("O",          701)
TOKEN_NOT     = ("NO",         702)

# Símbolos de puntuación — rango 800
TOKEN_PC      = ("PC",         800)
TOKEN_COMA    = ("COMA",       801)
TOKEN_PAREN   = ("PAREN",      802)
TOKEN_TESIS   = ("TESIS",      803)

# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 2: TABLA DE PALABRAS RESERVADAS
# ─────────────────────────────────────────────────────────────────────

PALABRAS_RESERVADAS = {
    "pf2025"    : TOKEN_PROG,
    "decl"      : TOKEN_DECL,
    "inicio"    : TOKEN_INICIO,
    "fin"       : TOKEN_FIN,
    "finsi"     : TOKEN_END,
    "si"        : TOKEN_IF,
    "entonces"  : TOKEN_THEN,
    "sino"      : TOKEN_ELSE,
    "y"         : TOKEN_AND,
    "o"         : TOKEN_OR,
    "no"        : TOKEN_NOT,
    "verdadero" : TOKEN_TRUE,
    "falso"     : TOKEN_FALSE,
    "impdig"    : TOKEN_IMPDIG,
    "impcad"    : TOKEN_IMPCAD,
    "impBool"   : TOKEN_IMPBOOL,
    "leerdig"   : TOKEN_LEERDIG,
    "leercad"   : TOKEN_LEERCAD,
    "leerBool"  : TOKEN_LEERBOOL,
    "Ent"       : TOKEN_TIPO,
    "cad"       : TOKEN_TIPO,
    "Bool"      : TOKEN_TIPO,
}

# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 3: CLASE TOKEN
# ─────────────────────────────────────────────────────────────────────

class Token:
    """
    Representa una unidad léxica reconocida en el programa fuente.
    Atributos:
        nombre (str) : nombre del token  ej: "ID", "MAS"
        ref    (int) : referencia numérica ej: 300, 500
        lexema (str) : texto exacto del fuente
        linea  (int) : número de línea donde se encontró
    """
    def __init__(self, tipo_tupla, lexema, linea):
        self.nombre = tipo_tupla[0]
        self.ref    = tipo_tupla[1]
        self.lexema = lexema
        self.linea  = linea

    def __str__(self):
        return f"<{self.nombre}({self.ref}), '{self.lexema}', línea {self.linea}>"


# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 4: CLASE ANALIZADOR LÉXICO
# ─────────────────────────────────────────────────────────────────────

class AnalizadorLexico:
    """
    Implementa el AFD que reconoce todos los tokens de FLYNNS.
    """

    def __init__(self, fuente):
        self.fuente         = fuente
        self.posicion       = 0
        self.linea_actual   = 1
        self.tokens         = []
        self.errores        = []
        self.texto_dep      = ""
        self.tabla_sim      = {}
        self.contador_ids   = 300   # IDs se numeran desde 300
        self.contador_const = 400   # Constantes desde 400
        self._orden_tabla   = []    # orden de inserción en tabla

    # ── Navegación ────────────────────────────────────────────────────

    def caracter_actual(self):
        """Devuelve el carácter en la posición actual sin avanzar."""
        if self.posicion < len(self.fuente):
            return self.fuente[self.posicion]
        return None

    def siguiente_caracter(self):
        """Devuelve el siguiente carácter sin avanzar la posición."""
        if self.posicion + 1 < len(self.fuente):
            return self.fuente[self.posicion + 1]
        return None

    def avanzar(self):
        """Avanza al siguiente carácter, contando saltos de línea."""
        if self.fuente[self.posicion] == '\n':
            self.linea_actual += 1
        self.posicion += 1

    def fin_de_archivo(self):
        """True si ya se procesó todo el archivo."""
        return self.posicion >= len(self.fuente)

    # ── Clasificadores ────────────────────────────────────────────────

    def es_letra(self, c):
        """E.R: [a-zA-Z]"""
        return c is not None and c.isalpha()

    def es_digito(self, c):
        """E.R: [0-9]"""
        return c is not None and c.isdigit()

    def es_alfanumerico(self, c):
        """E.R: [a-zA-Z0-9]"""
        return self.es_letra(c) or self.es_digito(c)

    def es_espacio(self, c):
        """E.R: [ \\t\\n\\r] — se elimina del depurado sin generar token."""
        return c is not None and c in ' \t\n\r'

    # ── Sub-autómatas ─────────────────────────────────────────────────

    def saltar_comentario(self):
        """
        AFD para comentarios /* ... */
        Estados: q0→q1(/) → q2(*) → q3(cualquier) → q4(*posible cierre)
                 → q5(/ cierre confirmado) | q3(sigue)
        Error: EOF sin cerrar el comentario.
        """
        linea_inicio = self.linea_actual
        self.avanzar()  # consume '/'
        self.avanzar()  # consume '*'
        while not self.fin_de_archivo():
            c = self.caracter_actual()
            if c == '*':
                self.avanzar()
                if not self.fin_de_archivo() and self.caracter_actual() == '/':
                    self.avanzar()
                    return
            else:
                self.avanzar()
        self.errores.append(
            f"ERROR LÉXICO en línea {linea_inicio}: "
            f"comentario '/*' nunca cerrado con '*/'"
        )

    def leer_identificador_o_reservada(self):
        """
        AFD: E.R. letra(letra|digito)*
        q0→q1(letra) → q1(letra|digito)* → aceptación
        Si coincide con PALABRAS_RESERVADAS → token reservado
        Si no → token ID con referencia dinámica desde 300
        """
        lexema = ""
        while not self.fin_de_archivo() and self.es_alfanumerico(self.caracter_actual()):
            lexema += self.caracter_actual()
            self.avanzar()

        if lexema in PALABRAS_RESERVADAS:
            return Token(PALABRAS_RESERVADAS[lexema], lexema, self.linea_actual)
        else:
            ref = self._agregar_identificador(lexema)
            return Token(("ID", ref), lexema, self.linea_actual)

    def leer_numero_entero(self):
        """
        AFD: E.R. digito+
        q0→q1(digito) → q1(digito)* → aceptación
        Referencia dinámica desde 400.
        """
        lexema = ""
        while not self.fin_de_archivo() and self.es_digito(self.caracter_actual()):
            lexema += self.caracter_actual()
            self.avanzar()
        ref = self._agregar_constante(lexema)
        return Token(("CENT", ref), lexema, self.linea_actual)

    def leer_cadena_literal(self):
        """
        AFD: E.R. "[^\"\\n]*"
        q0→q1(") → q1(cualquier excepto " y \\n)* → q2(" cierre)
        Error: fin de línea o EOF sin cerrar la cadena.
        """
        linea_inicio = self.linea_actual
        lexema = '"'
        self.avanzar()
        while not self.fin_de_archivo():
            c = self.caracter_actual()
            if c == '"':
                lexema += '"'
                self.avanzar()
                return Token(TOKEN_CADENA, lexema, linea_inicio)
            elif c == '\n':
                break
            else:
                lexema += c
                self.avanzar()
        self.errores.append(
            f"ERROR LÉXICO en línea {linea_inicio}: "
            f"cadena no cerrada, falta '\"' de cierre"
        )
        return None

    def leer_dos_puntos(self):
        """
        AFD para ':='
        q0→q1(:) → q2(=) aceptación ASIG
        q1 → ERROR si el siguiente no es '='
        """
        linea = self.linea_actual
        self.avanzar()
        if not self.fin_de_archivo() and self.caracter_actual() == '=':
            self.avanzar()
            return Token(TOKEN_ASIG, ":=", linea)
        self.errores.append(
            f"ERROR LÉXICO en línea {linea}: "
            f"se esperaba ':=' pero se encontró ':' solitario"
        )
        return None

    def leer_mayor(self):
        """AFD para '>' y '>='"""
        linea = self.linea_actual
        self.avanzar()
        if not self.fin_de_archivo() and self.caracter_actual() == '=':
            self.avanzar()
            return Token(TOKEN_MAYOREQ, ">=", linea)
        return Token(TOKEN_MAYOR, ">", linea)

    def leer_menor(self):
        """AFD para '<' y '<='"""
        linea = self.linea_actual
        self.avanzar()
        if not self.fin_de_archivo() and self.caracter_actual() == '=':
            self.avanzar()
            return Token(TOKEN_MENOREQ, "<=", linea)
        return Token(TOKEN_MENOR, "<", linea)

    def leer_igual(self):
        """AFD para '=' y '=='"""
        linea = self.linea_actual
        self.avanzar()
        if not self.fin_de_archivo() and self.caracter_actual() == '=':
            self.avanzar()
            return Token(TOKEN_EQEQ, "==", linea)
        return Token(TOKEN_IGUAL, "=", linea)

    def leer_distinto(self):
        """
        AFD para '!='
        q0→q1(!) → q2(=) aceptación DISTINTO
        q1 → ERROR si el siguiente no es '='
        """
        linea = self.linea_actual
        self.avanzar()
        if not self.fin_de_archivo() and self.caracter_actual() == '=':
            self.avanzar()
            return Token(TOKEN_NEQ, "!=", linea)
        self.errores.append(
            f"ERROR LÉXICO en línea {linea}: "
            f"carácter '!' no válido, ¿quiso escribir '!='?"
        )
        return None

    # ── AFD principal ─────────────────────────────────────────────────

    def analizar(self):
        """
        Método principal. Recorre el fuente carácter a carácter.
        El .dep se construye en UNA SOLA LÍNEA: sin comentarios,
        sin saltos de línea, sin tabulaciones, sin espacios extra.
        Los errores léxicos (ej: '@', '#') se reportan con su línea.
        """
        partes_dep = []   # tokens que irán al .dep en una sola línea

        while not self.fin_de_archivo():
            c = self.caracter_actual()

            # Espacios, saltos de línea y tabulaciones → se eliminan
            if self.es_espacio(c):
                self.avanzar()

            # Comentario /* ... */ → se elimina completamente
            elif c == '/' and self.siguiente_caracter() == '*':
                self.saltar_comentario()

            # Identificador o palabra reservada
            elif self.es_letra(c):
                tok = self.leer_identificador_o_reservada()
                self.tokens.append(tok)
                partes_dep.append(tok.lexema)

            # Constante entera
            elif self.es_digito(c):
                tok = self.leer_numero_entero()
                self.tokens.append(tok)
                partes_dep.append(tok.lexema)

            # Cadena literal
            elif c == '"':
                tok = self.leer_cadena_literal()
                if tok:
                    self.tokens.append(tok)
                    partes_dep.append(tok.lexema)

            # Asignación :=
            elif c == ':':
                tok = self.leer_dos_puntos()
                if tok:
                    self.tokens.append(tok)
                    partes_dep.append(tok.lexema)

            # Operadores relacionales dobles o simples
            elif c == '>':
                tok = self.leer_mayor()
                self.tokens.append(tok)
                partes_dep.append(tok.lexema)

            elif c == '<':
                tok = self.leer_menor()
                self.tokens.append(tok)
                partes_dep.append(tok.lexema)

            elif c == '=':
                tok = self.leer_igual()
                self.tokens.append(tok)
                partes_dep.append(tok.lexema)

            elif c == '!':
                tok = self.leer_distinto()
                if tok:
                    self.tokens.append(tok)
                    partes_dep.append(tok.lexema)

            # Operadores aritméticos simples
            elif c == '+':
                self.tokens.append(Token(TOKEN_MAS, "+", self.linea_actual))
                partes_dep.append("+")
                self.avanzar()

            elif c == '-':
                self.tokens.append(Token(TOKEN_MENOS, "-", self.linea_actual))
                partes_dep.append("-")
                self.avanzar()

            elif c == '*':
                self.tokens.append(Token(TOKEN_MUL, "*", self.linea_actual))
                partes_dep.append("*")
                self.avanzar()

            elif c == '/':
                self.tokens.append(Token(TOKEN_DIV, "/", self.linea_actual))
                partes_dep.append("/")
                self.avanzar()

            # Signos de puntuación
            elif c == ';':
                self.tokens.append(Token(TOKEN_PC, ";", self.linea_actual))
                partes_dep.append(";")
                self.avanzar()

            elif c == ',':
                self.tokens.append(Token(TOKEN_COMA, ",", self.linea_actual))
                partes_dep.append(",")
                self.avanzar()

            elif c == '(':
                self.tokens.append(Token(TOKEN_PAREN, "(", self.linea_actual))
                partes_dep.append("(")
                self.avanzar()

            elif c == ')':
                self.tokens.append(Token(TOKEN_TESIS, ")", self.linea_actual))
                partes_dep.append(")")
                self.avanzar()

            # Carácter no reconocido → Error léxico
            # Ejemplos: @, #, $, %, ^, &, ~, etc.
            else:
                msg_error = (
                    f"ERROR LÉXICO en línea {self.linea_actual}: "
                    f"símbolo no identificado '{c}' (posible error)"
                )
                self.errores.append(msg_error)
                # También se agrega a la lista de tokens como entrada de error
                # para que aparezca en el .tok en el lugar donde ocurrió
                tok_error = Token(("ERROR", 900), c, self.linea_actual)
                tok_error.mensaje_error = msg_error
                self.tokens.append(tok_error)
                self.avanzar()

        # .dep: todos los tokens en una sola línea separados por espacio
        self.texto_dep = "".join(partes_dep)
        return self.tokens

    # ── Tabla de símbolos ─────────────────────────────────────────────

    def _agregar_identificador(self, nombre):
        """
        Agrega un ID a la tabla si no existe.
        La referencia se asigna dinámicamente desde 300 en adelante.
        Retorna la referencia numérica del identificador.
        """
        if nombre not in self.tabla_sim:
            ref = self.contador_ids
            self.contador_ids += 1
            self.tabla_sim[nombre] = {
                "no"     : len(self._orden_tabla) + 1,
                "nombre" : nombre,
                "tipo"   : "ID",
                "linea"  : self.linea_actual,
                "ref"    : ref,
            }
            self._orden_tabla.append(nombre)
        return self.tabla_sim[nombre]["ref"]

    def _agregar_constante(self, valor):
        """
        Agrega una constante entera a la tabla si no existe.
        La referencia se asigna dinámicamente desde 400 en adelante.
        Retorna la referencia numérica de la constante.
        """
        clave = f"CONST_{valor}"
        if clave not in self.tabla_sim:
            ref = self.contador_const
            self.contador_const += 1
            self.tabla_sim[clave] = {
                "no"     : len(self._orden_tabla) + 1,
                "nombre" : valor,
                "tipo"   : "CENT",
                "linea"  : self.linea_actual,
                "ref"    : ref,
            }
            self._orden_tabla.append(clave)
        return self.tabla_sim[clave]["ref"]


# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 5: GENERACIÓN DE FICHEROS DE SALIDA
# ─────────────────────────────────────────────────────────────────────

def generar_archivo_depurado(ruta_salida, texto_depurado):
    """
    Genera progfte.dep en UNA SOLA LÍNEA:
    sin comentarios, sin saltos de línea, sin tabulaciones.
    """
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write("=" * 65 + "\n")
        f.write("  PROGRAMA FUENTE DEPURADO - LENGUAJE FLYNNS\n")
        f.write("  (una sola linea, sin comentarios ni espacios en blanco)\n")
        f.write("=" * 65 + "\n\n")
        f.write(texto_depurado + "\n")
    print(f"  -> Archivo depurado generado: {ruta_salida}")


def generar_archivo_tokens(ruta_salida, lista_tokens, lista_errores):
    """
    Genera progfte.tok con formato:
        Renglón: N, Lexema: X, Token: REF NOMBRE

    Los errores aparecen al final con formato:
        ERROR LÉXICO en línea N: símbolo no identificado 'X' (posible error)
    """
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write("=" * 65 + "\n")
        f.write("  LISTA DE LEXEMAS - LENGUAJE FLYNNS\n")
        f.write("=" * 65 + "\n")
        f.write(f"  Total de tokens reconocidos: {len(lista_tokens)}\n")
        f.write("-" * 65 + "\n\n")

        for tok in lista_tokens:
            if tok.nombre == "ERROR":
                # El token de error se muestra en su posición con formato especial
                f.write(
                    f"Renglón: {tok.linea}, "
                    f"Símbolo no identificado '{tok.lexema}' (posible error)\n"
                )
            else:
                f.write(
                    f"Renglón: {tok.linea}, "
                    f"Lexema: {tok.lexema}, "
                    f"Token: {tok.ref} {tok.nombre}\n"
                )

        f.write("\n" + "-" * 65 + "\n")
        if lista_errores:
            f.write(f"  ERRORES LÉXICOS ENCONTRADOS: {len(lista_errores)}\n")
            f.write("-" * 65 + "\n")
            for error in lista_errores:
                f.write(f"{error}\n")
        else:
            f.write("  SIN ERRORES LÉXICOS\n")
        f.write("=" * 65 + "\n")
    print(f"  -> Lista de lexemas generada:  {ruta_salida}")


def generar_tabla_simbolos(ruta_salida, tabla, orden):
    """
    Genera progfte.tab con formato:
        No | LEXEMA | TOKEN | REF | LÍNEA
    En el orden en que aparecieron por primera vez en el fuente.
    """
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write("=" * 65 + "\n")
        f.write("  TABLA DE SIMBOLOS - LENGUAJE FLYNNS\n")
        f.write("=" * 65 + "\n")
        f.write(f"  Total de entradas: {len(orden)}\n")
        f.write("-" * 65 + "\n\n")

        f.write(f"{'No':<5} {'LEXEMA':<20} {'TOKEN':<10} {'REF':<8} {'LINEA'}\n")
        f.write("-" * 65 + "\n")

        for clave in orden:
            info = tabla[clave]
            f.write(
                f"{info['no']:<5} "
                f"{info['nombre']:<20} "
                f"{info['tipo']:<10} "
                f"{info['ref']:<8} "
                f"{info['linea']}\n"
            )

        f.write("\n" + "=" * 65 + "\n")
        f.write("  RANGOS DE REFERENCIA:\n")
        f.write("  300-399  Identificadores (ID)\n")
        f.write("  400-499  Constantes enteras (CENT)\n")
        f.write("=" * 65 + "\n")
    print(f"  -> Tabla de simbolos generada: {ruta_salida}")


# ─────────────────────────────────────────────────────────────────────
# SECCIÓN 6: FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────

def principal():
    print("\n" + "=" * 65)
    print("       ANALIZADOR LÉXICO - LENGUAJE FLYNNS v2.0")
    print("=" * 65)

    if len(sys.argv) < 2:
        print("\n  USO: python flynns.py <archivo.isos>\n")
        sys.exit(1)

    ruta_fuente = sys.argv[1]

    if not ruta_fuente.endswith('.isos'):
        print(f"\n  ADVERTENCIA: '{ruta_fuente}' no tiene extensión .isos\n")

    if not os.path.exists(ruta_fuente):
        print(f"\n  ERROR: No se encontró '{ruta_fuente}'\n")
        sys.exit(1)

    with open(ruta_fuente, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()

    print(f"\n  Archivo fuente : {ruta_fuente}")
    print(f"  Tamaño         : {len(contenido)} caracteres")

    print("\n  Ejecutando análisis léxico...")
    analizador = AnalizadorLexico(contenido)
    tokens = analizador.analizar()

    carpeta_salida = "salidas"
    os.makedirs(carpeta_salida, exist_ok=True)

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
        analizador.tabla_sim,
        analizador._orden_tabla
    )

    print("\n" + "=" * 65)
    print("  RESUMEN DEL ANÁLISIS")
    print("=" * 65)
    print(f"  Tokens reconocidos : {len(tokens)}")
    print(f"  Errores léxicos    : {len(analizador.errores)}")
    print(f"  Símbolos en tabla  : {len(analizador._orden_tabla)}")

    if analizador.errores:
        print("\n  ERRORES ENCONTRADOS:")
        for error in analizador.errores:
            print(f"  {error}")
        print("\n  Análisis terminado CON ERRORES LÉXICOS.")
    else:
        print("\n  Análisis completado SIN ERRORES LÉXICOS.")

    print("=" * 65 + "\n")


if __name__ == "__main__":
    principal()
