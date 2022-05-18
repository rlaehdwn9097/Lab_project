from distutils import core
from queue import Empty
from re import X
from typing import List
import network as nt
import config as cf
import content as ct

class Agent():

    def __init__(self):

        self.network = nt.Network
        # BackBone 인 Data Center 에는 다 있다고 가정?
        # [path 중 Mirco Base Station에 저장, path 중 Base Station에 저장]
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

        # reward parameter
        self.a = 0.5
        self.b = 0.5
        self.d_core = 0
        self.d_cache = 0
        self.R_cache = 0
        self.H_arg = 0
        self.c_node = 0


        # Station에 해당하는 NodeList
        self.CoreNodeList = []
        self.DataCenterNodeList = []
        self.BSNodeList = []
        self.MicroBSNodeList = []


    def set_reward(self):
        """
        Return the reward.
        The reward is:
        
            Reward = a*(d_core - d_cache) - b*(R_cache/H_arg)

            a,b = 임의로 정해주자 실험적으로 구하자
            d_core  : 네트워크 코어에서 해당 컨텐츠를 전송 받을 경우에 예상되는 지연 시간.
            d_cache : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간
            c_node : 캐싱된 contents가 포괄하는 device의 갯수
        """
        self.reward = 0


        self.reward = self.a*(self.d_core - self.d_cache) + self.b*self.coverage_node
        return self.reward

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

    def get_d_core(self):
        # 코어 인터넷까지 가서 가져오는 경우를 봐야함
        # path 뒤에 추가해서 구하자

        self.path = self.network.request_and_get_path()

        # [4,68] 일 경우 ---> [4,68, search_next_path(microBS.x, microBS.y):BS, search_next_path(BS.x, BS.y):Datacenter, search_next_path(Datacenter.x, Datacenter.y):Core Internet]
        # path 다 채워질 떄까지 돌리자
        while len(self.path) != 5:

            # Micro에 캐싱되어 있는 경우, BS 추가
            if len(self.path) == 2:
                id = self.path[-1]
                closestID = self.network.search_next_path(self.network.microBSList[id].pos_x,self.network.microBSList[id].pos_y,1)
                self.path.append(closestID)

            # BS에 캐싱 되어 있는 경우, Data Center 추가
            elif len(self.path) ==  3:
                self.path.append(0)

            # 데이터 센터에 캐싱이 되어 있는 경우, Core Internet 추가
            elif len(self.path) == 4:
                self.path.append(0)

        d_core = self.network.uplink_latency(self.path) + self.network.downlink_latency(self.path)

        return d_core

    def get_d_cache(self):
        # TODO : 가장 가까운 레벨의 캐시 서버에서 해당 컨텐츠를 받아올 때 걸리는 실제 소요 시간

        self.path = self.network.request_and_get_path()

        d_cache = self.network.uplink_latency(self.path) + self.network.downlink_latency(self.path)

        return d_cache

    def get_c_node(self, type, id):
        # TODO : 캐싱된 station이 커버하는 device의 수 구하기

        if type == "MicroBS":

            c_node = (self.MicroBSNodeList[id])

        

        return c_node

    # network.py 에 옮겨야 할수도 있음.
    # 네트워크 연결 구조 만들기
    def get_c_nodeList(self):

        # TODO : Core Internet --> 모든 노드
        # TODO : Data Center --> 모든 노드
        # 각각 따로 for 문이 돌아갈 필요 X
        for id in range(cf.NB_NODES):
            self.CoreNodeList.append(id)
            self.DataCenterNodeList.append(id)


        # TODO : 먼저 모든 노드들의 path를 구한뒤 배열로 각각 따로 저장하자
        # TODO : Micro Base Station --> Node들을 저장
        # TODO : Base Station --> 연결 되어있는 Micro Base Station 저장

        nodePathList = []
        tmpPath = []
        for id in range(cf.NB_NODES):
            tmpPath = self.network.get_simple_path(id)
            nodePathList.append(tmpPath)
            tmpPath = []


        for i in range(cf.NB_NODES):

            tmpMicroNodeList = []
            tmpBSNodeList = []

            for MicroBS_Id in range(cf.NUM_microBS[0]*cf.NUM_microBS[1]):
                # nodePathList = [[0, 64, 7, 0, 0], ... , [300, 5, 2, 0, 0]]
                # MicroNodePathList 에는 MicroBS 의 id 가 index 
                # 해당 index 에 node id 들이 append 됌
                if nodePathList[i][1] == MicroBS_Id:
                    tmpMicroNodeList.append(nodePathList[i][0])

            for BS_Id in range(cf.NUM_BS[0]*cf.NUM_BS[1]):
                # BSNodePathList 에는 BS 의 id 가 index 
                # 해당 index 에 MicroBS id 들이 append 됌
                if nodePathList[i][2] == BS_Id:
                    tmpBSNodeList.append(nodePathList[i][1])
            
            self.MicroBSNodeList.append(tmpMicroNodeList)
            self.BSNodeList.append(tmpBSNodeList)


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
