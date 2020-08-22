import os, sys, csv,json,datetime,time,math,scipy.stats,collections,re;
import copy;
from sklearn import preprocessing;
import numpy as np;
import pandas as pd;
import subprocess, gzip;
from subprocess import Popen, PIPE,STDOUT
import os.path;
import pymongo;
from bson.objectid import ObjectId;
from pymongo import MongoClient;
import scanpy;
# import scanpy.api as sc
import scanpy as sc
import scanpy.external as sce
sc.settings.verbosity = 3  # verbosity: errors (0), warnings (1), info (2), hints (3)
sc.settings.set_figure_params(dpi=80)
from pymongo import IndexModel, ASCENDING, DESCENDING

import os.path;
import urllib.request

class ProcessPipline:
    def __init__(self):
        self.data="";
        self.CountsFile="";
        self.samples="";
        
    def runCellRange(self,workspace,fastq_path,samples,expect_cells,transcriptpath,run_name):
        run_name=run_name.replace(" ","_");
        resultfile ="";
        pcheck = subprocess.Popen("cellranger", shell=True, stdin=PIPE, stdout=PIPE,stderr=STDOUT)
        output =pcheck.stdout.read();
        output=str(output)
        if "command not found" in output:
            print("Please install cellranger 3.0");
            print("Tutorial: https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/installation")
            print("If you have counts data. please skip this step.")
            return ""
        if not os.path.isdir(workspace):
            print("workspace is not a dir");
            return;


        if len(samples) ==0 :
            print("Please input samples");
            return;
        if not os.path.isdir(fastq_path):
            print("fastq path is not a dir");
            return;
        ResPath = workspace+"/"+run_name;
        if os.path.isdir(ResPath):
            print("run name is already in workspace");
            return;
        else:
            os.mkdir(ResPath);
        
        self.samples=samples;
        shstr = "";
        shstr +="wd=\"" +ResPath+  "\"\n"
        shstr +="cd ${wd}\n";
        
        for i in samples:
            jobstr="cellranger count ";
            jobstr+="--id "+i+" ";
            jobstr+="--fastqs "+fastq_path+" "
            jobstr+="--transcriptome "+transcriptpath+" ";
            jobstr+="--expect-cells "+ str(expect_cells)+" "
            jobstr+="--sample=\""+i+"\"";

            shstr+=jobstr+"\n";


        if len(samples) >1:
            csvstr=["library_id,molecule_h5"]
            for i in samples:
                temp=i+","+ResPath+"/"+i+"/outs/molecule_info.h5"
                csvstr.append(temp)

            csvstr="\n".join(csvstr);
            
            csvf=ResPath+"/"+run_name+".csv"
            with open(csvf,"w") as f:
                f.write(csvstr)
                
            shstr+="cellranger aggr "
            shstr+="--id aggr " 
            #--csv=test.csv --normalize=mapped
            shstr+= "--csv="+csvf+" --normalize=mapped"

            resultfile = "aggr";

        else:
            resultfile =samples[0]
            
        shfile=ResPath+"/"+run_name+".sh"
        with open(shfile,"w") as f:
            f.write(shstr)
            
        command = "bash "+shfile;
        
        print("it will take a few hours . please wait.....")
        prun = subprocess.Popen(command, shell=True, stdin=PIPE, stdout=PIPE,stderr=STDOUT)
        output =prun.stdout.read();
        print(output)
        print("---------------------------------------------------------------------------------");
        print("finish");
        resultpath = ResPath+"/"+resultfile;
        print("results path: "+resultpath);
        self.CountsFile=resultpath+"/outs/filtered_feature_bc_matrix/";
        
        print("counts file path: "+self.CountsFile);
        
        return self.CountsFile;
    
    def downloadTestData(self):
    
        datafolder="pbmc3k";
        downloadFile="bmc3k.tar.gz";
        dataname=datafolder+"/"+downloadFile;
        if os.path.exists(datafolder):
            pass;
        else:
            os.mkdir(datafolder);

        if os.path.exists(dataname):
            pass;
        else:
            urllib.request.urlretrieve("http://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz",dataname);
            print("download success");

        command = subprocess.Popen("cd "+datafolder+"\ntar -zxvf "+downloadFile, shell=True, stdin=PIPE, stdout=PIPE,stderr=STDOUT)
        output =command.stdout.read();
        countsFile=datafolder+"/filtered_gene_bc_matrices/hg19"
        self.CountsFile = countsFile;
        print(countsFile)
        return countsFile;


    def readData(self,countsFile=""):
        if countsFile=="":
            countsFile = self.CountsFile;
            
        if countsFile=="":
            print("please input counts file path");
            return ""
        
        self.CountsFile=countsFile;
        
        datapath = self.CountsFile;
        if os.path.isdir(datapath):
            files = os.listdir(datapath)
            for i in files:
                if i.endswith(".gz"):
                    print(i)
                    target = datapath+"/*.gz";
                    print(target)
                    command = subprocess.Popen("gunzip "+target, shell=True, stdin=PIPE, stdout=PIPE,stderr=STDOUT)
                    output =command.stdout.read();
                    break;
                    
            files=os.listdir(datapath);
            for i in files:
                if i =="features.tsv":
                    os.rename(datapath+"/features.tsv",datapath+"/genes.tsv");
                    break;
            files = list(os.listdir(datapath));
            if ('barcodes.tsv' in files) and ('barcodes.tsv' in files) and ("genes.tsv" in files):
                adata = sc.read_10x_mtx(datapath, var_names='gene_symbols');
                self.data=adata;
                self.preprocess();
            else:
                print("input data is not correct")
                return ""
            
        elif os.path.isfile(datapath):
            if datapath.endswith(".h5ad"):
                adata=sc.read_h5ad(datapath);
            else:
                adata = sc.read_csv(datapath)
                adata = adata.T;
            self.data=adata;
            #self.preprocess();
        else:
            print("file or dir not exists")
            return ""
        
    
    def preprocess(self):
        self.data.var_names_make_unique()
        sc.pp.filter_cells(self.data, min_genes=0);
        sc.pp.filter_genes(self.data, min_cells=1);
        mito_genes = [name for name in self.data.var_names if name.startswith('MT-')]
        self.data.obs['percent_mito'] = np.sum(self.data[:, mito_genes].X, axis=1)  / np.sum(self.data.X, axis=1)
        self.data.obs['n_counts'] = self.data.X.sum(axis=1);
        
        
    def QC(self,max_n_genes="" ,min_n_genes="",min_n_cells="",max_percent_mito=""):
        if min_n_genes!="":
            print("filter cells");
            sc.pp.filter_cells(self.data, min_genes=min_n_genes);
        if min_n_cells != "":
            print("filter genes");
            sc.pp.filter_genes(self.data, min_n_cells)
        if max_n_genes !="":
            print("filter n_genes < "+str(max_n_genes))
            self.data = self.data[self.data.obs['n_genes'] < max_n_genes , :]
        if max_percent_mito != "":
            print("filter percent_mito < "+str(max_percent_mito))
            self.data = self.data[self.data.obs['percent_mito'] < max_percent_mito, :];
        
    def scanpyQuickProcess(self):
        adata = self.data.copy();
        sc.pp.normalize_per_cell(adata, counts_per_cell_after=1e4)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
        adata = adata[:, adata.var['highly_variable']]
        sc.pp.regress_out(adata, ['n_counts', 'percent_mito'])
        sc.pp.scale(adata, max_value=10)
        sc.tl.pca(adata, svd_solver='arpack')
        
        vr=list(adata.uns["pca"]["variance_ratio"]);
        vr = [round(x,5) for x in vr];
        dup=0;
        pre=""
        npcs=0;
        for i in range(len(vr)):
            if vr[i]==pre:
                dup+=1;
                if dup>=2:
                    npcs=i-2;
                    break;
            else:
                pre=vr[i];
                dup=0;

        npcs =40 if npcs>40 else npcs;
        npcs =4 if npcs<4 else npcs;
            
        print("n pcs: "+str(npcs));
        self.npcs=npcs;
        
        vr=list(adata.uns["pca"]["variance_ratio"]);
        vr = [round(x,4) for x in vr];
        dup=0;
        pre=""
        tsne_npcs=0;
        for i in range(len(vr)):
            if vr[i]==pre:
                dup+=1;
                if dup>=3:
                    tsne_npcs=i-1;
                    break;
            else:
                pre=vr[i];
                dup=0;

        tsne_npcs =30 if tsne_npcs>30 else tsne_npcs;
        tsne_npcs =4 if tsne_npcs<4 else tsne_npcs;
            
        print("tsne n pcs: "+str(tsne_npcs));
        self.tsne_npcs=tsne_npcs;
        
        sc.pp.neighbors(adata, n_neighbors=10, n_pcs=npcs);
        sc.settings.set_figure_params(dpi=80);
        #sc.tl.louvain(adata)
        sc.tl.leiden(adata)
        sc.tl.umap(adata)
        sc.tl.phate(adata)
        sc.tl.tsne(adata,n_pcs=tsne_npcs);
        self.saveAnnotation(adata=adata);
        print("done. ready to save to database")
        

        
    def showTsne(self,color='leiden'):
        sc.settings.set_figure_params(dpi=80)
        sc.pl.tsne(self.data, color=color)

    def showUmap(self,color='leiden'):
        sc.settings.set_figure_params(dpi=80)
        sc.pl.umap(self.data, color=color);
    
    def showPhate(self,color='leiden'):
        sc.settings.set_figure_params(dpi=80)
        sc.pl.phate(self.data, color=color);
    
    
    """
    def creatNormalData(self):
        sc.pp.normalize_per_cell(self.data, counts_per_cell_after=1e4)
        p.ndata=self.data.to_df();
    """
    
    def saveAnnotation(self,adata=None,mapinfo=None):
        if adata != None:
            for i in adata.obs:
                self.data.obs[i]=adata.obs[i]

            if hasattr(adata,"uns"):
                self.data.uns = adata.uns;

            if hasattr(adata,"obsm"):
                self.data.obsm = adata.obsm;
        if mapinfo != None:
            
            if "mapName" in mapinfo:
                mapinfo["name"]=mapinfo["mapName"];
                del mapinfo["mapName"];
                
            if "mapname" in mapinfo:
                mapinfo["name"]=mapinfo["mapname"];
                del mapinfo["mapname"];
            
            if "name" not in mapinfo:
                print("name not in mapinfo");
                return;          
            
            if "tissue" not in mapinfo:
                mapinfo["tissue"]="";
                
            if "sample" not in mapinfo:
                mapinfo["sample"]="";
                
            if "study" not in mapinfo:
                mapinfo["study"]="";
                
            
            
            if "subjectid" not in mapinfo:
                mapinfo["subjectid"]="";
            if "source" not in mapinfo:
                mapinfo["source"]="";
                
            if "disease" not in mapinfo:
                mapinfo["disease"]="";
                
            if "comment" not in mapinfo:
                mapinfo["comment"]="";
            
            self.data.uns["mapinfo"]=mapinfo;
        
            
           
    
    
    def insertToDB(self,dbname='scDB',dbport=27017,dbhost="localhost",
                   rawDataIsNormalized=False,
                   saveRawCounts=False,
                  ):
        
        try:
            mapinfo = self.data.uns["mapinfo"];
            
        except:
            print("no mapinfo in the data");
            return;
        
        if "name" not in mapinfo:
            print("name cannot empty");
            return;
        
        if "study" not in mapinfo:
            print("study cannot empty");
            return;
        
        if "subjectid" not in mapinfo:
            print("subjectid cannot empty");
            return;
        
        if "disease" not in mapinfo:
            print("disease cannot empty");
            return;
        
        if "source" not in mapinfo:
            print("source cannot empty");
            return;
        
        if "comment" not in mapinfo:
            print("comment cannot empty");
            return;
        
        
        
        client = MongoClient(dbhost,dbport)
        db = client[dbname];
        
        coor=None;
        
        if not hasattr(self.data,"obsm"):
            print("no coordinate")
            
            return;
        
        
        if "mapType" not in mapinfo:
            print("mapType cannot empty");
            return;
        
        
        mapType=mapinfo["mapType"];
            
        if mapType=='tsne':
            coor = self.data.obsm["X_tsne"];
        elif mapType == "umap":
            coor = self.data.obsm["X_umap"];
        elif mapType == "phate":
            coor = self.data.obsm["X_phate"];
        else:
            print("no matched plot");
            return;
        
        cells =self.data.obs.index
        
        if rawDataIsNormalized == False:
            adata=self.data.copy();
            sc.pp.normalize_per_cell(adata, counts_per_cell_after=1e4);
        else:
            adata=self.data;
        
        obslist=[];
        for i in adata.obs:
            if i != "n_genes" and i !="percent_mito" and i != "n_counts":
                typelen = len(set(list(adata.obs[i])));
                #print(str(i)+" ");
                if typelen < 50:
                    obslist.append(i)
        
        
        metaDict=dict();
        for i in range(len(cells)):
            temp={}
            for j in obslist:
                j2=str(j).strip();
                if j2 !="nan" and j2 != "" and j2 != "None":
                    try:
                        j2val = adata.obs[j][i];
                        temp[j2]=j2val;
                    except:
                        pass;
            metaDict[i]=temp;
            
        
        coordata=[];
        #mapsamples=dict();
        samplesCluster=dict();
        
        for i in range(len(cells)):
            cell = cells[i];
            tx = str(coor[i][0]);
            ty= str(coor[i][1]);
            
            cell2=cell.split("-");
            if len(cell2)>1:
                cell2=cell2[-1];
                if cell2.isnumeric():
                    if cell2 in samplesCluster:
                        samplesCluster[cell2].append(i);
                    else:
                        samplesCluster[cell2]=[i];
                    
            #mapsamples[cell]=i;
            temp={"_id":cell,"x":round(float(tx),7),"y":round(float(ty),7),"order":i  };
            coordata.append(temp);
            
        if self.samples !="" and len(samplesCluster.keys())==len(self.samples):
            sampleClstrkeys=list(samplesCluster.keys());
            for i in sampleClstrkeys:
                i2=int(i)-1;
                newClstrName=self.samples[i2];
                samplesCluster[newClstrName]=samplesCluster.pop(i);
        
        
        #exprhead=list(self.ndata.columns.values)
        exprhead=list(adata.obs.index)
        genes=list(adata.var.index);
        
        print("start insert to db");

        #init end,start insert
        mapinfo=copy.deepcopy(mapinfo);
        newmap = db.dataInfo.insert(mapinfo);
        newmap = str(newmap);
        exprCollection = "expr_"+newmap;
        for i in range(len(genes)):
            gene=genes[i].strip().upper();
            expr=adata[:,i].X;
            expr=[round(float(x),3) for x in expr]
            if (rawDataIsNormalized == False) and (saveRawCounts == True):
                counts = self.data[:,i].X;
                counts = [int(x) for x in counts];
                db[exprCollection].update({"_id":gene},{"$set":{"normalize":expr,"counts":counts}},upsert=True);
            else:
                db[exprCollection].update({"_id":gene},{"$set":{"normalize":expr}},upsert=True);
                
            if i%3000==0:
                print(str(i));
        
        metaCollection ='meta_'+newmap;
        for i in coordata:
            db[metaCollection].insert(i);
        
        colorlist = ["#EF4036","#907DBA" ,"#38B449","#F7931D","#F8ED31","#484B5A","#55B5E6","#F37E87","#70C38F" , "#3399FF","#0078AE", "#0000FF", "#A6E286", "#00AE3C",'#006400',"#F4C2C2","#FA6E79","#D1001C",'#660000','#FFD831','#FF8C00',"#AA6C39","#966FD6", "#B23CBF","#713E90", "#999999","#D1BEA8",'#54626F','#3B3C36']
        
        clstrdict={};
        for i in metaDict:
            temp = metaDict[i];
            for j in temp:
                clstrtype = j;
                clstrname=temp[j];
            
                if clstrtype not in clstrdict:
                    clstrdict[clstrtype]=dict();
                    
                if clstrname in clstrdict[clstrtype]:
                    clstrdict[clstrtype][clstrname].append(i);
                    
                else:
                    clstrdict[clstrtype][clstrname]=[i];
                    
                    
        metaDict=None;
                    
        for i in clstrdict:
            clstrType = i;
            indx=0
            for j in clstrdict[clstrType]:
                tempcolor = colorlist[indx];
                db.cluster.insert({"mapid":ObjectId(newmap),"clstrType":clstrType,"clstrName":str(j),
                              "cells":clstrdict[clstrType][j],"color":tempcolor,
                               "x":"","y":"","label":False,"prerender":True
                              })
                
                indx +=1;
                if indx == len(colorlist):
                    indx=0;
        
        print("success")
        print("mapid: "+newmap);
        return newmap

    
    
    
    def read_annotated_csv(self,folderPath="",counts_csv="counts.csv",coords_csv="coords.csv",mapinfo_csv="mapinfo.csv"):
        
        if os.path.isdir(folderPath):
            os.chdir(folderPath)
        
        
        self.data=None;
        
        self.readData(counts_csv);
      
        
        with open(mapinfo_csv) as f:
            csvf = csv.reader(f, delimiter=',');
            csvf = list(csvf);
            head = csvf[0];
            name=0;
            value=1;
            if len(head) ==3:
                name=1;
                value=2;
                
            mapinfo=dict();
            for i in csvf[1:]:
                mapinfo[i[name]]=i[value];
                
        self.saveAnnotation(mapinfo=mapinfo);
        key=""
        if mapinfo["mapType"]=="tsne" or mapinfo["mapType"]=="umap" or mapinfo["mapType"]=="phate":
            key="X_"+mapinfo["mapType"];
                
        else:
            print( "mapType not found"); 
            return ""
        with open(coords_csv) as f:
            csvf = csv.reader(f, delimiter=',');
            clstrdict=dict();
            coordict=dict();
            head=next(csvf);
            cellsOrder=dict();
            
            index=0
            for i in csvf:
                
                cell=i[0];
                cellsOrder[cell]=index;
                x=i[1];
                y=i[2];
                
                coordict[cell]=[x,y];
                
                temp=dict();
                for j in range(3,len(i)):
                    clstrType=head[j];
                    clstrName=i[j];
                    
                    if clstrType in clstrdict:
                        clstrdict[clstrType].append(clstrName)
                    else:
                        clstrdict[clstrType]=[clstrName];
                        
                index+=1;
            
            
            
            coordlist=[];
            
            for i in self.data.obs.index:
                coordlist.append(coordict[i]);
            
            coordict=None;
            head=None;
            
            self.data.obsm[key]=np.array(coordlist);
    
            coordlist=None;
        
            for clstrType in clstrdict:
                temp=[];
                for i in self.data.obs.index:
                    index = cellsOrder[i];
                    
                    value= clstrdict[clstrType][index];
                    #print(value);
                    temp.append(value)
                
                
                self.data.obs[clstrType]=temp;
                
        print("done");
    
    
