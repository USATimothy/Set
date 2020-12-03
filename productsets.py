# -*- coding: utf-8 -*-
"""
Created on Tue Nov 5 16:37:09 2019

@author: Timothy Fleck


This is a mathematical representation of the Set card game.
https://en.wikipedia.org/wiki/Set_(card_game)

In this representation, each card is a tuple of length 4:
    (number, shape, color, shade)
Each tuple element takes on the value 0,1, or 2

For example, the one red solid diamond card could be coded (0,0,2,1) and
the two red shaded squiggles could be (1,0,1,2)

Mathematically, summing the tuples element by element, and then taking mod 3
for each element will result in the tuple (0,0,0,0) if and only if the cards
are a set.

Some of the code would work for different numbers of variants
(e.g. 5 different colors, shapes, numbers, and shading patterns) or
different numbers of properties (e.g. all cards same color and shading).

Some of the code would not still work, most notably the modulus operation.

"""
import itertools
from random import shuffle
from matplotlib import pyplot as plt
import numpy
import time
from operator import itemgetter
import pandas

#Hard coded for the typical game of Set.
properties=4 #shape, fill, number, color
variants=3 #3 shapes, 3 fills, 3 numbers, 3 colors
board_size=12 #12 cards at a time

trials=1000#number of simulated 12-card setups

#Create full deck (81 for Set game)
deck = list(itertools.product(range(variants),repeat=properties))


#Several different functions and subfunctions for calculating the number of sets
#on the board.

#check every 3-card triple, one by one for Y/N
def triplecheck(board,variants,func):
    sets=0
    r=range(len(board[0]))#r is a range object, length is # of properties
    
    #triples is an iterable
    triples=itertools.combinations(board,3)
    #triple is a 3-tuple of p-tuples, where p is the number of properties
    for triple in triples:
        sets+=func(triple,variants,r)#pass in func that returns whether it is a set
    return sets#return total number of sets on the board

#check whether a triple is a set, going property by property, and returning 0
    #immediately if one doesn't work
def stepcheck(triple,variants,p):
    for i in p:
        sm=sum([card[i] for card in triple])%variants
        if sm>0:
            return 0
    else:
        return 1

#check every triple, one by one for Y/N
    #Sum and mod in every category, then sum again
def comprehensioncheck(triple,variants,r):
    return sum([sum([card[i] for card in triple])%variants for i in r])==0

#check every double to generate missing card
#check for missing card
#Each set will be found 3 times   
def doublecheck(board,variants):
    sets=0
    r=range(len(board[0]))
    #doubles is an iterable
    doubles=itertools.combinations(board,2)
    for double in doubles:
        targetcard=thirdcard(double,variants,r)
        if targetcard in board:
            sets+=1
    return sets//3
    
#The missing third card of a set, given two cards
#uses modulo method, in reverse
def thirdcard(double,variants,r):
    return tuple([-sum([card[i] for card in double])%variants for i in r])

#make list of missing cards
    #cards may be repeated in the list
#at the end, scan board for missing cards
#Each set will be found 3 times   
def doubledelayedcheck(board,variants):
    sets=0
    targetcards=[]
    r=range(len(board[0]))
    doubles=itertools.combinations(board,2)
    for double in doubles:
        targetcards.append(thirdcard(double,variants,r))
    for targetcard in targetcards:
        if targetcard in board:
            sets+=1
    return sets//3

#check every double to see whether it's already in the list of found sets.
#if not, generate the missing card, then check for it
def doubleskipcheck(board,variants,func):
    sets=0
    foundsets=[]
    r=range(len(board[0]))
    
    #doubles in an iterable of tuples
    doubles=itertools.combinations(board,2)
    for double in doubles:
        if not func(double,foundsets):
            targetcard=thirdcard(double,variants,r)
            if targetcard in board:
                sets+=1
                fdset=set(double)
                fdset.add(targetcard)
                foundsets.append(fdset)
    return sets

#check whether both cards in a double are already in the found sets.
def skipdoubleintersect(double,foundsets):
    this2=set(double)
    for fs in foundsets:
        if len(this2.intersection(fs))>1:
            return True
    else:
        return False

#check whether both cards in a double are already in the found sets.    
def skipdoublein(double,foundsets):
    for fs in foundsets:
        if double[0] in fs and double[1] in fs:
            return True
    else:
        return False

#Sort the board
#Check each double to generate missing card, then check only later cards for
#the missing card
def doublesubsetcheck(board,variants):
    sets=0
    r=range(len(board[0]))
    board_size=len(board)
    board.sort()
    #All sets including the last card will be found before evaluating doubles
    #with the last card, so including it in the list of doubles is unnecessary.
    doubles=list(itertools.combinations(board[:-1],2))
    doubles.sort(key=itemgetter(1))
    #i,j,k set up the indices for what counts as "later" cards
    j=[]
    for i in range(1,board_size-1):
        j+=[i+1]*i
    #smaller number of doubles to check
    for k,double in zip(j,doubles):
        targetcard=thirdcard(double,variants,r)
        if targetcard in board[k:]:
            sets+=1
    return sets

#alternate version of doublesubsetcheck
#indexing and slicing of subset to check is slightly different
def doubleslimcheck(board,variants):
    sets=0
    r=range(len(board[0]))
    board_size=len(board)
    board.sort()
    doubles=list(itertools.combinations(board[:-1],2))
    doubles.sort(key=itemgetter(1))
    j=[]
    for i in range(1,board_size-1):
        j+=[0]*(i-1)
        j.append(1)
    j[-1]=0
    subboard=board[2:]
    for k,double in zip(j,doubles):
        targetcard=thirdcard(double,variants,r)
        if targetcard in subboard:
            sets+=1
        if k>0:
            del subboard[0]
    return sets
    
#Time different methods
methods=((triplecheck,comprehensioncheck),(triplecheck,stepcheck),
         doublecheck,(doubleskipcheck,skipdoubleintersect),
         (doubleskipcheck,skipdoublein),doubledelayedcheck,doublesubsetcheck,
         doubleslimcheck)

board=[]
def time_methods(methods,variants,trials,deck,board_size):
    methodname=[]
    meansets=[]
    uspertrial=[]
    for m in methods:
        if type(m) is tuple:
            fun=m[0]
            fun_arg=[variants,m[1]]
            fname = m[0].__name__ + ' with ' + m[1].__name__
        else:
            fun=m
            fun_arg=[variants]
            fname=fun.__name__
        num_sets_list=[0]*trials
        tic=time.perf_counter()
        for t in range(trials):
            shuffle(deck)
            board=deck[:board_size]
            num_sets_list[t]=fun(board,*fun_arg)
        toc=time.perf_counter()
        methodname.append(fname)
        meansets.append(numpy.mean(num_sets_list))
        uspertrial.append(int(10**6*(toc-tic)/trials))
        #print(fname,str(trials),numpy.mean(num_sets_list),f'{(toc-tic):.4f}')
    table=pandas.DataFrame({'Method':methodname,'Avg. no. of sets':meansets,
                                'microseconds per trial':uspertrial})
    return table

#Record the number of sets in the initial card layout for each simulation
def plot_starting_sets(variants,trials,deck,board_size,method,subfunc=None):
    num_sets_list=[0]*trials
    for t in range(trials):
        shuffle(deck)
        board=deck[:board_size]
        if subfunc:
            num_sets_list[t]=method(board,variants,subfunc)
        else:     
            num_sets_list[t]=method(board,variants)
    maxsets=max(num_sets_list)
    ls=numpy.linspace(-0.5,maxsets+0.5,maxsets+2)
    plt.hist(num_sets_list,bins=ls)
    plt.ylabel('Frequency')
    plt.xlabel('Number of sets on the board')
    plt.title('Frequency of games by number of sets available at game start' )
    plt.show()
    return