#/usr/bin/python


import sys
import numpy as np

def find_scores(input_fn, num_ways):
    crs_data = np.load(input_fn)
    #print crs_data

    #get the max in each row
    #max_ticks = np.amax(crs_data, axis=1)
    #print max_ticks

    #get corresponding set that was replaced
    all_replaced_sets = crs_data[:,1]
    #print all_replaced_set


    sample = [0, 0, 34, 45, 32, 22]
    #crs_data = sample
    #all_replaced_sets = [0]
    all_last_touched = np.array((all_replaced_sets.shape[0],num_ways))
    all_next_touched = np.array((all_replaced_sets.shape[0],num_ways))
    for i, repl_set in enumerate(all_replaced_sets):
        last_touched = np.array((1,num_ways))
        next_touched = np.array((1,num_ways))
        beg_assoc_ways = (3 + (((num_ways * 2) + 1)* repl_set))
        end_assoc_ways = beg_assoc_ways + (num_ways * 2) + 1
        touched_ticks = crs_data[i,beg_assoc_ways + 1:end_assoc_ways]
        #print touched_ticks
        #sys.exit(1)
        for j in range(0,end_assoc_ways - beg_assoc_ways - 1, 2):
            last_touched[j/2] = touched_ticks[j]
            next_touched[j/2] = touched_ticks[j+ 1]

        curr_tick = crs_data[i, 2]
        print "Current tick is: " + str(curr_tick)
        print "Last touched: " + str(last_touched)
        #all_last_touched[i,] = last_touched
        print "Next touched: " + str(next_touched)
        #all_next_touched[i,] = next_touched
        
        
        #find the current tick based on the highest value of last touched
        #for every sey
        way_scores = np.array((1,num_ways))
        for i in range(len(last_touched)):
            way_scores[i] = next_touched[i] - curr_tick
            
        print way_scores



        


if __name__ == "__main__":
    if(len(sys.argv) != 3):
        print "Usage: crs_to_score.py <crs_data.npy> <num_ways>"
        sys.exit(1)

    input_filename = sys.argv[1]
    num_ways = int(sys.argv[2])
    find_scores(input_filename, num_ways)
