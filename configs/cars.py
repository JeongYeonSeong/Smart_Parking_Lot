import configs.config as cf
########################       
# node condition
########################
class Parks:
    nodes = [[], [], [], [], [], [], [],
             [], {}, [], {}, [], {}, [],
             [], [], [], [], [], [], [],
             [], {}, [], {}, [], {}, [], 
             [], [], [], [], [], [], []]

    space = [[] for i in range(21)]

    # condition set
    @staticmethod
    def set_space(position, car_num):
        if car_num not in Parks.space[position - 1]:
            Parks.space[position - 1].append(car_num)
        
        for i, spaces in enumerate(Parks.space):
            if i != position - 1 and (car_num in spaces):
                Parks.del_space(i + 1, car_num)

    # condition change
    @staticmethod
    def change_space(p_position, n_position, car_num, ):
        Parks.space[p_position - 1].remove(car_num)
        Parks.space[n_position - 1].append(car_num)

    @staticmethod
    def del_space(p_position, car_num):
        Parks.space[p_position - 1].remove(car_num)

########################       
# car object
########################
class Car(Parks):
    """
    <string> id 
            for identifiy
    
    <integer> pos_x, pos_y 
            for navigating and detect position
    
    <integer> position
            position on Area
    
    <list> detected 
            for calculate detecting rate
    """
    def __init__(self, argId=None, argX=None, argY=None, argRoute=None, argMain_cars=None, inits=None):
        if inits != None:
            self.init_parked(inits)
            """
            inits = {id : int, position : int}
            """
        else:
            self.id = argId
            self.prev_pos = 6
            self.position = 9
            self.route = argRoute
            self.route_stop = False
            self.set_position(argX, argY, argMain_cars)

    def init_parked(self, inits):
        self.id = inits['id']
        positions = ['', 
                    'AAA11', 'AAA12', 'AAA13', 'AAA21', 'AAA22', 'AAA23', 
                    'BBB11', 'BBB12', 'BBB13', 'BBB21', 'BBB22', 'BBB23',
                    'CCC11', 'CCC12', 'CCC13', 'CCC21', 'CCC22', 'CCC23',
                    'DDD11', 'DDD12', 'DDD13', 'DDD21', 'DDD22', 'DDD23'
        ]
        ##################################################################
        # 초기화 포지션 설정
        ##################################################################

        pos_xy = {'AAA11' :[1,1], 'AAA12' :[1,1], 'AAA13' :[1,1], 
                  'BBB11' :[1,1], 'BBB12' :[1,1], 'BBB13' :[1,1],
                  'AAA21' :[1,1], 'AAA22' :[1,1], 'AAA23' :[1,1], 
                  'BBB21' :[1,1], 'BBB22' :[1,1], 'BBB23' :[1,1],
                  'CCC11' :[1,1], 'CCC12' :[1,1], 'CCC13' :[1,1], 
                  'DDD11' :[1,1], 'DDD12' :[1,1], 'DDD13' :[1,1], 
                  'CCC21' :[1,1], 'CCC22' :[1,1], 'CCC23' :[1,1],
                  'DDD21' :[1,1], 'DDD22' :[1,1], 'DDD23' :[1,1]
        }

        ############## - set y - ##############
        #Y ---- A, B
        aby1 = cf.PARK_Y_POS[1]
        aby2 = cf.PARK_Y_POS[2]

        #Y ---- C, D
        cdy1 = cf.PARK_Y_POS[3]
        cdy2 = cf.PARK_Y_POS[4]

        # set y position
        line1_y = aby1 + (aby1 - aby2) / 4
        line2_y = aby1 + (aby1 - aby2) / 4 * 3
        line3_y = cdy1 + (cdy1 - cdy2) / 4
        line4_y = cdy1 + (cdy1 - cdy2) / 4 * 3

        for i in pos_xy:
            if i[-3:-1] == 'A1' or 'B1':
                pos_xy[i][1] = line1_y
            elif i[-3:-1] == 'A2' or 'B2':
                pos_xy[i][1] = line2_y
            elif i[-3:-1] == 'C1' or 'D1':
                pos_xy[i][1] = line3_y
            elif i[-3:-1] == 'C1' or 'D1':
                pos_xy[i][1] = line4_y
        #######################################

        ############## - set x - ##############
        #X ---- A, C
        acx1 = cf.PARK_X_POS[1]
        acx2 = cf.PARK_X_POS[2]

        #X ---- B, D
        bdx1 = cf.PARK_X_POS[3]
        bdx2 = cf.PARK_X_POS[4]

        for i in pos_xy:
            if i[0] == 'A' or i[0] == 'C':
                left = acx1['start'] - (acx1['start'] - acx1['end']) / 1440 * pos_xy[i][1]
                right = acx2['start'] - (acx2['start'] - acx2['end']) / 1440 * pos_xy[i][1]
                pos_xy[i][0] = left + (right - left) / 6 * (int(i[-1]) * 2 - 1)
            elif i[0] == 'B' or i[0] == 'D':
                left = bdx1['start'] - (bdx1['start'] - bdx1['end']) / 1440 * pos_xy[i][1]
                right = bdx2['start'] - (bdx2['start'] - bdx2['end']) / 1440 * pos_xy[i][1]
                pos_xy[i][0] = left + (right - left) / 6 * (int(i[-1]) * 2 - 1)

        self.position = positions[inits['position']]
        self.prev_pos = self.position
        self.pos_x = pos_xy[self.position][0]
        self.pos_y = pos_xy[self.position][1]

        self.route = None
        self.route_stop = True
        return

    def set_position(self, pos_x, pos_y, main_cars):
        self.pos_x = pos_x
        self.pos_y = pos_y
        print('x :',self.pos_x, 'y :',self.pos_y,'p :', self.position, 'pp :', self.prev_pos)
        
        y_pos = cf.PARK_Y_POS

        # fomul sets
        sets = cf.PARK_X_POS
        checks = 0
        if y_pos[0] <= pos_y < y_pos[1]:
            for i in range(len(sets)):
                track1 = (sets[i]['start'] - sets[i]['end']) / 1440
                track2 = ((sets[i + 1]['start'] - sets[i + 1]['end']) / 1440) if i != len(sets) - 1 else 0
                for k in range(y_pos[0], y_pos[1], 5):
                    if i == len(sets) - 1:
                        if sets[i]['start'] - k * track1 <= pos_x and k <= pos_y < k + 5:
                            self.prev_pos = self.position
                            self.position = i + 1
                            Parks.set_space(self.position, self.id)
                            checks = 1
                            break
                    elif sets[i]['start'] - k * track1 <= pos_x < sets[i + 1]['start'] - k * track2  and k <= pos_y < k + 5:
                        self.prev_pos = self.position
                        self.position = i + 1
                        Parks.set_space(self.position, self.id)
                        checks = 1
                        break
                if checks:
                    break
            if checks == 0:
                self.position = 'outsider'
                if int(self.prev_pos) not in range(1, 22):
                    for index, car in enumerate(main_cars):
                        if car.id == self.id:
                            main_cars.cars.pop(index)
                
        elif y_pos[1] <= pos_y < y_pos[2]:
            for i in range(len(sets[0::2])):
                p = i * 2
                track1 = (sets[p]['start'] - sets[p]['end']) / 1440
                track2 = ((sets[p + 1]['start'] - sets[p + 1]['end']) / 1440) if p != len(sets) - 1 else 0

                for k in range(y_pos[1], y_pos[2], 5):
                    if p == len(sets) - 1:
                        if sets[p]['start'] - k * track1 <= pos_x and k <= pos_y < k + 5:
                            print('k :', k)
                            self.prev_pos = self.position
                            self.position = i + 6
                            Parks.set_space(self.position, self.id)
                            checks = 1
                            break
                    elif sets[p]['start'] - k * track1 <= pos_x < sets[p + 1]['start'] - k * track2 and k <= pos_y < k + 5:
                        print('k :', k)
                        self.prev_pos = self.position
                        self.position = i + 6
                        Parks.set_space(self.position, self.id)
                        checks = 1
                        break
                if checks:
                    break
                    
            if checks == 0:
                self.prev_pos = self.position
                self.position = 'outsider'
                self.route_stop = True
                half = int((y_pos[2] - y_pos[1]) / 2)

                left1 = (sets[1]['start'] - sets[1]['end']) / 1440 * (half + y_pos[1])
                right1 = (sets[2]['start'] - sets[2]['end']) / 1440 * (half + y_pos[1])
                left2 = (sets[3]['end'] - sets[3]['start']) / 1440 * (half + y_pos[1])
                right2 = (sets[4]['end'] - sets[4]['start']) / 1440 * (half + y_pos[1])

                third_x = (left1 - right1) / 3
                third_x2 = (right2 - left2) / 3
                if sets[1]['start'] - left1 <= self.pos_x < sets[1]['start'] - left1 + third_x:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[1] + half:
                        self.position = 'AAA11'
                    else:
                        self.position = 'AAA24'
                elif sets[1]['start'] - left1 + third_x <= self.pos_x < sets[1]['start'] - left1 + third_x * 2:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[1] + half:
                        self.position = 'AAA12'
                    else:
                        self.position = 'AAA25'
                elif sets[1]['start'] - left1 + third_x * 2 <= self.pos_x < sets[1]['start'] - left1 + third_x * 3:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[1] + half:
                        self.position = 'AAA13'
                    else:
                        self.position = 'AAA26'
                elif sets[3]['start'] + left2 <= self.pos_x < sets[3]['start'] + left2 + third_x2:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[1] + half:
                        self.position = 'BBB11'
                    else:
                        self.position = 'BBB24'
                elif sets[3]['start'] + left2 + third_x2 <= self.pos_x < sets[3]['start'] + left2 + third_x2 * 2:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[1] + half:
                        self.position = 'BBB12'
                    else:
                        self.position = 'BBB25'
                elif sets[3]['start'] + left2 + third_x2 * 2 <= self.pos_x < sets[3]['start'] + left2 + third_x2 * 3:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[1] + half:
                        self.position = 'BBB13'
                    else:
                        self.position = 'BBB26'

        elif y_pos[2] <= pos_y < y_pos[3]:
            for i in range(len(sets)):
                track1 = (sets[i]['start'] - sets[i]['end']) / 1440
                track2 = ((sets[i + 1]['start'] - sets[i + 1]['end']) / 1440) if i != len(sets) - 1 else 0
                for k in range(y_pos[2], y_pos[3], 5):
                    if i == len(sets) - 1:
                        if sets[i]['start'] - k * track1 <= pos_x and k <= pos_y < k + 5:
                            self.prev_pos = self.position
                            self.position = i + 9
                            Parks.set_space(self.position, self.id)
                            checks = 1
                            break
                    elif sets[i]['start'] - k * track1 <= pos_x < sets[i + 1]['start'] - k * track2 and k <= pos_y < k + 5:
                        self.prev_pos = self.position
                        self.position = i + 9
                        Parks.set_space(self.position, self.id)
                        checks = 1
                        break
                if checks:
                    break
            if checks == 0:# and self.pos_x < 600:
                self.position = 'outsider'
                if int(self.prev_pos) not in range(1, 22):
                    for index, car in enumerate(main_cars):
                        if car.id == self.id:
                            main_cars.cars.pop(index)

        elif y_pos[3] <= pos_y < y_pos[4]:
            for i in range(len(sets[0::2])):
                p = i * 2
                track1 = (sets[p]['start'] - sets[p]['end']) / 1440
                track2 = ((sets[p + 1]['start'] - sets[p + 1]['end']) / 1440) if p != len(sets) - 1 else 0

                for k in range(y_pos[3], y_pos[4], 5):
                    if p == len(sets) - 1:
                        if sets[p]['start'] - k * track1 <= pos_x and k <= pos_y < k + 5:
                            print('k :', k)
                            self.prev_pos = self.position
                            self.position = i + 14
                            Parks.set_space(self.position, self.id)
                            checks = 1
                            break
                    elif sets[p]['start'] - k * track1 <= pos_x < sets[p + 1]['start'] - k * track2 and k <= pos_y < k + 5:
                        print('k :', k)
                        self.prev_pos = self.position
                        self.position = i + 14
                        Parks.set_space(self.position, self.id)
                        checks = 1
                        break
                if checks:
                    break
            if checks == 0:
                self.route_stop = True
                half = int((y_pos[4] - y_pos[3]) / 2)
                self.position = 'outsider'

                left1 = (sets[1]['start'] - sets[1]['end']) / 1440 * (half + y_pos[3])
                right1 = (sets[2]['start'] - sets[2]['end']) / 1440 * (half + y_pos[3])
                left2 = (sets[3]['end'] - sets[3]['start']) / 1440 * (half + y_pos[3])
                right2 = (sets[4]['end'] - sets[4]['start']) / 1440 * (half + y_pos[3])

                third_x = int((left1 - right1) / 3)
                third_x2 = int((right2 - left2) / 3)
                if sets[1]['start'] - left1 <= self.pos_x < sets[1]['start'] - left1 + third_x:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[3] + half:
                        self.position = 'CCC11'
                    else:
                        self.position = 'CCC24'
                elif sets[1]['start'] - left1 + third_x <= self.pos_x < sets[1]['start'] - left1 + third_x * 2:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[3] + half:
                        self.position = 'CCC12'
                    else:
                        self.position = 'CCC25'
                elif sets[1]['start'] - left1 + third_x * 2 <= self.pos_x < sets[1]['start'] - left1 + third_x * 3:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[3] + half:
                        self.position = 'CCC13'
                    else:
                        self.position = 'CCC26'
                elif sets[3]['start'] <= self.pos_x < sets[3]['start'] + third_x2:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[3] + half:
                        self.position = 'DDD11'
                    else:
                        self.position = 'DDD24'
                elif sets[3]['start'] + third_x2 <= self.pos_x < sets[3]['start'] + third_x2 * 2:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[3] + half:
                        self.position = 'DDD12'
                    else:
                        self.position = 'DDD25'
                elif sets[3]['start'] + third_x2 * 2 <= self.pos_x < sets[3]['start'] + third_x2 * 3:
                    self.prev_pos = self.position
                    if self.pos_y <= y_pos[3] + half:
                        self.position = 'DDD13'
                    else:
                        self.position = 'DDD26'
                
        elif y_pos[4] <= pos_y < y_pos[5]:
            for i in range(len(sets)):
                track1 = (sets[i]['start'] - sets[i]['end']) / 1440
                track2 = (sets[i + 1]['start'] - sets[i + 1]['end']) / 1440 if i != len(sets) - 1 else 0
                for k in range(y_pos[4], y_pos[5], 5):
                    if i == len(sets) - 1:
                        if sets[i]['start'] - k * track1 <= pos_x and  k <= pos_y < k + 5:
                            print('k :', k)
                            self.prev_pos = self.position
                            self.position = i + 17
                            Parks.set_space(self.position, self.id)
                            checks = 1
                            break
                    elif sets[i]['start'] - k * track1 <= pos_x < sets[i + 1]['start'] - k * track2 and k <= pos_y < k + 5:
                        print('k :', k)
                        self.prev_pos = self.position
                        self.position = i + 17
                        Parks.set_space(self.position, self.id)
                        checks = 1
                        break
                if checks:
                    break
            if checks == 0:# and self.pos_x < 600:
                self.position = 'outsider'
                if self.prev_pos != 'outsider' and int(self.prev_pos) not in range(1, 22) :
                    for index, car in enumerate(main_cars):
                        if car.id == self.id:
                            main_cars.cars.pop(index)

        if self.position == 'outsider':
            self.route_stop = True
            return True

        # changed position => server connection(get route)
        if self.prev_pos != self.position:
            return False

        # no need server connection
        return True

    def set_route(self, argRoute):
        self.route = argRoute
        self.count = 0

    def is_on_route(self):
        self.count = 0
        if self.route[self.count] != self.position:
            return False
        else:
            self.count += 1
            return True

class Car_List:
    """
    list cars 
            for get detected cars
    """
    def __init__(self, argleftFrame):
        """"""
        
        self.cars = []

