/**
 * Copyright (c) 2018 Inria
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Authors: Daniel Carvalho
 */

#include "mem/cache/replacement_policies/nn.hh"
#include "debug/Cache.hh"

#include <cassert>
#include <memory>
#include "math.h"

#include "params/NN.hh"


#define INPUT_SIZE 2
#define LAYER_1_SIZE 10
#define OUTPUT_SIZE 2

//(35759, 2)
//loss: 87.2106 - acc: 0.7852 - val_loss: 60.8464 - val_acc: 0.9209
//Train on 28607 samples, validate on 7152 samples

float l1_weights[(INPUT_SIZE + 1) * LAYER_1_SIZE] = 
    {   -0.49845946,  0.22325927, -0.52610946, -0.60933924,  0.6860388 ,
         0.40856093,  0.15512687, -0.31920674, -0.31920826, -0.60659343,
         0.24248731,  0.18161821, -0.23300144, -0.5184017 , -0.48359376,
        -0.02296668,  0.30648226,  0.4508106 ,  0.6115821 , -0.6988966 };
float l1_biases[LAYER_1_SIZE] = 
    {   -3.5849648,  4.0219626, -3.9680274, -3.91506  ,  2.8699818,
        -3.1494424,  4.0392165,  4.003411 , -4.2274265, -3.9415686 };

float output_weights[(LAYER_1_SIZE + 1) * OUTPUT_SIZE] = 
    {    -5.115885  ,  -0.68475986,
         4.3482156 ,   5.1769676 ,
        -4.3589253 ,  -4.3728127 ,
        -4.275265  ,  -3.7644014 ,
        -6.507751  ,   5.0700903 ,
       -12.787315  ,  -7.6008844 ,
         5.016292  ,   4.693456  ,
         2.9304671 ,  -2.6469643 ,
        -1.3608078 ,  -3.96286   ,
        -4.136699  ,  -4.2638526 };
float output_biases[OUTPUT_SIZE] = 
    {   5.1044316, 5.2467995};
NN::NN(const Params *p)
    : BaseReplacementPolicy(p)
{
}

void
NN::invalidate(const std::shared_ptr<ReplacementData>& replacement_data)
const
{
    // Reset last touch timestamp
    std::static_pointer_cast<NNReplData>(
        replacement_data)->lastTouchTick = Tick(0);
}

void
NN::touch(const std::shared_ptr<ReplacementData>& replacement_data) const
{
    // Update last touch timestamp
    std::static_pointer_cast<NNReplData>(
        replacement_data)->lastTouchTick = curTick();
}

void
NN::reset(const std::shared_ptr<ReplacementData>& replacement_data) const
{
    // Set last touch timestamp
    std::static_pointer_cast<NNReplData>(
        replacement_data)->lastTouchTick = curTick();
}

//TODO
float
activation_func(float something){
    return tanh(something);
}

ReplaceableEntry*
NN::getVictim(const ReplacementCandidates& candidates) const
{
    // There must be at least one replacement candidate
    assert(candidates.size() > 0);
    ReplaceableEntry* candidate;
    int i = 0;
    int j;

    float l1_output[LAYER_1_SIZE];
    float final_output[OUTPUT_SIZE];
    for(i = 0; i < LAYER_1_SIZE; i++){
        l1_output[i] = l1_biases[i];
        for(j = 0; j < INPUT_SIZE; j++){
            candidate = candidates[j];
            l1_output[i] += l1_weights[(j * LAYER_1_SIZE) + i] 
                   * log(curTick() - std::static_pointer_cast<NNReplData>(
                    candidate->replacementData)->lastTouchTick);        
        }
        l1_output[i] = activation_func(l1_output[i]);
    }

    float max_value = 0;
    int max_index = 0;
    for(i = 0; i < OUTPUT_SIZE; i++){
        final_output[i] = output_biases[i];
        for(j = 0; j < LAYER_1_SIZE + 1; j++){
            final_output[i] += output_weights[(j * OUTPUT_SIZE) + i] * l1_output[i]; 
        }
        if(final_output[i] > max_value){
            max_index =  i;
        }
    }


    // Visit all candidates to find victim
    DPRINTF(Cache, "Replacment index is %d\n", max_index);
    ReplaceableEntry* victim = candidates[max_index];

    return victim;
}

std::shared_ptr<ReplacementData>
NN::instantiateEntry()
{
    return std::shared_ptr<ReplacementData>(new NNReplData());
}

NN*
NNParams::create()
{
    return new NN(this);
}
