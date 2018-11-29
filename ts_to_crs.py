

# moves a numpy array generated from time series data
# to a cache replacement state

import sys
import numpy as np


g_replacement_num = 0
g_last_repl_loc = 0
g_num_sets = 0
g_crs = []
g_cache_state = []
g_num_way = 0

def to_crs(np_file):
    global g_last_repl_loc
    global g_cache_state
    global g_num_ways
    global g_replacement_num

    #load in the time series data
    ts_data = np.load(np_file)

    #get the number of sets
    g_num_sets = len(np.unique(ts_data[:,-2]))
    total_misses = np.count_nonzero(ts_data[:,1] == 0)
    total_hits = np.count_nonzero(ts_data[:,1] == 1)
    g_num_ways = len(np.unique(ts_data[:,-1]))
    print "Number of sets used in data set: " + str(g_num_sets)
    print "Number of misses in data set:" + str(total_misses) 

    #set up our cache array
    # each way needs last touched + next touched (num_ways * 2)
    # each set needs info for each way (g_num_sets *)
    # each replacement needs to know replacement number and set number AND current tick (+3)
    g_crs = np.zeros((total_misses , (g_num_sets * ((2 * g_num_ways) + 1)) + 3), dtype=np.int64)
    g_cache_state = np.zeros((g_num_sets, (2 * g_num_ways) + 1), dtype=np.int64)

    

    # initialize each entry
    # setup: repl_num, cache set replaced, last touched way 0, next touched way 0, last touched way 1, last touched way 1, ...  
    # each "cache_set" contains
    max_int = np.iinfo(np.int64).max
    for cache_set,cache_addr in zip(g_cache_state,np.unique(ts_data[:,-2])):
        #init (won't be on order) 
        cache_set[0] = int(cache_addr)

        #set next (and last) touched to inf for every way
        for i in range(1,g_num_ways + 1):
            cache_set[i*2] = max_int
            cache_set[i*2 - 1] = 0



    #process all misses
    while True:
        miss = np.argmax(0 == ts_data[g_last_repl_loc + 1:,1])

        #if one isnt found, will return 0 and no more misses
        start_update_index = g_last_repl_loc
        end_update_index = g_last_repl_loc + miss
        

        print "Updating cache between ticks: "  + str(ts_data[start_update_index][0]) \
                                     + " and "  + str(ts_data[end_update_index + 1][0])


        for index in range(start_update_index, end_update_index + 1):
            #get the set that is either hit or missed
            last_touched_set = ts_data[index][-2]
            last_touched_tick = ts_data[index][0]
            last_touched_way  = ts_data[index][-1]

            #now get the tick its next touched (will be set to negative if never touched again)
            #need to make sure that both way and set match
            next_touched_set_index = 1
            next_touched_way_index = 0
            match_set_and_way_index = index + 1
            try:
                while(next_touched_set_index != next_touched_way_index):
                    next_touched_set_index = np.argmax(last_touched_set == ts_data[match_set_and_way_index:, -2])
                    next_touched_way_index = np.argmax(last_touched_way == ts_data[match_set_and_way_index:, -1])

                    if(next_touched_set_index < 0):
                        #set never touched again
                        next_touch_tick = np.iinfo(np.int64).max
                        break;

                    #increment to search from smaller of next touched set or index
                    match_set_and_way_index += min(next_touched_set_index, next_touched_way_index) + 1

                next_touch_tick = 0
                if(next_touched_index == 0):
                    if(ts_data[index + next_touched_index + 1,-2] != last_touched_set):
                        #print str(ts_data[index + next_touched_index + 1, -2]) + " =?= " + str(last_touched_set)
                        next_touch_tick = np.iinfo(np.int64).max
                    else:
                        next_touch_tick = ts_data[index + next_touched_index + 1,0]
                else:
                    next_touch_tick = ts_data[index + next_touched_index + 1,0]

            # will fall through when the rest of the data is empty
            except ValueError:
                next_touch_tick = np.iinfo(np.int64).max

            if(next_touch_tick <= last_touched_tick):

                print "ERROR -- Last touch: " + str(last_touched_tick) + " Next: " + str(next_touch_tick)
                print g_cache_state
                sys.exit(1)

            #update the appropriate way with when last touched
            print "Set: " + str(last_touched_set) + " Way: " + str(last_touched_way) + " Last: " + str(last_touched_tick) \
                                             + " Next: " + str(next_touch_tick)

            #get set in cache state to update
            update_cs_index = np.argmax(last_touched_set == g_cache_state[:,0])
            g_cache_state[update_cs_index, (last_touched_way * 2) + 1] = last_touched_tick
            g_cache_state[update_cs_index, (last_touched_way * 2) + 2] = next_touch_tick

            print g_cache_state[update_cs_index,]

        #once all updates to the cache state are made,
        #add the current cache state to g_crs for each replacement
        #print g_crs[g_replacement_num].shape
        g_crs[g_replacement_num,3:] = g_cache_state.flatten()
        g_crs[g_replacement_num,2] = ts_data[end_update_index,0]
        g_crs[g_replacement_num,0] = g_replacement_num
        g_crs[g_replacement_num,1] = last_touched_set
        #print g_crs[g_replacement_num]
        g_replacement_num = g_replacement_num + 1
        if(g_replacement_num == total_misses):
            break


        #update where to look for misses
        g_last_repl_loc = end_update_index + 1

    print "Finished processing cache replacements!"
    #get rid of '.npy'
    output_filename = input_filename.split('.')[:-2]
    output_filename = ''.join(output_filename)
    output_filename = output_filename + '.crs'

    np.save(output_filename, g_crs)

if __name__ == "__main__":
    if(len(sys.argv) < 2):
        print "Usage: ts_to_crs.py [np_array_file.npy]"

    input_filename = sys.argv[1]
    to_crs(input_filename)
