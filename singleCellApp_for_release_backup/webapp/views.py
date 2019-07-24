from django.shortcuts import render
import json
import os;
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect

# Create your views here.

from . import service;




# C""reate your views here.
def index(request):

	return render(request,"index/index.html");


def neuralNetwork(request):

	return render(request,"index/neuralNetwork.html");

def rendermap(request,mapid):

	return render(request,"index/scmap.html",{"mapid":mapid} );


def compareplot(request):

	return render(request,"index/compareplot.html" );


def administration(request):

	return render(request,"index/admin.html");


def renderdatatable(request,diseaseCategory):

	return render(request,"index/mapTable.html",{"diseaseCategory":diseaseCategory})

def getMapInfoByDiseaseCategory(request):

	diseaseCategory = request.POST.get("diseaseCategory").strip();

	data = service.getMapInfoByDiseaseCategory(diseaseCategory);

	return JsonResponse({"data":data });

def querybarcodes(request):

	cellids = request.POST.get("cellids");
	cellids = cellids.split(",");
	sampleid = request.POST.get("sampleid");
	
	data = service.getBarcodes(cellids,sampleid);
	return JsonResponse({"data":data });


def updateMap(request):
	mapid = request.POST.get("cid");
	attrkey = request.POST.get("attrkey");
	attrval = request.POST.get("attrval");
	pwd = request.POST.get("adminpwd");

	res = service.updateMap(mapid,attrkey,attrval,pwd);

	return JsonResponse(res)

def updateMap_backup(request):
	mapid = request.POST.get("_id").strip();
	name = request.POST.get("name").strip();
	subjectid = request.POST.get("subjectid").strip();
	source = request.POST.get("source").strip();
	study = request.POST.get("study").strip();
	disease = request.POST.get("disease").strip();
	tissue = request.POST.get("tissue").strip();
	res =  service.updateMap(mapid,name,subjectid,source,study,disease,tissue);
	

	return JsonResponse({"status":res });


def savennresult(request):
	mapid = request.POST.get("mapid");
	clstrType = request.POST.get("clusterTypeName");
	cluster = request.POST.get("cluster").split(",");
	labels= request.POST.get("labels").split(",");
	colors = request.POST.get("colors").split(",");
	res = service.savennresult(mapid,clstrType,cluster,labels,colors);

	return JsonResponse(res);


def getNNmodelNames(request):
	nnlist = service.getNNmodelsList();
	return JsonResponse({"data":nnlist});


def predictnnresult(request):
	mapid = request.POST.get("mapid");
	nnmodel = request.POST.get("nnmodel");

	data = service.nnpredict(mapid,nnmodel);
	return JsonResponse(data);


def getClstrsByTypeAndMapid2(request):
	mapid = request.POST.get("mapid");
	clstrType = request.POST.get("clstrType");
	clstrs = service.getClusterInfo3(mapid,clstrType);

	return JsonResponse({"res":clstrs});

def getClstrsByTypeAndMapid(request):
	mapid = request.POST.get("mapid");
	clstrType = request.POST.get("clstrType");

	clstrs = service.getClusterInfo2(mapid,clstrType);

	return JsonResponse({"res":clstrs});


def getMapDataByMapId(request):
	mapid = request.POST.get("mapid");

	data = service.getMapDataBySampleId(mapid);
	clstrInfo = service.listClusters(mapid);

	mapinfo = service.getMapInfoBySampleId(mapid);

	return JsonResponse({"tsneData":data,"clstr":clstrInfo,"info":mapinfo});

def getMapDataBySampleId(request):
	
	sampleid = request.POST.get("sampleid");

	data = service.getMapDataBySampleId(sampleid);
	clstrInfo = service.getClusterInfo(sampleid);

	mapinfo = service.getMapInfoBySampleId(sampleid);

	return JsonResponse({"tsneData":data,"clstr":clstrInfo,"info":mapinfo});

def getGeneSearchPlotData(request):
	gene = request.POST.get("gene");
	spid = request.POST.get("spid");
	data = service.getGeneSearchPlotData(gene,spid);
	
	return JsonResponse({"data": data});


def queryClstrType(request):
	data = service.queryClstrType();
	return JsonResponse({"data": data}); 


def deleteMapById(request):
	
	mapid = request.POST.get("mapid");
	pwd = request.POST.get("adminpwd");
	result = service.deleteMapById(mapid,pwd);

	return JsonResponse(result);


def getGeneSearchPlotDataByclstrType(request):

	mapid = request.POST.get("mapid");
	gene = request.POST.get("gene");
	clstrType = request.POST.get("clstrType");

	data = service.getGeneSearchPlotDataBycellType(gene,mapid,clstrType);

	return JsonResponse({"data":data});


def genelistSearch(request):
	sampleid = request.POST.get("sampleid");
	genestr = request.POST.get("genestr");

	gene = genestr.replace(" ","");
	gene = gene.split(",");
	
	gene2=[];
	for i in gene:
		if len(i) > 0:
			gene2.append(i.upper());


	data="";
	geneCount=0;
	gene="";
	if len(gene2) >1:
		data = service.listExistsGenes(sampleid,gene2);
		geneCount = len(data);
		if geneCount == 1:
			gene = data[0];
			data = service.getExprdataByGene(sampleid,data[0]);

		elif geneCount ==2:
			g1 = data[0];
			g2 = data[1];

			data = service.getExprPosCountsByGene(sampleid,g1,g2);
			
	elif len(gene2) == 1:
		gene2=gene2[0];
		lastWord = gene2[-1];
		if lastWord == "*":
			data = service.listExistsGenesRegex(sampleid,gene2[0:-1]);
			geneCount = len(data);
			if geneCount == 1:
				gene = data[0];
				data = service.getExprdataByGene(sampleid,data[0]);
				
		else:
			data = service.getExprdataByGene(sampleid,gene2);
			gene=gene2;
			if data== None:
				geneCount=0;
			else:
				geneCount=1;
	maxval=0;
	if geneCount==1:
		for i in data:
			if data[i] > maxval:
				maxval =data[i];

	return JsonResponse({"res":data,"count":geneCount,"gene":gene,"maxval":maxval});

def getClusterCellids(request):
	sampleid = request.POST.get("sampleid");
	return JsonResponse({"res":sampleid});



def savecluster(request):
	sampleid = request.POST.get("sampleid");
	name = request.POST.get("name");
	ctype = request.POST.get("type");
	comment = request.POST.get("comment");
	cells = request.POST.get("cells");
	cells = cells.split(",");
	cells2 = [];
	for i in cells:
		cells2.append(int(i));

	marks = request.POST.get("marks");
	marks = marks.split(",");
	marks2 = [];
	for i in marks:
		marks2.append( i );


	negmarks = request.POST.get("negmarks");
	negmarks = negmarks.split(",");
	negmarks2 = [];
	for i in negmarks:
		negmarks2.append( i );

	data = service.savecluster(sampleid,name,ctype,cells2,comment,marks2,negmarks2);

	return JsonResponse(data);





def queryClstrCellsAndLabelByCid(request):

	cid = request.POST.get("cid");
	data = service.queryClstrCellsAndLabelByCid(cid);


	return JsonResponse(data);



def getSampleLists(request):

	samples = service.getAllSampleInfo();

	return JsonResponse({"result":samples})



def getClusterClassification(request):

	clstrType= request.POST.get("clstrType");

	data = service.getClusterClassification(clstrType);

	return JsonResponse({"clstrTypes":data})


def updatecluster(request):
	target = request.POST.get("target");
	clstrid = request.POST.get("clstrid");

	if target == "POS":
		x = request.POST.get("x");
		y = request.POST.get("y");
		
		res = service.updateClusterPostition(clstrid,x,y);
	elif target =="NAME":
		newname = request.POST.get("name");
		res = service.updateClusterName(clstrid,newname);
	elif target =="prerender":
		val = request.POST.get("val");
		res = service.updateClusterIsPreRender(clstrid,val);

	elif target =="MARKS":
		val = request.POST.get("marks");
		val = val.split(",")
		res = service.updateClusterMarks(clstrid,val);

	elif target =="NEGMARKS":
		val = request.POST.get("marks");
		val = val.split(",")
		res = service.updateClusterNegMarks(clstrid,val);

	elif target =="BOTHMARKS":
		val = request.POST.get("marks");
		negmarks =request.POST.get("negmarks");
		val = val.split(",")
		negmarks = negmarks.split(",")
		res0= service.updateClusterMarks(clstrid,negmarks);
		res = service.updateClusterNegMarks(clstrid,val);

	elif target =="COLOR":
		val = request.POST.get("val");
		val = val.strip();
		res = service.updateClusterColor(clstrid,val);


	return JsonResponse({"res":res});


def deleteCluster(request):
	clstrid = request.POST.get("clstrid");
	res = service.deleteCluster(clstrid);

	return JsonResponse({"res":res});

def contrast(request):
	cells = request.POST.get("cells");
	target = request.POST.get("target");
	sampleid = request.POST.get("sampleid");

	cells = cells.split(",");

	if target=="ALL":
		#data = service.contrastwithrest(sampleid,cells);
		data = service.doContrast(sampleid,cells,"","contrastwithrest");
	else:
		clstrid = target
		data = service.doContrast(sampleid,cells,clstrid,"contrastCellsVsClstr");
		
		#data = service.contrast()


	return JsonResponse({"res":data});

def getContrastResult(request):
	resultid = request.POST.get("resultid");

	res = service.getContrastResult(resultid);

	return JsonResponse(res);


def contrast2(request):
	sampleid = request.POST.get("sampleid");
	clstr= request.POST.get("clstr");
	target = request.POST.get("target");
	
	if target=="ALL":
		cells = service.getClusterCellsById(clstr);
		data = service.doContrast(sampleid,cells,"","contrastwithrest");
	else:
		cells = service.getClusterCellsById(clstr);
		clstrid = target
		data = service.doContrast(sampleid,cells,clstrid,"contrastCellsVsClstr");

	return JsonResponse({"res":data});


def contrastGeneSearch(request):
	sampleid = request.POST.get("sampleid");
	data1 = request.POST.get("data1");
	data2 = request.POST.get("data2");
	gene =request.POST.get("gene");
	dttype = request.POST.get("dttype");

	if dttype =='cid':
		name1 = service.getClusterNameById(data1);
		data1 = service.getClusterCellsById(data1);
		
	else:
		data1=service.strarrayToIntarray(data1);
		name1 ='Selected Cells'


	if data2 =="ALL":
		
		data2 = service.getClusterRestCells(sampleid,data1);
		name2= "Others"

	else:
		name2 = service.getClusterNameById(data2);
		data2 = service.getClusterCellsById(data2);


	plotdata,expr,maxval = service.contrastGeneSearch(gene,data1,data2,sampleid,name1,name2);

	return JsonResponse({"expr":expr,"plot":plotdata,"maxval":maxval});




def getAllClusterStudies(request):

	data = service.getAllClusterStudies();

	return JsonResponse({"data":data});


def getAllTissueByStudies(request):
	study = request.POST.get("study");
	data = service.getAllTissueByStudies(study);

	return JsonResponse({"data":data});


def getAllClusterTypesByStudyAndTissues(request):
	study = request.POST.get("study");
	tissue = request.POST.get("tissue");
	tissue = tissue.split("//,")
	data = service.getAllClusterTypesByStudyAndTissues(study,tissue);

	return JsonResponse({"data":data});



def queryComparePlotData(request):

	study = request.POST.get("study");
	tissues = request.POST.get("tissues");
	tissues = tissues.split("//,")
	gene = request.POST.get("gene");

	cluster = request.POST.get("cluster");
	clusterType = request.POST.get("clusterType");


	data = service.queryComparePlotData(study,tissues,gene,cluster,clusterType);


	return JsonResponse(  data );


def getGeneMarkers(request):
	data = service.getGeneMarkers();
	return JsonResponse(data)

def uploadGeneMarkers(request):
	genestr = request.POST.get("genestr");

	genes = genestr.replace(" ","").upper();
	genes = genes.split(",");

	name = request.POST.get("name");

	data = service.uploadGeneMarkers(name,genes);

	return JsonResponse(data);



def deleteGeneMarkers(request):
	pwd = request.POST.get("adminpwd");
	name = request.POST.get("name");

	res = service.deleteGeneMarkers(name,pwd);

	return JsonResponse(res)


def genelistHeatmap(request):
	mapid = request.POST.get("mapid");
	genestr = request.POST.get("genestr");

	gene = genestr.replace(" ","").upper();
	gene = gene.split(",");



	barcodes = request.POST.get("selectnodes").replace(" ","");
	if barcodes =="":
		barcodes=[]
	else:
		barcodes=barcodes.split(",");
	data=[];
	if len(gene)==1:
		lastWord = gene[0][-1];
		if lastWord == "*":
			gene=gene[0];
			data = service.listExistsGenesRegex(mapid,gene[0:-1]); 
		else:
			data = service.listExistsGenes(mapid,gene); 


	elif len(gene) >1:
		data = service.listExistsGenes(mapid,gene);

	if len(data) >0:
		data = service.getExprByGenes(mapid,data,barcodes,meanstd=True);


	#print(data)
	return JsonResponse({"res":data})



def getCellsByStudyAndTissueAndclstrtypeAndClstr(request,study,tissue,clstrType,clstr):

	data = service.getCellsByStudyAndTissueAndclstrtypeAndClstr(study,tissue,clstrType,clstr);


	return JsonResponse(data);



def getClstrNameByclstrType(request):

	clstrType = request.POST.get("clstrType");
	mapid = request.POST.get("mapid");

	data =  service.getClstrNameByclstrType(mapid,clstrType);

	return JsonResponse({"data":data})




#api

def getMarkGenesByMapidAndClstrType(request):
	mapid = request.POST.get("mapid");
	clstrType = request.POST.get("clstrType");

	result = service.getMarkGenesByMapidAndClusterType(mapid,clstrType);
	return JsonResponse(result);

def getMetaData(request):
	mapid = request.POST.get("mapid");
	result = service.getMapInfoBySampleId(mapid)
	return JsonResponse(result)



def getClstrsByMapidAndClstrType(request):
	mapid = request.POST.get("mapid");
	clstrType = request.POST.get("clstrType");
	result = service.getClstrsByMapidAndClstrType(mapid,clstrType)
	return JsonResponse(result)


def getNormalizedGeneExpr(request):
	mapid = request.POST.get("mapid");
	clstrType = request.POST.get("clstrType");
	clstrName = request.POST.get("clstrName");
	genes = request.POST.get("genes");
	genes = genes.split(",");

	result = service.getNormalizedGeneExpr(mapid=mapid,clstrType=clstrType,clstrName=clstrName,genes=genes);

	return  JsonResponse(result)


def getAllNormalizedGeneExpr(request):
	mapid = request.POST.get("mapid");
	clstrType = request.POST.get("clstrType");
	clstrName = request.POST.get("clstrName");
	result = service.getNormalizedGeneExpr(mapid=mapid,clstrType=clstrType,clstrName=clstrName,genes="all");

	return JsonResponse(result)

def getMaps(request):
	query = dict(request.POST);
	query2=dict();
	for i in query:
		query2[i]=query[i][0];

	data=service.getMaps(query2);

	return JsonResponse(data)


def getNormalizedGeneExprByTwoClstrs(request):
	mapid = request.POST.get("mapid");
	clstrType1 = request.POST.get("clstrType1");
	clstrName1 = request.POST.get("clstrName1");
	clstrType2 = request.POST.get("clstrType2");
	clstrName2 = request.POST.get("clstrName2");
	zsfilter = request.POST.get("zscoreFilter");
	log2fc = request.POST.get("log2fc");

	data = service.getNormalizedGeneExprByTwoClstrs(mapid,clstrType1,clstrName1,clstrType2,clstrName2,zsfilter,log2fc);

	return JsonResponse(data)
"""
import csv;
from django.http import StreamingHttpResponse


class Echo:
	def write(self, value):
		return value


def testCSV(request):
	rows=[["a",'b','c'],[1,2,3],['x','y',"z"]];
	pseudo_buffer = Echo()
	writer = csv.writer(pseudo_buffer)
	response = StreamingHttpResponse((writer.writerow(row) for row in rows),content_type="text/csv")
	response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
	return response

"""