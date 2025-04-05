# ***********************************************************************************
#   ExibePoligonos.py
#       Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
#   Este programa cria um conjunto de INSTANCIAS
#   Para construir este programa, foi utilizada a biblioteca PyOpenGL, disponível em
#   http://pyopengl.sourceforge.net/documentation/index.html
#
#   Sugere-se consultar também as páginas listadas
#   a seguir:
#   http://bazaar.launchpad.net/~mcfletch/pyopengl-demo/trunk/view/head:/PyOpenGL-Demo/NeHe/lesson1.py
#   http://pyopengl.sourceforge.net/documentation/manual-3.0/index.html#GLUT
#
#   No caso de usar no MacOS, pode ser necessário alterar o arquivo ctypesloader.py,
#   conforme a descrição que está nestes links:
#   https://stackoverflow.com/questions/63475461/unable-to-import-opengl-gl-in-python-on-macos
#   https://stackoverflow.com/questions/6819661/python-location-on-mac-osx
#   Veja o arquivo Patch.rtf, armazenado na mesma pasta deste fonte.
# ***********************************************************************************

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Poligonos import *
from InstanciaBZ import *
from Bezier import *
from ListaDeCoresRGB import *
import numpy as np  # 
# ***********************************************************************************

# Modelos de Objetos
MeiaSeta = Polygon()
Mastro = Polygon()

# Limites da Janela de Seleção
Min = Ponto()
Max = Ponto()

# lista de instancias do Personagens
Personagens = [] 

# ***********************************************************************************
# Lista de curvas Bezier
Curvas = []

# Variaveis de controle da curva Bezier
Curvas = []
PontosClicados = []
atual = Ponto()
PoligonoDeControle = None
mostra = True
cont = 0
deriv = False
#controle mouse
isdown = False
PosAtualDoMouse = Ponto(0,0)
continuos = False
#**********************************************************************
# Lista de mensagens
#**********************************************************************
Mensagens = [
    "Clique o primeiro ponto.",
    "Clique o segundo ponto.",
    "Clique o terceiro ponto."
]

angulo = 0.0
desenha = True


# **********************************************************************
# Imprime o texto S na posicao (x,y), com a cor 'cor'
# **********************************************************************
def PrintString(S: str, x: int, y: int, cor: tuple):
    defineCor(cor) 
    glRasterPos3f(x, y, 0) # define posicao na tela
    
    for c in S:
        # GLUT_BITMAP_HELVETICA_10
        # GLUT_BITMAP_TIMES_ROMAN_24
        # GLUT_BITMAP_HELVETICA_18
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(c)) # type: ignore


# **********************************************************************
# Imprime as coordenadas do ponto P na posicao (x,y), com a cor 'cor'
# **********************************************************************
def ImprimePonto(P: Ponto, x: int, y: int, cor: tuple):
    S = f'({P.x:.2f}, {P.y:.2f})'
    PrintString(S, x, y, cor)

# **********************************************************************
#  Imprime as mensagens do programa.
#  Funcao chamada na 'display'
# **********************************************************************
def ImprimeMensagens():
    PrintString(Mensagens[len(PontosClicados)], -14, 13, White)

    if len(PontosClicados) > 0:
        PrintString("Ultimo ponto clicado: ", -14, 11, Red)
        ImprimePonto(PontosClicados[len(PontosClicados)-1], -1,11, Red)

# **********************************************************************
def animate():
    glutPostRedisplay()
     

# ***********************************************************************************
def reshape(w,h):
    global Min, Max

    # Reseta sistema de coordenadas antes de modifica-lo
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Define a area a ser ocupada pela area OpenGL dentro da Janela
    glViewport(0, 0, w, h)
    
    # Define os limites logicos da area OpenGL dentro da Janela
    glOrtho(Min.x, Max.x, Min.y, Max.y, -10, 10)

    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

# **************************************************************
def DesenhaEixos():
    global Min, Max

    Meio = Ponto(); 
    Meio.x = (Max.x+Min.x)/2
    Meio.y = (Max.y+Min.y)/2
    Meio.z = (Max.z+Min.z)/2

    glBegin(GL_LINES)
    #  eixo horizontal
    glVertex2f(Min.x,Meio.y)
    glVertex2f(Max.x,Meio.y)
    #  eixo vertical
    glVertex2f(Meio.x,Min.y)
    glVertex2f(Meio.x,Max.y)
    glEnd()

# **************************************************************
def CarregaModelos():
    global MeiaSeta, Mastro
    MeiaSeta.LePontosDeArquivo("MeiaSeta.txt")
    Mastro.LePontosDeArquivo("Mastro.txt")

# **************************************************************
def CriaCurvas():
    global Curvas
    C = Bezier(PontosClicados[0], PontosClicados[1], PontosClicados[2])
    Curvas.append(C)

# ***********************************************************************************
def init():
    global Min, Max
    # Define a cor do fundo da tela (AZUL)
    glClearColor(0,0,0,0)

    CarregaModelos()

    d:float = 15
    Min = Ponto(-d,-d)
    Max = Ponto(d,d)

# ***********************************************************************************
def DesenhaLinha (P1: Ponto, P2: Ponto):
    glColor(SkyBlue)
    glBegin(GL_LINES)
    glVertex3f(P1.x,P1.y,P1.z)
    glVertex3f(P2.x,P2.y,P2.z)
    glEnd()

# ***********************************************************************************
def DesenhaCurvas():
    for I in Curvas:
        defineCor(DarkPurple)
        I.Traca()
        defineCor(SkyBlue)
        if(mostra):
            I.TracaPoligonoDeControle()

# **********************************************************************
def DesenhaPontos():
    defineCor(Yellow)
    glPointSize(4)
    glBegin(GL_POINTS)

    for Ponto in PontosClicados:
        glVertex2f(Ponto.x, Ponto.y)
    glEnd()
    glPointSize(1)

# **********************************************************************
def DesenhaMenu():
    PrintString("Modo Continuidade", -14, 13, White)
    PrintString(str(cont), 0, 13, White)

# ***********************************************************************************
def display():

    global PontosClicados
    global PosAtualDoMouse
    global atual
    global continuos
	# Limpa a tela coma cor de fundo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Define os limites lógicos da área OpenGL dentro da Janela
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	# Coloque aqui as chamadas das rotinas que desenham os objetos
	# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    glLineWidth(1)
    defineCor(White)

    DesenhaMenu()
    #DesenhaEixos()

    glLineWidth(3)
    defineCor(Red)
    
    if continuos and mostra:
        DesenhaLinha(PontosClicados[0],PosAtualDoMouse)
    
    if len(PontosClicados) == 2:
        DesenhaLinha(PontosClicados[0],PontosClicados[1])


    DesenhaPontos()
    DesenhaCurvas()
    #ImprimeMensagens()

    glutSwapBuffers()


# ***********************************************************************************
# The function called whenever a key is pressed. 
# Note the use of Python tuples to pass in: (key, x, y)
# ESCAPE = '\033'
# ***********************************************************************************
ESCAPE = b'\x1b'
def keyboard(*args):
    global desenha
    global mostra
    global cont

    # If escape is pressed, kill everything.
    if args[0] == b' ':
        desenha = not desenha
    if args[0] == ESCAPE:
        os._exit(0)

    if args[0] ==  b'q':
      mostra = not mostra

    if args[0] ==  b'c':
      Curvas.clear()
      PontosClicados.clear()
      
    if args[0] ==  b'w':
        if cont <2:
          cont+=1
        else:
            cont = 0

        PontosClicados.clear()
    
        if cont > 0 and len(Curvas) > 0:

            PontosClicados.append(Curvas[len(Curvas)-1].Coords[2])
    # Forca o redesenho da tela
    glutPostRedisplay()

# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )   
# **********************************************************************
def arrow_keys(a_keys: int, x: int, y: int):
    if a_keys == GLUT_KEY_UP:         # Se pressionar UP
        glutFullScreen()
        
    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        glutPositionWindow(50, 50)
        glutReshapeWindow(700, 500)
        
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        pass
        
    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        pass

    glutPostRedisplay()

# **********************************************************************
# Converte as coordenadas do ponto P de coordenadas de tela para
# coordenadas de universo (sistema de referencia definido na glOrtho
# (ver funcao reshape)
# Este codigo e baseado em http://hamala.se/forums/viewtopic.php?t=20
# **********************************************************************
def ConvertePonto(P: Ponto) -> Ponto:
    # Obtém as matrizes e o viewport
    viewport = glGetIntegerv(GL_VIEWPORT)
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)

    if viewport is None or modelview is None or projection is None:
        print("Erro: Falha ao obter matrizes ou viewport!")
        return P  # Retorna o ponto original se houver erro

    # Ajuste do eixo Y (OpenGL tem origem no canto inferior esquerdo)
    P.y = viewport[3] - P.y

    # Captura a profundidade do pixel (garantindo um único valor float)
    wz = glReadPixels(P.x, P.y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)

    # Garante que `wz` é um float válido
    if isinstance(wz, np.ndarray):  # Se for um array, pega o primeiro valor
        wz = float(wz[0])

    if wz is None or not (0.0 <= wz <= 1.0):  # Verifica se `wz` é válido
        print(f"Erro: Profundidade inválida lida ({wz})!")
        return P  # Retorna o ponto original se a leitura falhar

    # Converte as coordenadas de tela para coordenadas do mundo
    ox, oy, oz = gluUnProject(float(P.x), float(P.y), wz, modelview, projection, viewport)

    return Ponto(ox, oy, oz)

def getPontoDeriv(howfar):

    x = (1-howfar)*Curvas[len(Curvas)-1].Coords[1].x+(howfar)*Curvas[len(Curvas)-1].Coords[2].x
    y = (1-howfar)*Curvas[len(Curvas)-1].Coords[1].y+(howfar)*Curvas[len(Curvas)-1].Coords[2].y

    return Ponto(x,y)
    
def superColide(p:Ponto):

    global Curvas
    p =  ConvertePonto(p)
    margin = 3

    for i in range (len(Curvas)):

        if not verifyPoint(p,i):
            continue

        a = miniColide(Curvas[i].Coords[0].x,Curvas[i].Coords[0].y,Curvas[i].Coords[1].x,Curvas[i].Coords[1].y,p.x,p.y) 
        b = miniColide(Curvas[i].Coords[1].x,Curvas[i].Coords[1].y,Curvas[i].Coords[2].x,Curvas[i].Coords[2].y,p.x,p.y) 
        c = miniColide(Curvas[i].Coords[2].x,Curvas[i].Coords[2].y,Curvas[i].Coords[0].x,Curvas[i].Coords[0].y,p.x,p.y)
        print(a,b,c) 

    
        
        if  margin> a > - margin or  margin > b > - margin or margin > c > -margin: 
              return i
        
        
    return  -1

def getValCordmax(i:int):
    global Curvas
    xmax = 0
    xmin = 0
    ymax = 0
    ymin = 0

    for j in range (len(Curvas[i].Coords)):
        if j == 0:
            xmax = Curvas[i].Coords[j].x
            xmin = Curvas[i].Coords[j].x
            ymax = Curvas[i].Coords[j].y   
            ymin = Curvas[i].Coords[j].y
            continue

        if xmin > Curvas[i].Coords[j].x:
            xmin = Curvas[i].Coords[j].x

        if xmax < Curvas[i].Coords[j].x:
            xmax = Curvas[i].Coords[j].x

        if ymin > Curvas[i].Coords[j].y:
            ymin = Curvas[i].Coords[j].y

        if ymax < Curvas[i].Coords[j].y:
            ymax = Curvas[i].Coords[j].y

    return [xmin,xmax,ymin,ymax]
        
def verifyPoint(p:Ponto,i:int):

    x = getValCordmax(i)
    print(x)
    if x[0] < p.x < x[1] and x[2] < p.y < x[3]:

        return True
    
    return False


def miniColide(p1x,p1y,p2x,p2y,x,y):

   D = (x - p1x) * (p2y - p1y) - (y - p1y) * (p2x - p1x)

   return D

# **********************************************************************
# Captura as coordenadas do mouse do mouse sobre a area de
# desenho, enquanto um dos botoes esta sendo pressionado
# **********************************************************************
def Motion(x: int, y: int):
    global PosAtualDoMouse
    global continuos
    PosAtualDoMouse = ConvertePonto(Ponto(x,y))

    if cont ==0 or (cont == 1 and len(Curvas)== 0):
        if len(PontosClicados)> 1:
            
            if len(Curvas)> 0:
                Curvas.pop(len(Curvas)-1)

            if len(PontosClicados) <3:
                    PontosClicados.append(PosAtualDoMouse)
            else:
                PontosClicados.pop(2)
                PontosClicados.append(PosAtualDoMouse)

            CriaCurvas()
            return
        if not continuos:
            PontosClicados.append(ConvertePonto(Ponto(x, y)))
            continuos = True
    elif cont == 1:
        if len(PontosClicados)> 1:
            
            if len(Curvas)> 0:
                Curvas.pop(len(Curvas)-1)

            if len(PontosClicados) <3:
                    PontosClicados.append(PosAtualDoMouse)
            else:
                PontosClicados.pop(2)
                PontosClicados.append(PosAtualDoMouse)

            CriaCurvas()
            return
        if not continuos:
            continuos = True
            
    else:
        return
    
# ***********************************************************************************
# Captura o clique do botao esquerdo do mouse sobre a area de desenho
# ***********************************************************************************
def mouse(button: int, state: int, x: int, y: int):
    global PontosClicados
    global Curvas
    global isdown
    global PosAtualDoMouse
    global atual
    global deriv
    global continuos
    
    atual = ConvertePonto(Ponto(x, y))
    
    if deriv == True:
        print(atual.x)
        PontosClicados.append(getPontoDeriv(1.5))
        deriv = False
        return
    
    if (button == GLUT_RIGHT_BUTTON and mostra):
        x = superColide(Ponto(x, y))
        if x >= 0:
            Curvas.pop(x)

        return
    
    
    if (state == GLUT_UP and len(PontosClicados) < 3): 
        print("oi do clique up")
        if cont == 0 or len(Curvas) == 0 or cont == 1:
            PontosClicados.append(ConvertePonto(Ponto(x, y)))
        continuos  = False
    if (state == GLUT_DOWN): 
         print("oi do clique down")
        
    if len(PontosClicados) == 3:
        CriaCurvas()
        PontosClicados.clear()
        if cont:
            PontosClicados.append(ConvertePonto(Ponto(x, y)))

            if cont == 2:
                deriv = True
                print(deriv)
                          
    glutPostRedisplay()


# ***********************************************************************************
# Programa Principal
# ***********************************************************************************

print("Programa OpenGL")

glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_DEPTH | GLUT_RGB)

# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(500, 500)
glutInitWindowPosition(100, 100)

# Cria a janela na tela, definindo o nome da
# que aparecera na barra de título da janela
wind = glutCreateWindow(b"Animacao com Bezier")

# executa algumas inicializações
init()

# Define que o tratador de evento para
# o redesenho da tela. A funcao "display"
# sera chamada automaticamente quando
# for necessario redesenhar a janela
glutDisplayFunc(display)

# Define que o tratador de evento para
# o invalidacao da tela. A funcao "display"
# sera chamada automaticamente sempre que a
# maquina estiver ociosa (idle)
glutIdleFunc(animate)

# Define que o tratador de evento para
# o redimensionamento da janela. A funcao "reshape"
# sera chamada automaticamente quando
# o usuario alterar o tamanho da janela
glutReshapeFunc(reshape)

# Define que o tratador de evento para
# as teclas. A funcao "keyboard"
# sera chamada automaticamente sempre
# o usuario pressionar uma tecla comum
glutKeyboardFunc(keyboard)

# Define que o tratador de evento para
# as teclas especiais(F1, F2,... ALT-A,
# ALT-B, Teclas de Seta, ...).
# A funcao "arrow_keys" será chamada
# automaticamente sempre o usuário
# pressionar uma tecla especial
glutSpecialFunc(arrow_keys)
glutMouseFunc(mouse)
glutMotionFunc(Motion)

try:
    glutMainLoop()
except SystemExit:
    pass
