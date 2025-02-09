#Juego que conciste en mover cajas a un punto especifíco, al dejar todas las cajas en el objetivo se completa el juego. 

"""Diccionario"""
PARED = "#"
PJ = "@"
CAJA = "$"
OBJETIVO = "."
CAJA_EN_PUNTO = "*"
PJ_EN_PUNTO = "+"
VACIO = " "
""" Eje de coordenadas
y = filas
x = columnas
"""

def direcciones(direccion):
    if direccion == 'OESTE':
        return (-1, 0)
    if direccion == 'ESTE':
        return (1, 0)
    if direccion == 'NORTE':
        return (0, -1)
    if direccion == 'SUR':
        return (0, 1)


def crear_grilla(desc):
    '''Crea una grilla a partir de la descripción del estado inicial.

    La descripción es una lista de cadenas, cada cadena representa una
    fila y cada caracter una celda. Los caracteres pueden ser los siguientes:

    Caracter  Contenido de la celda
    --------  ---------------------
           #  Pared
           $  Caja
           @  Jugador
           .  Objetivo
           *  Objetivo + Caja
           +  Objetivo + Jugador

    Ejemplo:

    crear_grilla([
        '#####',
        '#.$ #',
        '#@  #',
        '#####',
    ])
    '''
    return [list(i) for i in desc]

def dimensiones(grilla):
    '''Devuelve una tupla con la cantidad de columnas y filas de la grilla.'''
    filas = len(grilla)
    columnas = 0
    for i in grilla:
        columnas += len(i) / len(grilla) 
    return int(columnas), int(filas)

def hay_pared(grilla, c, f):
    '''Devuelve True si hay una pared en la columna y fila (c, f).'''
    return grilla[f][c] == PARED

def hay_objetivo(grilla, c, f):
    '''Devuelve True si hay un objetivo en la columna y fila (c, f).'''
    return grilla[f][c] in [OBJETIVO, PJ_EN_PUNTO, CAJA_EN_PUNTO]

def hay_caja(grilla, c, f):
    '''Devuelve True si hay una caja en la columna y fila (c, f).'''
    return grilla[f][c] in (CAJA, CAJA_EN_PUNTO)

def hay_jugador(grilla, c, f):
    '''Devuelve True si el jugador está en la columna y fila (c, f).'''
    return grilla[f][c] == PJ or grilla[f][c] == PJ_EN_PUNTO

def juego_ganado(grilla):
    '''Devuelve True si el juego está ganado.'''
    columnas, filas = dimensiones(grilla)
    contador = 0
    
    for i in range (len(grilla)):
        for j in range (len(grilla[i])):
            if grilla[i][j] == OBJETIVO or grilla[i][j] == PJ_EN_PUNTO:
                contador += 1
    return contador == 0

def caja_movimiento(grilla,j,i,x,y):
    '''Función que realiza todas las opciones de movimiento que puede hacer la caja (de forma generica)'''
    mapa = crear_grilla(grilla)

    if hay_caja(grilla,j+x,i+y) and not hay_objetivo(grilla,j+x,i+y) and not hay_caja(grilla,j+2*x,i+2*y) and not hay_pared(grilla,j+2*x,i+2*y):
        if hay_objetivo(grilla,j+2*x,i+2*y):
            mapa[i+2*y][j+2*x] = CAJA_EN_PUNTO
        if not hay_objetivo(grilla,j+2*x,i+2*y):
            mapa[i+2*y][j+2*x] = CAJA
        mapa[i+y][j+x] = PJ
        mapa[i][j] = VACIO

    if hay_objetivo(grilla,j,i) and hay_caja(grilla,j+x,i+y) and not hay_objetivo(grilla,j+x,i+y) and not hay_caja(grilla,j+2*x,i+2*y) and not hay_pared(grilla,j+2*x,i+2*y):
        if hay_objetivo(grilla,j+2*x,i+2*y):
            mapa[i+2*y][j+2*x] = CAJA_EN_PUNTO
        if not hay_objetivo(grilla,j+2*x,i+2*y):
            mapa[i+2*y][j+2*x] = CAJA
        mapa[i+y][j+x] = PJ
        mapa[i][j] = OBJETIVO   
    
    if hay_objetivo(grilla,j+x,i+y):

        if hay_caja(grilla,j+x,i+y) and not hay_caja(grilla,j+2*x,i+2*y) and not hay_pared(grilla,j+2*x,i+2*y):
            if hay_objetivo(grilla,j+2*x,i+2*y):
                mapa[i+2*y][j+2*x] = CAJA_EN_PUNTO
                mapa[i+y][j+x] = PJ_EN_PUNTO
                mapa[i][j] = VACIO 
                
            if not hay_objetivo(grilla,j+2*x,i+2*y):
                mapa[i+2*y][j+2*x] = CAJA
                mapa[i+y][j+x] = PJ_EN_PUNTO
                mapa[i][j] = VACIO 
                
        if not hay_caja(grilla,j+x,i+y):
            mapa[i+y][j+x] = PJ_EN_PUNTO
            mapa[i][j] = VACIO

    return mapa 

def mover(grilla, direccion): 
    '''Mueve el jugador en la dirección indicada.

    La dirección es una tupla con el movimiento horizontal y vertical. Dado que
    no se permite el movimiento diagonal, la dirección puede ser una de cuatro
    posibilidades:

    direccion  significado
    ---------  -----------
    (-1, 0)    Oeste
    (1, 0)     Este
    (0, -1)    Norte
    (0, 1)     Sur

    La función debe devolver una grilla representando el estado siguiente al
    movimiento efectuado. La grilla recibida NO se modifica; es decir, en caso
    de que el movimiento sea válido, la función devuelve una nueva grilla.
    '''
    new_map = crear_grilla(grilla)
    x, y = direcciones(direccion)
    for i in range (len(grilla)):
        for j in range (len(grilla[i])): 
            
            if hay_jugador(grilla,j,i):          
                if hay_objetivo(grilla,j,i):

                    new_map = caja_movimiento(new_map,j,i,x,y)
                    if not hay_caja(grilla,j+x,i+y) and not hay_objetivo(grilla,j+x,i+y) and not hay_pared(grilla,j+x,i+y):
                        new_map[i+y][j+x] = PJ
                        new_map[i][j] = OBJETIVO
                    if hay_objetivo(grilla,j+x,i+y):
                        if not hay_caja(grilla,j+x,i+y):
                            new_map[i+y][j+x] = PJ_EN_PUNTO
                            new_map[i][j] = OBJETIVO
                        if hay_caja(grilla,j+x,i+y) and not hay_pared(grilla,j+2*x,i+2*y) and not hay_caja(grilla,j+2*x,i+2*y):
                            new_map = caja_movimiento(new_map,j,i,x,y)
                            new_map[i][j] = OBJETIVO
                
                if not hay_objetivo(grilla,j,i):
                    new_map = caja_movimiento(new_map,j,i,x,y)
                    if not hay_objetivo(grilla,j+x,i+y) and not hay_pared(grilla,j+x,i+y) and not hay_caja(grilla,j+x,i+y):
                        new_map[i+y][j+x] = PJ
                        new_map[i][j] = VACIO

    return new_map