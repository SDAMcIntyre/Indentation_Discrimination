import random
# how many points on each side to create
TOTAL_ON_ONE_SIDE = 3
# how far away from the midline should they be
HORIZONTAL_DISTANCE = 3
# how far away in vertical direction should they be spaced
VERTICAL_DISTANCE = 2

class Coordinator():

    '''
        Motor will move to the right and down 
        from the start position (from top left corner)
        Square A is always to the left of Square B!
        
        square A  square B
        -------------------
        |        |        |
        |        |        |
        -------------------
    '''
    def __init__(self,total=TOTAL_ON_ONE_SIDE,horizontal=HORIZONTAL_DISTANCE,vertical=VERTICAL_DISTANCE):
        self.total = total
        self.horizontal = horizontal
        self.vertical = vertical
        # side of each squre in mm
        # default = 10mm
        self.side = 10
        self.mid_point = self.crete_mid_point_border()
        self.left_coordinates = self.create_left_coordinates()
        self.right_coordinates = self.create_right_coordinates()

    def crete_mid_point_border(self):
        x = self.side
        y = int(self.side/2)
        return (x,y)

    def create_left_coordinates(self):
        coord_list = []
        for i in range(self.total):
            x = self.mid_point[0]-self.horizontal
            if i%2==0:
                if i == 0:
                    y = self.mid_point[1]
                else:
                    y = coord_list[-2][1]+self.vertical
            else:
                if i==1:
                    y = self.mid_point[1]-self.vertical
                else:
                    y = coord_list[-2][1]-self.vertical
            if y <= self.side:
                coord_list.append((x,y))
        return coord_list

    def create_right_coordinates(self):
        coord_list = []
        for i in range(self.total):
            x = self.mid_point[0]+self.horizontal
            if i%2==0:
                if i == 0:
                    y = self.mid_point[1]
                else:
                    y = coord_list[-2][1]+self.vertical
            else:
                if i==1:
                    y = self.mid_point[1]-self.vertical
                else:
                    y = coord_list[-2][1]-self.vertical
            if y <= self.side:
                coord_list.append((x,y))
        return coord_list


    # randomly shuffle odd
    # reverse order of even pair
    # Standard areas names can be either A or B (A is to the left of midline, B is to the right of midline)
    def create_left_right_random_sequences(self,total_repetitions,standard_area='A',comparison_area='B'):
        if standard_area == 'A' and comparison_area == 'B':
            areas = [self.left_coordinates,self.right_coordinates]
        elif standard_area == 'B' and comparison_area == 'A':
            areas = [self.right_coordinates, self.left_coordinates]
        else:
            print("Standard and comparison areac can be only called A or B!")
            return []
        # 0 stands for standard area, 1 stands for comparison area
        order = [0, 1]
        # this is a list of dictionaries for psychopy trials
        sequences = []
        if total_repetitions > 0:
            for i in range(total_repetitions):
                if i%2 == 0: #always shuffle first
                    random.shuffle(order)
                    my_order_translated = 'standard first' if order[0] == 0 else 'standard second'
                    my_dict = {'standard':random.choice(areas[0]),
                                'comparison':random.choice(areas[1]),
                                'presentation order':my_order_translated}
                    sequences.append(my_dict)
                elif i%2 != 0:
                    my_order_translated = 'standard first' if sequences[-1]['presentation order'] == 'standard second' else 'standard second'
                    my_dict = {'standard':random.choice(areas[0]),
                                'comparison':random.choice(areas[1]),
                                'presentation order':my_order_translated}
                    sequences.append(my_dict)
        else:
            print("choose to generate at least one pair")
        ##################################################
        # # debug
        for i in range(len(sequences)):
            # print(sequences[i]['presentation order'])
            if standard_area == 'A':
                if sequences[i]['presentation order'] == 'standard first':
                    print('AB')
                else:
                    print('BA')
            else:
                if sequences[i]['presentation order'] == 'standard first':
                    print('BA')
                else:
                    print('AB')
            print(sequences[i])
            print()
        return sequences
