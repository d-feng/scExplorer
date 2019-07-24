from django.urls import path,re_path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path("plots",views.compareplot,name='compareplot'),
	#path("administration",views.administration,name='administration'),


	path("getGeneMarkers",views.getGeneMarkers,name='getGeneMarkers'),
	path("uploadGeneMarkers",views.uploadGeneMarkers,name='uploadGeneMarkers'),
	path("deleteGeneMarkers",views.deleteGeneMarkers,name='deleteGeneMarkers'),

	path("neuralNetwork",views.neuralNetwork,name='neuralNetwork'),
	path("genelistHeatmap",views.genelistHeatmap),
	path("getMapDataBySampleId",views.getMapDataBySampleId,name='getMapDataBySampleId'),
	path("getMapDataByMapId",views.getMapDataByMapId,name='getMapDataByMapId'),
	path("getClstrsByTypeAndMapid",views.getClstrsByTypeAndMapid,name="getClstrsByTypeAndMapid"),
	path("getClstrsByTypeAndMapid2",views.getClstrsByTypeAndMapid2,name="getClstrsByTypeAndMapid2"),
	path("genelistSearch",views.genelistSearch,name='genelistSearch'),
	path("getClusterCellids",views.getClusterCellids,name='getClusterCellids'),
	path("savecluster",views.savecluster,name="savecluster"),
	path("queryClstrCellsAndLabelByCid",views.queryClstrCellsAndLabelByCid,name="queryClstrCellsAndLabelByCid"),
	path("getSampleLists",views.getSampleLists,name="getSampleLists"),
	path("getClusterClassification",views.getClusterClassification,name="getClusterClassification"),
	path("updatecluster",views.updatecluster,name="updatecluster"),
	path("deleteCluster",views.deleteCluster,name="deleteCluster"),
	path("deleteMapById",views.deleteMapById,name="deleteMapById"),
	path("updateMap",views.updateMap,name="updateMap"),
	path("contrast",views.contrast,name="contrast"),
	path("contrast2",views.contrast2,name="contrast2"),
	path("getGeneSearchPlotData",views.getGeneSearchPlotData,name="getGeneSearchPlotData"),
	path("getGeneSearchPlotDataByclstrType",views.getGeneSearchPlotDataByclstrType,name="getGeneSearchPlotDataByclstrType"),

	path("contrastGeneSearch",views.contrastGeneSearch,name='contrastGeneSearch'),
	path("queryClstrType",views.queryClstrType,name='queryClstrType'),

	path("getClstrNameByclstrType",views.getClstrNameByclstrType,name="getClstrNameByclstrType"),

	path("getAllClusterStudies",views.getAllClusterStudies,name='getAllClusterStudies'),
	path("getAllTissueByStudies",views.getAllTissueByStudies,name='getAllTissueByStudies'),
	path("getContrastResult",views.getContrastResult,name='getContrastResult'),

	path("getAllClusterTypesByStudyAndTissues",views.getAllClusterTypesByStudyAndTissues,name='getAllClusterTypesByStudyAndTissues'),

	path("queryComparePlotData",views.queryComparePlotData,name='queryComparePlotData'),
	path("querybarcodes",views.querybarcodes,name='querybarcodes'),
	path("dataTable/<slug:diseaseCategory>/",views.renderdatatable,name='renderdatatable'),
	path("getMapInfoByDiseaseCategory",views.getMapInfoByDiseaseCategory,name="getMapInfoByDiseaseCategory"),
	path("getNNmodelNames",views.getNNmodelNames,name="getNNmodelNames"),
	path("predictnnresult",views.predictnnresult,name="predictnnresult"),
	path("savennresult",views.savennresult,name="savennresult"),
	#path("map/<slug:pk>",views.rendermap, name='rendermap')
	#re_path(r'^map/(\w+)/$', views.rendermap, name='rendermap'),
	path("map/<slug:mapid>/",views.rendermap, name='rendermap'),




	#path("getAllCellExpr")
	#url(r'^samplesplot/getplotdata/([ _\w]+)/([ _\w]+)/([, _\w]+)/([, _\w]+)/$',views.getplotdata),
	re_path(r"^getCellsByStudyAndTissueAndclstrtypeAndClstr/([, _\w]+)/([, _\w]+)/([, _\w]+)/([, _\w]+)/$",views.getCellsByStudyAndTissueAndclstrtypeAndClstr,name='getCellsByStudyAndTissueAndclstrtypeAndClstr'),

	#api
	path("api/getMarkGenesByMapidAndClstrType",views.getMarkGenesByMapidAndClstrType),
	path("api/getMetaData",views.getMetaData),
	path("api/getClstrsByMapidAndClstrType",views.getClstrsByMapidAndClstrType),
	path("api/getNormalizedGeneExpr",views.getNormalizedGeneExpr),
	path("api/getAllNormalizedGeneExpr",views.getAllNormalizedGeneExpr),
	path("api/getMaps",views.getMaps),
	path("api/getNormalizedGeneExprByTwoClstrs",views.getNormalizedGeneExprByTwoClstrs),





]
