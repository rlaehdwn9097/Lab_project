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
    for i in network.microBSList:

      for j in range(len(i.storage.storage)):
        print("id: {}  storage:{}".format(i.id, i.storage.__dict__))
        print("storage.title : {}     storage.size : {}".format(i.storage.storage[j].title, i.storage.storage[j].size))
        

    network.simulate()


if __name__ == '__main__':
  #run_parameter_sweep()
  run_scenarios() 