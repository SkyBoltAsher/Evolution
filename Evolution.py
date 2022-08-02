from tkinter import *
import random
import threading
import time

org_list = []   #the lists of organisms, foods, and obstacles, respectively
food_list = []
obs_list = []
running = False #starts program paused

class Organism:   #organism creator
    
    def __init__(self,name, x, y, energy, focus, boredom, mate_threshold, offspring_contribution, strength, speed, generation, age, parent_frame, colour): #the stats that an organism will be created with
        self.x = int(x)   #based on parents                                                                                                         
        self.y = int(y)   #based on parents
        self.energy = energy #contributed from parents
        self.focus = focus #derived from parents
        self.boredom = boredom #derived from parents
        self.mate_threshold = mate_threshold #derived from parents
        self.offspring_contribution = offspring_contribution #derived from parents
        self.strength = strength #derived from parents
        self.speed = speed #derived from parents
        self.generation = generation #increased by one from oldest generation parent
        self.age = age #amount of game ticks old, increases by one each tick
        self.parent_frame = parent_frame
        self.name = name
        self.turns_since_act = 0 #keeps track of how long until the organism is bored
        self.current_boredom = 0 #when organism is bored, counts down until org is focused again
        self.target = True #organisms start with no target, but one should be assigned immediately in the logic def
        self.boredom_timer = 0 #when org is bored, it will be bored for this many turns
        self.distance = 0 #used in target finding
        
        #determines if the organisms starts ready to mate
        if self.energy >= self.mate_threshold:
            self.mate_ready = True
        else: self.mate_ready = False
        
        self.bored = False #organisms starts not bored
        
        #colour setting
        self.colour_hex = hex(colour)
        self.colour = '#' + self.colour_hex[2:9]
        while len(self.colour) < 7:    #ensures the colour is valid hex
            self.colour = self.colour + '0'
        
        #adds self to org_list
        org_list.append(self)
        
        #creates the organisms frame
        self.frame = Frame(self.parent_frame, bg = self.colour , width = 4, height = 4)
        self.frame.grid(row = int(self.y), column = int(self.x))
        
    def __repr__(self):
        return self.name
    

    def kill_self_org(self):     #removes the organisms frame
        self.frame.destroy()
        del self
        
        
class Food:
    def __init__(self, name, nutrition, parent_frame):
        self.x = random.randint(1,250)
        self.y = random.randint(1,250)
        self.nutrition = nutrition * 5
        self.parent_frame = parent_frame
        self.name = name
        self.distance = 0 #used in target finding
        #adds the food to the food list
        food_list.append(self)
        
        #creates the food frames
        self.frame = Frame(self.parent_frame, bg='green', width = 4, height = 4)
        self.frame.grid(row = int(self.y), column = int(self.x))
        
    def __repr__(self):
        return self.name        
        

    def kill_self_food(self):
        self.frame.destroy()
        del self
    
class Obstacle:
    def __init__(self,name,parent_frame):
        self.x = random.randint(1,250)
        self.y = random.randint(1,250)
        self.strength = random.randint(1,250)
        self.obs_name = name
        self.parent_frame = parent_frame
        
        #adds the obs to the obstacle list
        obs_list.append(self)
        
        self.frame = Frame(self.parent_frame, bg ='black', width = 4, height = 4)
        self.frame.grid(row = int(self.y), column = int(self.x))
        
    def __repr__(self):
        return self.obs_name

    def kill_self_obs(self):
        self.frame.destroy()
        del self


class Board:  #creates the board
    def __init__(self, parent):
        background_colour = 'gainsboro'
        
        #frame
        self._board_frame = Frame(parent, bg = background_colour, padx=10, pady=10)
        self._board_frame.grid()
        
        #gui:
        grid_count = 250
    
        while grid_count > 0:
            tile_name = str(grid_count)
            exec('self.B' + str(grid_count) + '=' + 'Frame(self._board_frame, bg = "gainsboro", width=4, height=4)')
            exec('self.B' + str(grid_count) + '.grid(row =' + str(grid_count) + ', column =' + str(grid_count) +')')  
            grid_count -= 1
            
            
        self.controls_frame = Frame(parent, bg = 'white',)
        self.controls_frame.grid(row = 0, column = 1, sticky = N)
        
        #running button
        self.running = Button(self.controls_frame, text = 'Paused', font=('Ariel', '13', 'bold'), bg = 'red', width = 15, command = self.toggle_running)
        self.running.grid(row = 0, column = 0, padx=10, pady=10)
    
        
        #speed slider label
        self.speed_label = Label(self.controls_frame, text = 'Game Speed:', bg = 'white', font=('Ariel', '16', 'bold'), height = 2)
        self.speed_label.grid(row = 1, column = 1, sticky = W)
        
        #speed slider
        self.speed_scale = Scale(self.controls_frame, from_ = 1, to = 100, orient = HORIZONTAL, length = 400, bg = 'white')
        self.speed_scale.grid(row=2, columnspan=3, )        
            
        #food abundance label
        self.food_abundance_label = Label(self.controls_frame, text = 'Food Abundance:', bg = 'white', font=('Ariel', '16', 'bold'), height = 2)
        self.food_abundance_label.grid(row = 3, column = 1,sticky = W)        
        
        #food abundance slider
        self.food_abundance_scale = Scale(self.controls_frame, from_ = 0, to = 100, orient = HORIZONTAL, length = 400, bg = 'white')
        self.food_abundance_scale.grid(row=4, columnspan=3, )         
        
        #food nutrition label
        self.food_abundance_label = Label(self.controls_frame, text = 'Food Nutrition:', bg = 'white', font=('Ariel', '16', 'bold'), height = 2)
        self.food_abundance_label.grid(row = 5, column = 1,sticky=W)           
        
        #food nutrition slider
        self.food_nutrition_scale = Scale(self.controls_frame, from_ = 0, to = 100, orient = HORIZONTAL, length = 400, bg = 'white')
        self.food_nutrition_scale.grid(row=6, columnspan=3, )            
        
        #obstacle frequency label
        self.obstacle_frequency_label = Label(self.controls_frame, text = 'Obstacle Frequency:', bg = 'white', font=('Ariel', '16', 'bold'), height = 2)
        self.obstacle_frequency_label.grid(row = 7, column = 1,sticky=W)              
        
        #obstacle frequency slider
        self.obstacle_frequency_scale = Scale(self.controls_frame, from_ = 0, to = 100, orient = HORIZONTAL, length = 400, bg = 'white')
        self.obstacle_frequency_scale.grid(row=8, columnspan=3, )               
        
        #spawn count label
        self.spawn_count_label = Label(self.controls_frame, text = 'Spawn Count:', bg = 'white', font=('Ariel', '16', 'bold'), height = 2)
        self.spawn_count_label.grid(row = 9, column = 1,sticky=W)           
        
        #spawn count slider
        self.spawn_count_scale = Scale(self.controls_frame, from_ = 0, to = 50, orient = HORIZONTAL, length = 400, bg = 'white')
        self.spawn_count_scale.grid(row=10, columnspan=3, )    
        self.spawn_count_scale.set(5)
        
        #apply_settings_button
        self.apply_settings = Button(self.controls_frame, text = 'Apply Settings', font=('Ariel', '13', 'bold'), bg = 'white', width = 15, command = self.apply_settings)
        self.apply_settings.grid(row = 11, column = 0, padx=10, pady=10)        
        
        #restore_default_button
        self.restore_default = Button(self.controls_frame, text = 'Restore Defaults', font=('Ariel', '13', 'bold'), bg = 'white', width = 15, command = self.restore_defaults)
        self.restore_default.grid(row = 11, column = 2, padx=10, pady=10)        
        
        #populate_button
        self.Populate = Button(self.controls_frame, text = 'Populate', font=('Ariel', '13', 'bold'), bg = 'white', width = 15, command = self.org_populate)
        self.Populate.grid(row = 12, column = 0, padx=10, pady=10)        
        
        #reset_board_button
        self.reset_board = Button(self.controls_frame, text = 'Reset Board', font=('Ariel', '13', 'bold'), bg = 'white', width = 15, command = self.reset_board)
        self.reset_board.grid(row = 12, column = 2, padx=10, pady=10)  
        
        #population count label
        self.population_count_label = Label(self.controls_frame, text = 'Population Count:', font=('Ariel', '13', 'bold'), bg = 'white', )
        self.population_count_label.grid(row = 13, column = 0, sticky = W, pady= 20)
        
        #population count display
        self.population_count_display = Label(self.controls_frame, text = str(len(org_list)), font=('Ariel', '13', 'bold'), bg= 'white', width= 5)
        self.population_count_display.grid(row = 13, column = 1, pady = 20, sticky = W)
        
        #energy avg label
        self.energy_avg_label = Label(self.controls_frame, text = 'Average Energy:', font=('Ariel', '13', 'bold'), bg = 'white', )
        self.energy_avg_label.grid(row = 14, column = 0, sticky = W, pady= 5)
        
        #energy avg display
        self.energy_avg_display = Label(self.controls_frame, text = FindMean('energy'), font=('Ariel', '13', 'bold'), bg= 'white', width= 5)
        self.energy_avg_display.grid(row = 14, column = 1, pady = 5, sticky = W)
        
        #speed avg label
        self.speed_avg_label = Label(self.controls_frame, text = 'Average Speed:', font=('Ariel', '13', 'bold'), bg = 'white', )
        self.speed_avg_label.grid(row = 15, column = 0, sticky = W, pady= 5)
        
        #speed avg display
        self.speed_avg_display = Label(self.controls_frame, text = str(len(org_list)), font=('Ariel', '13', 'bold'), bg= 'white', width= 5)
        self.speed_avg_display.grid(row = 15, column = 1, pady = 5, sticky = W)
        
        #strength avg label
        self.strength_avg_label = Label(self.controls_frame, text = 'Average Strength:', font=('Ariel', '13', 'bold'), bg = 'white', )
        self.strength_avg_label.grid(row = 16, column = 0, sticky = W, pady= 5)
        
        #strength avg display
        self.strength_avg_display = Label(self.controls_frame, text = str(len(org_list)), font=('Ariel', '13', 'bold'), bg= 'white', width= 5)
        self.strength_avg_display.grid(row = 16, column = 1, pady = 5, sticky = W)
        
        #mate threshold avg label
        self.mate_threshold_avg_label = Label(self.controls_frame, text = 'Average Mate Threshold:', font=('Ariel', '13', 'bold'), bg = 'white',)
        self.mate_threshold_avg_label.grid(row = 17, column = 0, sticky = W, pady= 5)
        
        #mate threshold avg display
        self.mate_threshold_avg_display = Label(self.controls_frame, text = str(len(org_list)), font=('Ariel', '13', 'bold'), bg= 'white', width= 5)
        self.mate_threshold_avg_display.grid(row = 17, column = 1, pady = 5, sticky = W)
        
        #offspring contribution avg label
        self.offspring_contribution_avg_label = Label(self.controls_frame, text = 'Average Offspring Contribution:', font=('Ariel', '13', 'bold'), bg = 'white')
        self.offspring_contribution_avg_label.grid(row = 18, column = 0, sticky = W, pady= 5)
        
        #offspring contribution avg display
        self.offspring_contribution_avg_display = Label(self.controls_frame, text = str(len(org_list)), font=('Ariel', '13', 'bold'), bg= 'white', width= 5)
        self.offspring_contribution_avg_display.grid(row = 18, column = 1, pady = 5, sticky = W)
        
        #focus avg label
        self.focus_avg_label = Label(self.controls_frame, text = 'Average Focus:', font=('Ariel', '13', 'bold'), bg = 'white', )
        self.focus_avg_label.grid(row = 19, column = 0, sticky = W, pady= 5)
        
        #focus avg display
        self.focus_avg_display = Label(self.controls_frame, text = str(len(org_list)), font=('Ariel', '13', 'bold'), bg= 'white', width= 5)
        self.focus_avg_display.grid(row = 19, column = 1, pady = 5, sticky = W)
        
        #boredom avg label
        self.boredom_avg_label = Label(self.controls_frame, text = 'Average Boredom:', font=('Ariel', '13', 'bold'), bg = 'white', )
        self.boredom_avg_label.grid(row = 20, column = 0, sticky = W, pady= 5)
        
        #boredom avg display
        self.boredom_avg_display = Label(self.controls_frame, text = str(len(org_list)), font=('Ariel', '13', 'bold'), bg= 'white', width= 5)
        self.boredom_avg_display.grid(row = 20, column = 1, pady = 5, sticky = W)
        
        #newest generation label
        self.newest_generation_label = Label(self.controls_frame, text = 'Newest Generation:', font=('Ariel', '13', 'bold'), bg = 'white', )
        self.newest_generation_label.grid(row = 21, column = 0, sticky = W, pady= 5)
        
        #newest generation display
        self.newest_generation_display = Label(self.controls_frame, text = str(len(org_list)), font=('Ariel', '13', 'bold'), bg= 'white', width= 5)
        self.newest_generation_display.grid(row = 21, column = 1, pady = 5, sticky = W)
                                  
        
        
        #starts program at correct settings
        self.speed_scale.set(20)
        self.spawn_count_scale.set(25)
        self.food_nutrition_scale.set(50)
        self.food_abundance_scale.set(10)
        self.obstacle_frequency_scale.set(10)
        self.running_test = 0        
        self.base_nutrition = self.food_nutrition_scale.get()        
        self.spawn_count_number = self.spawn_count_scale.get()        
        self.food_abundance = self.food_abundance_scale.get()
        self.obstacle_frequency = self.obstacle_frequency_scale.get()
        self.game_delay = (self.speed_scale.get() ** -1) / 10
        self.obs_populate()
        self.food_populate()
        
    def toggle_running(self):  #this section pauses and plays the program
        global running
        board.running_test += 1
        if board.running_test > 1:
            board.running_test = 0
        if board.running_test == 1:
            running = True
            self.running.config(bg = 'green', text = 'Running')
        elif board.running_test == 0:
            running = False
            self.running.config(bg = 'red', text = 'Paused')
    
    
    
    def reset_board(self):
        global running
        if running == False:
            while len(org_list) > 0: #kills organism
                for org in org_list:
                    org_list.remove(org)
                    org.kill_self_org()
                    
            while len(food_list) > 0: #kills fod
                for food in food_list:
                    food_list.remove(food)
                    food.kill_self_food()  
                    
            while len(obs_list) > 0: #kills obstacles
                for obs in obs_list:
                    obs_list.remove(obs)
                    obs.kill_self_obs()
            
            self.obs_populate()
            self.food_populate()
            
            #resets displays
            board.population_count_display.config(text = 0)  #updates displays with the new organisms      
            board.energy_avg_display.config(text=0)
            board.speed_avg_display.config(text=0)
            board.strength_avg_display.config(text=0)
            board.mate_threshold_avg_display.config(text=0)
            board.offspring_contribution_avg_display.config(text=0)
            board.focus_avg_display.config(text=0)
            board.boredom_avg_display.config(text=0)           
    
    #allows program to be reset    
    def restore_defaults(self):
        self.spawn_count_scale.set(25)
        self.food_nutrition_scale.set(50)
        self.food_abundance_scale.set(10)
        self.obstacle_frequency_scale.set(10)
        self.speed_scale.set(20)
        
    #applys the settings selected by the slider
    def apply_settings(self):

        board.spawn_count_number = self.spawn_count_scale.get()  #the number of organisms that are spawned per click
        board.base_nutrition = self.food_nutrition_scale.get()    #on average, how nutritious food is
        board.food_abundance = self.food_abundance_scale.get()
        board.obstacle_frequency = self.obstacle_frequency_scale.get()
        if self.speed_scale.get() == 100:
            board.game_delay = 0
        else:
            board.game_delay = (self.speed_scale.get() ** -1) / 10
        
    
    #populates board with organisms   
    def org_populate(self):
        spawn_count = board.spawn_count_number
        while spawn_count > 0:
        
            spawn_count -= 1
            name_number = 0
            match = True
            
            while match == True:     #this section makes sure that the organism is given a unique name
                name_number += 1
                match = False
                
                for organism in org_list:
                   
                    if str(organism) == str('P' + str(name_number)):
                        match = True
                       
                        
                        
                  

                if match == False:
                            
                    organism_name = 'P' + str(name_number)                     
                    
                    exec('P' + str(name_number) + \
                         '=Organism(' +'"' +str(organism_name)+'"' +','+ str(random.randint(1,250)) + \
                         ',' + str(random.randint(1,250)) + \
                         ',' + str(500) + \
                         ',' + str(random.randint(1,20)) + \
                         ',' + str(random.randint(1,20)) + \
                         ',' + str(random.randint(1,250)) + \
                         ',' + str(random.randint(1,250)) + \
                         ',' + str(random.randint(1,250)) + \
                         ',' + str(random.randint(1,250)) + \
                         ',' + '0,0' + ', self._board_frame' + ',' + str(random.randint(1,16777215)) + ')')  #16777215 is the largest hex number that is a colour
        board.population_count_display.config(text = str(len(org_list)))   #updates displays with the new organisms     
        board.energy_avg_display.config(text=FindMean('energy'))
        board.speed_avg_display.config(text=FindMean('speed'))
        board.strength_avg_display.config(text=FindMean('strength'))
        board.mate_threshold_avg_display.config(text=FindMean('mate_threshold'))
        board.offspring_contribution_avg_display.config(text=FindMean('offspring_contribution'))
        board.focus_avg_display.config(text=FindMean('focus'))
        board.boredom_avg_display.config(text=FindMean('boredom'))                    
    
    #populates board with food 
    def food_populate(self):
        food_spawn_count = self.food_abundance
        while food_spawn_count > 0:
            
            current_nutrition = int((random.randint(500000,1500000)/1000000) * self.base_nutrition)
            food_spawn_count -= 1
            name_number = 0
            match = True

            while match == True:     #this section makes sure that the food is given a unique name
                name_number += 1
                match = False

                for food in food_list:

                    if str(food) == str('F' + str(name_number)):
                        match = True


                if match == False:

                    food_name = 'F' + str(name_number)                     

                    exec('F' + str(name_number) + \
                         '=Food(' +'"' +str(food_name) + '",' + str(current_nutrition) + ', self._board_frame' + ')')
    
    #populates board with obstacles
    def obs_populate(self):
        obs_spawn_count = self.obstacle_frequency * 5
        while obs_spawn_count > 0:

            obs_spawn_count -= 1
            name_number = 0
            match = True

            while match == True:     #this section makes sure that the obstacle is given a unique name
                name_number += 1
                match = False

                for obs in obs_list:

                    if str(obs) == str('O' + str(name_number)):
                        match = True


                if match == False:

                    obs_name = 'O' + str(name_number)                     

                    exec('O' + str(name_number) + \
                         '=Obstacle(' +'"' +str(obs_name) + '"' + ', self._board_frame' + ')')        

def Breed(org):
    org.energy -= org.offspring_contribution
    org.target.energy -= org.target.offspring_contribution
    
    offspring_energy = org.offspring_contribution + org.target.offspring_contribution
    offspring_name = 'P' + UniqueName()
    offspring_x = org.x
    offspring_y = org.y
    offspring_generation = org.generation + 1
    offspring_age = 0
    
    mutation_chance = random.randint(1,10) #one in ten chance for a random stat to be random, instead of derived from parents
    mutated_stat = 0
    if mutation_chance == 1:
        mutated_stat = random.randint(1,7)
        
    if mutated_stat == 1:
        offspring_focus = random.randint(1,250)
    else:
        offspring_focus = int((random.randint(90000,110000) / 100000) * ((org.focus + org.target.focus) / 2))
        
    if mutated_stat == 2:
        offspring_boredom = random.randint(1,250)
    else:
        offspring_boredom = int((random.randint(90000,110000) / 100000) * ((org.boredom + org.target.boredom) / 2))
    
    if mutated_stat == 3:
        offspring_mate_threshold = random.randint(1,250)
    else:
        offspring_mate_threshold = int((random.randint(90000,110000) / 100000) * ((org.mate_threshold + org.target.mate_threshold) / 2))
        
    if mutated_stat == 4:
        offspring_offspring_contribution = random.randint(1,250)
    else:
        offspring_offspring_contribution = int((random.randint(90000,110000) / 100000) * ((org.offspring_contribution + org.target.offspring_contribution) / 2))
        
    if mutated_stat == 5:
        offspring_strength = random.randint(1,250)
    else:
        offspring_strength = int((random.randint(90000,110000) / 100000) * ((org.strength + org.target.strength) / 2))
        
    if mutated_stat == 6:
        offspring_speed = random.randint(1,250)
    else:
        offspring_speed = int((random.randint(90000,110000) / 100000) * ((org.speed + org.target.speed) / 2))
        
    if mutated_stat == 7:
        offspring_colour = random.randint(1,16777215)
    else:
        parent_colour_choice = random.randint(1,2) #offspring gets either one of its parents colour. i cant figure out how to do hex arithmetic to find the average
        if parent_colour_choice == 1:
            offspring_colour = org.colour_hex
        else:
            offspring_colour = org.target.colour_hex
            
    exec(str(offspring_name) + '=Organism(' +'"'+ str(offspring_name)+'"' +','+ str(offspring_x) +','+str(offspring_y)+','+str(offspring_energy)+','+str(offspring_focus)+','+str(offspring_boredom)+','+str(offspring_mate_threshold)+','+str(offspring_offspring_contribution)+','+str(offspring_strength)+','+str(offspring_speed)+','+str(offspring_generation)+','+str(offspring_age)+','+'board._board_frame'+','+str(offspring_colour) +')') #abomination line    


def UniqueName():
    name_number = 0
    match = True

    while match == True:     #this section makes sure that the organism is given a unique name
        name_number += 1
        match = False

        for organism in org_list:

            if str(organism) == str('P' + str(name_number)):
                match = True





        if match == False:
            return str(name_number)


def AbsoluteValue(x): #used for calculating distances bewtween organisms and targets
    if x <0:
        x = x * -1
    return x

def FindMean(statistic): #this function finds the mean, across all organisms, of a certain statistic
    stat_total = 0
    mean = 0
    for org in org_list: #adds up all stats to find the mean
        stat_total += eval('org.' + statistic)
        
    if len(org_list) > 0: #only bothers finding the mean if there are any organisms
        mean = int(stat_total / len(org_list))
    return(mean)


#main routine
def GUI():
    if __name__ == '__main__':
        root = Tk()
        root.title('Evolution')
        global board
        board = Board(root)
        root.mainloop()



#movement functions
def move_up(org,distance):
    food_in_path = False
    obs_in_path = False
    move_count = distance
    
    #checks if the organism may run into something, so that it doesnt nessacarily have to check each time it moves
    for food in food_list:
        if org.x == food.x:
            food_in_path = True
    for obs in obs_list:
        if org.x == obs.x and obs.strength > org.strength:
            obs_in_path = True
    
    #actual movement logic
    while move_count > 0 and org.y > 1:
        global running
        if running == True:
            blocked = False
            if obs_in_path == True:
                for obs in obs_list:
                    if (org.y == obs.y + 1) and org.x == obs.x and org.strength < obs.strength: #will this obs block this org
                        blocked = True
                    if (org.y == obs.y + 1) and org.x == obs.x and org.strength >= obs.strength: #if an organisms powers through an obstacles, removes energy
                        org.energy -= org.speed                    
            if blocked == False: #moves organism if it isnt blocked
                org.y -= 1
                org.energy -= 1
                org.frame.grid(row = int(org.y))
            if org.target != False and org.target != True:
                if org.target.y == org.y: #stops the organism if it is in line with its target
                    org.energy -= move_count #organisms still loses full energy equal to speed even if it stops early. a balance btween movement and efficiency will evolve
                    move_count = 0        
                if org.y == org.target.y and org.x == org.target.x and org.target.name[0] == 'P' and org.mate_ready == True and org.target.mate_ready == True:  #breeding logic
                    Breed(org)
                    org.turns_since_act = 0
    
            
            if food_in_path == True: #organism consumes any food it comes across.
                for food in food_list:
                    if org.y == food.y and org.x == food.x:
                        org.energy += food.nutrition
                        org.turns_since_act = 0
                        food_list.remove(food)
                        food.kill_self_food()
            if org.energy <= 0: #kills organism if it reches 0 energy
                move_count = 0
                org_list.remove(org)
                org.kill_self_org()
        
        
        move_count -= 1 #wont try to move forever
        time.sleep(board.game_delay)
        
    if org.bored == False:  #wont keep track of inaction if org is already bored
        org.turns_since_act += 1  
    if org.bored == True: #time down if this turn org was bored
        org.boredom_timer -= 1
        org.turns_since_act = 0 #doesnt count towards being bored if already bored

def move_down(org,distance):
    food_in_path = False
    obs_in_path = False
    move_count = distance

    #checks if the organism may run into something, so that it doesnt nessacarily have to check each time it moves
    for food in food_list:
        if org.x == food.x:
            food_in_path = True
    for obs in obs_list:
        if org.x == obs.x and obs.strength > org.strength:
            obs_in_path = True

    #actual movement logic
    while move_count > 0 and org.y < 250:
        global running
        if running == True:
            blocked = False
            if obs_in_path == True:
                for obs in obs_list:
                    if (org.y == obs.y - 1) and org.x == obs.x and org.strength < obs.strength: #will this obs block this org
                        blocked = True
                    if (org.y == obs.y - 1) and org.x == obs.x and org.strength >= obs.strength: #if an organisms powers through an obstacles, removes energy
                        org.energy -= org.speed                    
            if blocked == False: #moves organism if it isnt blocked
                org.y += 1
                org.energy -= 1
                org.frame.grid(row = int(org.y))
            if org.target != False and org.target != True:
                if org.target.y == org.y: #stops the organism if it is in line with its target
                    org.energy -= move_count #organisms still loses full energy equal to speed even if it stops early. a balance btween movement and efficiency will evolve
                    move_count = 0 
                if org.y == org.target.y and org.x == org.target.x and org.target.name[0] == 'P' and org.mate_ready == True and org.target.mate_ready == True:  #breeding logic
                    Breed(org)
                    org.turns_since_act = 0

            if food_in_path == True: #organism consumes any food it comes across.
                for food in food_list:
                    if org.y == food.y and org.x == food.x:
                        org.energy += food.nutrition
                        org.turns_since_act = 0
                        food_list.remove(food)
                        food.kill_self_food()
            if org.energy <= 0:
                move_count = 0
                org_list.remove(org)
                org.kill_self_org()

        move_count -= 1 #wont try to move forever
        time.sleep(board.game_delay)

    if org.bored == False:  #wont keep track of inaction if org is already bored
        org.turns_since_act += 1  
    if org.bored == True: #time down if this turn org was bored
        org.boredom_timer -= 1   
        org.turns_since_act = 0 #doesnt count towards being bored if already bored

def move_left(org,distance):
    food_in_path = False
    obs_in_path = False
    move_count = distance

    #checks if the organism may run into something, so that it doesnt nessacarily have to check each time it moves
    for food in food_list:
        if org.y == food.y:
            food_in_path = True
    for obs in obs_list:
        if org.y == obs.y and obs.strength > org.strength:
            obs_in_path = True

    #actual movement logic
    while move_count > 0 and org.x > 1:
        global running
        if running == True:
            blocked = False
            if obs_in_path == True:
                for obs in obs_list:
                    if (org.x == obs.x + 1) and org.y == obs.y and org.strength < obs.strength: #will this obs block this org
                        blocked = True
                    if (org.x == obs.x + 1) and org.y == obs.y and org.strength >= obs.strength: #if an organisms powers through an obstacles, removes energy
                        org.energy -= org.speed                    
            if blocked == False: #moves organism if it isnt blocked
                org.x -= 1
                org.energy -= 1
                org.frame.grid(column = int(org.x))
            if org.target != False and org.target != True:
                if org.target.x == org.x: #stops the organism if it is in line with its target
                    org.energy -= move_count #organisms still loses full energy equal to speed even if it stops early. a balance btween movement and efficiency will evolve
                    move_count = 0        
                if org.y == org.target.y and org.x == org.target.x and org.target.name[0] == 'P' and org.mate_ready == True and org.target.mate_ready == True:  #breeding logic
                    Breed(org)
                    org.turns_since_act = 0


            if food_in_path == True: #organism consumes any food it comes across.
                for food in food_list:
                    if org.y == food.y and org.x == food.x:
                        org.energy += food.nutrition
                        org.turns_since_act = 0
                        food_list.remove(food)
                        food.kill_self_food()
            if org.energy <= 0:
                move_count = 0
                org_list.remove(org)
                org.kill_self_org()


        move_count -= 1 #wont try to move forever
        time.sleep(board.game_delay)

    if org.bored == False:  #wont keep track of inaction if org is already bored
        org.turns_since_act += 1  
    if org.bored == True: #time down if this turn org was bored
        org.boredom_timer -= 1   
        org.turns_since_act = 0 #doesnt count towards being bored if already bored
    
    
def move_right(org,distance):
    food_in_path = False
    obs_in_path = False
    move_count = distance

    #checks if the organism may run into something, so that it doesnt nessacarily have to check each time it moves
    for food in food_list:
        if org.y == food.y:
            food_in_path = True
    for obs in obs_list:
        if org.y == obs.y and obs.strength > org.strength:
            obs_in_path = True

    #actual movement logic
    while move_count > 0 and org.x < 250:
        global running
        if running == True:
            blocked = False
            if obs_in_path == True:
                for obs in obs_list:
                    if (org.x == obs.x - 1) and org.y == obs.y and org.strength < obs.strength: #will this obs block this org
                        blocked = True
                    if (org.x == obs.x - 1) and org.y == obs.y and org.strength >= obs.strength: #if an organisms powers through an obstacles, removes energy
                        org.energy -= org.speed
            if blocked == False: #moves organism if it isnt blocked
                org.x += 1
                org.energy -= 1
                org.frame.grid(column = int(org.x))
            if org.target != False and org.target != True:
                if org.target.x == org.x: #stops the organism if it is in line with its target
                    org.energy -= move_count  #organism still loses full energy equal to speed even if it stops early. a balance btween movement and efficiency will evolve
                    move_count = 0        
                if org.y == org.target.y and org.x == org.target.x and org.target.name[0] == 'P' and org.mate_ready == True and org.target.mate_ready == True:  #breeding logic
                    Breed(org)
                    org.turns_since_act = 0


            if food_in_path == True: #organism consumes any food it comes across.
                for food in food_list:
                    if org.y == food.y and org.x == food.x:
                        org.energy += food.nutrition
                        org.turns_since_act = 0
                        food_list.remove(food)
                        food.kill_self_food()
            if org.energy <= 0:
                move_count = 0
                org_list.remove(org)
                org.kill_self_org()


        move_count -= 1 #wont try to move forever
        time.sleep(board.game_delay)

    if org.bored == False:  #wont keep track of inaction if org is already bored
        org.turns_since_act += 1  
    if org.bored == True: #time down if this turn org was bored
        org.boredom_timer -= 1 
        org.turns_since_act = 0 #doesnt count towards being bored if already bored

#the main logic for the game:
def logic():
    global running
    while True:
        while running == True:
            board.population_count_display.config(text = str(len(org_list))) #updates display even when all organisms are dead
            board.energy_avg_display.config(text=FindMean('energy'))
            board.speed_avg_display.config(text=FindMean('speed'))
            board.strength_avg_display.config(text=FindMean('strength'))
            board.mate_threshold_avg_display.config(text=FindMean('mate_threshold'))
            board.offspring_contribution_avg_display.config(text=FindMean('offspring_contribution'))
            board.focus_avg_display.config(text=FindMean('focus'))
            board.boredom_avg_display.config(text=FindMean('boredom'))            
            if len(food_list) < 250:
                board.food_populate() #first, new food grows
            
            gen_test = 0
            for org in org_list:
                if org.generation > gen_test:
                    gen_test = org.generation
            board.newest_generation_display.config(text=gen_test)
                
            for org in org_list:   #next, the bored organisms have their stats altered, then move
                
                #display updating
                board.population_count_display.config(text = str(len(org_list)))    
                board.energy_avg_display.config(text=FindMean('energy'))
                board.speed_avg_display.config(text=FindMean('speed'))
                board.strength_avg_display.config(text=FindMean('strength'))
                board.mate_threshold_avg_display.config(text=FindMean('mate_threshold'))
                board.offspring_contribution_avg_display.config(text=FindMean('offspring_contribution'))
                board.focus_avg_display.config(text=FindMean('focus'))
                board.boredom_avg_display.config(text=FindMean('boredom'))
                
                
                
                #aging
                org.age += 1
                
                #bored?
                if org.bored == True and org.boredom_timer <= 0:
                    org.bored = False
                if org.turns_since_act >= org.focus and org.bored == False:
                    org.bored = True
                    org.boredom_timer = org.boredom   
                    
                
                #mate ready?
                if org.energy >= org.mate_threshold and org.age >= 10:
                    org.mate_ready = True
                else:
                    org.mate_ready = False
                
                #targeting
                if org.bored == False and ((len(food_list)>0) or (len(org_list)>0)):

                    if len(food_list) > 0:
                        for food_test in food_list:
                            org.target = food_test #gives the organisms a random starting target
                            break
                    elif len(org_list) > 0:
                        org.target = org
                    org.distance = 1000 #distance is too high, and so will absolutely be overwritten by another target
                    if org.mate_ready == False: #targets food if not ready to mate
                        for food_target in food_list:
                            food_target.distance = AbsoluteValue(org.x - food_target.x) + AbsoluteValue(org.y - food_target.y)
                            if food_target.distance < org.target.distance:
                                org.target = food_target
                    elif org.mate_ready == True:  #targets organism if ready to mate 
                        for org_target in org_list:
                            if org_target != org and org_target.mate_ready == True:
                                org_target.distance = AbsoluteValue(org.x - org_target.x) + AbsoluteValue(org.y - org_target.y)
                                if org_target.distance < org.target.distance:
                                    org.target = org_target
                        if org.target.name[0] != 'P':  #if the organism is mate ready, but cant find a ready partner, looks for food instead
                            for food_target in food_list:
                                food_target.distance = AbsoluteValue(org.x - food_target.x) + AbsoluteValue(org.y - food_target.y)
                                if food_target.distance < org.target.distance:
                                    org.target = food_target                            
                elif org.bored == True:
                    org.target = False
                
                
                #distance choosing
                chosen_direction = 0
                if org.bored == True:
                    chosen_direction = random.randint(1,4)
                elif org.bored == False and org.target != False and org.target != True:            
                    y_dist = AbsoluteValue(org.y - org.target.y)
                    x_dist = AbsoluteValue(org.x - org.target.x)
                    
                    if y_dist >= x_dist and org.y - org.target.y > 0: #conditions for moving up
                        chosen_direction = 1
                    elif y_dist > x_dist and org.y - org.target.y < 0: #conditions for moving down
                        chosen_direction = 3
                    elif x_dist > y_dist and org.x - org.target.x > 0: #conditions for moving left
                        chosen_direction = 4
                    elif x_dist > y_dist and org.x - org.target.x < 0: #conditions for moving right
                        chosen_direction = 2
                    else: #failsafe movement
                        chosen_direction = random.randint(1,4) 
               
               #more failsafes
                if org.target == True or False:
                    chosen_direction = random.randint(1,4) 

                if chosen_direction == 1:
                    move_up(org,org.speed)
                elif chosen_direction == 2:
                    move_right(org,org.speed)
                elif chosen_direction == 3:
                    move_down(org,org.speed)
                elif chosen_direction == 4:
                    move_left(org,org.speed)
                if org.age > 100: #organism can die of old age
                    org.energy = -500
                
            
            
            
            
            time.sleep(0.1)
        time.sleep(1) #this delay ensures that the startup is efficient
        
        
    


gui_thread = threading.Thread(target = GUI, args=())
logic_thread = threading.Thread(target = logic,args=())
gui_thread.start()
logic_thread.start()
