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

total_day = 7*cf.TOTAL_PRIOD
days = random.choices(range(total_day), k=cf.MAX_ROUNDS)
days.sort()
def run_scenarios():
    network = nt.Network()
    network.simulate()


if __name__ == '__main__':
  #run_parameter_sweep()
  run_scenarios() 
