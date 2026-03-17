# ====================================================
# IMPORTS
# ====================================================

import tkinter as tk
from functools import partial

# ====================================================
# CLASES DE PIEZAS 
# ====================================================
class Pieza:
    def __init__(self, color, simbolo):
        self.color = color
        self.simbolo = simbolo

    def movimiento_correcto(self, origen, destino, tablero):
        return True
# ====================================================
# CLASES DE SUBPIEZAS 
# ====================================================
class King(Pieza):
    def __init__(self, color):
        simbolo = "♔" if color == "blanco" else "♚"
        super().__init__(color, simbolo)

    def movimiento_correcto(self, origen, destino, tablero):
        x1, y1 = origen
        x2, y2 = destino
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        if max(dx, dy) == 1:
            target = tablero[(x2, y2)]["pieza"]
            return target is None or target.color != self.color
        return False

class Queen(Pieza):
    def __init__(self, color):
        simbolo = "♕" if color == "blanco" else "♛"
        super().__init__(color, simbolo)

    def movimiento_correcto(self, origen, destino, tablero):
        return Rook(self.color).movimiento_correcto(origen, destino, tablero) or \
               Bishop(self.color).movimiento_correcto(origen, destino, tablero)

class Rook(Pieza):
    def __init__(self, color):
        simbolo = "♖" if color == "blanco" else "♜"
        super().__init__(color, simbolo)

    def movimiento_correcto(self, origen, destino, tablero):
        x1, y1 = origen
        x2, y2 = destino
        if x1 != x2 and y1 != y2:
            return False
        if y1 == y2:
            paso = 1 if x2 > x1 else -1
            for x in range(x1 + paso, x2, paso):
                if tablero[(x, y1)]["pieza"]:
                    return False
        if x1 == x2:
            paso = 1 if y2 > y1 else -1
            for y in range(y1 + paso, y2, paso):
                if tablero[(x1, y)]["pieza"]:
                    return False
        target = tablero[(x2, y2)]["pieza"]
        return target is None or target.color != self.color

class Bishop(Pieza):
    def __init__(self, color):
        simbolo = "♗" if color == "blanco" else "♝"
        super().__init__(color, simbolo)

    def movimiento_correcto(self, origen, destino, tablero):
        x1, y1 = origen
        x2, y2 = destino
        if abs(x2 - x1) != abs(y2 - y1):
            return False
        paso_x = 1 if x2 > x1 else -1
        paso_y = 1 if y2 > y1 else -1
        x, y = x1 + paso_x, y1 + paso_y
        while (x, y) != (x2, y2):
            if tablero[(x, y)]["pieza"]:
                return False
            x += paso_x
            y += paso_y
        target = tablero[(x2, y2)]["pieza"]
        return target is None or target.color != self.color

class Knight(Pieza):
    def __init__(self, color):
        simbolo = "♘" if color == "blanco" else "♞"
        super().__init__(color, simbolo)

    def movimiento_correcto(self, origen, destino, tablero):
        x1, y1 = origen
        x2, y2 = destino
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        if (dx, dy) in [(1, 2), (2, 1)]:
            target = tablero[(x2, y2)]["pieza"]
            return target is None or target.color != self.color
        return False

class Pawn(Pieza):
    def __init__(self, color):
        simbolo = "♙" if color == "blanco" else "♟"
        super().__init__(color, simbolo)

    def movimiento_correcto(self, origen, destino, tablero):
        x1, y1 = origen
        x2, y2 = destino
        direccion = -1 if self.color == "blanco" else 1
        if x1 == x2 and y2 - y1 == direccion and tablero[(x2, y2)]["pieza"] is None:
            return True
        if x1 == x2 and ((self.color == "blanco" and y1 == 6) or (self.color == "negro" and y1 == 1)):
            if y2 - y1 == 2*direccion and tablero[(x1, y1+direccion)]["pieza"] is None and tablero[(x2, y2)]["pieza"] is None:
                return True
        if abs(x2 - x1) == 1 and y2 - y1 == direccion:
            target = tablero[(x2, y2)]["pieza"]
            if target and target.color != self.color:
                return True
        return False

# ====================================================
# INTERFAZ GRÁFICA con coordenadas toggleables
# ====================================================
class Tablero_prueba(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Ajedrez")
        self.geometry("760x720")
        self.resizable(False, False)

        self.turno = "blanco"
        self.celdas = {}
        self.seleccion = None

        # Flag para mostrar coordenadas (por defecto True)
        self.mostrar_coordenadas = True

        self.crear_menu()
        self.frame_exterior = tk.Frame(self, bg="#333333", padx=6, pady=6)
        self.frame_exterior.pack(expand=True, fill="both")

        # Marco del tablero
        self.frame_tablero = tk.Frame(self.frame_exterior, bg="#333333")
        self.frame_tablero.grid(row=1, column=1, padx=3, pady=3)

        # Panel derecho compacto con canvas+scrollbar para capturadas
        self.frame_capturados = tk.Frame(self.frame_exterior, bg="#222222")
        self.frame_capturados.grid(row=1, column=2, sticky="n", padx=(8,6), pady=6)

        lbl_title = tk.Label(self.frame_capturados, text="Capturadas", bg="#222222", fg="white", font=("Arial", 11, "bold"))
        lbl_title.pack(anchor="n", pady=(4,6))

        self.canvas_capt = tk.Canvas(self.frame_capturados, bg="#222222", highlightthickness=0, width=140, height=560)
        self.scrollbar = tk.Scrollbar(self.frame_capturados, orient="vertical", command=self.canvas_capt.yview)
        self.canvas_capt.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas_capt.pack(side="left", fill="both", expand=True)
        self.inner_frame = tk.Frame(self.canvas_capt, bg="#222222")
        self.canvas_capt.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", lambda e: self.canvas_capt.configure(scrollregion=self.canvas_capt.bbox("all")))

        lbl_b = tk.Label(self.inner_frame, text="Blancas:", bg="#222222", fg="white", font=("Arial", 10, "bold"))
        lbl_b.grid(row=0, column=0, sticky="w", padx=6, pady=(4,2))
        lbl_n = tk.Label(self.inner_frame, text="Negras:", bg="#222222", fg="white", font=("Arial", 10, "bold"))
        lbl_n.grid(row=0, column=1, sticky="w", padx=6, pady=(4,2))

        self.container_blancas = tk.Frame(self.inner_frame, bg="#222222")
        self.container_blancas.grid(row=1, column=0, padx=6, pady=(2,6))
        self.container_negras = tk.Frame(self.inner_frame, bg="#222222")
        self.container_negras.grid(row=1, column=1, padx=6, pady=(2,6))

        self.capturados = {"blanco": [], "negro": []}

        # Coordenadas (labels) se guardan para poder ocultarlas/actualizarlas
        self.coord_labels = []

        # Crear todo
        self.crear_coordenadas()
        self.crear_tablero()
        self.colocar_piezas_iniciales()
        self.actualizar_tablero()

    # -------------------------
    # MENÚ (añadido toggle de coordenadas)
    # -------------------------
    def crear_menu(self):
        barra = tk.Menu(self)
        self.config(menu=barra)
        menu_archivo = tk.Menu(barra, tearoff=0)
        barra.add_cascade(label="Archivo", menu=menu_archivo)
        # Toggle de coordenadas
        menu_archivo.add_checkbutton(label="Mostrar coordenadas", onvalue=True, offvalue=False,
                                     variable=tk.BooleanVar(value=self.mostrar_coordenadas),
                                     command=self.toggle_coordenadas)
        menu_archivo.add_command(label="Reiniciar", command=self.reiniciar)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.destroy)

    def toggle_coordenadas(self):
        # Cambia flag y actualiza la vista
        self.mostrar_coordenadas = not self.mostrar_coordenadas
        self._dibujar_coordenadas()

    # -------------------------
    # COORDENADAS (estándar: a1 en esquina inferior izquierda)
    # -------------------------
    def crear_coordenadas(self):
        # Crea labels pero no asume visibilidad; se dibujan en _dibujar_coordenadas
        letras = "abcdefgh"
        # Limpiamos lista previa si existe
        for lbl in self.coord_labels:
            lbl.destroy()
        self.coord_labels = []

        # Creamos labels para las 4 filas/columnas exteriores:
        # superior letras, inferior letras, izquierda números, derecha números
        for i in range(8):
            lbl_top = tk.Label(self.frame_exterior, text="", font=("Arial", 10), bg="#333333", fg="white")
            lbl_bottom = tk.Label(self.frame_exterior, text="", font=("Arial", 10), bg="#333333", fg="white")
            lbl_left = tk.Label(self.frame_exterior, text="", font=("Arial", 10), bg="#333333", fg="white")
            lbl_right = tk.Label(self.frame_exterior, text="", font=("Arial", 10), bg="#333333", fg="white")
            self.coord_labels.append((lbl_top, lbl_bottom, lbl_left, lbl_right))

        # Dibujar según flag
        self._dibujar_coordenadas()

    def _dibujar_coordenadas(self):
        # Borra cualquier label previo de coordenadas (si estaban colocados)
        # y vuelve a colocar según self.mostrar_coordenadas
        letras = "abcdefgh"
        # Si no mostrar, ocultar y salir
        if not self.mostrar_coordenadas:
            for lbls in self.coord_labels:
                for lbl in lbls:
                    lbl.grid_forget()
            return

        # Mostrar: colocamos letras arriba/abajo y números izquierda/derecha
        # Importante: la orientación estándar es con 'a' a la izquierda y '1' abajo.
        for i, (lbl_top, lbl_bottom, lbl_left, lbl_right) in enumerate(self.coord_labels):
            letra = letras[i].upper()
            numero = str(8 - i)  # fila 0 -> 8, fila 7 -> 1

            # Top: fila 0 (columna i+1)
            lbl_top.config(text=letra)
            lbl_top.grid(row=0, column=i+1, pady=2)

            # Bottom: fila 2 (columna i+1)
            lbl_bottom.config(text=letra)
            lbl_bottom.grid(row=2, column=i+1, pady=2)

            # Left: fila 1 (fila i)
            lbl_left.config(text=numero)
            lbl_left.grid(row=1, column=0, sticky="e", padx=2)

            # Right: fila 1 (columna 9)
            lbl_right.config(text=numero)
            lbl_right.grid(row=1, column=9, sticky="w", padx=2)

    # -------------------------
    # COLORES
    # -------------------------
    def color_casilla(self, x, y):
        return "#EEEED2" if (x + y) % 2 == 0 else "#769656"

    # -------------------------
    # CREAR BOTONES (tamaño reducido para que quepan mejor)
    # -------------------------
    def crear_tablero(self):
        for y in range(8):
            for x in range(8):
                boton = tk.Button(
                    self.frame_tablero,
                    text="",
                    bg=self.color_casilla(x, y),
                    width=4,
                    height=1,
                    font=("Segoe UI Symbol", 14),
                    relief="flat",
                    command=partial(self.mover_piezas, x, y)
                )
                self.celdas[(x, y)] = {"boton": boton, "pieza": None, "color": self.color_casilla(x, y)}
                boton.grid(row=y, column=x, padx=0, pady=0)

    # -------------------------
    # PIEZAS INICIALES
    # -------------------------
    def colocar_piezas_iniciales(self):
        for pos in self.celdas:
            self.celdas[pos]["pieza"] = None
        for x in range(8):
            self.celdas[(x, 1)]["pieza"] = Pawn("negro")
            self.celdas[(x, 6)]["pieza"] = Pawn("blanco")
        orden = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for x, clase in enumerate(orden):
            self.celdas[(x, 0)]["pieza"] = clase("negro")
            self.celdas[(x, 7)]["pieza"] = clase("blanco")

    # -------------------------
    # ACTUALIZAR CELDA / TABLERO
    # -------------------------
    def actualizar_celda(self, x, y):
        pieza = self.celdas[(x, y)]["pieza"]
        simbolo = pieza.simbolo if pieza else ""
        self.celdas[(x, y)]["boton"].config(text=simbolo)

    def actualizar_tablero(self):
        for x in range(8):
            for y in range(8):
                self.actualizar_celda(x, y)
                self.celdas[(x, y)]["boton"].config(bg=self.celdas[(x, y)]["color"])

    # -------------------------
    # PANEL DE CAPTURADAS (rejilla con wrap y scrollbar)
    # -------------------------
    def agregar_capturado(self, pieza):
        if pieza is None:
            return
        self.capturados[pieza.color].append(pieza)
        self.actualizar_capturados()

    def actualizar_capturados(self):
        for w in self.container_blancas.grid_slaves():
            w.destroy()
        for w in self.container_negras.grid_slaves():
            w.destroy()
        max_por_col = 6
        font_size = 12
        for idx, p in enumerate(self.capturados["blanco"]):
            col = idx // max_por_col
            row = idx % max_por_col
            lbl = tk.Label(self.container_blancas, text=p.simbolo, bg="#222222", fg="white",
                           font=("Segoe UI Symbol", font_size))
            lbl.grid(row=row, column=col, padx=2, pady=2)
        for idx, p in enumerate(self.capturados["negro"]):
            col = idx // max_por_col
            row = idx % max_por_col
            lbl = tk.Label(self.container_negras, text=p.simbolo, bg="#222222", fg="white",
                           font=("Segoe UI Symbol", font_size))
            lbl.grid(row=row, column=col, padx=2, pady=2)
        self.canvas_capt.configure(scrollregion=self.canvas_capt.bbox("all"))

    # -------------------------
    # RESALTADOS Y POSIBLES MOVIMIENTOS
    # -------------------------
    def mostrar_posibles(self, origen):
        pieza = self.celdas[origen]["pieza"]
        if not pieza:
            return
        for pos, celda in self.celdas.items():
            if pieza.movimiento_correcto(origen, pos, self.celdas):
                celda["boton"].config(bg="#4DA6FF")

    def reset_colores(self):
        for pos, celda in self.celdas.items():
            celda["boton"].config(bg=celda["color"])

    def resaltar(self, x, y):
        self.celdas[(x, y)]["boton"].config(bg="#BACA44")

    # -------------------------
    # ANIMACIÓN
    # -------------------------
    def animar_movimiento(self, x, y):
        boton = self.celdas[(x, y)]["boton"]
        boton.config(bg="#F6F669")
        boton.after(120, lambda: boton.config(bg=self.celdas[(x, y)]["color"]))

    # -------------------------
    # MOVER PIEZAS
    # -------------------------
    def mover_piezas(self, x, y): 
        if self.seleccion is None: # si no existe una seleccion pues se cumple el if
            pieza = self.celdas[(x, y)]["pieza"] # pilla la pieza con sus simbolo, color...
            if pieza is None or pieza.color != self.turno: # si la pieza es nula o el color no es como el turno
                return

            self.seleccion = (x, y) # si se cumple el if ahora la seleccion tendra las cordenadas
            self.resaltar(x, y) # se resalta esas cordenadas
            self.mostrar_posibles(self.seleccion) # se muestran las posibles
            return
        else: # si no se cumple pues ocurre esto
            origen = self.seleccion  # origen tiene las coordenadas originales
            destino = (x, y) # destino tiene las nuevas coordenadas
            pieza = self.celdas[origen]["pieza"] # se guarda de nuevo la pieza puesto que no se cumplio el if

            if not pieza.movimiento_correcto(origen, destino, self.celdas): # si la pieza no esta en un movimiento correcto se resetea la seleccion y los colores y se devuelve un return vacio
                self.seleccion = None
                self.reset_colores()
                return

            target = self.celdas[destino]["pieza"] # target es el objetivo que guarda el objeto pieza de ese momento
            if target and target.color != pieza.color: # si hay una pieza y el color de esa pieza no coincide con el con el origen de esa pieza es porque se ha capturado y por tanto se añade a la lista
                self.agregar_capturado(target)

            self.celdas[destino]["pieza"] = pieza # ahora en la lista de celdas las coordenadas donde esta destino tiene la pieza guardada
            self.celdas[origen]["pieza"] = None # ahora en la lista de celdas donde estan las coordenadas del orgien ya no tienen pieza

            self.actualizar_celda(*origen) # el * convierte los parametros x e y de origen x,y
            self.actualizar_celda(*destino)
            self.animar_movimiento(*destino)

            self.turno = "blanco" if self.turno == "negro" else "negro" # es blanco si el turno es negro y viceversa
            self.seleccion = None # resetea la seleccion
            self.reset_colores() # resetea colores


    # -------------------------
    # REINICIAR PARTIDA
    # -------------------------
    def reiniciar(self):
        self.turno = "blanco"
        for celda in self.celdas.values():
            celda["pieza"] = None
        self.capturados = {"blanco": [], "negro": []}
        self.actualizar_capturados()
        self.colocar_piezas_iniciales()
        self.actualizar_tablero()
        self.limpiar_seleccion()
        # restaurar coordenadas visibles según flag
        self._dibujar_coordenadas()

# ====================================================
# EJECUCIÓN
# ====================================================
Activo = Tablero_prueba()
Activo.mainloop()