import os, sys, csv,json,datetime,time,math,scipy.stats, collections;
import re

import numpy as np;
import scipy as sp;
import math;
import linecache

from scipy.spatial import distance 
from scipy.stats import ranksums;

import pymongo;
from bson.objectid import ObjectId
from pymongo import MongoClient


from bson.json_util import dumps

import sklearn;


#import copy
import random
#import operator;

import multiprocessing as mp




import torch
from torch import nn
import torch.nn.functional as F
from torch.autograd import Variable



#init config;
print("start loading config file");
configFile = json.load( open("config.json") );
print("start connect database");


client = MongoClient(configFile["database_host"], int(configFile["database_port"]) );


databaseName=configFile["database_name"];

db = client[databaseName];

admin_password=configFile["admin_password"];

print("connect database success");


def checkDataLength(mapid):

	return "";



def getMapInfoBySampleId(sampleid):
	sampleid = ObjectId(sampleid);
	data = db.dataInfo.find_one( {"_id":sampleid},{"name":1})
	info =dict();
	info["mapname"]=data["name"];
	
	return info;

def getMapDataBySampleId(sampleid):
	
	tsneMetaCollection = "meta_"+sampleid;

	tsneMap = db[tsneMetaCollection].find({}).sort([("order", pymongo.ASCENDING)]);

	tsneMap = list(tsneMap);

	return tsneMap;

def getAllSampleInfo():
	data = db.dataInfo.find({});
	resdata=[];
	for i in data:
		temp=dict();
		for j in i:
			if i[j] is None or i[j] == "":
				continue
			else:
				temp[j]=str(i[j]);
		resdata.append(temp);
	return resdata;



def listClusters(mapid):
	mapid = ObjectId(mapid);
	clstrs = db.cluster.distinct("clstrType",{"mapid":mapid});
	clstrs = list(clstrs);
	return clstrs;


def getClusterInfo2(mapid,clstrType):

	mapid = ObjectId(mapid);
	clstrs = db.cluster.find({"mapid":mapid,"clstrType":clstrType},{"_id":1,"clstrName":1,"color" :1, "x":1, "y" : 1, "label" : 1, "prerender" : 1,"marks":1,"negmarks":1,"cells":1});

	res=[];
	for i in clstrs:
		i["_id"] = str(i["_id"]);
		res.append(i)

	return res;

def getClusterInfo3(mapid,clstrType):

	mapid = ObjectId(mapid);
	clstrs = db.cluster.find({"mapid":mapid,"clstrType":clstrType},{"_id":1,"clstrName":1});

	res=[];
	for i in clstrs:
		i["_id"] = str(i["_id"]);
		res.append(i)

	return res;

def getClusterInfo(sampleid):


	sampleid = ObjectId(sampleid);
	clstrs = db.cluster.find({"mapid":sampleid},{"_id":1,"clstrName":1,"clstrType":1,"color" :1, "x":1, "y" : 1, "label" : 1, "prerender" : 1,"marks":1,"negmarks":1});

	resclstrs=dict();
	for i in clstrs:
		clstrtype = i["clstrType"];
		idstr=str(i["_id"]);
		i["_id"]=idstr;
		if clstrtype in resclstrs:
			resclstrs[clstrtype].append(i);
		else:
			resclstrs[clstrtype]=[i];

	return resclstrs;



def getExprByGenes(mapid,genes,barcodes,meanstd=False):

	if len(barcodes) ==0:
		genexpr = db["expr_"+mapid].aggregate([
			{"$match":{"_id": {"$in":genes} }},
			{"$project":{"_id":1,"normalize":1, "mean":{"$avg":"$normalize"},"std":{"$stdDevPop":"$normalize"}    }}
		],allowDiskUse=True);
	else:
		aggEleAtarr=[]
		for i in barcodes:
			aggEleAtarr.append({"$arrayElemAt":["$normalize",int(i)]});

		if meanstd== False:
			
			genexpr = db["expr_"+mapid].aggregate([
				{"$match":{"_id": {"$in":genes} }},
				{"$project":{"_id":1,"normalize":aggEleAtarr}}
			],allowDiskUse=True);
		else:

			genexpr = db["expr_"+mapid].aggregate([
				{"$match":{"_id": {"$in":genes} }},
				{"$project":{"_id":1,"normalize":aggEleAtarr}},
				{"$project":{"_id":1,"normalize":1, "mean":{"$avg":"$normalize"},"std":{"$stdDevPop":"$normalize"}    }}
			],allowDiskUse=True);

	return list(genexpr);

def getExprdataByGene(sampleid,gene):
	
	genexpr = db["expr_"+sampleid].find_one({"_id":gene},{"normalize":1});

	if genexpr == None:
		return None;
	countexpr= genexpr["normalize"];

	res =dict();

	for i in range(len(countexpr)):
		if countexpr[i] >0:
			res[i]=countexpr[i];


	return res;


def queryClstrType():
	clstrTypes = db.clusterType.distinct("_id");
	clstrTypes = list(clstrTypes);
	return clstrTypes;




def deleteMapById(mapid,pwd):

	if pwd == admin_password:
		
		db.dataInfo.remove({"_id":ObjectId(mapid)});
		db.cluster.remove({"mapid":ObjectId(mapid)});
		db.drop_collection("expr_"+mapid)
		db.drop_collection("meta_"+mapid);

		msg="Delete success";
		status=1;
	else:
		msg = "Pasword incorrect";
		status=0;

	return {"status":status,"message":msg};



def updateMap(mapid,attrkey,attrval,pwd):
	mapid = ObjectId(mapid);
	if pwd == admin_password:
		
		res = db.dataInfo.update({"_id":mapid},{"$set":{ attrkey:attrval }},upsert=False);
		msg="Save success";
		status=1;

	else:
		msg = "Pasword incorrect";
		status=0

	return {"status":status,"message":msg};



def getMapInfoByDiseaseCategory(diseaseCategory):

	if diseaseCategory == "ALL":
		res = db.dataInfo.find();
		
	
	res2 = dict();
	for i in res:
		key=  i["disease"]+i["study"]+i["source"]+ i["subjectid"];
		
		if key in res2:
			res2[key].append({"_id":str(i["_id"]),"disease":i["disease"],"study":i["study"],"source":i["source"],"tissue":i["tissue"],"subjectid":i["subjectid"],"name":i["name"] });
		else:
			res2[key]=[{"_id":str(i["_id"]),"disease":i["disease"],"study":i["study"],"source":i["source"],"tissue":i["tissue"],"subjectid":i["subjectid"],"name":i["name"] }]


	res3=[];
	for i in res2:
		datas= res2[i];
		data=datas[0];
		common={"disease":data["disease"],"study":data["study"],"source":data["source"] ,"subjectid":data["subjectid"]};
		temp=[];
		for j in datas:
			temp.append({"cid":j["_id"],"sample":j["tissue"],"name":j["name"]});

		common["samples"]=temp
		res3.append(common)

	return res3;



def getGeneSearchPlotDataBycellType(gene,mapid,clstrType):

	genexpr = db["expr_"+mapid].find_one({"_id":gene},{"normalize":1});
	if genexpr == None:
		return None;
	countexpr= genexpr["normalize"];
	clusters = db.cluster.find({"mapid":ObjectId(mapid),"clstrType":clstrType},{"cells":1,"clstrName" : 1, "_id":1,"color":1});
	res=[]
	for i in clusters:
		cid = str(i["_id"]);
		cells=i["cells"]
		clstrlen = len(cells);
		nonzeros=[];
		for pos in cells:
			expr_val = countexpr[pos];
			if expr_val >0:
				nonzeros.append(expr_val);
		if len(nonzeros)==0:
			nonzeros_mean = 0;
			nonzeros_median = 0;
			nonzeros_1percentile=0;
			nonzeros_3percentile=0;
			nonzeros_perc = 0;
			nonzeros_min = 0;
			nonzeros_max = 0;
			p100=0;
			p0=0;
		else:
			nonzeros_mean = np.mean(nonzeros);
			
			nonzeros_1percentile = np.percentile(nonzeros,25);
			nonzeros_median = np.percentile(nonzeros,50);
			nonzeros_3percentile = np.percentile(nonzeros,75);
			nonzeros_perc = len(nonzeros)/clstrlen;
			#print(nonzeros_1percentile);
			#print(nonzeros_median)
			#print(nonzeros_3percentile);
			
			iqr = nonzeros_3percentile-nonzeros_1percentile;
			nonzeros_min = nonzeros_1percentile-1.5*iqr;
			nonzeros_max = nonzeros_3percentile+1.5*iqr;

			p100=np.percentile(nonzeros,100);
			p0=np.percentile(nonzeros,0);
			if nonzeros_min < p0:
				nonzeros_min=p0

			if nonzeros_max > p100:
				nonzeros_max=p100;

		res.append({"name":i["clstrName"],"color":i["color"],"cid":cid,"mean":nonzeros_mean,"median":nonzeros_median,"perc":nonzeros_perc,"1q":nonzeros_1percentile,"3q":nonzeros_3percentile,"min":nonzeros_min,"max":nonzeros_max,"p100":p100,"p0":p0,"cells":cells})

	return res;

def getGeneSearchPlotData(gene,sampleid):
	
	genexpr = db["expr_"+sampleid].find_one({"_id":gene},{"normalize":1});

	if genexpr == None:
		return None;
	countexpr= genexpr["normalize"];

	clusters = db.cluster.find({"mapid":ObjectId(sampleid)},{"cells":1,"clstrName" : 1, "clstrType":1,"_id":1,"color":1});

	res=[]
	for i in clusters:
		
		cid = str(i["_id"]);
		cells=i["cells"]
		clstrlen = len(cells);
		nonzeros=[];
		for pos in cells:
			expr_val = countexpr[pos];
			if expr_val >0:
				nonzeros.append(expr_val);

		if len(nonzeros)==0:
			nonzeros_mean = 0;
			nonzeros_median = 0;
			nonzeros_1percentile=0;
			nonzeros_3percentile=0;
			nonzeros_perc = 0;
			nonzeros_min = 0;
			nonzeros_max = 0;
			p100=0;
			p0=0;
		else:
			nonzeros_mean = np.mean(nonzeros);
			
			nonzeros_1percentile = np.percentile(nonzeros,25);
			nonzeros_median = np.percentile(nonzeros,50);
			nonzeros_3percentile = np.percentile(nonzeros,75);
			nonzeros_perc = len(nonzeros)/clstrlen;
			#print(nonzeros_1percentile);
			#print(nonzeros_median)
			#print(nonzeros_3percentile);
			
			iqr = nonzeros_3percentile-nonzeros_1percentile;
			nonzeros_min = nonzeros_1percentile-1.5*iqr;
			nonzeros_max = nonzeros_3percentile+1.5*iqr;

			p100=np.percentile(nonzeros,100);
			p0=np.percentile(nonzeros,0);
			if nonzeros_min < p0:
				nonzeros_min=p0

			if nonzeros_max > p100:
				nonzeros_max=p100


		res.append({"name":i["clstrName"],"color":i["color"],"ctype":i["clstrType"],"cid":cid,"mean":nonzeros_mean,"median":nonzeros_median,"perc":nonzeros_perc,"1q":nonzeros_1percentile,"3q":nonzeros_3percentile,"min":nonzeros_min,"max":nonzeros_max,"p100":p100,"p0":p0})
		#break;

	return res;





def getExprNormailizedataByGene(sampleid,gene):
	
	genexpr = db["expr_"+sampleid].find_one({"_id":gene},{"normalize":1});

	if genexpr == None:
		return None;
	countexpr= genexpr["normalize"];

	res =[];
	for i in range(len(countexpr)):
		if countexpr[i] >0:
			res.append(i);
	
	return res;




def listExistsGenes(sampleid,genes):

	fitGenes= db["expr_"+sampleid].distinct("_id",{"_id":{"$in":genes}})

	return fitGenes;

def listExistsGenesRegex(sampleid,geneRegex):

	fitGenes= db["expr_"+sampleid].distinct("_id",{"_id":{"$regex":"^"+geneRegex,"$options": "i" }})
	
	return fitGenes;


def savecluster(sampleid,name,ctype,cells,comment,marks,negmarks):

	sampleid = ObjectId(sampleid);

	color =getRandomColor();

	clstrcount = db.cluster.find({"mapid":sampleid,"clstrName":name,"clstrType":ctype}).count();

	if clstrcount == 0:
		comment = comment.strip();
		db.cluster.insert_one({"mapid":sampleid,"clstrName":name,"clstrType":ctype,"color":color,"cells":cells,"comment":comment,"x" : "", "y" : "", "label" : False, "prerender" : True,"marks":marks,"negmarks":negmarks})
		clstr = db.cluster.find_one({"mapid":sampleid,"clstrName":name,"clstrType":ctype});

		clstr_id=str(clstr["_id"])
		return {"status":"success","cid":clstr_id,"color":color}

	else:

		return {"status":"failed"}



def getClusterCellsById(clstrid):
	clstrid = ObjectId(clstrid);
	clstrCells = db.cluster.find_one({"_id":clstrid},{"cells":1});
	clstrCells= clstrCells["cells"];
	return clstrCells;


def contrastCellsVsClstr(sampleid,cells,clstr,contrastId):
	cell2 = getClusterCellsById(clstr);
	cell1= np.array(cells,dtype='i');
	data = contrast(sampleid,cell1,cell2);
	db2=pymongo.MongoClient(configFile["database_host"], int(configFile["database_port"]) )[databaseName];
	db2.contrastResult.update_one({"_id":contrastId},{"$set":{"p":data["p"],"n":data["n"],"done":True} })

	return "";


def queryClstrCellsAndLabelByCid(cid):
	cid = ObjectId(cid);
	clstr = db.cluster.find_one({"_id":cid},{"cells":1,"label":1,"x":1,"y":1,"clstrName":1});
	
	res=dict();
	res["cellids"]=clstr["cells"];
	res["name"] = clstr["clstrName"];
	res["labeled"]=clstr["label"];
	res["x"] = clstr["x"];
	res["y"]= clstr["y"];

	return res;



def getClusterClassification(clstrtype):

	data = db[clstrtype].find({});

	return list(data);


def getExprPosCountsByGene(sampleid,g1,g2):
	genexpr1 = db["expr_"+sampleid].find_one({"_id":g1},{"normalize":1})["normalize"];
	genexpr2 = db["expr_"+sampleid].find_one({"_id":g2},{"normalize":1})["normalize"];

	c1=0;
	c2=0;
	c3=0;
	d1=[];
	d2=[];
	d3=[];
	for i in range(len(genexpr1)):
		v1 = genexpr1[i];
		v2 = genexpr2[i];

		if v1>0 and v2 >0:

			c3+=1;
			d3.append(i);
		else:
			if v1>0:
				c1+=1;
				d1.append(i);

			if v2>0:
				c2+=1;
				d2.append(i);

	return {"g":[g1,g2,"intersc"],"c":[c1,c2,c3],"d1":d1,"d2":d2,"d3":d3}



def getExprPosCountByGene(sampleid,gene):
	genexpr = db["expr_"+sampleid].find_one({"_id":gene},{"normalize":1});

	if genexpr == None:
		return None;
	countexpr= genexpr["normalize"];

	count=0;
	for i in countexpr:
		if i >0:
			count+=1;


	return count;


def updateClusterColor(clstrid,color):
	res = db.cluster.update_one({"_id":ObjectId(clstrid)},{"$set":{"color": color}});

	return "success";

def updateClusterPostition(clstrid,x,y):
	res = db.cluster.update_one({"_id":ObjectId(clstrid)},{"$set":{"x":float(x),"y":float(y),"label":True}});
	return "success";

def updateClusterName(clstrid,name):
	res = db.cluster.update_one({"_id":ObjectId(clstrid)},{"$set":{"clstrName":name}});
	return "success";

def deleteCluster(clstrid):
	res = db.cluster.remove({"_id":ObjectId(clstrid)});

	return "success";


def updateClusterMarks(clstrid,marks):
	res = db.cluster.update_one({"_id":ObjectId(clstrid)},{"$set":{"marks":marks}});

	return "success";


def updateClusterNegMarks(clstrid,marks):
	res = db.cluster.update_one({"_id":ObjectId(clstrid)},{"$set":{"negmarks":marks}});

	return "success";


def updateClusterIsPreRender(clstrid,val):
	if val =='T':
		val =True;
	elif val =="F":
		val = False;
	res = db.cluster.update_one({"_id":ObjectId(clstrid)},{"$set":{"prerender":val}});
	return "success";




def contrast_new(sampleid,cells1,cells2):


	return "";



def contrast(sampleid,cells1,cells2):

	xlen = len(cells1);
	ylen = len(cells2);

	p=dict();
	n=dict();
	allexpr = db["expr_"+sampleid].find({},{"_id":1,"normalize":1});
	for i in allexpr:
		g = i["_id"];
		expr = i["normalize"];
		x=[];
		y=[];

		xpos=0;
		ypos=0;

		for j in cells1:
			x.append(expr[j])
			if expr[j]>0:
				xpos+=1;


		for j in cells2:
			y.append(expr[j]);
			if expr[j]>0:
				ypos+=1;


		percx = xpos/xlen;
		percy = ypos/ylen;

		
		if abs(percx-percy) <  0.25:
			continue; 

		#ranksumsres = scipy.stats.ranksums(x,y);
		ranksumsres = scipy.stats.ranksums(x,y);
		statics = ranksumsres[0];
		pval = ranksumsres[1];
			
		if pval < 0.01:
			if statics >=0:
				p[g]=pval;
			else:
				n[g]=pval;

	p = sorted(p.items(), key=lambda kv: kv[1] );
	n =	sorted(n.items(), key=lambda kv: kv[1] );

	p2=[];
	n2=[];
	for i in p:
		p2.append(i[0]);
	p=None;
	for i in n:
		n2.append(i[0]);
	n=None;
	return {"p":p2,"n":n2}




def getContrastResult(resultid):

	resultid = ObjectId(resultid);

	data = db.contrastResult.find_one({"_id":resultid});
	
	done = data["done"];
	if done:
		p=data["p"];
		n=data["n"];
		db.contrastResult.remove({"_id":resultid});
		return {"done":done,"p":p,"n":n}
	else:
		return {"done":done}






def doContrast(sampleid,cells,clstr,contrastModel):
	currentTime = time.time()
	contrastId = db.contrastResult.insert({"startTime":currentTime,"done":False}); 
	returncontrastId = str(contrastId);


	if contrastModel == "contrastwithrest":
		p1 = mp.Process(target=contrastwithrest,args=(sampleid,cells,contrastId) )
		p1.start();

	if contrastModel == "contrastCellsVsClstr":

		p1 = mp.Process(target=contrastCellsVsClstr,args=(sampleid,cells,clstr,contrastId) )
		p1.start();


	return returncontrastId;




def contrastwithrest_new(sampleid,cells,contrastId):
	return ""


def uploadGeneMarkers(name,genes):

	res={};
	exists = db.geneMarkers.count_documents({"_id":name});
	if exists ==0:

		db.geneMarkers.insert({"_id":name,"genes":genes});

		res={"status":1,"msg":"Success"};
	else:
		res={"status":0,"msg":"name exists"};


	return res;


def getGeneMarkers():

	data=db.geneMarkers.find();

	data2=dict();
	for i in data:
		data2[i["_id"]]=i["genes"];


	return data2;

def deleteGeneMarkers(name,pwd):
	if pwd == admin_password:
		
		db.geneMarkers.remove({"_id":name});

		msg="Delete success";
		status=1;
	else:
		msg = "Pasword incorrect";
		status=0;

	return {"status":status,"msg":msg};

def contrastwithrest(sampleid,cells,contrastId):	
	#db.contrastResult.insert_one()
	db2=pymongo.MongoClient(configFile["database_host"], int(configFile["database_port"]) )[databaseName];

	#cells=np.array(cells,dtype="i");
	cellsdict= dict();
	xlen=0
	for i in cells:
		xlen+=1;
		cellsdict[int(i)]=None;



	p=dict();
	n=dict();

	allexpr = db2["expr_"+sampleid].find({},{"_id":1,"normalize":1});
	for i in allexpr:
		g = i["_id"];
		expr = i["normalize"];
		#filter

		totallen = len(expr)
		ylen = totallen-xlen;

		xpos=0;
		ypos=0;
		x=[];
		y=[];
		for j in range(len(expr)):
			if j in cellsdict:
				x.append(expr[j]);
				if expr[j]>0:
					xpos+=1;
			else:
				y.append(expr[j]);
				if expr[j]>0:
					ypos+=1;



		percx = xpos/xlen;
		percy = ypos/ylen;

		
		if abs(percx-percy) < 0.25:
			continue; 

		ranksumsres = scipy.stats.ranksums(x,y);
		
		statics = ranksumsres[0];
		pval = ranksumsres[1];

		
		
		if pval < 0.01:
			if statics >=0:
				p[g]=pval;
			else:
				n[g]=pval;

	p = sorted(p.items(), key=lambda kv: kv[1] );
	n =	sorted(n.items(), key=lambda kv: kv[1] );

	p2=[];
	n2=[];
	for i in p:
		p2.append(i[0]);
	p=None;
	for i in n:
		n2.append(i[0]);
	n=None;
	
	db2.contrastResult.update_one({"_id":contrastId},{"$set":{"p":p2,"n":n2,"done":True}} );

	#return {"p":p2,"n":n2}
	return "";

def runRanksums(sampleid,arr,compareTargets):

	if compareTargets =='all':
		pass;
	else:
		print(compareTargets);





	return ""


def contrastGeneSearch(gene,cells1,cells2,sampleid,name1,name2):


	genexpr = db["expr_"+sampleid].find_one({"_id":gene},{"normalize":1});

	if genexpr == None:
		return None;
	countexpr= genexpr["normalize"];

	maxval =0;

	exprdict =dict();
	for i in range(len(countexpr)):
		if countexpr[i] >0:
			exprdict[i]=countexpr[i];
			if countexpr[i] > maxval:
				maxval	= countexpr[i];
	
	res=[];

	for i in [1,2]:
		if i ==1:
			cells=cells1;
			name=name1;
			color="orange";
		elif i ==2:
			cells=cells2;
			name=name2;
			color="steelblue";

		clstrlen = len(cells);
		nonzeros=[];
		for pos in cells:
			expr_val = countexpr[pos];
			if expr_val >0:
				nonzeros.append(expr_val);

		if len(nonzeros)==0:
			nonzeros_mean = 0;
			nonzeros_median = 0;
			nonzeros_1percentile=0;
			nonzeros_3percentile=0;
			nonzeros_perc = 0;
			nonzeros_min = 0;
			nonzeros_max = 0;
			p100=0;
			p0=0;
		else:
			nonzeros_mean = np.mean(nonzeros);
			
			nonzeros_1percentile = np.percentile(nonzeros,25);
			nonzeros_median = np.percentile(nonzeros,50);
			nonzeros_3percentile = np.percentile(nonzeros,75);
			nonzeros_perc = len(nonzeros)/clstrlen;
			#print(nonzeros_1percentile);
			#print(nonzeros_median)
			#print(nonzeros_3percentile);
			
			iqr = nonzeros_3percentile-nonzeros_1percentile;
			nonzeros_min = nonzeros_1percentile-1.5*iqr;
			nonzeros_max = nonzeros_3percentile+1.5*iqr;

			p100=np.percentile(nonzeros,100);
			p0=np.percentile(nonzeros,0);
			if nonzeros_min < p0:
				nonzeros_min=p0

			if nonzeros_max > p100:
				nonzeros_max=p100


		res.append({"name":name,"color": color,"mean":nonzeros_mean,"median":nonzeros_median,"perc":nonzeros_perc,"1q":nonzeros_1percentile,"3q":nonzeros_3percentile,"min":nonzeros_min,"max":nonzeros_max,"p100":p100,"p0":p0})
	

	return res,exprdict,maxval;



#import multiprocessing as mp;
#p1=mp.Process(target=runWilcoxon,args=(arr))
#p1.start();
#p1.join();


def getClusterRestCells(sampleid,cells):
	
	cellorders = db["meta_"+sampleid].find({},{"order":1});
	
	cellsdict=dict();
	for i in cells:
		cellsdict[i]=None;


	res=[];
	for i in cellorders:
		if i["order"] not in cellsdict:
				res.append(i["order"]);

	return res;




def strarrayToIntarray(cellstr):
	cells = np.array(cellstr.split(","),dtype='i');
	return list(cells);



def getRandomColor():
	r = lambda: random.randint(0,255);
	color = '#%02X%02X%02X' % (r(),r(),r());

	return color;






def getClusterNameById(cid):
	clstrid = ObjectId(cid);
	clstrName = db.cluster.find_one({"_id":clstrid},{"clstrName":1});
	clstrName= clstrName["clstrName"];
	return clstrName;



def getAllClusterStudies():

	studies = db.dataInfo.aggregate([
		{"$group":{
			 "_id":"$study" ,
			 "tissues":{"$addToSet":"$tissue"} 
		}}
	]);


	studies =list(studies);

	return studies;



def getAllTissueByStudies(study):
	data = db.dataInfo.find({"study":study});




def getAllClusterTypesByStudyAndTissues(study,tissues):


	mapids = db.dataInfo.distinct("_id",{"study":study,"tissue":{"$in":tissues}});
	data = db.cluster.aggregate([
		{"$match":{"mapid":{"$in" :mapids}}},

		{"$project":{"clstrName":1,"clstrType":1}},
		{"$group":{"_id":"$clstrType","clstrName":{"$addToSet":"$clstrName"}}},
		{"$project":{"clstrType":"$_id","clstrName":1,"_id":0}},


	])

	datadict=dict();
	for i in data:
		datadict[i["clstrType"]]=i["clstrName"];


	return datadict;



def queryComparePlotData(study,tissues,gene,cluster,clusterType):
	
	gene = gene.upper();

	maps = db.dataInfo.find({"study":study,"tissue":{"$in":tissues}},{"_id":1,"tissue":1,"subjectid":1,"name":1});

	mapids=[];

	result = dict();

	for i in maps:
		mapids.append(i["_id"]);
		result[str(i["_id"])]={"tissue":i["tissue"],"subjid":i["subjectid"],"name":i["name"]};

	clusterinfo = db.cluster.find( {"mapid":{"$in" :mapids},"clstrName":cluster,"clstrType":clusterType },{"mapid":1,"cells":1}   )
	for i in clusterinfo:

		mapid = str(i["mapid"]);
		cells = i["cells"];
		expr = db["expr_"+mapid].find_one({"_id":gene},{"gene":1,"normalize":1});
		if expr is not None:
			normVal = expr["normalize"];

			nonzeros=[];
			allexpr =[]
			for pos in cells:
				expr_val = normVal[pos];
				if expr_val >0:
					nonzeros.append(expr_val);

				allexpr.append(expr_val);

			if len(nonzeros)==0:
				nonzeros_mean = 0;
				nonzeros_median = 0;
				nonzeros_1percentile=0;
				nonzeros_3percentile=0;
				nonzeros_perc = 0;
				nonzeros_min = 0;
				nonzeros_max = 0;
				p100=0;
				p0=0;
			else:
				nonzeros_mean = np.mean(nonzeros);
				
				nonzeros_1percentile = np.percentile(nonzeros,25);
				nonzeros_median = np.percentile(nonzeros,50);
				nonzeros_3percentile = np.percentile(nonzeros,75);
				nonzeros_perc = len(nonzeros)/len(allexpr);
				
				iqr = nonzeros_3percentile-nonzeros_1percentile;
				nonzeros_min = nonzeros_1percentile-1.5*iqr;
				nonzeros_max = nonzeros_3percentile+1.5*iqr;

				p100=np.percentile(nonzeros,100);
				p0=np.percentile(nonzeros,0);
				if nonzeros_min < p0:
					nonzeros_min=p0

				if nonzeros_max > p100:
					nonzeros_max=p100


			result[mapid]["expr"]=allexpr;
			result[mapid]["mean"]=nonzeros_mean;
			result[mapid]["median"]=nonzeros_median;
			result[mapid]["perc"]=nonzeros_perc;
			result[mapid]["1q"]=nonzeros_1percentile;
			result[mapid]["3q"]=nonzeros_3percentile;
			result[mapid]["min"]=nonzeros_min;
			result[mapid]["max"]=nonzeros_max;
			result[mapid]["p100"]=p100;
			result[mapid]["p0"]=p0;

	result2=dict();

	for i in result:
		subj = result[i]["subjid"];
		if "expr" in result[i]:
			if subj in result2:
				result2[subj].append(result[i]);
				
			else:
				result2[subj]=[result[i]];

	return result2;

def getBarcodes(cellids,mapid):
	cellids2 =[];
	for i in cellids:
		cellids2.append(int(i));
	barcodes = db["meta_"+mapid].distinct("_id",{"order":{"$in":cellids2} } );

	return barcodes;


def getCellsByStudyAndTissueAndclstrtypeAndClstr(study,tissue,clusterType,cluster):

	study = str(study).strip();
	clusterType = str(clusterType).strip();
	cluster = str(cluster).strip();
	tissue = str(tissue).strip();

	maps = db.dataInfo.find({"study":study,"tissue": tissue},{"_id":1,"subjectid":1,"tissue":1});
	
	result=dict();
	mapids=[]
	for i in maps:
		result[str(i["_id"])]={"name": str(i["subjectid"])+"__"+str(i["tissue"])};
		mapids.append(i["_id"]);
	clstrs = db.cluster.aggregate([
		{"$match":{"mapid":{"$in":mapids},"clstrType":clusterType,"clstrName":cluster}},
		{"$project":{"_id":0,"mapid":1,"cells":1}},
	]);
	for i in clstrs:
		cells = db["meta_"+str(i["mapid"])].find({"order":{"$in":i["cells"]} },{"_id":1,"order":1});

		result[str(i["mapid"])]["cells"]=list(cells);

	"""
	result2=dict();
	for i in result:
		mapid = i;
		name = result[i]["name"].replace(" ","_");
		cells = result[i]["cells"];

		for c in cells:
			cname = name+"_"+c["_id"];
			order = c["order"];

			result2[cname]={"id":mapid,"odr":order};

	return result2;

	"""
	return result;

#def getALLCellTypeByStudy(study):


def getNNmodelsPath():
	appPath = os.getcwd();
	NNmodelsPath = os.path.join(appPath,"NNmodels");

	return NNmodelsPath;

def getNNmodelsList():
	NNmodelsPath = getNNmodelsPath();
	folders= os.listdir(NNmodelsPath);

	return folders;


def nnpredict(mapid,nnmodel):
	NNmodelsPath = getNNmodelsPath();
	targetPath = os.path.join(NNmodelsPath,nnmodel);
	files = os.listdir(targetPath);
	netinfo="";
	for i in files:
		if i.endswith("json"):
			netinfo = os.path.join(targetPath,i);
			break;

	if netinfo =="":
		return {"status":"error"}
	else:
		pass;

	netinfo = json.load(open(netinfo));
	inputGenes = netinfo["inputGenes"];
	outputLabel = netinfo["output"];
	netmodel = torch.load( os.path.join(targetPath,netinfo["netfile"]) );

	expr_query = db["expr_"+mapid].find({"_id":{"$in":inputGenes}});
	exprs=dict();
	for i in expr_query:
		exprs[i["_id"]]=i["normalize"];

	datalength = len(exprs[list(exprs.keys())[0]]);
	inputMatrix = [];
	for i in inputGenes:
		if i in exprs:
			inputMatrix.append(exprs[i]);
		else:
			temp = [0]*datalength;
			inputMatrix.append(temp);
	predict = netmodel(torch.tensor(np.asarray(inputMatrix).T).type(torch.FloatTensor));
	predict = torch.sigmoid(predict);
	inputMatrix = None;
	outputLabel2 = {v:k for k,v in outputLabel.items()}
	result=[];
	for i in predict:
		i=i.tolist();
		temp =np.argsort(i);
		if i[temp[-1]]<0.6:
			result.append("");
		elif i[temp[-1]]-i[temp[-2]] < 0.65:
			result.append("");
		else:
			result.append(  int(temp[-1])  );

	return {"status":"success","data":result,"label":outputLabel2}



def savennresult(mapid,clstrType,clusterArr,labels,colors):
	mapid = ObjectId(mapid);
	clstrCount = db.cluster.count_documents({"clstrType":clstrType,"mapid":mapid});
	if clstrCount >0 :
		return {"status":"clstrType already exists"}
	else:
		pass;

	colordict=dict();
	clusters=dict();
	for i in range(len(labels)):
		clusters[labels[i]]=[];
		colordict[labels[i]]=colors[i];

	for i in range(len(clusterArr)):
		clstrOrder = clusterArr[i];
		if clstrOrder != "":
			clstrName = labels[int(clstrOrder)];
			clusters[clstrName].append(int(i));

	insertList=[];
	for i in clusters:
		insertList.append({"mapid":mapid,"clstrType":clstrType,"clstrName":str(i),
			"cells":clusters[i],"color":colordict[i],"x":"","y":"","label":False,"prerender":True
		});

	for i in insertList:
		db.cluster.insert_one(i);


	return {"status":"success"}


def getClstrNameByclstrType(mapid,clstrType):

	mapid = ObjectId(mapid);
	#clstrNames = db.cluster.distinct("clstrName",{"mapid":mapid,"clstrType":clstrType})

	clstrObjs = db.cluster.find({"mapid":mapid,"clstrType":clstrType},{"clstrName":1,"cells":1});
	clstrObjs2=dict();
	for i in clstrObjs:
		clstrObjs2[i["clstrName"]]=i["cells"];
	return clstrObjs2;




def getMaps(query):
	maps=db.dataInfo.find(query);
	map2=dict();
	for i in maps:
		i["_id"]=str(i["_id"]);
		map2[i["_id"]]=i;
	return map2;

def getNormalizedGeneExpr(mapid=None,clstrType=None,clstrName=None,genes=None):
	query = dict();
	aggrlist=[];
	if mapid is None:
		print("please input map id.")
		return ""
	else:
		query["mapid"]=ObjectId(mapid);

	if genes is None:
		print("please input a gene list")

		return ""
	elif genes =="all":
		pass;
	elif type(genes) is list:
		genes = [x.upper() for x in genes ];
		aggrlist.append({"$match":{"_id":{"$in":genes}  }});

	else:
		print("please make sure genes is list");


	if clstrType is None:
		pass;
	else:
		query["clstrType"] =clstrType;
	if clstrName is None:
		pass;
	else:
		query["clstrName"] =clstrName;

	if clstrType is None and clstrName is None:
		aggrlist.append({"$project":{"_id":0,"gene":"$_id","expr": "$normalize"}});
		meta = db["meta_"+mapid].find({  },{"_id":1,"order":1}).sort([("order", pymongo.ASCENDING)]);
		barcodes=[];
		for i in meta:
			barcodes.append(i["_id"]);
	else:
		cellsPosList = db.cluster.find(query).distinct("cells");
		meta = db["meta_"+mapid].find({"order":{"$in": cellsPosList} },{"_id":1,"order":1});
		metaMap = dict();
		for i in meta:
			metaMap[i["order"]]=i["_id"];

		barcodes=[];
		for i in cellsPosList:
			barcodes.append(metaMap[i]);

		aggEleAtarr=[]
		for i in cellsPosList:
			aggEleAtarr.append({"$arrayElemAt":["$normalize",i]});

		aggrlist.append({"$project":{"_id":0,"gene":"$_id","expr": aggEleAtarr}}); 
	data = db["expr_"+mapid].aggregate(aggrlist,allowDiskUse=True)
	result=[];
	index=[];
	for i in data:
		index.append(i["gene"]);
		result.append(i["expr"])

	return {"head":barcodes,"data":result,"index":index}

def exportNormalizedGeneExpr():
	pass;


def getMarkGenesByMapidAndClusterType(mapid,clstrType):
	
	clstrs = db.cluster.find({"mapid":ObjectId(mapid),"clstrType":clstrType},{"clstrName":1,"marks":1,"negmarks":1});
	res = dict();
	for i in clstrs:
		res[i["clstrName"]]={"marks":i["marks"],"negmarks":i["negmarks"]}

	return res;



def getClstrsByMapidAndClstrType(mapid,clstrType):
	mapidObj = ObjectId(mapid);
	clstrs = db.cluster.find({"mapid":mapidObj,"clstrType":clstrType},{"cells":1,"clstrName":1});
	clstrdict=dict();
	for i in clstrs:
		for c in i["cells"]:
			clstrdict[c]=i["clstrName"];

	metadict=dict();
	meta = db["meta_"+mapid].find({},{"order":1,"_id":1})
	for i in meta:
		if i["order"] in clstrdict:
			metadict[i["_id"]]=clstrdict[i["order"]];

	return metadict;

def exportClstrsByMapidAndClstrType(mapid,clstrType):
	pass;


def getNormalizedGeneExprByTwoClstrs(mapid,clstrType1,clstrName1,clstrType2,clstrName2,zsfilter,log2fc):
	mapidObj = ObjectId(mapid);
	cells1 = db.cluster.find_one({"mapid":mapidObj,"clstrType":clstrType1,"clstrName":clstrName1},{"cells":1})["cells"];
	cells2 = db.cluster.find_one({"mapid":mapidObj,"clstrType":clstrType2,"clstrName":clstrName2},{"cells":1})["cells"];

	aggrlist=[];

	aggEleAtarr1=[]
	for i in cells1:
		aggEleAtarr1.append({"$arrayElemAt":["$normalize",i]});

	aggEleAtarr2=[]
	for i in cells2:
		aggEleAtarr2.append({"$arrayElemAt":["$normalize",i]});
	
	aggrlist.append({"$project":{"_id":1, "group1": aggEleAtarr1 ,"group2": aggEleAtarr2 }});

	aggrlist.append({"$project":{
		"_id":1,
		"group1": 1 ,
		"group2": 1, 
		"mean1":{"$add":[{"$avg":"$group1"},0.000001] },
		"mean2":{"$add":[{"$avg":"$group2"},0.000001] },
		
	}});

	aggrlist.append({"$project":{
		"_id":1,
		"group1": 1 ,
		"group2": 1, 
		"mean1":1,
		"mean2":1,
		"meandiff":{
			"$abs":{
				"$subtract": [ "$mean1", "$mean2" ]
			} 
		},
			
	}});

	aggrlist.append({"$match":{"meandiff": {"$gt":0}  }});


	if log2fc !=False and log2fc !="" and log2fc !=None:
		fc = 2**float(log2fc);
		fc2 = 1/fc;
		aggrlist.append({"$project":{
			"_id":1,
			"group1": 1 ,
			"group2": 1, 
			"fc": {"$divide":["$mean1","$mean2"]  },
			"meandiff":1

		}});

		aggrlist.append({"$match": { "$or":[ {"fc": {"$gt": fc}  }, {"fc": {"$lt": fc2}  }  ] } });
		#result = db["expr_"+mapid].aggregate(aggrlist,allowDiskUse=True);
		#print(list(result))
		
		"""
		aggrlist.append({"$project":{
			"_id":1,
			"group1": 1 ,
			"group2": 1, 
			"log2fc":{
				"$abs":{
					"$log":[{"$divide":["$mean1","$mean2"] },2]
				},
			},
			"meandiff":1

		}});

		aggrlist.append({"$match":{"log2fc": {"$gt":float(log2fc)}  }});
		"""

	if zsfilter !=None and zsfilter != "" and zsfilter != False :

		aggrlist.append({"$project":{
			"_id":1,
			"group1": 1 ,
			"group2": 1, 
			"zs":{
				"$divide":[
					"$meandiff",
					{
						"$stdDevPop":{ 
							"$concatArrays":["$group1","$group2"]
						}
					}
				]
			}
		}}); 
		aggrlist.append({"$match":{"zs": {"$gt":float(zsfilter)}  }});

	aggrlist.append({"$project":{"_id":1, "group1": 1 , "group2": 1 }});

	result = db["expr_"+mapid].aggregate(aggrlist,allowDiskUse=True);

	result2=dict();
	for i in result:
		result2[i["_id"]]=[i["group1"],i["group2"]];

	return result2;

"""
def savetoFile(self,resfile,data):
	head = data["barcode"];
	expr = data["expr"]
	with open(resfile,"w") as f:
		head=",".join(head)
		head="gene,"+head;
		f.write(head);

	with open(resfile,"a") as f:
		for i in expr:
			temp=[]
			temp.append(i["gene"]);
                for x in i["expr"]:
                    temp.append(str(x));
                f.write("\n"+(",".join(temp)));

            print("success.")
"""

