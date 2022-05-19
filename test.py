from distutils import core
from queue import Empty
from re import X
from typing import List
import network as nt
import config as cf
import content as ct

from collections import deque

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam



class Agent():

    def __init__(self):

        self.network = nt.Network()
        # BackBone 인 Data Center 에는 다 있다고 가정?
        # [path 중 Mirco Base Station에 저장, path 중 Base Station에 저장,DataCenter에 저장]
        self.actions = [0,1,2]
        # path는 [node, Micro BS, BS, Data center, Core Internet]
        self.path = []
        # DNN network BS 
        # state 서비스의 종류, 서비스의 요청 빈도, 캐시 가용 자원 크기
        self.state = []

        # DNN 하이퍼파라미터
        self.episodes = 50
        self.eps_start = 0.9
        self.eps_end = 0.05
        self.eps_decay = 200
        self.gamma = 0.8
        self.learningRate = 0.001
        self.batchSize = 64


        # Model 
        self.model = self.model()
        self.targetModel = self.model()
        # ADAM
        self.optimizer = tf.keras.optimizers.Adam(lr=self.learningRate)
        self.steps = 0
        self.memory = deque(maxlen = 10000)

        # state 정의
        # 1. DataCenter 가용 캐시 자원의 크기
        # 2. BS 가용 캐시 자원의 크기
        # 3. MicroBS 가용 캐시 자원의 크기

        # 4번부터는 나중에
        # 4. 서비스의 요청 빈도

        self.DataCenter_AR = self.get_AR("DataCenter")
        self.BS_AR = self.get_AR("BS")
        self.MicroBS_AR = self.get_AR("MicroBS")
        
        

        # reward parameter
        self.a = 0.5
        self.b = 0.5
        self.d_core = 0
        self.d_cache = 0
        self.R_cache = 0
        self.H_arg = 0
        self.c_node = 0
    
    def get_AR(self, type):

        available_resource = 0
        storage = 0
        stored = 0
        if type == "DataCenter":
            available_resource = self.network.dataCenter.storage.capacity - self.network.dataCenter.storage.stored
            
        elif type == "BS":
            for i in range(cf.NUM_BS[0]*cf.NUM_BS[1]):

                stored = stored + self.network.BSList[i].storage.stored

            storage = cf.BS_SIZE * cf.NUM_BS[0]*cf.NUM_BS[1] 
            available_resource = storage - stored

        elif type == "MicroBS":
            for i in range(cf.NUM_microBS[0]*cf.NUM_microBS[1]):

                stored = stored + self.network.microBSList[i].storage.stored

            storage = cf.microBS_SIZE * cf.NUM_microBS[0]*cf.NUM_microBS[1] 
            available_resource = storage - stored

        return available_resource

    def create_model(self):

        # state 갯수는 일단 3개로 하자
        model = tf.keras.Sequential([
            tf.keras.layers.InputLayer(input_shape=(3,)),
            tf.keras.layers.Dense(units=9, activation=tf.nn.relu),
            tf.keras.layers.Dense(units=6, activation=tf.nn.relu),
            tf.keras.layers.Dense(units=3, activation=tf.nn.softmax)
        ])
        
        return model
        
        
    def memorize(self, state, action, reward, next_state):

        self.memory.append(state,action,reward,next_state)

    def act(self, state):



    def set_reward(self):
        """
        Return the reward.
        The reward is:
        
            Reward = a*(d_core - d_cache) - b*coverage_node

            a,b = 임의로 정해주자 실험적으로 구하자
            d_core  : 네트워크 코어에서 해당 컨텐츠를 전송 받을 경우에 예상되는 지연 시간.
            d_cache : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간
            c_node : 캐싱된 contents가 포괄하는 device의 갯수
        """
        reward = 0
        reward = self.a*(self.d_core - self.d_cache) # + self.b*self.c_node

        return reward

    def get_reward_parameter(self):

        # d_core  : 네트워크 코어에서 해당 컨텐츠를 전송 받을 경우에 예상되는 지연 시간.
        #          

        # d_cache : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간
                   
        # R_cache : 네트워크에 존재하는 동일한 캐시의 수
        #           for 문으로 돌려야겠다

        # c_node   : 캐싱된 파일이 커버하는 노드의 수 (coverage node)
        #           

        self.d_core = self.get_d_core()
        self.d_cache = self.get_d_cache()
        self.c_node = self.get_c_node()



    def get_d_core(self):
        # 코어 인터넷까지 가서 가져오는 경우를 봐야함
        # path 뒤에 추가해서 구하자
        path = []
        path = self.network.request_and_get_path()

        # [4,68] 일 경우 ---> [4,68, search_next_path(microBS.x, microBS.y):BS, search_next_path(BS.x, BS.y):Datacenter, search_next_path(Datacenter.x, Datacenter.y):Core Internet]
        # path 다 채워질 떄까지 돌리자
        while len(path) != 5:

            # Micro에 캐싱되어 있는 경우, BS 추가
            if len(path) == 2:
                id = path[-1]
                closestID = self.network.search_next_path(self.network.microBSList[id].pos_x,self.network.microBSList[id].pos_y,1)
                path.append(closestID)

            # BS에 캐싱 되어 있는 경우, Data Center 추가
            elif len(path) ==  3:
                path.append(0)

            # 데이터 센터에 캐싱이 되어 있는 경우, Core Internet 추가
            elif len(path) == 4:
                path.append(0)

        d_core = self.network.uplink_latency(path) + self.network.downlink_latency(path)

        return d_core

    def get_d_cache(self):
        # TODO : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간
        path = []
        path = self.network.request_and_get_path()

        d_cache = self.network.uplink_latency(path) + self.network.downlink_latency(path)

        return d_cache

    def get_c_node(self,type,id):
        # TODO : Contents가 캐싱된 station이 커버하는 device의 수 구하기
        # * 해당 MicroBS 와 BS 가 커버하는 노드의 수는 구할 수 있는데
        # * Contents를 알아야함.
        c_node = 0
        tmpcnt = 0
    
        if type == "MicroBS":
            c_node = len(self.network.MicroBSNodeList[id])
        
        elif type == "BS":
            for i in self.network.BSNodeList[id]:
                tmpcnt = tmpcnt + len(self.network.MicroBSNodeList[i])
            c_node = tmpcnt

        elif type == "DataCenter" or type == "Core":
            c_node = cf.NB_NODES

        return c_node

    """
    #! H_arg 에 대한 수식 정의를 아직 내리지 못하여
    #! get_R_cache 와 get_H_arg 를 사용하는 수식은 연기한다. (2022/05/11)


    def set_reward(self):
    
    # Return the reward.
    # The reward is:
    
    #    Reward = a*(d_core - d_cache) - b*(R_cache/H_arg)

    #    a,b = 임의로 정해주자 실험적으로 구하자

    #    d_core  : 네트워크 코어에서 해당 컨텐츠를 전송 받을 경우에 예상되는 지연 시간.
    #    d_cache : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간

    #    ! 연기함 
    #    R_cache : 네트워크에 존재하는 동일한 캐시의 수
    #    H_arg   : 동일한 캐시 사이의 평균 홉 수 (캐시의 분산도를 나타냄)
    
    self.reward = 0


    self.reward = self.a*(self.d_core - self.d_cache) - self.b*(self.R_cache/self.H_arg)
    return self.reward

    def get_reward_parameter(self):

        # d_core  : 네트워크 코어에서 해당 컨텐츠를 전송 받을 경우에 예상되는 지연 시간.
        #           이해 못함

        # d_cache : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간
                   
        # R_cache : 네트워크에 존재하는 동일한 캐시의 수
        #           for 문으로 돌려야겠다

        # H_arg   : 동일한 캐시 사이의 평균 홉 수 (캐시의 분산도를 나타냄)
        #           준영쓰

        return d_core, d_cache, R_cache, H_arg

    # R_cache 구하기
    def get_R_cache(self, content:ct.Content):

        # 요청이 들어온 컨텐츠에 대해서 R_cache 구하기
        self.R_cache = 0

        # INFO : network.storage : [capacity , stored_size, [contents:contentStorage]]
        #        network.storage.storage : [{'title' : '개콘', 'size' : 123}, ... ,{'title' : '9시뉴스', 'size' : 123}]

        # TODO : 1. Data Center 에 있는 지 확인
        
        if content in self.network.dataCenter.storage.storage:

            self.R_cache = self.R_cache + 1

        # TODO : 2. Base Station 에 있는 지 확인
        # 2.1 Base Station List 가져옴
        for i in self.network.BSList:

            # 2.2 해당 Base Station의 stored 된 contents List를 가져옴
            storedContentsList:List = i.storage.storage

            if content in storedContentsList:
                self.R_cache = self.R_cache + 1


        # TODO : 3. Micro Base Station 에 있는 지 확인
        for i in self.network.microBSList:

            # 2.2 해당 Base Station의 stored 된 contents List를 가져옴
            storedContentsList:List = i.storage.storage

            if content in storedContentsList:
                self.R_cache = self.R_cache + 1

        return self.R_cache

    def get_H_arg():


    """
