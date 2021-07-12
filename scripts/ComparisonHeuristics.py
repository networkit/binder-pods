from networkit import *
from networkit.dynamic import *
from networkit.centrality import *
import operator
import pandas as pd

import random

def computeRanking(x, bc, G):
    n = G.numberOfNodes()
    ranking = 0
    for v in range(n):
        if bc.score(v) > bc.score(x):
            ranking = ranking + 1
    return ranking

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
	print("number of nodes: ", G.numberOfNodes())
	print ("number of edges: ", G.numberOfEdges())
	print("All the edges have been scanned")
	return G


if __name__ == "__main__":
    setNumberOfThreads(1)
    if len(sys.argv) > 1:
        directed = sys.argv[1]
    else:
        # by default, we set it to false
        directed = False
    kMax = 10
    nExperiments = 10

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

    labels = ["Mus-musculus","HC-BIOGRID","Caenor-eleg","ca-GrQc","advogato","hprd-pp",
    "ca-HepTh","dr-melanog","oregon1","oregon2","Homo-sapiens","GoogleNw","CA-CondMat"]

    if directed:
        labels = ["subelj-jung", "wiki-Vote", "elec", "freeassoc", "dblp-cite", "subelj-cora", "ego-twitter", "ego-gplus",
         "munmun-digg", "linux"]

    fileResults = "resultsCompHeuristicsUndirected2.txt"
    if directed:
        fileResults = "resultsCompHeuristicsDirected2.txt"

    f = open(fileResults, "w+")
    f.write("Graph,Nodes,Edges,k,In. Score,In. Rank,Fin. Score Greedy,Fin. Rank Greedy,Fin. Score Degree,Fin. Rank Degree,Fin. Score Betw.,Fin. Rank Betw.,Fin. Score Random,Fin. Rank Random\n")
    nodes = {}
    edges = {}
    init_scores = {}
    init_ranks = {}
    scores_greedy = {}
    ranks_greedy = {}
    scores_bc = {}
    ranks_bc = {}
    scores_deg = {}
    ranks_deg = {}
    scores_rand = {}
    ranks_rand = {}
    for index, g in enumerate(graphs):
        graph_name = path + g
        init_scores[g] = {}
        init_ranks[g] = {}
        scores_greedy[g] = {}
        ranks_greedy[g] = {}
        scores_bc[g] = {}
        ranks_bc[g] = {}
        scores_deg[g] = {}
        ranks_deg[g] = {}
        scores_rand[g] = {}
        ranks_rand[g] = {}
        for sample in range(nExperiments):
            print("graph: ", labels[index], ", sample = ", sample)
            f = open(fileResults, "w+")
            f.write("Graph: "+ labels[index] + ", sample: "+str(int(sample))+"\n")
            G = readGraphUnweighted(graph_name, directed)
            nodes[g] = G.numberOfNodes()
            edges[g] = G.numberOfEdges()
            n = nodes[g]

            scores_greedy[g][sample] = {}
            ranks_greedy[g][sample] = {}
            scores_bc[g][sample] = {}
            ranks_bc[g][sample] = {}
            scores_deg[g][sample] = {}
            ranks_deg[g][sample] = {}
            scores_rand[g][sample] = {}
            ranks_rand[g][sample] = {}

            # sample a random node
            x = graphtools.randomNode(G)

            bc = centrality.DynBetweennessOneNode(G, x)
            bc.run()

            # needed for the ranking
            bcAll = centrality.DynBetweenness(G)
            bcAll.run()

            #initial score and ranking of the node
            init_scores[g][sample] = bc.getbcx()
            init_ranks[g][sample] = computeRanking(x, bcAll, G)

            currentbc = 0
            oldScores = [0] * nodes[g]

            # new we compute scores according to our greedy algorithm
            for k in range(kMax):
                print("k = ", k)
                maxnode = 0
                currentbc = bc.getbcx()
                print("bc = ", currentbc)
                maxbc = 0
                for v in range(n):
                    if not(G.hasEdge(v, x)) and ( not(directed) or (oldScores[v] == 0 or oldScores[v] > maxbc - currentbc)):
                        G.addEdge(v,x)
                        event = GraphEvent(GraphEvent.EDGE_ADDITION, v, x, 1)
                        bc.update(event)
                        score = bc.getbcx()
                        oldScores[v] = score - currentbc
                        if score > maxbc:
                            maxnode = v
                            maxbc = score
                        G.removeEdge(v,x)
                G.addEdge(maxnode, x)
                event = GraphEvent(GraphEvent.EDGE_ADDITION, maxnode, x, 1);
                bc.update(event)
                bcAll.update(event)
                scores_greedy[g][sample][k] = bc.getbcx()
                ranks_greedy[g][sample][k] = computeRanking(x, bcAll, G)

            #now we re-read the graph and compute the scores adding edges to the top-k nodes with highest Betweenness
            G = readGraphUnweighted(graph_name, directed)
            # we need to run betweenness to compute the ranking of all nodes
            bc = DynBetweenness(G)
            bc.run()
            ranking = bc.ranking()

            j = 0
            for k in range(kMax):
                while(G.hasEdge(ranking[j][0], x)):
                    j += 1
                G.addEdge(ranking[j][0], x)
                event = GraphEvent(GraphEvent.EDGE_ADDITION, ranking[j][0], x, 1);
                bc.update(event)
                scores_bc[g][sample][k] = bc.score(x)
                ranks_bc[g][sample][k] = computeRanking(x, bc, G)
                j += 1


            #now we re-read the graph and compute the scores adding edges to the top-k nodes with highest degree
            G = readGraphUnweighted(graph_name, directed)
            # we compute the ranking according to degree
            ranking = [(u, G.degree(u)) for u in G.iterNodes()]
            ranking.sort(key=operator.itemgetter(1),reverse=True)

            bc = DynBetweenness(G)
            bc.run()
            j = 0
            for k in range(kMax):
                while(G.hasEdge(ranking[j][0], x)):
                    j += 1
                G.addEdge(ranking[j][0], x)
                event = GraphEvent(GraphEvent.EDGE_ADDITION, ranking[j][0], x, 1);
                bc.update(event)
                scores_deg[g][sample][k] = bc.score(x)
                ranks_deg[g][sample][k] = computeRanking(x, bc, G)
                j += 1

            #now we re-read the graph and compute the scores for random insertions
            G = readGraphUnweighted(graph_name, directed)
            # we run betweenness of a single node to update ranking quickly
            bc = DynBetweenness(G)
            bc.run()

            for k in range(kMax):
                v = graphtools.randomNode(G)
                while(G.hasEdge(v, x)):
                    v = graphtools.randomNode(G)
                G.addEdge(v, x)
                event = GraphEvent(GraphEvent.EDGE_ADDITION, v, x, 1);
                bc.update(event)
                scores_rand[g][sample][k] = bc.score(x)
                ranks_rand[g][sample][k] = computeRanking(x, bc, G)

            f = open(fileResults, "w+")
            for k in range(kMax):
                f.write(labels[index]+","+str(int(nodes[g]))+","+str(int(edges[g]))+","+str(init_scores[g][sample])+","+str(init_ranks[g][sample])+","+str(scores_greedy[g][sample][k])+","+str(ranks_greedy[g][sample][k])+","+str(scores_deg[g][sample][k])+","+str(ranks_deg[g][sample][k])+","+str(scores_bc[g][sample][k])+","+str(ranks_bc[g][sample][k])+","+str(scores_rand[g][sample][k])+","+str(ranks_rand[g][sample][k])+"\n")
    f.close()
