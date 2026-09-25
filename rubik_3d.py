from vpython import *
import random

# --- Configuración de la Escena ---
scene = canvas(
    title='Cubo de Rubik 3D (Sistema Rígido Perfecto)',
    width=800,
    height=550,
    background=color.gray(0.12)
)
scene.camera.pos = vector(4.5, 4.5, 4.5)
scene.camera.axis = vector(-4.5, -4.5, -4.5)

# Colores estándar del cubo
colors = {
    'U': color.white,   # Arriba
    'D': color.yellow,  # Abajo
    'F': color.green,   # Frente
    'B': color.blue,    # Atrás
    'L': color.orange,  # Izquierda
    'R': color.red      # Derecha
}

d = 1.0  
s = 0.98 


class Cubie:
    def __init__(self, x, y, z):
        self.parts = []
        # Bloque base interior de la pieza
        base = box(pos=vector(x*d, y*d, z*d), size=vector(s, s, s), color=color.gray(0.15))
        self.parts.append(base)
        
        st_size = s * 0.90
        st_thick = 0.01
        offset = s/2 + st_thick/2
        
        if y == 1:  self.parts.append(box(pos=vector(x*d, y*d + offset, z*d), size=vector(st_size, st_thick, st_size), color=colors['U']))
        if y == -1: self.parts.append(box(pos=vector(x*d, y*d - offset, z*d), size=vector(st_size, st_thick, st_size), color=colors['D']))
        if z == 1:  self.parts.append(box(pos=vector(x*d, y*d, z*d + offset), size=vector(st_size, st_size, st_thick), color=colors['F']))
        if z == -1: self.parts.append(box(pos=vector(x*d, y*d, z*d - offset), size=vector(st_size, st_size, st_thick), color=colors['B']))
        if x == 1:  self.parts.append(box(pos=vector(x*d + offset, y*d, z*d), size=vector(st_thick, st_size, st_size), color=colors['R']))
        if x == -1: self.parts.append(box(pos=vector(x*d - offset, y*d, z*d), size=vector(st_thick, st_size, st_size), color=colors['L']))

    @property
    def pos(self):

        return self.parts[0].pos

    def rotate(self, angle, axis):
   
        for p in self.parts:
            p.rotate(angle=angle, axis=axis, origin=vector(0,0,0))

    def snap(self):

        for p in self.parts:
            p.pos = vector(round(p.pos.x, 2), round(p.pos.y, 2), round(p.pos.z, 2))


cubies = []
for x in [-1, 0, 1]:
    for y in [-1, 0, 1]:
        for z in [-1, 0, 1]:
            if x == 0 and y == 0 and z == 0: continue
            cubies.append(Cubie(x, y, z))

move_history = []


def rotate_layer(face, angle_deg):
    angle_rad = radians(angle_deg)
    
    if face == 'U':   axis = vector(0, 1, 0);  layer = [c for c in cubies if round(c.pos.y) == 1]
    elif face == 'D': axis = vector(0, -1, 0); layer = [c for c in cubies if round(c.pos.y) == -1]
    elif face == 'F': axis = vector(0, 0, 1);  layer = [c for c in cubies if round(c.pos.z) == 1]
    elif face == 'B': axis = vector(0, 0, -1); layer = [c for c in cubies if round(c.pos.z) == -1]
    elif face == 'R': axis = vector(1, 0, 0);  layer = [c for c in cubies if round(c.pos.x) == 1]
    elif face == 'L': axis = vector(-1, 0, 0); layer = [c for c in cubies if round(c.pos.x) == -1]
    else: return

    steps = 10
    step_angle = angle_rad / steps

    for _ in range(steps):
        rate(100)
        for c in layer:
            c.rotate(angle=step_angle, axis=axis)
            
    for c in layer:
        c.snap()

def turn(move_str, record=True):
    if not move_str: return
    face = move_str[0].upper()
    angle = -90 if "'" in move_str else (180 if "2" in move_str else 90)
    
    rotate_layer(face, angle)
    if record:
        move_history.append(move_str)

def invert_move(m):
    if m.endswith("2"): return m
    return m[0] if m.endswith("'") else m[0] + "'"

def btn_scramble():
    faces, modifiers = ['U', 'D', 'L', 'R', 'F', 'B'], ['', "'", '2']
    scramble = []
    last_f = ''
    for _ in range(15):
        f = random.choice([x for x in faces if x != last_f])
        m = random.choice(modifiers)
        scramble.append(f"{f}{m}")
        last_f = f
    
    for m in scramble:
        turn(m)

def btn_solve():
    global move_history
    if not move_history: return
    solution = [invert_move(m) for m in reversed(move_history)]
    for m in solution:
        turn(m, record=False)
    move_history.clear()

scene.append_to_caption("<b>ACCIONES PRINCIPALES:</b>\n")
button(bind=btn_scramble, text='🔀 Scramble (Mezclar)', background=color.cyan, color=color.black)
scene.append_to_caption("   ")
button(bind=btn_solve, text='✨ Solve (Resolver)', background=color.green, color=color.black)

scene.append_to_caption("\n\n" + "="*50 + "\n")
scene.append_to_caption("<b>MOVIMIENTOS DE CARAS:</b>\n\n")

face_actions = [
    ('U (Arriba)', 'U'), ("U' (Arriba Inverso)", "U'"),
    ('D (Abajo)', 'D'), ("D' (Abajo Inverso)", "D'"),
    ('F (Frente)', 'F'), ("F' (Frente Inverso)", "F'"),
    ('B (Atrás)', 'B'), ("B' (Atrás Inverso)", "B'"),
    ('L (Izquierda)', 'L'), ("L' (Izquierda Inverso)", "L'"),
    ('R (Derecha)', 'R'), ("R' (Derecha Inverso)", "R'")
]

for i, (label, code) in enumerate(face_actions):
    def make_handler(m_code):
        return lambda: turn(m_code)
    
    button(bind=make_handler(code), text=f" {label} ")
    scene.append_to_caption("   ")
    
    if i % 2 == 1:
        scene.append_to_caption("\n\n")

while True:
    rate(10)