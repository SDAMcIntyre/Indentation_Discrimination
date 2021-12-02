import random
class Squares():
    '''
        Motor will move to the right and down 
        from the start position (from top left corner)
        -------------------
        |        |        |
        |        |        |
        -------------------
    '''
    def __init__(self): 
        # side of each squre in mm
        # default = 10mm
        self.side = 10
        # how far apart from eachother are points in the square area (mm)
        self.step = 4
        # instantiate default suare coordinates:
        # name left: area A and right: area B
        self.square_left = {'A':self.create_left_area_coordinates(self.side,self.step)}
        self.square_right = {'B':self.create_right_area_coordinates(self.side,self.step)}

        
    # creates a list of coordinates for left square
    def create_left_area_coordinates(self,side,step):
        # print("creating left square")
        coordinates = []
        start_x = 0
        start_y = 0
        while start_x < side-step:
            start_x = start_x + step
            while start_y < side-step:
                start_y = start_y + step
                # print(start_x,start_y)
                coordinates.append((start_x,start_y))
            start_y = 0
        return coordinates
    # creates a list of coordinates for right square   
    def create_right_area_coordinates(self,side,step):
        # print("creating right square")
        coordinates = []
        start_x = side
        start_y = 0
        while start_x < 2*side-step:
            start_x = start_x + step
            while start_y < side-step:
                start_y = start_y + step
                # print(start_x,start_y)
                coordinates.append((start_x,start_y))
            start_y = 0
        return coordinates

    # randomly shuffle odd
    # reverse order of even pair
    def create_left_right_random_sequences(self,total):
        areas = [self.square_left,self.square_right]
        order = [0, 1]
        sequences = []
        if total > 0:
            for i in range(total):
                if i == 0 or i%2 == 0: #always shuffle first
                    random.shuffle(order)
                    my_order_translated = 'standard first' if order[0] == 0 else 'standard second'
                    my_dict = {'standard':areas[0]['A'],
                                'comparison':areas[1]['B'],
                                'presentation order':my_order_translated}
                    # areas = [areas[order[0]],areas[order[1]]]
                    sequences.append(my_dict)
                elif i%2 != 0:
                    my_order_translated = 'standard first' if sequences[-1]['presentation order'] == 'standard second' else 'standard second'
                    my_dict = {'standard':areas[0]['A'],
                                'comparison':areas[1]['B'],
                                'presentation order':my_order_translated}
                    # areas = [areas[1],areas[0]]
                    sequences.append(my_dict)
        else:
            print("choose to generate at least one pair")
        ##################################################
        # # debug
        # for i in range(len(sequences)):
        #     print(sequences[i]['presentation order'])
        #     print(sequences[i])
        #     print()
        return sequences