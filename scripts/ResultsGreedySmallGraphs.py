from networkit import *
from networkit.dynamic import *
from networkit.centrality import *
import operator
import pandas as pd
import os

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



def computeRanking(x, bc, G):
    n = G.numberOfNodes()
    ranking = 0
    for v in range(n):
        if bc.score(v) > bc.score(x):
            ranking = ranking + 1
    return ranking

if __name__ == "__main__":
    setNumberOfThreads(1)
    directed = True
    k = 10


    path = "../dataset/graphs_dir_opt/"
    graphs = []

    for root, dirs, files in os.walk(path):
        for f in files:
            if not f.endswith("target") and not f.startswith("."):
                graphs.append(f)


    nFiles = len(graphs)
    for g in graphs:
        graph_name = path + g
        nodes_name = graph_name + ".target"
        file_nodes = open(nodes_name, "r+")
        nodes = []
        for line in file_nodes:
            nodes.append(int(line.strip()))

        print("Number of targets: ", len(nodes))
        scoresPerNode = {}
        for x in nodes:
            print("Node", x, ":")
            times = []
            t = stopwatch.Timer()
            G = readGraph(graph_name, Format.EdgeList, firstNode=0, continuous=True, separator=' ', directed=directed)
            n = G.numberOfNodes()
            bc = centrality.DynBetweennessOneNode(G, x)
            bc.run()
            bcstatic = Betweenness(G)
            bcstatic.run()

            currentbc = 0
            scores = {}
            oldScores = [0] * n
            for i in range(k):
                maxnode = 0
                currentbc = bc.getbcx()
                scores[i] = currentbc
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
                bcstatic = Betweenness(G)
                bcstatic.run()
                event = GraphEvent(GraphEvent.EDGE_ADDITION, maxnode, x, 1);
                bc.update(event)
                timeSoFar = t.stop()
                times.append(timeSoFar)
                t = stopwatch.Timer()
            for i in range(1, k):
                times[i] = times[i-1] + times[i]
            scores[k] = bc.getbcx()
            scoresPerNode[x] = scores
        title = "Node"
        for i in range(k+1):
            title += "\tk = "+str(i)
        output = open("resultsSmallGreedy/" + g + "_results.txt", "w+")
        output.write(title+"\n")
        for x in nodes:
            line = str(x)
            for i in range(k+1):
                line += "\t"+'{0:.1f}'.format(scoresPerNode[x][i])
            output.write(line+"\n")
        output.close()
