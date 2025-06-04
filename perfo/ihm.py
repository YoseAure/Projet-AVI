import tkinter as tk
from ivyserver import Server, IHMMessageInterpreter
import sys
import time
import multiprocessing
import signal

class IHM:
    def __init__(self, root, ivy_instance):
        self.root = root
        self.ivy = ivy_instance
        self.volets_etat = 0
        self.trains_etat = "Déployés"
        
        # Créer les éléments de l'interface
        self.frame_volets = tk.Frame(root, bd=2, relief=tk.RAISED)
        self.label_volets = tk.Label(self.frame_volets, text="Volets: " + self.get_volets_position(), font=("Arial", 12))
        self.levier_volets = tk.Canvas(self.frame_volets, width=50, height=120)
        self.btn_volets_inc = tk.Button(self.frame_volets, text="+", command=self.incrementer_volets, width=2, font=("Arial", 12, "bold"))
        self.btn_volets_dec = tk.Button(self.frame_volets, text="-", command=self.decrementer_volets, width=2, font=("Arial", 12, "bold"))
        
        self.frame_trains = tk.Frame(root, bd=2, relief=tk.RAISED)
        self.label_trains = tk.Label(self.frame_trains, text="Trains d'atterrissage:", font=("Arial", 12))
        self.levier_trains = tk.Canvas(self.frame_trains, width=50, height=120)
        self.btn_trains = tk.Button(self.frame_trains, text=self.trains_etat, command=self.changer_trains, font=("Arial", 12))
        
        # Create the button for sending the configuration
        self.btn_send_config = tk.Button(root, text="Send Configuration", command=self.send_config)
        self.btn_send_config.pack(pady=10)
        
        # Positionner les éléments dans la fenêtre
        self.label_volets.pack(pady=5)
        self.levier_volets.pack()
        self.btn_volets_inc.pack(side=tk.LEFT, padx=5)
        self.btn_volets_dec.pack(side=tk.LEFT, padx=5)
        self.frame_volets.pack(side="left", padx=10)
        
        self.label_trains.pack(pady=5)
        self.levier_trains.pack()
        self.btn_trains.pack()
        self.frame_trains.pack(side="left", padx=10)
        
        self.dessiner_levier_volets()
        self.dessiner_levier_trains()

        self.autorize_config = ivy_instance.authorizeConfig

        # Reset the IHM if authorizeConfig is False
        if not self.autorize_config:
            self.update_ihm()
        
    def send_config(self):
        trains_etat = "1" if self.trains_etat == "Déployés" else "0"
        message = "IHM : " + "Volets=" + self.get_volets_position() + " Trains=" + trains_etat
        print(message)
        self.ivy.send_message(message)
          
    def reset_ihm(self):
        self.volets_etat = 0
        self.trains_etat = "Rentrés"
        self.label_volets.config(text="Volets: " + self.get_volets_position())
        self.dessiner_levier_volets()
        self.dessiner_levier_trains()      
      
    def update_ihm(self):
        if self.autorize_config:
            state = tk.NORMAL
        else:
            state = tk.DISABLED

        self.btn_volets_inc.config(state=state)
        self.btn_volets_dec.config(state=state)
        self.btn_trains.config(text=self.trains_etat, state=state)
        self.btn_send_config.config(state=state)


    def incrementer_volets(self):
        if self.autorize_config:
            if self.volets_etat < 4:
                self.volets_etat += 1
                self.label_volets.config(text="Volets: " + self.get_volets_position())
                self.dessiner_levier_volets()

                if self.volets_etat == 4:
                    self.btn_volets_inc.config(state=tk.DISABLED)

            self.btn_volets_dec.config(state=tk.NORMAL)
            self.send_config()
    
    def decrementer_volets(self):
        if self.autorize_config:
            if self.volets_etat > 0:
                self.volets_etat -= 1
                self.label_volets.config(text="Volets: " + self.get_volets_position())
                self.dessiner_levier_volets()

                if self.volets_etat == 0:
                    self.btn_volets_dec.config(state=tk.DISABLED)

            self.btn_volets_inc.config(state=tk.NORMAL)
            self.send_config()
    
    def changer_trains(self):
        if self.autorize_config:
            if self.trains_etat == "Rentrés":
                self.trains_etat = "Déployés"
            else:
                self.trains_etat = "Rentrés"
            self.btn_trains.config(text=self.trains_etat)
            self.send_config()
            self.dessiner_levier_trains()  # Update landing gear frame

    
    def dessiner_levier_volets(self):
        self.levier_volets.delete("all")
        x = 25
        y = 10
        position = self.volets_etat * 30
        
        self.levier_volets.create_rectangle(x-10, y, x+10, y+100, fill="gray")
        self.levier_volets.create_rectangle(x-15, y+100, x+15, y+120, fill="gray")
        self.levier_volets.create_rectangle(x-5, y+100, x+5, y+120, fill="black")
        self.levier_volets.create_line(x, y, x, y+position, width=5, fill="red")
    
    def dessiner_levier_trains(self):
        self.levier_trains.delete("all")
        x = 25
        y = 10
        
        if self.trains_etat == "Rentrés":
            self.levier_trains.create_rectangle(x-10, y, x+10, y+100, fill="gray")
        else:
            self.levier_trains.create_rectangle(x-10, y, x+10, y+20, fill="red")
            self.levier_trains.create_rectangle(x-15, y+20, x+15, y+120, fill="gray")
            self.levier_trains.create_rectangle(x-5, y+20, x+5, y+120, fill="black")
    
    def get_volets_position(self):
        positions = ["0", "1", "2", "3", "4"]
        return positions[self.volets_etat]

def runIHM(IvyServerIHM):
    # Créer la fenêtre principale
    root = tk.Tk()
    root.title("Config")

    # Créer l'interface graphique de l'avion en injectant une Ivy instance
    ihm = IHM(root, IvyServerIHM)

    def update_ivy():
        new_autorize_config = IvyServerIHM.authorizeConfig  # Get the updated authorizeConfig from IvyServerIHM
        if ihm.autorize_config and not new_autorize_config:
            ihm.reset_ihm()
            ihm.send_config()

        ihm.autorize_config = new_autorize_config
        ihm.update_ihm()

        root.after(1000, update_ivy)
        
    def interrupt_handler(signal, frame):
        IvyServerIHM.stop()  # Stop the Ivy server
        root.destroy()  # Destroy the Tkinter window
        print("Keyboard interrupt received.")
        sys.exit(0)
        
    # Register the interrupt handler for Ctrl+C
    signal.signal(signal.SIGINT, interrupt_handler)
    
    # Schedule the first update
    root.after(1000, update_ivy)

    # Lancer la boucle principale de l'interface
    root.mainloop()

    
if __name__ == '__main__': 
    ihm_interpreter = IHMMessageInterpreter()
    IvyServerIHM = Server("IHM", "127.255.255.255:2049",["FCUVertical (.*)"],[],ihm_interpreter,True)
    IvyServerIHM.run()
    time.sleep(1)
    multiprocessing.Process(target=IvyServerIHM.start_loop)
    runIHM(IvyServerIHM)


