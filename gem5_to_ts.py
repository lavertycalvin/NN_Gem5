#!/bin/python3

# takes in raw output from gem5 and outputs a numpy array to file 
# for next data transformation


import sys
import numpy as np

HIT_KEYWORD = "access"
MISS_KEYWORD = "moving"
IGNORE_KEYWORD = "miss" #doesn't contain info for where the data is placed in cache

#cache block location for hit
LOC_H_CACHE_BLOCK = 5

#cache block location for miss
LOC_M_CACHE_BLOCK = 4

#valid for both hit and miss
#location in line split
LOC_WAY = -1
LOC_SET = -3
LOC_TAG = -5
LOC_TICK = 0

#global numpy array for fun
#values in each section of the array: tick, hit/miss, address, tag, set, way
g_np_ts_data = np.empty((6,))
g_ts_data = []

### Extracts info for hit or miss and adds to global np array
def format_for_np_array(f_line):
    global g_ts_data
    line_split = f_line.split()
    if(IGNORE_KEYWORD in line_split):
        return

    # NOTE: when converting to int with str prefix of '0x'
    #       a second parameter of 0 allows for hex str->int

    #set is reserved word in python
    c_set = np.int64(line_split[LOC_SET], 0)
    tick  = np.int64(line_split[LOC_TICK][:-1]) #get rid of ':'
    tag   = np.int64('0x0', 0)
    way   = np.int64(line_split[LOC_WAY], 0)

    if(MISS_KEYWORD in line_split):
        #was a miss
        cache_block_start = np.int64(line_split[LOC_M_CACHE_BLOCK], 0)
        access_type = np.int64(0)
    elif(HIT_KEYWORD in line_split):
        #was a touch/hit
        #format for this is the entire cache line. e.g.: [5ea0:5ea7]
        cache_block = line_split[LOC_H_CACHE_BLOCK].split(':')
        cache_block_start = np.int64("0x" + cache_block[0][1:], 0) #get rid of '[' and add hex identifier
        access_type = np.int64(1)

    #add to the numpy array
    new_addition = [tick, access_type, cache_block_start, tag, c_set, way]
    if((len(g_ts_data) == 0) or (new_addition != g_ts_data[-1])):
        g_ts_data.append(new_addition)

    if(len(g_ts_data) % 1000000 == 0):

        data_type=np.dtype('int64', [('tick', 'int64'), ('h_m', 'int8'), ('addr', 'int64'), ('tag','int64'), ('set', 'int32'), ('way', 'int32')])
        g_np_ts_data = np.array(g_ts_data, dtype=data_type)
        print g_np_ts_data.shape
        #print " [ tick    h/m   addr  tag  set  way]"

        #have to get rid of duplicates 
        print g_np_ts_data
        np.save(output_file, g_np_ts_data)


    


### Parses each line in the input file and searches for Hit or Miss
### Omits any unimportant lines
### Passes to format_for_np_array
def to_time_series(input_filename):
    global g_ts_data
    data_file = open(input_filename, "r")
    count = 0
    for line in data_file:
        # moving = miss / access =  hit
        #if(count < 100000):
        #    count = count + 1
        #    continue
        if any(word in line for word in [HIT_KEYWORD, MISS_KEYWORD]):
            format_for_np_array(line)
 
        #if(len(g_ts_data) == 1000000):
            #print g_ts_data[-1]
            #break

    data_file.close()

if __name__ == "__main__":
    global output_file
    if(len(sys.argv) < 2):
        print "Usage: gem5_to_ts.py [input_file]"
        sys.exit(1)

    output_file = sys.argv[1] + ".ts"
    to_time_series(sys.argv[1])
    print g_ts_data[:2]
    #g_ts_data = map(tuple, g_ts_data)
    data_type=np.dtype('int64', [('tick', 'int64'), ('h_m', 'int8'), ('addr', 'int64'), ('tag','int64'), ('set', 'int32'), ('way', 'int32')])
    g_np_ts_data = np.array(g_ts_data, dtype=data_type)
    print g_np_ts_data.shape
    #print " [ tick    h/m   addr  tag  set  way]"

    #have to get rid of duplicates 
    print g_np_ts_data


    np.save(output_file, g_np_ts_data)
