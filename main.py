import soko
import gamelib
import clase


'''___________________________________________ Mapa __________________________________________________________'''


def niveles():
    '''Busca y abre el archivo "niveles.txt" y lo transforma en un diccionario
       donde la clave es el numero del nivel y el valor es el mapa listo para jugar, y esto se hace para cada nivel.'''

    resultado = {}
    nivel = 1
    buscador = (f'Level {nivel}')            
    try:
        with open('niveles.txt') as archivo:
            lineas = archivo.readlines()
            
            for linea in lineas:
                if linea == '\n':
                    resultado[nivel] = soko.crear_grilla(resultado[nivel])
                    nivel += 1
                else:    
                    linea = linea.rstrip()

                    if linea.startswith(' ') or linea.startswith('#'):
                        resultado[nivel] = resultado.get(nivel, [])
                        resultado[nivel].append(linea)         
                        
    except FileNotFoundError:
        return gamelib.say('El archivo "niveles.txt" no se a encontrado')
    
    return resultado


'''______________________________________________ Teclas (y relacionados) ______________________________________________________ '''


def teclas():
    diccionario_teclas = {}
    try:

        with open('teclas.txt') as archivo:
            for linea in archivo:
                linea = linea.rstrip()
                linea = linea.split(' = ')
                if len(linea) == 2:
                    diccionario_teclas[linea[1]] = diccionario_teclas.get(linea[1], [])
                    diccionario_teclas[linea[1]].append(linea[0])

    except FileNotFoundError:
        return gamelib.say('El archivo "teclas.txt" no se a encontrado')

    resultado = {}
    for clave in diccionario_teclas:
        for valor in diccionario_teclas[clave]:
            resultado[valor] = clave

    return resultado


def _teclas_main(diccionario_actual, diccionario_movimientos, diccionario_niveles, tecla):
    juego = diccionario_actual['grilla']
    accion = diccionario_movimientos[tecla]

    if accion == 'SALIR':
        return diccionario_actual, 'salir'

    if accion == 'REINICIAR':

        juego = diccionario_niveles[diccionario_actual['nivel']]
        diccionario_actual['grilla'] = juego

        diccionario_actual = _inicializar_guardados(diccionario_actual['nivel'], juego)

        return diccionario_actual, 'REINICIAR'

    if accion == 'CONTROLES':
        return diccionario_actual, 'controles'
    
    if accion == 'LEYENDA':
        return diccionario_actual, 'leyenda'

    if accion == 'DESHACER':
        diccionario_actual = deshacer(diccionario_actual)
        if juego == diccionario_actual['grilla']:
            return diccionario_actual, None
        return diccionario_actual, 'deshacer'

    if accion == 'REHACER':
        diccionario_actual = rehacer(diccionario_actual)
        return diccionario_actual, None

    if accion == 'BACKTRACKING':
        diccionario_actual = _revisar(diccionario_actual)

        juego = devolver_pistas(diccionario_actual)
        diccionario_actual['grilla'] = juego
        diccionario_actual['deshacer'].apilar(juego)

        diccionario_actual = _revisar(diccionario_actual)

        return diccionario_actual, 'pista'
        
    if accion in ('NORTE', 'SUR', 'ESTE', 'OESTE'): 
        diccionario_actual = _revisar(diccionario_actual)

        diccionario_actual['grilla'] = soko.mover(juego, accion)

        diccionario_actual = _revisar(diccionario_actual)

        return diccionario_actual, None

'''___________________________________________ Movimiento (y relacionados) __________________________________________________________'''

def _revisar(diccionario_actual): 
    '''Modifica el diccionario_actual dependiendo la accion y el momento en el que el jugador se mueve'''
    juego = diccionario_actual['grilla']
    d = diccionario_actual['deshacer']
    r = diccionario_actual['rehacer']
    p = diccionario_actual['pistas']
    if d.esta_vacia():
        d.apilar(juego)
    if d.ver_tope() == juego:
        return diccionario_actual
    if d.ver_tope() != juego:
        d.apilar(juego)
    if not r.esta_vacia():
        diccionario_actual['rehacer'] = clase.Pila()
    if not p.esta_vacia():
        diccionario_actual['pistas'] = clase.Pila()
    return diccionario_actual

def _buscar_solucion(estado_inicial, diccionario_actual):
    visitados = set() 
    return _backtrack(estado_inicial, visitados, diccionario_actual)

def _estado_inmutable(estado): 
    '''Convierte al estado en un nivel potencial e inmutable'''
    resultado = ()
    for fila in estado:
        linea = ''.join(fila)
        resultado += (linea,)
    return resultado

def _agregar(visitados, estado):
    nuevo = _estado_inmutable(estado)
    visitados.add(nuevo)

def _pertenece(visitados, nuevo_estado):
    buscar = _estado_inmutable(nuevo_estado)
    if buscar in visitados:
        return True


def _backtrack(estado, visitados, diccionario_actual):
    try: 
        _agregar(visitados, estado)                            
        
        if soko.juego_ganado(estado): 
            return True, ()

        for a in ('NORTE', 'SUR', 'ESTE', 'OESTE'):          
            nuevo_estado = soko.mover(estado, a)

            if _pertenece(visitados, nuevo_estado):            
                continue

            solución_encontrada, acciones = _backtrack(nuevo_estado, visitados, diccionario_actual)

            if solución_encontrada == None and acciones == None:
                return None, None

            if solución_encontrada:
                return True, acciones + (a,)                

        return False, ()

    except RecursionError:
        return None, None

def devolver_pistas(diccionario_actual):
    p = diccionario_actual['pistas']
    juego = diccionario_actual['grilla']

    if p.esta_vacia():
        booleano, solucion_acciones = _buscar_solucion(juego, diccionario_actual)

        if booleano == None and solucion_acciones == None:
            gamelib.say('Ha ocurrido un problema, no se han encontrado pistas')
            return juego

        for i in range(len(solucion_acciones)):
            p.apilar(solucion_acciones[i])
    
    return soko.mover(juego, p.desapilar())

def deshacer(diccionario_actual):
    juego = diccionario_actual['grilla']
    d = diccionario_actual['deshacer']

    if diccionario_actual['rehacer'].esta_vacia():
        diccionario_actual['rehacer'].apilar(juego)
    if d.esta_vacia():
        return diccionario_actual
    else:
        if juego == d.ver_tope():
            d.desapilar()
            if not d.esta_vacia():
                juego = d.desapilar()    
        else:
            juego = d.desapilar()

        diccionario_actual['rehacer'].apilar(juego)

    diccionario_actual['grilla'] = juego
    return diccionario_actual

def rehacer(diccionario_actual):
    rehacer = diccionario_actual['rehacer']
    juego = diccionario_actual['grilla']
    if diccionario_actual['deshacer'].esta_vacia():
        diccionario_actual['deshacer'].apilar(juego)

    if rehacer.esta_vacia():
        return diccionario_actual

    else:
        if not rehacer.esta_vacia():
            if rehacer.ver_tope() == juego:
                    rehacer.desapilar()
                    if not rehacer.esta_vacia():
                        juego = rehacer.desapilar()
            else: 
                juego = rehacer.desapilar()

            diccionario_actual['grilla'] = juego
            diccionario_actual['deshacer'].apilar(juego)
            return diccionario_actual
        

'''___________________________________________ Pantalla (y relacionados) __________________________________________________________'''

def juego_mostrar(grilla):
    """Actualizar la ventana"""

    
    imagen_juego = {soko.PARED:'img/wall.gif', soko.CAJA:'img/box.gif', soko.VACIO:'img/ground.gif', soko.OBJETIVO:'img/goal.gif', soko.PJ:'img/player.gif', soko.CAJA_EN_PUNTO:('$','.'), soko.PJ_EN_PUNTO:('@','.')}
    celda_dim = 64

    for i in range (len(grilla)):
        for j in range (len(grilla[i])):

            
            gamelib.draw_image(imagen_juego[' '], j*celda_dim, i*celda_dim) 
            
            if soko.hay_objetivo(grilla, j, i) and (soko.hay_jugador(grilla, j, i) or soko.hay_caja(grilla, j, i)): 

                for objeto in imagen_juego[grilla[i][j]]:
                    gamelib.draw_image(imagen_juego[objeto], j*celda_dim, i*celda_dim)

            else: 

                gamelib.draw_image(imagen_juego[grilla[i][j]], j*celda_dim, i*celda_dim)

     
def pantalla_gamelib(grilla):
    '''Dadao un mapa te devuelve las proporciones optimas de la pantalla en pixeles (alto y ancho)'''
    alto_grilla = len(grilla)
    largo_grilla = 0

    for i in grilla:
        if len(i) > largo_grilla:
            largo_grilla = len(i)

    alto_ventana = 64 * alto_grilla 
    ancho_ventana = 64 * largo_grilla

    return alto_ventana, ancho_ventana

def vida(n):
    res = '' 
    dato = '❤'
    for i in range(n):
        res += ' ' + dato
    return res

'''___________________________________________ Main __________________________________________________________'''

def _inicializar_main():
    ganado = None
    diccionario_movimientos = teclas()
    diccionario_niveles = niveles()
    nivel = 1
    vida = 5
    juego = diccionario_niveles[nivel]

    return ganado, nivel, vida, juego, diccionario_movimientos, diccionario_niveles


def _inicializar_guardados(nivel, juego):
    diccionario_actual = {}
    diccionario_actual['nivel'] = nivel
    diccionario_actual['grilla'] = juego
    diccionario_actual['deshacer'] = clase.Pila()
    diccionario_actual['rehacer'] = clase.Pila()
    diccionario_actual['pistas'] = clase.Pila()
    diccionario_actual['deshacer'].apilar(juego)

    return diccionario_actual 

MENSAJE_INICIO = '''
    Bienvenido a Sokoban: 

    Este es un videojuego estilo puzzle o rompecabezas en el que el jugador empuja un conjunto de cajas en un depósito, con el objetivo de ubicar las cajas en lugares específicos. Al comenzar la partida tendras 5 corazones que iras perdiendo a medida que vayas reiniciando el nivel, pero no te preocupes que al pasar de escenario las iras recuperando, eso ... si no perdes antes. Para evitar que reinicies tenes las ayudas, esta herramienta sirve para volver hacia atras tus movimientos y para ir hacia adelante en el tiempo, con las pistas, pero son limitadas las ayudas, por lo que deberas usarlas con cuidado. Como se que te estas aburriendo de leer esto que esperas... segui con tu partida.'''
    
CONTROLES = '''
    Los controles para jugar son: 

    ↑ = NORTE       w = NORTE
    ← = OESTE       a = OESTE
    ↓ = SUR             s = SUR
    → = ESTE          d = ESTE
    
    r = REINICIAR
    h = HISTORIA Y JUGABILIDAD
    1 = DESHACER
    2 = REHACER
    Space = PISTA (MOVIMIENTO)  
    Escape = SALIR
    '''


def main():
    ganado, nivel, v, juego, diccionario_movimientos, diccionario_niveles = _inicializar_main()
    diccionario_actual = _inicializar_guardados(nivel, juego)

    while gamelib.is_alive():

        alto_ventana, ancho_ventana = pantalla_gamelib(juego)
        gamelib.resize(ancho_ventana, alto_ventana)

        gamelib.draw_begin()

        juego_mostrar(juego)
        gamelib.draw_text(vida(v), (ancho_ventana - (10*v)), 20)
        gamelib.draw_text('Nivel: ' + str(nivel), 40, 20, 15, 15, 15)
        gamelib.draw_text('Tab para controles', 70, 40)
        if nivel % 5 == 0:
            gamelib.draw_text('Punto de guardado', (ancho_ventana//2), 20)

        gamelib.draw_end()
        
        ev = gamelib.wait(gamelib.EventType.KeyPress)
        if not ev:
            break

        tecla = ev.key
        if not tecla in diccionario_movimientos:
            continue
        diccionario_actual, dato = _teclas_main(diccionario_actual, diccionario_movimientos, diccionario_niveles, tecla)
        
        if dato == 'salir':
            break
        
        if dato == 'controles':
            gamelib.say(CONTROLES)
        
        if dato == 'leyenda':
            gamelib.say(MENSAJE_INICIO)
    
        if dato == 'REINICIAR':
            v -= 1
            if v == 0:
                gamelib.say('Has perdido')
                for i in range(nivel-5,nivel):
                    if i%5 == 0:
                        nivel = i
                if nivel <= 0:
                    nivel = 1
                juego = diccionario_niveles[nivel]
                diccionario_actual = _inicializar_guardados(nivel, juego)
                v = 5

        juego = diccionario_actual['grilla']

        ganado = soko.juego_ganado(diccionario_actual['grilla'])

        if ganado and nivel <= len(diccionario_niveles):

            nivel += 1
            if v < 5:
                v += 1
            juego = diccionario_niveles[nivel]
            diccionario_actual = _inicializar_guardados(nivel, juego)

        if nivel > len(diccionario_niveles):
            gamelib.say('Enhorabuena, usted a completado el Sokoban')
            return

gamelib.init(main)
