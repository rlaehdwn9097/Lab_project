from re import M
import config as cf
import logging
import node as nd
import random
import scenario as sc
import math
import random
import content as ct
import numpy as np

class Network(list):
    nodeList=[]
    microBSList=[]
    BSList=[]
    dataCenter = nd.dataCenter(0,0)

    def __init__(self):

        self.nodeList=nd.generateNode()
        self.microBSList= nd.generateMicroBS()
        self.BSList=nd.generateBS()

        # 내가 만든 변수
        self.CoreNodeList = []
        self.DataCenterNodeList = []
        self.BSNodeList = []
        self.MicroBSNodeList = []

        # nodeList Init에서 바로하자
        self.get_c_nodeList()


        # Contents에 대한 접근이 필요함
        self.requested_content:ct.Content

    def simulate(self):
        for round_nb in range(0, cf.MAX_ROUNDS):
            self.round = round_nb
            print("The current round number is",self.round)
            self.run_round()

    def run_round(self):
        path = self.request_and_get_path()
        print("path is :", path)

        if len(path) == 5:
            print("need to cache the data somewhere")
            #print("path is :", path)
            #caching_phase()
        else:
            print("cache hit successfully")


        print("uplink latency is:", round(self.uplink_latency(path)[0]*1000,6))
        print("downlink latency is:", round(self.downlink_latency(path)[0]*1000,6))

    def search_next_path(self,x,y,type):
        #type node:0, microbs:1 bs:2
        if type is 0:
            minRange = cf.AREA_LENGTH
            closestNode:nd.microBS
            closestID:int
            for i in self.microBSList:
                range=  math.sqrt(math.pow((x-i.pos_x),2) + math.pow((y-i.pos_y),2))
                if minRange>range:
                    closestNode=i
                    minRange=range
                    closestID=closestNode.id

        if type is 1:
            minRange = cf.AREA_LENGTH
            closestNode:nd.BS
            closestID:int
            for i in self.BSList:
                range =  math.sqrt(math.pow((x-i.pos_x), 2) + math.pow((y-i.pos_y),2))
                if minRange>range:
                    closestNode=i
                    minRange=range
                    closestID=closestNode.id
                    
        return closestID 
        
    def request_and_get_path(self):
        path=[]
        #시작 
        id = random.choice(range(0,cf.NB_NODES))
        time_delay = 0 
        #요청 content 선택
        requested_content = self.request()
        path.append(id)#노드
        
        # 노드 x,y 좌표를 통해 [micro - BS - Data center - Core Internet]
        micro_hop = self.search_next_path(self.nodeList[id].pos_x,self.nodeList[id].pos_y,0)
        path.append(micro_hop)#microBS

        if self.microBSList[micro_hop].storage.isstored(requested_content)==0:
            bs_hop = self.search_next_path(self.microBSList[micro_hop].pos_x,self.microBSList[micro_hop].pos_y, 1)
            path.append(bs_hop)#BS
            if self.BSList[bs_hop].storage.isstored(requested_content)==0:
                path.append(0)#center
                if self.dataCenter.storage.isstored(requested_content)==0:
                    path.append(0)
        return path

    def DL_transmission_time(self,index_i,index_j,type):
        #type 1 : node <-> micro
        if type ==1:
            range = math.sqrt(math.pow((self.nodeList[index_i].pos_x-self.microBSList[index_i].pos_x), 2) + math.pow((self.nodeList[index_i].pos_y-self.microBSList[index_i].pos_y),2))
            propagation_delay = range/ cf.LIGHT_SPEAD
            transmission_delay = cf.PACKET_SIZE/cf.DLthroughput
            traffic_intensity = 1-abs(np.random.normal(0, 0.1, 1))
            queuing_delay = traffic_intensity*(1-traffic_intensity)*cf.PACKET_SIZE/cf.DLthroughput
            return propagation_delay+transmission_delay+queuing_delay
        #type 2 : microBS <-> B
        if type ==2:
            range = math.sqrt(math.pow((self.microBSList[index_i].pos_x-self.BSList[index_i].pos_x), 2) + math.pow((self.microBSList[index_i].pos_y-self.BSList[index_i].pos_y),2))
            propagation_delay = range/ cf.LIGHT_SPEAD
            transmission_delay = cf.PACKET_SIZE/cf.DLthroughput
            queuing_delay = traffic_intensity*(1-traffic_intensity)*cf.PACKET_SIZE/cf.DLthroughput
            return propagation_delay+transmission_delay+queuing_delay
        #type 3 : BS <-> datacenter
        if type ==3:
            range = math.sqrt(math.pow((self.BSList[index_i].pos_x-self.dataCenter.pos_x), 2) + math.pow((self.BSList[index_i].pos_y-self.dataCenter.pos_y),2))
            propagation_delay = range/ cf.LIGHT_SPEAD
            transmission_delay = cf.PACKET_SIZE/cf.DLthroughput
            queuing_delay = traffic_intensity*(1-traffic_intensity)*cf.PACKET_SIZE/cf.DLthroughput
            return propagation_delay+transmission_delay+queuing_delay
        #type 4: datacenter <-> internet
        if type ==4:
            return cf.LATENCY_INTERNET

    def UL_transmission_time(self,index_i,index_j,type):
        #type 1 : node <-> micro
        traffic_intensity = 1-abs(np.random.normal(0, 0.3, 1))
        #print("traffic_intensity:",traffic_intensity)
        if type ==0:

            range = math.sqrt(math.pow((self.nodeList[index_i].pos_x - self.microBSList[index_j].pos_x), 2) + math.pow((self.nodeList[index_i].pos_y-self.microBSList[index_j].pos_y),2))
            propagation_delay = range/ cf.LIGHT_SPEAD
            transmission_delay = cf.PACKET_SIZE/cf.ULthroughput
  
            queuing_delay = traffic_intensity*(1-traffic_intensity)*cf.PACKET_SIZE/cf.ULthroughput
            print("큐잉딜레이:",transmission_delay*1000)
            return propagation_delay+transmission_delay+queuing_delay
        #type 2 : microBS <-> B
        if type ==1:
            range = math.sqrt(math.pow((self.microBSList[index_i].pos_x-self.BSList[index_j].pos_x), 2) + math.pow((self.microBSList[index_i].pos_y-self.BSList[index_j].pos_y),2))
            propagation_delay = range/ cf.LIGHT_SPEAD
            transmission_delay = cf.PACKET_SIZE/cf.ULthroughput
            queuing_delay = traffic_intensity*(1-traffic_intensity)*cf.PACKET_SIZE/cf.ULthroughput
            return propagation_delay+transmission_delay+queuing_delay

        #type 3 : BS <-> datacenter
        if type ==2:
            range = math.sqrt(math.pow((self.BSList[index_i].pos_x-self.dataCenter.pos_x), 2) + math.pow((self.BSList[index_i].pos_y-self.dataCenter.pos_y),2))
            propagation_delay = range/ cf.LIGHT_SPEAD
            transmission_delay = cf.PACKET_SIZE/cf.ULthroughput
            queuing_delay = traffic_intensity*(1-traffic_intensity)*cf.PACKET_SIZE/cf.ULthroughput
            return propagation_delay+transmission_delay+queuing_delay

        #type 4: datacenter <-> internet
        if type ==3:
            return cf.LATENCY_INTERNET
    
    def uplink_latency(self,path):
        latency = 0
        for i in range(0,len(path)-1):
            latency = latency + self.UL_transmission_time(path[i],path[i+1],i)
        return latency

    def downlink_latency(self,path):
        latency = 0
        for i in range(0,len(path)-1):
            latency = latency + self.UL_transmission_time(path[i],path[i+1],i)
        return latency


# 내가 만든 함수들 
# 목록 : get_simple_path, get_c_nodeList

    def request(self):
        requested_content = random.choice(sc.testScenario)
        self.requested_content = requested_content
        print(self.requested_content.__dict__)
        return requested_content

    def get_simple_path(self, nodeId):

        path=[]
        #시작 
        id = nodeId
        path.append(id)#노드
        # 노드 x,y 좌표를 통해 [node - micro - BS - Data center - Core Internet]
        micro_hop = self.search_next_path(self.nodeList[id].pos_x,self.nodeList[id].pos_y,0)
        path.append(micro_hop)#microBS
        bs_hop = self.search_next_path(self.microBSList[micro_hop].pos_x,self.microBSList[micro_hop].pos_y, 1)
        path.append(bs_hop)# Base Station
        path.append(0)# Data Center
        path.append(0)# Core Internet
        return path


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
            tmpPath = self.get_simple_path(id)
            print(tmpPath)
            nodePathList.append(tmpPath)
            tmpPath = []
        
        #print(nodePathList)

        
        for MicroBS_Id in range(cf.NUM_microBS[0]*cf.NUM_microBS[1]):
            tmpMicroNodeList = []
            for i in range(cf.NB_NODES):
                # nodePathList = [[0, 64, 7, 0, 0], ... , [300, 5, 2, 0, 0]]
                # MicroNodePathList 에는 MicroBS 의 id 가 index 
                # 해당 index 에 node id 들이 append 됌
                
                if MicroBS_Id == nodePathList[i][1]:
                    #print("node의 id : " + str(nodePathList[i][0]) + " 추가")
                    tmpMicroNodeList.append(nodePathList[i][0])

            if len(tmpMicroNodeList) == 0:
                tmpMicroNodeList.append(-1)
            #print("MicroBSID 에 포함되는 NodeList : " + str(tmpMicroNodeList))
            self.MicroBSNodeList.append(tmpMicroNodeList)

        for BS_Id in range(cf.NUM_BS[0]*cf.NUM_BS[1]):
            tmpBSNodeList = []
            for i in range(cf.NB_NODES):
                # BSNodePathList 에는 BS 의 id 가 index 
                # 해당 index 에 MicroBS id 들이 append 됌
                if BS_Id == nodePathList[i][2]:

                    if nodePathList[i][1] not in tmpBSNodeList:
                        tmpBSNodeList.append(nodePathList[i][1])

            if len(tmpMicroNodeList) == 0:
                tmpBSNodeList.append(-1)
            #print(tmpBSNodeList)
            self.BSNodeList.append(tmpBSNodeList)
