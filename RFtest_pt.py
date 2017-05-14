import sys
import os 
import pandas as pd
import numpy as np
import gensim
import pickle
from tqdm import tqdm
from sklearn.ensemble import RandomForestClassifier

#load and train random forest classifier
X=np.load("X.npy")
X=np.float32(X)
#Swap question1 and 2 to get additional dataset
xx=np.concatenate((X[:,300:600],X[:,0:300]),axis=1)
X=np.concatenate((X,xx),axis=0)
del xx


with open('object.pickle') as f:
	Y,model,word2tfidf=pickle.load(f)
Y=np.concatenate((Y,Y),axis=0)

forest=RandomForestClassifier(n_estimators=10)
forest=forest.fit(X,Y)
del X,Y

with open('object_forest.pickle','w') as f:
	pickle.dump(forest,f)



	


#start testing
#load testing data
df_testq=pd.read_csv("testq_t1.csv",sep='\t')
df_testq['question1'] = df_testq['question1'].apply(lambda x: unicode(str(x),"utf-8"))
df_testq['question2'] = df_testq['question2'].apply(lambda x: unicode(str(x),"utf-8"))


#data transform for trainq question1
vecs1=[]
for stnc in tqdm(list(df_testq['question1'])):
	stnc_Token=list(gensim.utils.tokenize(stnc, deacc=True, lower=True))
	stncLength=np.shape(stnc_Token)[0]
	mean_vec=np.zeros(300)
	mean_idf=np.zeros(3) 
	
	wcount=0
	for word in stnc_Token:
		wposind=int(float(wcount)/stncLength*3)
		wcount+=1
		try:
			wordVec=model[str(word)]
		except:
			wordVec=np.zeros(100)
		
		try:
			idf=word2tfidf[str(word)]
		except:
			idf=0;
		mean_vec[wposind*100:wposind*100+100]+=wordVec*idf
		mean_idf[wposind]+=idf
	for mpi,mp in enumerate(mean_idf):	
		if mean_idf[mpi] !=0: 
			mean_vec[mpi*100:mpi*100+100]/=mean_idf[mpi]
		else:
			mean_vec[mpi*100:mpi*100+100]/=0.000000001
	vecs1.append(mean_vec)
#df_trainq['q1_feats']=list(vecs1)
b1=list(vecs1)


#data transform for trainq question2
vecs1=[]
for stnc in tqdm(list(df_testq['question2'])):
	stnc_Token=list(gensim.utils.tokenize(stnc, deacc=True, lower=True))
	stncLength=np.shape(stnc_Token)[0]
	mean_vec=np.zeros(300)
	mean_idf=np.zeros(3)
	
	wcount=0
	for word in stnc_Token:
		wposind=int(float(wcount)/stncLength*3)
		wcount+=1
		try:
			wordVec=model[str(word)]
		except:
			wordVec=np.zeros(100)
		
		try:
			idf=word2tfidf[str(word)]
		except:
			idf=0;
		mean_vec[wposind*100:wposind*100+100]+=wordVec*idf
		mean_idf[wposind]+=idf
	for mpi,mp in enumerate(mean_idf):	
		if mean_idf[mpi] !=0: 
			mean_vec[mpi*100:mpi*100+100]/=mean_idf[mpi]
		else:
			mean_vec[mpi*100:mpi*100+100]/=0.000000001
	vecs1.append(mean_vec)

T=np.concatenate((b1,list(vecs1)),axis=1)


#Performance test (basic accuracy)
NumSamples=np.shape(T)[0]
GroundTruth=df_testq["is_duplicate"][:]

c=0
Correct=0
for w in T:
	res=forest.predict(w)
	if(res==GroundTruth[c]):
		Correct+=1
	c+=1


