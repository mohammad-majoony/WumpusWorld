import tkinter as tk
from tkinter import Toplevel, Label, Button
import random

class WumpusWorldGUI:
    def __init__(self, root):
        # Initialize the main application window
        self.root = root
        self.root.title("Wumpus World")
        self.grid_size = 4  # 4x4 grid
        self.cell_size = 100  # Size of each grid position in pixels
        self.canvas_width = self.grid_size * self.cell_size  # Canvas width
        self.canvas_height = self.grid_size * self.cell_size  # Canvas height

        # Define possible agent moves (cardinal and diagonal)
        self.moves = [
            (-1, 0), (1, 0), (0, -1), (0, +1),  # Up, down, left, right
            (-1, -1), (-1, +1), (+1, -1), (+1, +1)  # Diagonal moves
        ]

        # Initialize game state
        self.grid = [["" for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.agent_pos = (0, 0)  # Agent starts at position (1,1)
        self.home = (0, 0)
        self.dead_wumpus = ()

        self.get_gold = False  # Tracks if gold is collected
        self.back_home = False

        self.use_arrow = False
        self.arrow = True
        self.find_best_arrow_cell = False
        self.best_arrow_cell = ()

        self.has_p = dict()
        self.has_w = dict()

        self.visited = {(0, 0)}  # Tracks visited positions
        self.reason = "Agent starts at position (1,1)."  # Initial action reason

        # Randomly place Wumpus, pits, and gold
        self.place_elements_randomly()

        # Create canvas for grid visualization
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Create frame for action log and control buttons
        self.reason_frame = tk.Frame(root)
        self.reason_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # Add label for action log
        self.reason_label = tk.Label(
            self.reason_frame,
            text="Agent Actions",
            font=("Arial", 16, "bold"),
            fg="#333333"
        )
        self.reason_label.pack()

        # Text box for displaying agent action reasons
        self.reason_text = tk.Text(
            self.reason_frame,
            width=40,
            height=10,
            state='disabled',
            font=("Arial", 13, "bold"),
            bg="lightblue",
            relief="flat",           # Remove border for a clean look
            borderwidth=0,           # No border
            highlightthickness=20,    # No highlight border
            padx=10, pady=5
        )
        self.reason_text.pack()

        # Frame for control buttons
        self.button_frame = tk.Frame(self.reason_frame)
        self.button_frame.pack(side=tk.BOTTOM, pady=10)

        # Button to trigger the next agent move
        self.next_button = tk.Button(
            self.button_frame,
            text="Next Move",
            command=self.move_agent,
            font=("Arial", 16),
            bg="lightblue",
            relief="flat",           # Remove border for a clean look
            borderwidth=0,           # No border
            width=12,
            highlightthickness=0,    # No highlight border
            padx=10, pady=5
        )
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Button to start a new game
        self.reset_button = tk.Button(
            self.button_frame,
            text="New Game",
            command=self.reset_game,
            font=("Arial", 16),
            bg="lightblue",
            relief="flat",           # Remove border for a clean look
            borderwidth=0,           # No border
            width=12,
            highlightthickness=0,    # No highlight border
            padx=10, pady=5
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Draw the initial game grid
        self.draw_grid()


    def reset_game(self):
        # Reset game state to initial conditions
        self.grid = [["" for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.agent_pos = (0, 0)  # Agent starts at position (1,1)
        self.home = (0, 0)
        self.dead_wumpus = ()
        self.get_gold = False  # Reset gold collection status
        self.back_home = False
        self.use_arrow = False
        self.arrow = True
        self.find_best_arrow_cell = False
        self.best_arrow_cell = ""
        self.has_p = dict()
        self.has_w = dict()
        self.visited = {(0, 0)}  # Reset visited positions
        self.reason = "Agent starts at position (1,1)."  # Reset action reason
        # Randomly place game elements
        self.place_elements_randomly()
        self.next_button.config(state='normal')
        self.update_reason(self.reason)
        self.draw_grid()


    def place_elements_randomly(self, pit_count=2):
        # Generate list of positions excluding home
        possible_positions = [(i, j) for i in range(self.grid_size) for j in range(self.grid_size) if (i, j) != self.home]
        random.shuffle(possible_positions)  # Randomize position order

        # Place Wumpus at a random position
        wumpus_pos = possible_positions.pop()
        self.grid[wumpus_pos[0]][wumpus_pos[1]] = "W"
        for move in self.moves:
            i, j = wumpus_pos[0] + move[0], wumpus_pos[1] + move[1]
            if 0 <= i < self.grid_size and 0 <= j < self.grid_size: 
                self.has_w[(i, j)] = True

        # Place gold at a random position
        gold_pos = possible_positions.pop()
        self.grid[gold_pos[0]][gold_pos[1]] = "G"

        # Place 1 to pit_count pits randomly
        num_pits = random.randint(1, pit_count)
        for _ in range(num_pits):
            if possible_positions:
                pit_pos = possible_positions.pop()
                self.grid[pit_pos[0]][pit_pos[1]] = "P"

                for move in self.moves:
                    i, j = pit_pos[0] + move[0], pit_pos[1] + move[1]
                    if 0 <= i < self.grid_size and 0 <= j < self.grid_size: 
                        self.has_p[(i, j)] = True


    def draw_grid(self):
        # Clear and redraw the game grid
        self.canvas.delete("all")
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size

                # Set background color based on position status
                if (i, j) in self.visited: # Visited position
                    fill_color = "lightgreen"  
                elif self.grid[i][j] == "W": # Wumpus
                    fill_color = "red"  
                elif self.grid[i][j] == "P": # Pit
                    fill_color = "blue"  
                elif self.grid[i][j] == "G": # Gold
                    fill_color = "gold"  
                else:
                    fill_color = "lightgray"  # Unexplored position
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")

                # Display position coordinates
                self.canvas.create_text(x1 + 20, y1 + 15, text=f"({i+1},{j+1})", font=("Arial", 10))

                # Display position contents
                if (i, j) == self.agent_pos:
                    self.canvas.create_oval(x1 + 20, y1 + 20, x2 - 20, y2 - 20, fill="green")  # Agent
                elif self.grid[i][j] == "W":
                    self.canvas.create_text(x1 + self.cell_size // 2, y1 + self.cell_size // 2, text="W", font=("Arial", 20, "bold"), fill="black")  # Wumpus
                elif self.grid[i][j] == "P":
                    self.canvas.create_text(x1 + self.cell_size // 2, y1 + self.cell_size // 2, text="P", font=("Arial", 20, "bold"), fill="black")  # Pit
                elif self.grid[i][j] == "G":
                    self.canvas.create_text(x1 + self.cell_size // 2, y1 + self.cell_size // 2, text="G", font=("Arial", 20, "bold"), fill="black")  # Gold

        # Show current observations
        self.display_observations()


    def display_observations(self):
        i, j = self.agent_pos
        observations = self.get_observations(i, j)
        if observations:
            x1, y1 = j * self.cell_size, i * self.cell_size
            obs_text = ", ".join(observations)
            self.canvas.create_text(x1 + self.cell_size // 2, y1 + self.cell_size - 10, text=obs_text, font=("Arial", 8))


    def get_observations(self, i, j):
        observations = set()
        for move in self.moves:
            ii, jj = i + move[0], j + move[1]
            if 0 <= ii < self.grid_size and 0 <= jj < self.grid_size:
                if self.grid[ii][jj] == 'W':
                    observations.add("Stench")
                if self.grid[ii][jj] == 'P':
                    observations.add("Breeze")
        return observations


    def update_reason(self, reason):
        # Update the action log display
        self.reason_text.config(state='normal')
        self.reason_text.delete(1.0, tk.END)
        self.reason_text.insert(tk.END, reason + "\n")  # Add newline for readability
        self.reason_text.config(state='disabled')


    def show_message(self, title, message, msg_type):
        # Display a custom message dialog
        dialog = Toplevel(self.root)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self.root)  # Link dialog to main window
        dialog.grab_set()  # Make dialog modal

        # Set background color based on message type
        bg_color = {"info": "#e6f3ff", "success": "#d4edda", "error": "#f8d7da"}.get(msg_type, "#e6f3ff")
        dialog.configure(bg=bg_color)

        # Create and pack the message label
        label = Label(
            dialog,
            text=message,
            font=("Arial", 12, "bold"),
            justify="center",
            wraplength=300,
            padx=20,
            pady=20,
            bg=bg_color,
            fg={"info": "black", "success": "darkgreen", "error": "darkred"}.get(msg_type, "black")
        )
        label.pack(pady=10)

        # Create and pack the OK button
        ok_button = Button(
            dialog,
            text="OK",
            command=dialog.destroy,
            font=("Arial", 10),
            bg="lightgray",
            relief="raised",
            width=10
        )
        ok_button.pack(pady=10)

        # Center dialog on the main window
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        
    dfs_visited = []
    def dfs(self, pos, target):
        if pos == target:
            return [(0, 0), 0]
        
        best = [(0, 0), 99]
        for move in self.moves:
            i, j = pos[0] + move[0], pos[1] + move[1]
            if 0 <= i < self.grid_size and 0 <= j < self.grid_size and ((i, j) in self.visited or (i, j) == target) and ((i, j) not in self.dfs_visited): 
                self.dfs_visited.append((i, j))
                next = self.dfs((i, j), target)
                self.dfs_visited.pop()
                if next[1] + 1 < best[1]:
                    best = [(i, j), next[1] + 1]
        
        return best


    def best_next_move(self, pos, target):
        self.dfs_visited.clear()
        self.dfs_visited.append(pos)
        return self.dfs(pos, target)


    def not_visited_safe(self):
        not_visited = [(i, j) for i in range(self.grid_size) for j in range(self.grid_size) if (i , j) not in self.visited]
        safe_cell = set()

        for pos in not_visited:

            vis_nei = False                
            has_p = True                
            no_p = []
            has_w = True                
            no_w = []

            for move in self.moves:
                i, j = pos[0] + move[0], pos[1] + move[1]
                if 0 <= i < self.grid_size and 0 <= j < self.grid_size and (i, j) in self.visited:
                    vis_nei = True
                    if (i, j) not in self.has_p:
                        has_p = False
                        no_p.append((i + 1, j + 1))
                    if (i, j) not in self.has_w:
                        has_w = False
                        no_w.append((i + 1, j + 1))
            
            if vis_nei and (((not has_p) and (not has_w)) or pos == self.dead_wumpus): 
                safe_cell.add((pos, no_p[0], no_w[0]))

        return safe_cell 


    def arrow_best_cell(self):
        # Identify optimal position for arrow shot based on stench
        not_visited = [(i, j) for i in range(self.grid_size) for j in range(self.grid_size) if (i , j) not in self.visited]
        best_pos = [(0, 0), 0]

        for pos in not_visited:
            can_be = True
            counter = 0

            for move in self.moves:
                i, j = pos[0] + move[0], pos[1] + move[1]
                if 0 <= i < self.grid_size and 0 <= j < self.grid_size and ((i, j) in self.visited):
                    if (i, j) not in self.has_w:                    
                        can_be = False
                    else:
                        counter += 1

            if can_be and best_pos[1] < counter:
                best_pos = [pos, counter]
                
        return best_pos


    def move_agent(self):
        i, j = self.agent_pos
        next_pos = ()

        if self.back_home or self.get_gold:
            # Navigate back to home position
            if self.agent_pos == self.home:
                self.show_message(
                    title="Victory!",
                    message="Agent has successfully returned to home!",
                    msg_type="success"
                )
                self.next_button.config(state='disabled')
                return

            else:
                # Select optimal move to return to home
                next_pos = self.best_next_move(self.agent_pos, self.home)[0]
                move_type = "diagonal" if abs(next_pos[0] - i) + abs(next_pos[1] - j) > 1 else "cardinal"
                self.reason = f"{move_type.capitalize()} move from ({i + 1}, {j + 1}) to ({next_pos[0] + 1}, {next_pos[1] + 1}) to return to home."

        elif self.use_arrow:
            # Handle arrow usage
            self.arrow = False

            if self.find_best_arrow_cell:
                is_nei = False
                for move in self.moves:
                    ii, jj = i + move[0], j + move[1]
                    if 0 <= i < self.grid_size and 0 <= j < self.grid_size and (ii, jj) == self.best_arrow_cell:
                        is_nei = True
                        break
                
                if is_nei:
                    # Fire arrow at target
                    if self.grid[self.best_arrow_cell[0]][self.best_arrow_cell[1]] == "W":
                        self.grid[self.best_arrow_cell[0]][self.best_arrow_cell[1]] = ""
                        self.has_w.clear()
                        self.dead_wumpus = self.best_arrow_cell

                    next_pos = self.agent_pos
                    self.reason = f"Arrow fired at position ({self.best_arrow_cell[0] + 1}, {self.best_arrow_cell[1] + 1})."

                    self.use_arrow = False
                else:
                    # Move toward optimal arrow target position
                    next_pos = self.best_next_move(self.agent_pos, self.best_arrow_cell)[0]
                    move_type = "diagonal" if abs(next_pos[0] - i) + abs(next_pos[1] - j) > 1 else "cardinal"
                    ii, jj = next_pos[0] + 1, next_pos[1] + 1
                    self.reason = f"{move_type.capitalize()} move from ({i + 1}, {j + 1}) to ({ii}, {jj}) to reach optimal position for arrow shot."

            else:
                best_cell = self.arrow_best_cell()
                self.find_best_arrow_cell = True

                if best_cell[1]:
                    self.best_arrow_cell = best_cell[0]
                    self.show_message(
                        title="Arrow Opportunity",
                        message=f"Agent will target position ({best_cell[0][0] + 1}, {best_cell[0][1] + 1}) with arrow.",
                        msg_type="info"
                    )
                    next_pos = self.agent_pos
                else: 
                    self.use_arrow = False
                    self.show_message(
                        title="No Arrow Target",
                        message="No suitable position found for arrow shot.",
                        msg_type="info"
                    )
                    return

        else:
            # Explore for safe positions or gold
            if self.grid[i][j] == "G":
                self.get_gold = True
                self.reason = "Gold collected! Agent will return to home."
                self.update_reason(self.reason)
                self.draw_grid()
                self.grid[i][j] = ""
                self.show_message(
                    title="Gold Collected!",
                    message="Agent has found the gold and will now return to home.",
                    msg_type="info"
                )
                return

            # Identify safe unvisited positions
            safe_moves = self.not_visited_safe()

            if len(safe_moves):
                # Select nearest safe position to explore
                nearest_safe_pos = sorted(safe_moves, key=lambda pos: abs(pos[0][0] + self.agent_pos[0]) + abs(pos[0][1] - self.agent_pos[1]))[0]
                next_pos = self.best_next_move(self.agent_pos, nearest_safe_pos[0])[0]
                move_type = "diagonal" if abs(next_pos[0] - i) + abs(next_pos[1] - j) > 1 else "cardinal"
                if nearest_safe_pos[0] == next_pos:
                    if next_pos == self.dead_wumpus:
                        self.reason = f"{move_type.capitalize()} move from ({i + 1}, {j + 1}) to ({next_pos[0] + 1}, {next_pos[1] + 1}) because we know this cell is safe — the Wumpus was killed here, and there's no stench around it."
                    else:
                        wumpus_text = f"no stench at position ({nearest_safe_pos[1][0]}, {nearest_safe_pos[1][1]})"
                        breeze_text = f"no breeze at position ({nearest_safe_pos[2][0]}, {nearest_safe_pos[2][1]})"
                        self.reason = f"{move_type.capitalize()} move from ({i + 1}, {j + 1}) to ({next_pos[0] + 1}, {next_pos[1] + 1}) because {wumpus_text} and {breeze_text}, indicating a safe position."
                else:
                    self.reason = f"{move_type.capitalize()} move from ({i + 1}, {j + 1}) to ({next_pos[0] + 1}, {next_pos[1] + 1}) as it is a safe position."
                    
            else:
                if self.arrow:                
                    # Attempt to use arrow to create safe positions
                    self.use_arrow = True
                    self.show_message(
                        title="No Safe Moves",
                        message="No safe positions to explore. Agent will attempt to use arrow.",
                        msg_type="info"
                    )
                    return
                
                else:
                    # Return to home due to lack of safe positions
                    self.back_home = True 
                    self.show_message(
                        title="No Safe Moves",
                        message="No safe positions to explore. Agent will return to home.",
                        msg_type="error"
                    )
                    return

        # Update agent position
        self.agent_pos = next_pos
        self.visited.add(next_pos)

        # Refresh the interface
        self.update_reason(self.reason)
        self.draw_grid()

if __name__ == "__main__":
    root = tk.Tk()
    app = WumpusWorldGUI(root)
    root.mainloop()