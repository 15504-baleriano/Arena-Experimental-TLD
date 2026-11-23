import cv2
from tkinter import *
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
import winsound
import serial
import time
from tkinter import filedialog
import csv
import serial
import sys

import serial.tools.list_ports


#Función para conectar automáticamente al puerto de Arduino
def conectarArduino():

    serPort = ""
    int1 = 0
    str1 = ""
    str2 = ""
    global arduino

    # Find Live Ports
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
       print(p) # This causes each port's information to be printed out.
               # To search this p data, use p[1].
       print(serial.tools.list_ports.comports())
       while int1 < 9:   # Loop checks "COM0" to "COM8" for Adruino Port Info. 

          if "CH340" in p[1]:  # Looks for "CH340" in P[1].
                str2 = str(int1) # Converts an Integer to a String, allowing:
                str1 = "COM" + str2 # add the strings together.

          if "CH340" in p[1] and str1 in p[1]: # Looks for "CH340" and "COM#"
             print ("Found Arduino Uno on " + str1)
             int1 = 9 # Causes loop to end.

          if int1 == 8:
             print( "Arduino UNO not found!")
             sys.exit() # Terminates Script.

          int1 = int1 + 1

    #time.sleep(5)  # Gives user 5 seconds to view Port information -- can be   changed/removed.

    # Establece la conección con el puerto identificado con Arduino
    arduino = serial.Serial(str1, 9600, timeout=10) # Introduce tu velocidad y valor de tiempo de espera.

arduino = None
#conectarArduino()

#Objeto que rastrea al raton
tracker = cv2.legacy.TrackerTLD_create()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#cap = cv2.VideoCapture("videoraton1.mp4")
ret, frame = cap.read()
if not ret:
    print("Error capturando cámara.")
    cap.release()
    exit()

frame_height, frame_width = frame.shape[:2]

# Objeto a rastrear
bbox = cv2.selectROI("Selecciona el objeto a rastrear", frame, False)
tracker.init(frame, bbox)

# Zona principal (3/4 del frame)
zona_w = int(frame_width * 0.85)
zona_h = int(frame_height * 0.85)
zona_x = (frame_width - zona_w) // 2
zona_y = (frame_height - zona_h) // 2

# Colores y sonidos
colores_activos = [(0, 0, 255), (0, 255, 0), (0, 255, 255)]  # Rojo, Verde, Amarillo
azul = (255, 0, 0)
frecuencias_sonido = [440, 523, 659]
color_default = (255, 0, 0)
color_activo_actual = color_default
comandoarduino = [['g', 'a', 'h'],['s', 'd', 'f']]
cuadro_activado=None
lado=0 #zona izquierda activa.

# Variables de control
ultimo_cuadro_activado = None
tiempo_ultimo_sonido = 0

folder_path = ""

zona_definida = True
resizing = False
resize_margin = 10
corner_clicked = None

start_time = time.time()
horaIni = time.time()
ConteoSegundosInicio = time.time()
ciclo=1
ultimo_segundo_guardado = -1
datos_rastreo = []

iniciar_Exp=False;


    
def finalizar():
    global cap
    cap.release()
    iniciar_Exp=False;
    # Guardar en CSV
    with open(folder_path.get() + "rastreo_datos.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Ciclo", "Segundo", "X", "Y", "Transcurrido (s)"])
        writer.writerows(datos_rastreo)

def iniciar():
    global iniciar_Exp;
    iniciar_Exp=True;

def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    print(filename)

root = tk.Tk()
root.state('zoomed')
root.title("Seguimiento de objeto")
marco = tk.LabelFrame(root, text="Configuración del experimento",font=("Comic Sans", 12,"bold"),width=200)
#marco.config(bd=2,pady=5)
marco.place(x=10, y=10)

label_ciclos=tk.Label(marco,text="Ciclos: ",font=("Comic Sans", 12,"bold")).grid(row=0,column=0,sticky='s',padx=5,pady=8)
txtCiclos=Entry(marco,width=10)
txtCiclos.focus()
txtCiclos.grid(row=0, column=1, padx=5, pady=8)

label_segundos=tk.Label(marco,text="Segundos por Ciclo: ",font=("Comic Sans", 12,"bold")).grid(row=0,column=2,sticky='s',padx=5,pady=8)
txtSegundos=Entry(marco,width=10)
txtSegundos.grid(row=0, column=3, padx=5, pady=8)

label_ruta=tk.Label(marco,text="Ruta archivo CSV: ",font=("Comic Sans", 12,"bold")).grid(row=0,column=4,sticky='s',padx=5,pady=8)

folder_path = StringVar()
lbl1 = tk.Label(master=marco,textvariable=folder_path)
lbl1.grid(row=0, column=5)
button2 = tk.Button(marco,text="Directorio", command=browse_button)
button2.grid(row=0, column=6)

btnIniciar = tk.Button(root, text="Iniciar", width=40, command=iniciar)
btnIniciar.place(x=10, y=100)
btnFinalizar = tk.Button(root, text="Finalizar", width=40, command=finalizar)
btnFinalizar.place(x=300, y=100)

lblTiempo = tk.Label(root, text="Ciclo 1:")
lblTiempo.place(x=10, y=130)
label_video = tk.Label(root)
label_video.place(x=10, y=150)

marcoTabla = tk.LabelFrame(root, text="Datos de rastreo", font=("Comic Sans", 12, "bold"), width=500)
marcoTabla.place(x=700, y=150)

style = ttk.Style()
style.theme_use("default")

# Define la fuente personalizada
fuente_personalizada = ("Comic Sans MS", 12)

# Aplica al Treeview
style.configure("Treeview", font=fuente_personalizada, rowheight=28)
style.configure("Treeview.Heading", font=("Comic Sans MS", 13, "bold"))

########## Tabla para visualizar datos de rastreo ###################
tree = ttk.Treeview(marcoTabla, columns=("ciclo", "seg", "x", "y", "transcurrido"), show="headings", height=15)
tree.heading("ciclo", text="Ciclo")
tree.heading("seg", text="Segundo")
tree.heading("x", text="X")
tree.heading("y", text="Y")
tree.heading("transcurrido", text="Transcurrido (s)")

tree.column("ciclo", width=60)
tree.column("seg", width=80)
tree.column("x", width=80)
tree.column("y", width=80)
tree.column("transcurrido", width=150)

tree.pack()
########################################################


def get_corner(x, y):
    corners = {
        'nw': (zona_x, zona_y),
        'ne': (zona_x + zona_w, zona_y),
        'sw': (zona_x, zona_y + zona_h),
        'se': (zona_x + zona_w, zona_y + zona_h),
    }
    for name, (cx, cy) in corners.items():
        if abs(x - cx) < resize_margin and abs(y - cy) < resize_margin:
            return name
    return None

def mouse_move(event):
    global resizing, corner_clicked
    corner = get_corner(event.x, event.y)
    if not resizing:
        if corner:
            cursor_map = {
                'nw': "top_left_corner",
                'ne': "top_right_corner",
                'sw': "bottom_left_corner",
                'se': "bottom_right_corner"
            }
            label_video.config(cursor=cursor_map.get(corner, "arrow"))
        else:
            label_video.config(cursor="arrow")
    elif resizing and corner_clicked:
        resize_rectangle(event.x, event.y)

def mouse_down(event):
    global resizing, corner_clicked
    corner = get_corner(event.x, event.y)
    if corner:
        resizing = True
        corner_clicked = corner

def mouse_up(event):
    global resizing, corner_clicked
    resizing = False
    corner_clicked = None

def resize_rectangle(mx, my):
    global zona_x, zona_y, zona_w, zona_h, corner_clicked
    min_size = 60
    if corner_clicked == 'se':
        zona_w = max(mx - zona_x, min_size)
        zona_h = max(my - zona_y, min_size)
    elif corner_clicked == 'nw':
        new_x = min(mx, zona_x + zona_w - min_size)
        new_y = min(my, zona_y + zona_h - min_size)
        zona_w += zona_x - new_x
        zona_h += zona_y - new_y
        zona_x = new_x
        zona_y = new_y
    elif corner_clicked == 'ne':
        new_y = min(my, zona_y + zona_h - min_size)
        zona_w = max(mx - zona_x, min_size)
        zona_h += zona_y - new_y
        zona_y = new_y
    elif corner_clicked == 'sw':
        new_x = min(mx, zona_x + zona_w - min_size)
        zona_h = max(my - zona_y, min_size)
        zona_w += zona_x - new_x
        zona_x = new_x

def verificar_colision(bbox_actual, cuadros):
    x_obj, y_obj, w_obj, h_obj = bbox_actual
    centro_obj = (x_obj + w_obj // 2, y_obj + h_obj // 2)
    for i, (x1, y1, x2, y2) in enumerate(cuadros):
        if x1 <= centro_obj[0] <= x2 and y1 <= centro_obj[1] <= y2:
            return i
    return None

def mostrar_frame():
    global ultimo_cuadro_activado, tiempo_ultimo_sonido, color_activo_actual
    global ConteoSegundosInicio
    global ciclo
    global ultimo_segundo_guardado
    global lado
    global cuadro_activado
    ret, frame = cap.read()
    encenderBebedero=True
    if not ret:
        return

    #frame = cv2.resize(frame, (1280,720))
    cuadros_izquierda = []
    cuadros_derecha = []

    if zona_definida:
        # Dibujar zona principal
        cv2.rectangle(frame, (zona_x, zona_y), (zona_x + zona_w, zona_y + zona_h), azul, 2)

        lado_cuadro = zona_h // 3
        espacio_total = 2 * lado_cuadro + 50
        x_inicio = zona_x + (zona_w - espacio_total) // 2

        x_izquierda = x_inicio
        x_derecha = x_inicio + lado_cuadro + 50

        if (ciclo % 2 == 1):
            for i in range(3):
                y1 = zona_y + i * lado_cuadro
                y2 = y1 + lado_cuadro
                cuadros_izquierda.append((x_izquierda, y1, x_izquierda + lado_cuadro, y2))
                cv2.rectangle(frame, (x_izquierda, y1), (x_izquierda + lado_cuadro, y2), colores_activos[i], 2)

            for i in range(3):
                y1 = zona_y + i * lado_cuadro
                y2 = y1 + lado_cuadro
                cuadros_derecha.append((x_derecha, y1, x_derecha + lado_cuadro, y2))
                cv2.rectangle(frame, (x_derecha, y1), (x_derecha + lado_cuadro, y2), color_activo_actual, 2)
        else:
            for i in range(3):
                y1 = zona_y + i * lado_cuadro
                y2 = y1 + lado_cuadro
                cuadros_izquierda.append((x_izquierda, y1, x_izquierda + lado_cuadro, y2))
                cv2.rectangle(frame, (x_izquierda, y1), (x_izquierda + lado_cuadro, y2), color_activo_actual, 2)

            for i in range(3):
                y1 = zona_y + i * lado_cuadro
                y2 = y1 + lado_cuadro
                cuadros_derecha.append((x_derecha, y1, x_derecha + lado_cuadro, y2))
                cv2.rectangle(frame, (x_derecha, y1), (x_derecha + lado_cuadro, y2), colores_activos[i], 2)
    segundos = int(time.time() - ConteoSegundosInicio)
    success, bbox_actual = tracker.update(frame)
    if success and iniciar_Exp:
        x, y, w, h = map(int, bbox_actual)
        cx, cy = x + w // 2, y + h // 2
        
        cv2.circle(frame,(cx,cy), 5, 255, -1)
        if segundos != ultimo_segundo_guardado:
            ultimo_segundo_guardado = segundos
            tiempo_total = int(time.time() - start_time)
            datos_rastreo.append((ciclo, segundos, cx, cy, tiempo_total))
            tree.insert("", "end", values=(ciclo, segundos, cx, cy, tiempo_total))

        if zona_x <= cx <= zona_x + zona_w and zona_y <= cy <= zona_y + zona_h:
            cv2.rectangle(frame, (x, y), (x + w, y + h), azul, 2)

            if(ciclo % 2 == 1):
                cuadro_activado = verificar_colision(bbox_actual, cuadros_izquierda)

                if cuadro_activado is not None and cuadro_activado != ultimo_cuadro_activado:
                    color_activo_actual = colores_activos[cuadro_activado]
                    winsound.Beep(frecuencias_sonido[cuadro_activado], 300)
                    #arduino.write(comandoarduino[0][cuadro_activado].encode())
                    #cv2.putText(frame,str(comandoarduino[0][cuadro_activado]),(cx,cy),cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0))
                    lado=0
                    ultimo_cuadro_activado = cuadro_activado
            else:
                cuadro_activado = verificar_colision(bbox_actual, cuadros_derecha)

                if cuadro_activado is not None and cuadro_activado != ultimo_cuadro_activado:
                    color_activo_actual = colores_activos[cuadro_activado]
                    winsound.Beep(frecuencias_sonido[cuadro_activado], 300)
                    #arduino.write(comandoarduino[1][cuadro_activado].encode())
                    #cv2.putText(frame,str(comandoarduino[1][cuadro_activado]),(cx,cy),cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0))
                    lado=1
                    ultimo_cuadro_activado = cuadro_activado
        else:
            # No se procesa si el objeto está fuera de la zona
            pass

    
    lblTiempo["text"]=str("Ciclo: "+str(ciclo)+ ", tiempo: "+ str(segundos))
    if(cuadro_activado is not None):
        if(cuadro_activado is not None):
            if(ciclo % 2 == 1):
                cv2.putText(frame,str(comandoarduino[0][cuadro_activado]),(cx,cy),cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0))
            else:
                cv2.putText(frame,str(comandoarduino[1][cuadro_activado]),(cx,cy),cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0))


    if segundos == 22 and encenderBebedero:
        encenderBebedero=False
        #if(cuadro_activado is not None):
            #if(ciclo % 2 == 1):
                #arduino.write(comandoarduino[0][cuadro_activado].encode())
            #else:
                #arduino.write(comandoarduino[1][cuadro_activado].encode())

    if(segundos >= 30):
        encenderBebedero=True
        ConteoSegundosInicio= time.time()
        ciclo+=1
        color_activo_actual = color_default
        #arduino.write(comandoarduino[lado][ultimo_cuadro_activado].encode())
        ultimo_cuadro_activado=None
        #colorActivo=None
        #arduino.write(b'0')

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(frame_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)
    label_video.imgtk = img_tk
    label_video.configure(image=img_tk)
    root.after(15, mostrar_frame)

# Eventos
label_video.bind("<Motion>", mouse_move)
label_video.bind("<ButtonPress-1>", mouse_down)
label_video.bind("<ButtonRelease-1>", mouse_up)

# Ejecutar
mostrar_frame()
root.mainloop()

# Limpiar
cap.release()
cv2.destroyAllWindows()
