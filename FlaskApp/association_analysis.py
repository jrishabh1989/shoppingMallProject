'''
Created on Mar 21, 2016

@author: Rishabh
'''

import math
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
import os
from os import path

def load_dataset(filename):
    #"Load the sample dataset."    
	print filename
	#catFile="C:/Users/Rishabh/Desktop/capstone project/dataStuff/latlongdata/jsonFiles/allStores/"+filename+'.txt'
	catFile="data/jsonFiles/allStores/"+filename+'.txt'
	list_of_malls_and_stores=[]
	d = {}
	with open(catFile) as f:
		counter=0
		key_orig=-1
		mylist = f.read().splitlines()
		for line in mylist:
			#print line
			(key, val) = line.split(":",1)
			#print key,':',val
			##if(key==key_orig):
			listOfStores=[x.lower() for x in (val.split(","))]
			list_of_malls_and_stores.insert(counter,listOfStores)
			counter=counter+1
			#print list_of_malls_and_stores[0]
	
	return list_of_malls_and_stores


def createC1(dataset):
    "Create a list of candidate item sets of size one."
    c1 = []
    for transaction in dataset:
        for item in transaction:
            if not [item] in c1:
                c1.append([item])
    c1.sort()
    #frozenset because it will be a ket of a dictionary.
    return map(frozenset, c1)


def scanD(dataset, candidates, min_support):
    "Returns all candidates that meets a minimum support level"
    sscnt = {}
    for tid in dataset:
        for can in candidates:
            if can.issubset(tid):
                sscnt.setdefault(can, 0)
                sscnt[can] += 1
    num_items = float(len(dataset))
    #print num_items
    retlist = []
    support_data = {}
    for key in sscnt:
        support = sscnt[key] / num_items
        if support >= min_support:
            retlist.insert(0, key)
        support_data[key] = support
    return retlist, support_data


def aprioriGen(freq_sets, k):
    "Generate the joint transactions from candidate sets"
    retList = []
    lenLk = len(freq_sets)
    for i in range(lenLk):
        for j in range(i + 1, lenLk):
            L1 = list(freq_sets[i])[:k - 2]
            L2 = list(freq_sets[j])[:k - 2]
            L1.sort()
            L2.sort()
            if L1 == L2:
                retList.append(freq_sets[i] | freq_sets[j])
    return retList


def apriori(dataset, minsupport=0.5):
    "Generate a list of candidate item sets"
    C1 = createC1(dataset)
    D = map(set, dataset)
    L1, support_data = scanD(D, C1, minsupport)
    L = [L1]
    k = 2
    while (len(L[k - 2]) > 0):
        Ck = aprioriGen(L[k - 2], k)
        Lk, supK = scanD(D, Ck, minsupport)
        support_data.update(supK)
        L.append(Lk)
        k += 1
    return L, support_data

def generateRules(L, support_data, min_confidence=0.7):
    """Create the association rules
    L: list of frequent item sets
    support_data: support data for those itemsets
    min_confidence: minimum confidence threshold
    """
    rules = []
    for i in range(1, len(L)):
        for freqSet in L[i]:
            H1 = [frozenset([item]) for item in freqSet]
            print "freqSet", freqSet, 'H1', H1
            if (i > 1):
                rules_from_conseq(freqSet, H1, support_data, rules, min_confidence)
            else:
                calc_confidence(freqSet, H1, support_data, rules, min_confidence)
    return rules


def calc_confidence(freqSet, H, support_data, rules, min_confidence=0.7):
    "Evaluate the rule generated"
    pruned_H = []
    for conseq in H:
        conf = support_data[freqSet] / support_data[freqSet - conseq]
        if conf >= min_confidence:
            print freqSet - conseq, '--->', conseq, 'conf:', conf
            rules.append((freqSet - conseq, conseq, conf))
            pruned_H.append(conseq)
    return pruned_H


def rules_from_conseq(freqSet, H, support_data, rules, min_confidence=0.7):
    "Generate a set of candidate rules"
    m = len(H[0])
    if (len(freqSet) > (m + 1)):
        Hmp1 = aprioriGen(H, m + 1)
        Hmp1 = calc_confidence(freqSet, Hmp1,  support_data, rules, min_confidence)
        if len(Hmp1) > 1:
            rules_from_conseq(freqSet, Hmp1, support_data, rules, min_confidence)

def find_suggestions(currentStore,listOfFreqItems,support_data,num=20):
    result=[]
    print listOfFreqItems[0]
    for item in listOfFreqItems:
        for item2 in item:
            loitem2=list(item2)
            if(currentStore.strip()!=''):
				if(currentStore in loitem2):
					print item2
					print support_data.get(item2)
					counter=0
					while(counter<len(result) and support_data.get(frozenset(result[counter]))>support_data.get(item2)):
						counter=counter+1
					result.insert(counter,loitem2)
					
            else:
				if(num<20):
					num=20
				result.append(loitem2)
				print item2
				print support_data.get(item2)
        if(len(result)==0):
            if(num<20):
                num=20
            resultantListOfStores=[list(x) for x in (listOfFreqItems[0])]
            result=(resultantListOfStores)
    print result
    temp=[] 
    (temp.append(currentStore))
    print (temp),'Current Element'
    if(temp in result):
    	result.remove(temp)
    return result[0:num]
"""
def find_suggestions_for_list(currentStores,listOfFreqItems,support_data):
    results=[]
    result=[]
    if(len(currentStores)>1):
        counter=0
        for store in currentStores:
            results.insert(counter,find_suggestions(store,listOfFreqItems,support_data))
            counter=counter+1
    result=results[0]
    for i in range( 1,len(results)):
        print results[i]
        print set(results[i])
        print set(result)
        #result=list(set(result) & set(results[i]))
        result = [filter(lambda x: x in result, sublist) for sublist in results[i]] 
    return result
"""

def getStoresBasedOnIncomeScores(storeName,rangeRegion=10):
    
    store_income_score_file="data/store_wise_cat_avg_score_filtered.txt"
    store_income_score = np.genfromtxt(store_income_score_file, dtype=None, names=True, delimiter='\t')
    lengthInput= store_income_score.shape[0]
    for i in range(0,lengthInput):
        #print store_income_score[i][0]
        if(storeName.strip().lower()==store_income_score[i][0].strip().lower()):
            low=0
            if(low<i-rangeRegion):
                low=i-rangeRegion
            high=i+rangeRegion
            if(high>store_income_score.shape):
                high=store_income_score.shape
            print low,high
            print store_income_score[low:high]
            #print store_income_score[low:high][0:1]
            return store_income_score[low:high]
    return []


def main():
    """
    dir_path='C:/Users/Rishabh/Desktop/capstone project/dataStuff/latlongdata/pumaPopHousSampleData/pumaSelectedFiles/'
    out_dir_path='C:/Users/Rishabh/Desktop/capstone project/dataStuff/latlongdata/pumaPopHousSampleData/pumaIncomeMeanData/'
    mallDataFile="C:/Users/Rishabh/Desktop/capstone project/dataStuff/latlongdata/mallsDataSelected.txt"
    pumaGeographicalFile="C:/Users/Rishabh/Desktop/capstone project/dataStuff/latlongdata/2010_Gaz_PUMAs_national.txt"
    stateMappingFile="C:/Users/Rishabh/Desktop/capstone project/dataStuff/latlongdata/stateAbbMapping.csv"
    outfile="C:/Users/Rishabh/Desktop/capstone project/dataStuff/latlongdata/mallPumaMapping.csv"
    incomeDataFile="C:/Users/Rishabh/Desktop/capstone project/dataStuff/latlongdata/pumaPopHousSampleData/3selectedss10pnj.csv"
    outfileForAggPuma='C:/Users/Rishabh/Desktop/capstone project/dataStuff/latlongdata/pumaPopHousSampleData/pumaIncomeMeanData/pnj_normalizedMeanIncome.csv'
    #stateAbbMapping=np.loadtxt(stateMappingFile,delimiter=',',dtype={'names': ('state', 'abb'),'formats': ('S4', 'S2')})
    catFile="C:/Users/Rishabh/Desktop/capstone project/dataStuff/latlongdata/jsonFiles/allStores/food.txt"
    listOfFreqSets=[]
    support_data={}
    d = {}
    with open(catFile) as f:
        counter=0
        for line in f:
            (key, val) = line.split()
            d[int(key)] = val
    """
    testFile="C:/Users/Rishabh/Desktop/capstone project/dataStuff/latlongdata/jsonFiles/allStores/allStores2/testFile.txt"
    list_of_malls_and_stores=[]
    d = {}
    with open(testFile) as f:
        counter=0
        key_orig=-1
        mylist = f.read().splitlines()
        mylist=mylist[1:]
        for line in mylist:
            print line
            (key, val) = line.split(":",1)
            #print key.strip()
            dataset=load_dataset(key.strip())
            #print key,':',val
            ##if(key==key_orig):
            frequency=0.2
            listOfFreqItems,support_data=apriori(dataset,frequency)
            (key, val) = val.split(":",1)
            #print val
            if(':' in val):
                (key, val) = val.split(":",1)
            input_var=1;
            print listOfFreqItems
            """
            print key
            while(key.strip()!='' and input_var!='0'):
                storeList=key.split(",")
                print storeList
                storeName = raw_input('enter any store')
                print storeName
                print find_suggestions(list(storeName),listOfFreqItems,support_data)
                tryAnother=raw_input('enter 1 to try same category, another mall')
                if(tryAnother=='1'):
                    (key, val) = val.split(":",1)
                else:
                    input_var=raw_input('enter 0 for another category')
            #list_of_malls_and_stores.insert(counter,(val.split(",")))
            #counter=counter+1
            #print list_of_malls_and_stores[0]
            """   
    print "done"          
    
if __name__ == "__main__":
    main()
