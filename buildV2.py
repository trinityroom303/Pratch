#!/usr/bin/env python3
import tkinter as tk
import tkinter.simpledialog as simpledialog
import math

#############################
# Classe Sprite
#############################
class Sprite:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.initial_x = x
        self.initial_y = y
        self.x = x
        self.y = y
        self.angle = 0  # Orientation initiale : 0°
        self.size = 20  # Rayon du sprite
        self.sprite_id = canvas.create_oval(
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size,
            fill="red"
        )

    def move(self, steps):
        rad = math.radians(self.angle)
        dx = steps * math.cos(rad)
        dy = steps * math.sin(rad)
        self.canvas.move(self.sprite_id, dx, dy)
        self.x += dx
        self.y += dy

    def turn(self, delta):
        self.angle = (self.angle + delta) % 360

    def go_to(self, x, y):
        dx = x - self.x
        dy = y - self.y
        self.canvas.move(self.sprite_id, dx, dy)
        self.x = x
        self.y = y

    def glide_to(self, seconds, x, y, callback):
        dx = x - self.x
        dy = y - self.y
        steps = max(int(seconds * 30), 1)
        step_dx = dx / steps
        step_dy = dy / steps

        def step(i):
            if i < steps:
                self.canvas.move(self.sprite_id, step_dx, step_dy)
                self.x += step_dx
                self.y += step_dy
                self.canvas.after(33, lambda: step(i+1))
            else:
                callback()
        step(0)

    def reset(self):
        dx = self.initial_x - self.x
        dy = self.initial_y - self.y
        self.canvas.move(self.sprite_id, dx, dy)
        self.x = self.initial_x
        self.y = self.initial_y
        self.angle = 0

#############################
# Classe Block
#############################
class Block:
    def __init__(self, canvas, x, y, block_type, value, color, engine, indent=0):
        self.canvas = canvas
        self.x = x  # Position gauche
        self.y = y  # Position haut
        self.block_type = block_type  # e.g., "move", "turn", "go_to", "glide_to", "repeat", "forever", "wait_seconds"
        self.value = value            # Peut être un entier ou un dictionnaire (pour go_to, glide_to, repeat)
        self.color = color
        self.engine = engine          # Référence vers le moteur (pour réorganiser ou supprimer)
        self.width = 140
        self.height = 40

        self.rectangle = canvas.create_rectangle(
            x, y, x + self.width, y + self.height,
            fill=color, outline="black"
        )
        self.text = canvas.create_text(
            x + self.width/2, y + self.height/2,
            text=self.display_text(), fill="black"
        )
        self.drag_data = {"x": 0, "y": 0}

        # Événements : clic gauche pour le drag & drop, double-clic pour modifier, clic droit pour supprimer
        canvas.tag_bind(self.rectangle, "<ButtonPress-1>", self.on_press)
        canvas.tag_bind(self.text, "<ButtonPress-1>", self.on_press)
        canvas.tag_bind(self.rectangle, "<B1-Motion>", self.on_drag)
        canvas.tag_bind(self.text, "<B1-Motion>", self.on_drag)
        canvas.tag_bind(self.rectangle, "<ButtonRelease-1>", self.on_release)
        canvas.tag_bind(self.text, "<ButtonRelease-1>", self.on_release)
        canvas.tag_bind(self.rectangle, "<Double-Button-1>", self.on_double_click)
        canvas.tag_bind(self.text, "<Double-Button-1>", self.on_double_click)
        canvas.tag_bind(self.rectangle, "<Button-3>", self.on_right_click)
        canvas.tag_bind(self.text, "<Button-3>", self.on_right_click)

    def display_text(self):
        t = self.block_type
        if t == "move":
            return f"Avancer {self.value} pas"
        elif t == "turn":
            return f"Tourner {self.value}° " + ("à droite" if self.value >= 0 else "à gauche")
        elif t == "go_to":
            return f"Aller à x:{self.value['x']} y:{self.value['y']}"
        elif t == "glide_to":
            return f"Glisser en {self.value['seconds']} s à x:{self.value['x']} y:{self.value['y']}"
        elif t == "repeat":
            return f"Répéter {self.value['times']} fois"
        elif t == "forever":
            return "Toujours"
        elif t == "wait_seconds":
            sec = self.value
            return f"Attendre {sec} seconde{'s' if sec != 1 else ''}"
        elif t == "end_loop":
            return "Fin des répétitions"
        return "Bloc inconnu"

    def on_press(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        self.canvas.move(self.rectangle, dx, dy)
        self.canvas.move(self.text, dx, dy)
        self.x += dx
        self.y += dy
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_release(self, event):
        if self.engine:
            self.engine.reorder_blocks()

    def on_double_click(self, event):
        t = self.block_type
        if t in ("move", "turn", "wait_seconds"):
            new_val = simpledialog.askinteger("Modifier", "Entrez la nouvelle valeur :", initialvalue=self.value)
            if new_val is not None:
                self.value = new_val
                self.canvas.itemconfig(self.text, text=self.display_text())
        elif t == "go_to":
            new_x = simpledialog.askinteger("Modifier", "Nouvelle valeur pour x :", initialvalue=self.value["x"])
            new_y = simpledialog.askinteger("Modifier", "Nouvelle valeur pour y :", initialvalue=self.value["y"])
            if new_x is not None and new_y is not None:
                self.value["x"] = new_x
                self.value["y"] = new_y
                self.canvas.itemconfig(self.text, text=self.display_text())
        elif t == "glide_to":
            new_sec = simpledialog.askinteger("Modifier", "Nombre de secondes :", initialvalue=self.value["seconds"])
            new_x = simpledialog.askinteger("Modifier", "Nouvelle valeur pour x :", initialvalue=self.value["x"])
            new_y = simpledialog.askinteger("Modifier", "Nouvelle valeur pour y :", initialvalue=self.value["y"])
            if new_sec is not None and new_x is not None and new_y is not None:
                self.value["seconds"] = new_sec
                self.value["x"] = new_x
                self.value["y"] = new_y
                self.canvas.itemconfig(self.text, text=self.display_text())
        elif t == "repeat":
            new_times = simpledialog.askinteger("Modifier", "Nombre de répétitions :", initialvalue=self.value["times"])
            if new_times is not None:
                self.value["times"] = new_times
                self.canvas.itemconfig(self.text, text=self.display_text())
        # Pour "forever", pas de valeur à modifier

    def on_right_click(self, event):
        if self.engine:
            self.engine.delete_block(self)

#############################
# Classe ScratchEngine
#############################
class ScratchEngine:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.setup_ui()
        self.sprite = Sprite(self.stage_canvas, 300, 200)
        self.script_blocks = []  # Blocs déposés dans la zone script

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Zone Stage (fond gris)
        self.stage_frame = tk.Frame(self.main_frame)
        self.stage_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.stage_canvas = tk.Canvas(self.stage_frame, width=600, height=400, bg="grey")
        self.stage_canvas.pack()

        # Panneau de Contrôle (Palette scrollable + Script)
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Palette de Blocs
        palette_label = tk.Label(self.control_frame, text="Palette de Blocs")
        palette_label.pack(pady=5)
        palette_frame = tk.Frame(self.control_frame)
        palette_frame.pack()
        self.palette_canvas = tk.Canvas(palette_frame, width=160, height=180, bg="white")
        vsb = tk.Scrollbar(palette_frame, orient="vertical", command=self.palette_canvas.yview)
        self.palette_canvas.configure(yscrollcommand=vsb.set)
        self.palette_canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.create_palette_blocks()  # Remplit la palette

        # Zone Script
        script_label = tk.Label(self.control_frame, text="Script")
        script_label.pack(pady=5)
        self.script_canvas = tk.Canvas(self.control_frame, width=160, height=300, bg="lightgrey")
        self.script_canvas.pack(pady=5)

        # Bouton "Drapeau Vert" pour lancer l'exécution (après reset du sprite)
        green_flag = tk.Button(self.control_frame, text="Drapeau Vert", bg="green", fg="white", command=self.run_script)
        green_flag.pack(pady=10)

        # Bouton "STOP": vide la liste de commandes instantanemment
        stop_the_car = tk.Button(self.control_frame, text="STOP", bg="red", fg="white", command=self.stop_script)
        stop_the_car.pack(pady=2)

    def create_palette_blocks(self):
        # Définition des blocs organisés par catégorie
        self.palette_definition = {
            "Mouvement": [
                ("move", 10, "lightblue"),
                ("turn", 15, "lightblue"),
                ("go_to", {"x": 0, "y": 0}, "lightblue"),
                ("glide_to", {"seconds": 1, "x": 0, "y": 0}, "lightblue")
            ],
            "Contrôle": [
                ("repeat", {"times": 10}, "lightgreen"),
                ("forever", {}, "lightgreen"),
                ("end_loop", {}, "lightgreen"),
                ("wait_seconds", 1, "lightgreen")
            ]
        }
        y_offset = 10
        for category, blocks in self.palette_definition.items():
            # Afficher le nom de la catégorie
            self.palette_canvas.create_text(80, y_offset, text=category, font=("Helvetica", 10, "bold"))
            y_offset += 20
            for (block_type, value, color) in blocks:
                rect = self.palette_canvas.create_rectangle(10, y_offset, 150, y_offset+40, fill=color, outline="black")
                if block_type == "move":
                    txt = f"Avancer {value} pas"
                elif block_type == "turn":
                    txt = f"Tourner {value}°"
                elif block_type == "go_to":
                    txt = f"Aller à x:{value['x']} y:{value['y']}"
                elif block_type == "glide_to":
                    txt = f"Glisser en {value['seconds']} s à x:{value['x']} y:{value['y']}"
                elif block_type == "repeat":
                    txt = f"Répéter {value['times']} fois"
                elif block_type == "forever":
                    txt = "Toujours"
                elif block_type == "wait_seconds":
                    txt = f"Attendre {value} s"
                elif block_type == "end_loop":
                    txt = "Fin des répétitions"
                else:
                    txt = "Bloc inconnu"
                text = self.palette_canvas.create_text(80, y_offset+20, text=txt, fill="black")
                # Lier l'événement pour créer une copie dans la zone script lors du clic
                self.palette_canvas.tag_bind(rect, "<ButtonPress-1>",
                    lambda event, t=block_type, d=value, c=color: self.on_palette_block_press(event, t, d, c))
                self.palette_canvas.tag_bind(text, "<ButtonPress-1>",
                    lambda event, t=block_type, d=value, c=color: self.on_palette_block_press(event, t, d, c))
                y_offset += 50
        # Mettre à jour la zone scrollable
        self.palette_canvas.configure(scrollregion=self.palette_canvas.bbox("all"))

    def on_palette_block_press(self, event, block_type, default_value, color):
        # Positionne le nouveau bloc dans la zone Script, empilé verticalement
        x = 10
        y = 10 + len(self.script_blocks) * 50
        new_block = Block(self.script_canvas, x, y, block_type, default_value, color, engine=self)
        self.script_blocks.append(new_block)
        new_block.on_press(event)

    def delete_block(self, block):
        try:
            self.script_blocks.remove(block)
        except ValueError:
            pass
        block.canvas.delete(block.rectangle)
        block.canvas.delete(block.text)
        self.reorder_blocks()

    def reorder_blocks(self):
        # Réorganise les blocs dans la zone Script avec un espacement fixe (ordre vertical)
        sorted_blocks = sorted(self.script_blocks, key=lambda blk: blk.y)
        spacing = 10
        base_y = 10
        for index, block in enumerate(sorted_blocks):
            new_y = base_y + index * (block.height + spacing)
            delta_y = new_y - block.y
            if abs(delta_y) > 0:
                block.canvas.move(block.rectangle, 0, delta_y)
                block.canvas.move(block.text, 0, delta_y)
                block.y = new_y

    def run_script(self):
        self.sprite.reset()
        if self.running:
            return
        self.running = True
        commands = sorted(self.script_blocks, key=lambda blk: blk.y)
        self.execute_commands(commands, 0)
    
    def stop_script(self):
        self.sprite.reset()
        self.script_blocks.clear()
        self.script_canvas.delete("all")
        self.running = False
    
    def blocks_in_loop(self, commands, index):
        # Returns block list + index of the next bloc to execute

        loop_commands = []
        i = index + 1
        while i < len(commands) and commands[i].block_type != "end_loop":
            loop_commands.append(commands[i])
            i += 1  
        return loop_commands, i

    def execute_commands(self, commands, index):
        if index >= len(commands):
            self.running = False
            return
        if self.script_blocks == []:
            return 
        
        cmd = commands[index]
        # Gestion des blocs de mouvement et contrôle
        if cmd.block_type == "move":
            self.sprite.move(cmd.value)
            delay = 300
            next_index = index + 1
        elif cmd.block_type == "turn":
            self.sprite.turn(cmd.value)
            delay = 300
            next_index = index + 1
        elif cmd.block_type == "go_to":
            self.sprite.go_to(cmd.value["x"], cmd.value["y"])
            delay = 300
            next_index = index + 1
        elif cmd.block_type == "glide_to":
            # Exécute le glissement de manière asynchrone
            self.sprite.glide_to(cmd.value["seconds"], cmd.value["x"], cmd.value["y"],
                callback=lambda: self.execute_commands(commands, index+1))
            return
        elif cmd.block_type == "wait_seconds":
            delay = int(cmd.value * 1000)
            next_index = index + 1
        elif cmd.block_type == "repeat":
            # Exécute blocs entre début et fin boucle
            if index+1 < len(commands):
                times = cmd.value["times"]
                loop_command_list, end_index = self.blocks_in_loop(commands,index)
                def repeat_block(iteration):
                    if iteration < times:
                        self.root.after(300,lambda: self.execute_commands(loop_command_list, 0))
                        self.root.after(800, lambda: repeat_block(iteration+1))
                    else:
                        self.root.after(300, lambda: self.execute_commands(commands, end_index))
                repeat_block(0)
                return
            else:
                next_index = index + 1
                delay = 300
        elif cmd.block_type == "forever":
            # Exécute en boucle infinie les blocs de la boucle
            if index+1 < len(commands):
                loop_command_list, end_index = self.blocks_in_loop(commands,index)
                def forever_block():
                    self.execute_commands(loop_command_list, 0)
                    self.root.after(300, forever_block)
                forever_block()
                return
            
            else:
                next_index = index + 1
                delay = 300
            
        else:
            delay = 300
            next_index = index + 1

        self.root.after(delay, lambda: self.execute_commands(commands, next_index))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pratch")
    app = ScratchEngine(root)
    root.mainloop()
