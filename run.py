import config as cf
import logging
import node as nd
import random
import scenario as sc
import math
import random
import content as ct
import numpy as np
import network as nt

def run_scenarios():
    network = nt.Network()
    #print(network.BSList)
    #print(network.dataCenter)
    #print(network.microBSList)

    network.simulate()
    
    
    for i in network.microBSList:
      print(i.storage.__dict__)
      """
      for j in range(len(i.storage.storage)):
        print("id: {}  storage:{}".format(i.id, i.storage.__dict__))
        print("storage.title : {}     storage.size : {}".format(i.storage.storage[j].title, i.storage.storage[j].size))
        """
      
    print(network.dataCenter.storage.__dict__)

    """
    cnt = 0
    for i in range(100):
      print("{} : {}".format(i, network.MicroBSNodeList[i]))
      for j in range(len(network.MicroBSNodeList[i])):
        if network.MicroBSNodeList[i][j] != -1:
          cnt = cnt + 1
    print(cnt)

    cnt = 0
    for i in range(9):
      print("{} : {}".format(i, network.BSNodeList[i]))

    for j in range(9):
      print("{}번 BS에 연결되어있는 MicroBaseStation ID : {}".format(j, network.BSNodeList[j]))
      tmpcnt = 0
      for i in network.BSNodeList[j]:
        print("{} : {} : {}".format(i, network.MicroBSNodeList[i], len(network.MicroBSNodeList[i])))
        tmpcnt = tmpcnt + len(network.MicroBSNodeList[i])
      print(tmpcnt)
      cnt = cnt + tmpcnt
    
    print(cnt)
    """

if __name__ == '__main__':
  #run_parameter_sweep()
  run_scenarios() 