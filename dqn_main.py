# DQN main
# coded by St.Watermelon

from dqn_learn import DQNagent

def main():

    max_episode_num = 2000
    agent = DQNagent()
    agent.train(max_episode_num)
    agent.plot_result()
    agent.plot_cache_hit_result()
    
if __name__=="__main__":
    main()
    