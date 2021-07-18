import socket
import configs.config as cf
import threading as th
import time
import requests

#Clients
class Clients:
    def __init__(self, ip, port):
        self.host = ip
        self.port = port

        self.client = socket.socket()
        self.client.connect((self.host, self.port))
        print('conect server')
        print('IP :', self.host)
        print('PORT :', self.port)

    def send_message(self, inputs):
        self.client.send(inputs.encode())    # send message
        data = self.client.recv(1024).decode()    # receive response

        data = data.split('/', 20)

        print('Received from server: ', data)  # receive response
        return data

    def end_client(self):
        self.client.close()
        print('connention closed')

#Server
class Servers:
    def __init__(self, navs):
        self.data_count = 1

        self.host = cf.SOC_IP
        self.port = cf.NAV_PORT
        print('host name :', self.host)
        print('host port :', self.port)
        self.server = socket.socket()
        self.server.bind((self.host, self.port))
        self.navs = navs
        self.parked = {'AAA1':{'now':0, 'max':3, 'edge': 2}, 'BBB1':{'now':0, 'max':3, 'edge': 4},
                    'AAA2':{'now':0, 'max':3, 'edge': 10}, 'BBB2':{'now':0, 'max':3, 'edge': 12},
                    'CCC1':{'now':0, 'max':3, 'edge': 10}, 'DDD1':{'now':0, 'max':3, 'edge': 12},
                    'CCC2':{'now':0, 'max':3, 'edge': 18}, 'DDD2':{'now':0, 'max':3, 'edge': 20}}

        """
        parked initialization
        """
        response = requests.get('http://34.204.54.60/api/initParking')
        datas = response.json()['parkingList']
        
        for i in datas:
            position = None
            if i['car_parking_id'] in [1,2,3]:
                position = 'AAA1'
            elif i['car_parking_id'] in [4,5,6]:
                position = 'AAA2' 
            elif i['car_parking_id'] in [7,8,9]:
                position = 'BBB1' 
            elif i['car_parking_id'] in [10,11,12]:
                position = 'BBB2' 
            elif i['car_parking_id'] in [13,14,15]:
                position = 'CCC1' 
            elif i['car_parking_id'] in [16,17,18]:
                position = 'CCC2' 
            elif i['car_parking_id'] in [19,20,21]:
                position = 'DDD1' 
            elif i['car_parking_id'] in [22,23,24]:
                position = 'DDD2' 
            
            self.parked[position]['now'] += 1

        self.disp_pos = ['3A', '3B', '9A', '9B', '11A', '11B', '13A', '13B', '19A', '19B']
        self.conns = []
        self.disp_prev = [[4,7],[2],[10,14],[6],[12,15],[7,10],[16],[8,12],[20],[15,18]]

        self.disp = [3,9,11,13,19]
        self.disp_next = [[[7,2,0], [2,0,4], [0,4,7]],
                          [[14,0,6], [0,6,10], [10,14,0]],
                          [[15,10,7], [10,7,12], [12,15,10], [7,12,15]],
                          [[12,8,0], [0,16,12], [8,0,16]],
                          [[0,18,15], [20,0,18], [15,20,0]]]

        self.routings = {}
        for i in self.parked:
            if self.parked[i]['now'] >= self.parked[i]['max'] and self.parked[i]['edge'] in self.navs.parking:
                self.navs.parking.remove(self.parked[i]['edge'])

        # dummy data
        self.queue = ['11가1111']

        self.start_server_func()

    def start_server_func(self):
        # self.server.listen(5)
        # counts = 0
        #
        # while True:
        #     self.connections()
        #     self.get_connect_rasp()
        #     counts += 1
        #     if counts == 2:
        #         break
        #     time.sleep(1)

        print('ready to start service')

        while 1:
            thread = th.Thread(target=self.send_message_tracking)
            thread.start()
            time.sleep(0.1)

    def connections(self):
        self.conn, self.address = self.server.accept()  # accept new connection
        print("Connection from: ", str(self.address))

    def get_connect_rasp(self):
        data = self.conn.recv(1024).decode()
        if not data:
            # if data is not received break
            return
        if data == '00':
            self.conns.append(self.conn)
            return

    def send_message_rasp(self, message):
        self.broad_cast(message)

    def send_request(self, argURL, car_num, position=''):
        URL = argURL
        postData = {
            'parking_id' : str(position),
            'numberPlate' : str(car_num)
        }
        print('requests',URL, postData)
        response = requests.post(URL, postData)
        print(response.status_code)

    def send_message_tracking(self):
        self.server.listen(1)
        self.conn, self.address = self.server.accept()
        data = self.conn.recv(1024).decode()
        if not data:
            # if data is not received break
            return
        
        data = data.split('/', 20)
        print("from connected user: ", data)

        # entered car's queue
        if data[0] == '1':
            self.queue.append(data[1])
            data = 'got it'
            self.conn.send(data.encode())
            print(self.queue)
            return 0
        # send entered car_num
        elif data[0] == '2':
            np = 9
            pp = 0
            data = ''
            routing = []
            if len(self.queue) == 0:
                data = 'no Data'
            else:
                data = self.queue.pop(0)
                routing = self.navs.routing(prev=pp, start = np)
                self.routings[data] = routing + [str(pp)]
            self.conn.send((data + '/' + str(routing)).encode())
            
            print('routing :', routing)
            
            if len(routing) >= 2:
                disp = '9B'
                direction = 2
                if routing[1] == '6':
                    direction = '1'
                elif routing[1] == '10':
                    direction = '2'
                elif routing[1] == '14':
                    direction = '3'
                print('rasp gogo data[0] = 2 :', direction + '/' + data + '/' + disp)
                self.send_message_rasp(direction + '/' + data + '/' + disp)

            print(self.routings)
            return 1
        # send routing
        elif data[0] == '3' or data[0] == '4':
            np = 9
            pp = 0
            if len(data) == 2:
                np = data[1]
            elif len(data) >= 3:
                np = data[1]
                pp = data[2]
                if len(data[1]) >= 4:
                    if data[1] == 'outsider':
                        self.conn.send('got it'.encode())
                        self.end_connection()
                        return
                    URL = cf.AWS_IP + '/api/carParked'
                    for i in range(1,25):
                        if data[1][4:] == str(i):
                            plus = 0
                            if data[1][0] == 'B':
                                plus = 6
                            elif data[1][0] == 'C':
                                plus = 12
                            elif data[1][0] == 'D':
                                plus = 18
                            self.send_request(URL, data[3], i + plus)
                            break

                    self.parked[data[1][:4]]['now'] += 1
                    if data[1][:4] == 'AAA2' or data[1][:4] == 'BBB2':
                        if self.parked['AAA2']['now'] >= self.parked['AAA2']['max'] and self.parked['BBB2']['now'] >= self.parked['BBB2']['max']:
                            self.parked[data[1][:4]]['now'] = self.parked[data[1][:4]]['max']
                            if self.parked[data[1][:4]]['edge'] in self.navs.parking:
                                self.navs.parking.remove(self.parked[data[1][:4]]['edge'])
                    elif data[1][:4] == 'CCC1' or data[1][:4] == 'DDD1':
                        if self.parked['CCC1']['now'] >= self.parked['CCC1']['max'] and self.parked['DDD1']['now'] >= self.parked['DDD1']['max']:
                            self.parked[data[1][:4]]['now'] = self.parked[data[1][:4]]['max']
                            if self.parked[data[1][:4]]['edge'] in self.navs.parking:
                                self.navs.parking.remove(self.parked[data[1][:4]]['edge'])
                    elif self.parked[data[1][:4]]['now'] >= self.parked[data[1][:4]]['max']:
                        self.parked[data[1][:4]]['now'] = self.parked[data[1][:4]]['max']
                        if self.parked[data[1][:4]]['edge'] in self.navs.parking:
                            self.navs.parking.remove(self.parked[data[1][:4]]['edge'])

                    self.conn.send(data[1].encode())
                    self.end_connection()
                    return

                if len(data[2]) >= 4 and data[2] != '0':
                    URL = cf.AWS_IP + '/api/carParked'

                    if data[2][:4] == 'AAA1':
                        self.send_request(URL, data[3])
                    elif data[2][:4] == 'AAA2':
                        self.send_request(URL, data[3])
                    elif data[2][:4] == 'BBB1':
                        self.send_request(URL, data[3])
                    elif data[2][:4] == 'BBB2':
                        self.send_request(URL, data[3])
                    elif data[2][:4] == 'CCC1':
                        self.send_request(URL, data[3])
                    elif data[2][:4] == 'CCC2':
                        self.send_request(URL, data[3])
                    elif data[2][:4] == 'DDD1':
                        self.send_request(URL, data[3])
                    elif data[2][:4] == 'DDD2':
                        self.send_request(URL, data[3])
                    elif data[2][:4] == 'outs':
                        self.conn.send(data[1].encode())
                        self.end_connection()
                        return

                    self.parked[data[2][:4]]['now'] -= 1
                    if data[2][:4] == 'AAA2' or data[2][:4] == 'BBB2':
                        if self.parked['AAA2']['now'] != self.parked['AAA2']['max'] or self.parked['BBB2']['now'] != self.parked['BBB2']['max']:
                            if self.parked[data[2][:4]]['edge'] not in self.navs.parking:
                                self.navs.parking.append(self.parked[data[2][:4]]['edge'])
                                self.navs.parking.sort()
                    elif data[2][:4] == 'CCC1' or data[2][:4] == 'DDD1':
                        if self.parked['CCC1']['now'] != self.parked['CCC1']['max'] or self.parked['DDD1']['now'] != self.parked['DDD1']['max']:
                            if self.parked[data[2][:4]]['edge'] not in self.navs.parking:
                                self.navs.parking.append(self.parked[data[2][:4]]['edge'])
                                self.navs.parking.sort()
                    elif self.parked[data[2][:4]]['now'] != self.parked[data[2][:4]]['max']:
                        if self.parked[data[2][:4]]['edge'] not in self.navs.parking:
                            self.navs.parking.append(self.parked[data[2][:4]]['edge'])
                            self.navs.parking.sort()

                    self.conn.send(data[1].encode())
                    self.end_connection()
                    return
            if data[0] == '3':
                route = self.navs.routing(prev=pp, start=np)
                self.routings[data[3]] = route + [str(pp)]
                print(self.routings)
                for i, node in enumerate(self.disp_prev):
                    if np in node and pp != int(self.disp_pos[i][0]):
                        sends = str(self.disp_pos[i]) + '/' + data[3] + '/' + route
                        for p in self.conns:
                            if len(self.conns) <= 0:
                                break
                            p.send(sends.encode())
                self.conn.send(('/' + str(route)).encode())

            # set space condition down
            if len(data[2]) < 4 or data[2] != '0':
                nodes = self.navs.graph[int(data[2]) - 1]
                for i in nodes:
                    distance = self.navs.g.get_distance(data[2], i)
                    if distance - 50 >= 1:
                        distance -= 50
                    else:
                        distance = 1
                    self.navs.g.set_distance(data[2], str(i), distance)
            
            # set space condition up
            if len(data[1]) < 4 or data[1] != '0':
                nodes = self.navs.graph[int(data[1]) - 1]
                for i in nodes:
                    distance = self.navs.g.get_distance(data[1], i) + 50
                    self.navs.g.set_distance(data[1], str(i), distance)

            # send display datas to raspberryPi
            if data[0] == '3':
                # find disp
                zahyou = []
                for i in self.routings:
                    disps = 0
                    direction = 0

                    # if navigating is over
                    print('sockets320 - self.routings[i] :', self.routings[i])
                    if len(self.routings[i]) == 1 :
                        msg =  '0/' +  str(i[1]) + '/0'
                        self.send_message_rasp(msg)
                        continue

                    # if current node is in display area
                    if int(self.routings[i][0]) in self.disp :
                        prev = int(self.routings[i][-1])
                        current = self.routings[i][0]
                        index = self.disp.index(int(current))

                        # start set disp
                        disps = str(current)

                        # A,B check
                        nodes1 = self.disp_prev[index * 2]
                        nodes2 = self.disp_prev[index * 2 + 1]

                        if prev in nodes1:
                            disps += 'A'
                        elif prev in nodes2:
                            disps += 'B'
                        else:
                            print('there\'s some erroe in set disps')

                        # ready for set direction
                        next_count = 0                        
                        for abCount, node12 in enumerate((nodes1 + nodes2)):
                            if prev == node12:
                                next_count = abCount

                        # set direction
                        nextt = self.routings[i][1]
                        direction_check = self.disp_next[index][next_count]
                        direction = direction_check.index(int(nextt)) + 1

                    zahyou.append([direction, disps, i])

                # send data
                for i in zahyou:
                    msg = str(i[0]) + '/' + str(i[2]) + '/' +  str(i[1])
                    print('rasp gogo data zahyou :', msg)
                    self.send_message_rasp(msg)

        elif data[0] == 'out':
            self.conn.send('got it'.encode())
        else:
            self.conn.send('disconnected'.encode())
            return 1
                
        self.end_connection()
        time.sleep(0.2)
    def broad_cast(self, message):
        for i in self.conns:
            print(message)
            i.send(message.encode())

    def end_connection(self):
        self.conn.close()    # close the connection
        print('connention closed')
