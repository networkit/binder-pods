from networkit import *
from networkit.dynamic import *
from networkit.centrality import *
import operator
import pandas as pd
import sys

import random

def extractLargestComponent(G):
    """
    Extract the subgraph of the largest connected component.

    Parameters
    ----------
    G : Graph
        Input graph.
    Returns
    -------
    Graph
        Subgraph of largest component, preserving node ids of orignal graph.
    """

    cc = properties.ConnectedComponents(G)
    cc.run()
    cSizes = cc.getComponentSizes()
    (largestCompo, size) = max(cSizes.items(), key=operator.itemgetter(1))
    compoNodes = [v for v in G.nodes() if cc.componentOfNode(v) is largestCompo]
    C = graph.Subgraph().fromNodes(G, compoNodes)
    return C

def readGraphUnweighted(file, directed_graph):
	print("Opening file")
	f = open(file, "r")
	print("File opened")
	n = 0
	minNode = 0
	i = 0
	#first scan to find out the number of nodes
	for line in f:
		fields = line.strip().split()
		if fields[0].startswith("%") or fields[0].startswith("#"):
			continue
		(u, v) = (int(fields[0]), int(fields[1]))
		if i == 0:
			minNode = u
		if u > n:
			n = u
		if v > n:
			n = v
		if v < minNode:
			minNode = v
		if u < minNode:
			minNode = u
		i = i + 1
	f.seek(0,0)
	n = n + 1
	print("number of nodes: "+str(n))
	print("i : ",i)
	print("min node: ", minNode)
	IDs=[];
	for k in range(n):
		IDs.append(False)
	for line in f:
		fields = line.strip().split()
		if fields[0].startswith("%") or fields[0].startswith("#"):
			continue
		(u, v) = (int(fields[0]), int(fields[1]))
		IDs[u] = True
		IDs[v] = True
		#print(u,v,IDs[u],IDs[v])
	isolatedSoFar = []
	counter = 0
	for k in range(n):
		if (k >= minNode and IDs[k] == False):
			counter = counter + 1
			isolatedSoFar.append(counter)
		else:
			isolatedSoFar.append(counter)
	print("Counter: ", counter, ", n = ", n)
	# we create a (unweighted) graph with the connections and a weighted graph with the timestamps
	if not directed_graph:
		G = Graph(n - counter - minNode)
	else:
		G = Graph(n - counter - minNode, False, True)
	f.seek(0,0)
	for line in f:
		fields = line.strip().split()
		if fields[0].startswith("%") or fields[0].startswith("#"):
			continue
		(u, v) = (int(fields[0]), int(fields[1]))
		u = u - minNode - isolatedSoFar[u]
		v = v - minNode - isolatedSoFar[v]
		if (u < 0 or v < 0):
			print("u = ", u, ", v = ", v, ", isolatedSoFar[u] = ", isolatedSoFar[u], ", isolatedSoFar[v] = ", isolatedSoFar[v], ", minode = ", minNode)
		if (u == v or G.hasEdge(u,v)):
			continue
		if G.hasEdge(v,u) and not directed_graph:
			continue
		G.addEdge(u, v)
	return G


if __name__ == "__main__":
    setNumberOfThreads(1)
    if len(sys.argv) > 1:
        directed = sys.argv[1]
    else:
        # by default, we set it to false
        directed = True
    nIter = 10

    path = "../dataset/undirected/"
    if directed:
        path = "../dataset/directed/"

    graphs = ["Mus_musculus.txt.graph","HC-BIOGRID.txt.graph","Caenorhabditis_elegans.txt.graph","ca-GrQc.txt.graph","advogato.txt.graph","hprd_pp.txt.graph",
    "ca-HepTh.txt.graph","Drosophila_melanogaster.txt.graph","oregon1_010526.txt.graph","oregon2_010526.txt.graph","Homo_sapiens.txt.graph","GoogleNw.txt.graph",
    "CA-CondMat.txt"]

    if directed:
        graphs = ["out.subelj_jung-j_jung-j.graph", "wiki-Vote.txt.graph", "out.elec.graph", "freeassoc.txt.graph",
        "out.dblp-cite.graph", "out.subelj_cora_cora.graph", "out.ego-twitter.graph",  "out.ego-gplus.graph",
        "out.munmun_digg_reply.graph", "out.linux.graph"]


    for g in graphs:
        graph_name = path + g
        G = readGraphUnweighted(graph_name, directed)
        print("Graph: ", g, ", Nodes: ", G.numberOfNodes())
        dynBc = DynBetweenness(G)
        dynBc.run()
        dynBcOne = DynBetweennessOneNode(G, True)
        dynBcOne.run()
        sigmaOld = {}
        distOld = {}
        for u in G.iterNodes():
            sigmaOld[u] = {}
            distOld[u] = {}
            for v in G.iterNodes():
                sigmaOld[u][v] = dynBcOne.getSigma(u, v);
                distOld[u][v] = dynBcOne.getDistance(u, v);
        timeDyn = []
        timeOne = []
        timeStatic = []
        affected = []

        for i in range(nIter):
            u = graphtools.randomNode(G)
            v = graphtools.randomNode(G)
            while (G.hasEdge(u, v)):
                u = graphtools.randomNode(G)
                v = graphtools.randomNode(G)
            G.addEdge(u, v)
            t = stopwatch.Timer()
            dynBc.update(GraphEvent(GraphEvent.EDGE_ADDITION, u, v, 1.0))
            secs = t.stop()
            t = stopwatch.Timer()
            dynBcOne.update(GraphEvent(GraphEvent.EDGE_ADDITION, u, v, 1.0))
            secs2 = t.stop()
            bc = Betweenness(G)
            t = stopwatch.Timer()
            bc.run()
            secs3 = t.stop()
            timeDyn.append(secs)
            timeOne.append(secs2)
            timeStatic.append(secs3)
            # now we compute the number of affected nodes
            affectedPairs = 0
            for u in G.iterNodes():
                for v in G.iterNodes():
                    if (not dynBcOne.getSigma(u, v) == sigmaOld[u][v]) or (not dynBcOne.getDistance(u, v) == distOld[u][v]):
                        affectedPairs += 1
                    sigmaOld[u][v] = dynBcOne.getSigma(u, v)
                    distOld[u][v] = dynBcOne.getDistance(u, v)
            affected.append(affectedPairs)
            print("Affected pairs: ", affectedPairs, ". Time one node: ", secs2, ", time dyn: ", secs, ", time static: ", secs3)
        a = pd.Series(timeStatic)
        b = pd.Series(timeDyn)
        c = pd.Series(timeOne)
        d = pd.Series(affected)
        df1 = pd.DataFrame({"Static bc": a, "Dyn" : b, "Dyn One Node" : c, "Affected" : d})
        if directed:
            df1.to_csv("resultsCompDirected/results_"+g+".csv")
        else:
            df1.to_csv("resultsCompUndirected/results_"+g+".csv")
