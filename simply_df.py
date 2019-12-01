#!/usr/bin/python3

def edge_length(edge):
  if edge[0]<edge[1]:
    return edge[1]-edge[0]-1
  return edge[0]-edge[1]+1

def are_overlapping(edge1,edge2):
  return not(edge1[0]<edge1[1]<=edge2[0]<edge2[1]
          or edge1[0]<edge1[1]<edge2[1]<=edge2[0]
          or edge1[1]<=edge1[0]<edge2[0]<edge2[1]
          or edge1[1]<=edge1[0]<edge2[1]<=edge2[0]
          or edge2[0]<edge2[1]<=edge1[0]<edge1[1]
          or edge2[0]<edge2[1]<edge1[1]<=edge1[0]
          or edge2[1]<=edge2[0]<edge1[0]<edge1[1]
          or edge2[1]<=edge2[0]<edge1[1]<=edge1[0])

def edges2print(successors):
  layers = []
  max_length = len(successors)+1
  for length in range(max_length+1):
    for i in range(len(successors)):
      for j in successors[i]:
        edge = [i,j]
        if edge_length(edge)==length and j!=-1:
          i_layer = 0
          ok = False
          while i_layer<len(layers) and not ok:
            ok = True
            i_edge = 0
            while i_edge<len(layers[i_layer]) and ok:
              ok = not are_overlapping(edge,layers[i_layer][i_edge])
              i_edge += 1
            if ok:
              layers[i_layer].append(edge)
            i_layer += 1
          if not ok:
            layers.append([edge])
  return layers

class CFGEdges:
  def __init__(self,successors=None):
    if successors:
      self.successors = successors
    else:
      self.successors = []
    self.reset()
  def __repr__(self):
    return self.toString("")
  def reset(self):
    self.predecessors = None
    self.immediate_dominators = None
    self.dominance_frontier = None
  def toString(self,prepend,contents=None):
    predecessors = self.getPredecessors()
    immediate_dominators = self.getImmediateDominators()
    dominance_frontier = self.getDominanceFrontier()
    if not contents:
      contents = []
      for i in range(len(self.successors)):
        contents.append(str(i))
    string = ""
    layers = edges2print(self.successors)
    for i in range(len(self.successors)):
      prepend_0 = prepend
      prepend_1 = prepend
      prepend_2 = prepend
      prepend_3 = prepend
      horizontal_0 = " "
      horizontal_2 = " "
      for layer in reversed(layers):
        vertical = False
        add_prepend_0 = 2*horizontal_0
        add_prepend_1 = "  "
        add_prepend_2 = 2*horizontal_2
        add_prepend_3 = "  "
        for edge in layer:
          if edge[0]<i and edge[1]>i or edge[1]<=i and edge[0]>=i:
            add_prepend_0 = "│"+horizontal_0
            add_prepend_1 = "│ "
            add_prepend_2 = "│"+horizontal_2
          if edge[0]<=i and edge[1]>i or edge[1]<=i and edge[0]>i:
            add_prepend_3 = "│ "
          if edge[0]==i:
            horizontal_2 = "─"
            if edge[1]>i:
              add_prepend_2 = "┌<"
            else:
              add_prepend_2 = "└<"
          if edge[1]==i:
            horizontal_0 = "─"
            if edge[0]<i:
              add_prepend_0 = "└>"
            else:
              add_prepend_0 = "┌>"
        prepend_0 += add_prepend_0
        prepend_1 += add_prepend_1
        prepend_2 += add_prepend_2
        prepend_3 += add_prepend_3
      prepend_1 += "║ "
      string += prepend_0+"╔═ block {} ══════════ pred>: {}, idom: {}\n".format(
         i,predecessors[i],immediate_dominators[i])
      string += prepend_1+contents[i].replace("\n","\n"+prepend_1)+"\n"
      string += prepend_2+"╚════════════════════ succ<: {}, df: {}\n".format(
        str(self.successors[i]),
        "{}" if dominance_frontier[i]==set() else dominance_frontier[i])
      string += prepend_3+"\n"
    return string
  def getPredecessors(self):
    # compute if needed
    if not self.predecessors:
      n = len(self.successors)
      self.predecessors = []
      for i in range(n):
        self.predecessors.append([])
      for i in range(n):
        for successor in self.successors[i]:
          self.predecessors[successor].append(i)
    return self.predecessors
  def deleteNode(self,index):
    assert index>0, "CFGEdges : should not delete entry point"
    assert len(self.successors[index])<2, "CFGEdges : should not delete node with more than one successor"
    assert len(self.successors[index])>0, "CFGEdges : should not delete an exit node"
    predecessors = self.getPredecessors()
    # shortcut
    for predecessor in predecessors[index]:
      for i in range(len(self.successors[predecessor])):
        if self.successors[predecessor][i]==index:
          self.successors[predecessor][i] = self.successors[index][0]
    # shift indices
    for node in range(0,len(self.successors)):
      for i in range(len(self.successors[node])):
        if self.successors[node][i]>index:
          self.successors[node][i] -= 1
    del self.successors[index]
    # delete previous calculations
    self.reset()
  def insertNode(self,index):
    # shift indices
    for node in range(0,len(self.successors)):
      for i in range(len(self.successors[node])):
        if self.successors[node][i]>=index:
          self.successors[node][i] += 1
    self.successors.insert(index,[])
    self.reset()
  def connectNode(self,index,successors):
    assert 0<=index<len(self.successors), "CFGEdges : try to connect non existing node"
    self.successors[index] = successors[:]
    self.reset()
  def getAllDominators(self):
    successors = self.successors
    predecessors = self.getPredecessors()
    # https://en.wikipedia.org/wiki/Dominator_(graph_theory)
    all_dominators = [{0}]
    n = len(successors)
    for i in range(len(successors)-1):
      all_dominators.append(set(range(0,n)))
    # computes iteratively
    changed = True
    while changed:
      changed = False
      for node in range(0,n):
        # compute the new set of dominators
        new = all_dominators[node]
        for node_predecessor in predecessors[node]:
          new = new.intersection(all_dominators[node_predecessor])
        new = new.union({node})
        if new!=all_dominators[node]:
          changed = True
        all_dominators[node] = new
    return all_dominators
  def getImmediateDominators(self):
    if not self.immediate_dominators:
      self.immediate_dominators = []
      all_dominators = self.getAllDominators()
      for dominators in all_dominators:
        immediate_dominator = [] # may be empty (entry)
        for i_dominator in dominators:
          if len(all_dominators[i_dominator])==len(dominators)-1:
            immediate_dominator.append(i_dominator)
        self.immediate_dominators.append(immediate_dominator)
    return self.immediate_dominators
  def getDominanceFrontier(self):
    if not self.dominance_frontier:
      successors = self.successors
      predecessors = self.getPredecessors()
      immediate_dominators = self.getImmediateDominators()
      # Cf. Wikipedia :
      # https://en.wikipedia.org/wiki/Static_single_assignment_form
      self.dominance_frontier = []
      n = len(successors)
      for i in range(len(successors)):
        self.dominance_frontier.append(set())
      for i in range(len(successors)):
        if len(predecessors[i])>=2:
          for p in predecessors[i]:
            runner = p
            while runner!=immediate_dominators[i][0]:
              self.dominance_frontier[runner].add(i)
              runner = immediate_dominators[runner][0]
    return self.dominance_frontier
  def nodesDF(self,set_of_nodes):
    dominance_frontier = self.getDominanceFrontier()
    nodes_df = set()
    for elem in set_of_nodes:
      for frontier_elem in dominance_frontier[elem]:
        nodes_df.add(frontier_elem)
    return nodes_df
  def nodesIteratedDF(self,set_of_nodes):
    iterated_0_df = self.nodesDF(set_of_nodes)
    iterated_1_df = self.nodesDF(set_of_nodes.union(iterated_0_df))
    while iterated_0_df!=iterated_1_df:
      iterated_0_df = iterated_1_df
      iterated_1_df = self.nodesDF(set_of_nodes.union(iterated_0_df))
    return iterated_0_df

def test_getPredecessors():
  edges = CFGEdges([[1],[2,3],[7],[4,5],[6],[6],[7],[2,8],[]])
  predecessors = [[],[0],[1,7],[1],[3],[3],[4,5],[2,6],[7]]
  assert edges.getPredecessors()==predecessors
  edges = CFGEdges([[1],[2,5],[3,4],[6],[6],[7],[7],[]])
  predecessors = [[],[0],[1],[2],[2],[1],[3,4],[5,6]]
  assert edges.getPredecessors()==predecessors

def test_deleteNode():
  edges = CFGEdges([[1],[2,3],[7],[4,5],[6],[6],[7],[2,8],[]])
  edges.deleteNode(4)
  assert edges.successors==[[1],[2,3],[6],[5,4],[5],[6],[2,7],[]]
  edges.deleteNode(2)
  assert edges.successors==[[1],[5,2],[4,3],[4],[5],[5,6],[]]

def test_insertNode():
  edges = CFGEdges([[1],[2,3],[7],[4,5],[6],[6],[7],[2,8],[]])
  edges.insertNode(4)
  assert edges.successors==[[1],[2,3],[8],[5,6],[],[7],[7],[8],[2,9],[]]

def test_getAllDominators():
  edges = CFGEdges([[1],[2,3],[7],[4,5],[6],[6],[7],[2,8],[]])
  all_dominators = [{0},{0,1},{0,1,2},{0,1,3},{0,1,3,4},{0,1,3,5},{0,1,3,6},{0,1,7},{0,1,7,8}]
  assert edges.getAllDominators()==all_dominators
  edges = CFGEdges([[1],[2,5],[3,4],[6],[6],[7],[7],[]])
  all_dominators = [{0},{0,1},{0,1,2},{0,1,2,3},{0,1,2,4},{0,1,5},{0,1,2,6},{0,1,7}]
  assert edges.getAllDominators()==all_dominators

def test_getImmediateDominators():
  edges = CFGEdges([[1],[2,3],[7],[4,5],[6],[6],[7],[2,8],[]])
  immediate_dominators = [[],[0],[1],[1],[3],[3],[3],[1],[7]]
  assert edges.getImmediateDominators()==immediate_dominators
  edges = CFGEdges([[1],[2,5],[3,4],[6],[6],[7],[7],[]])
  immediate_dominators = [[],[0],[1],[2],[2],[1],[2],[1]]
  assert edges.getImmediateDominators()==immediate_dominators

def test_getDominanceFrontier():
  edges = CFGEdges([[1],[2,5],[3,4],[6],[6],[1,7],[7],[]])
  dominance_frontier = [set(),{1},{7},{6},{6},{1,7},{7},set()]
  assert edges.getDominanceFrontier()==dominance_frontier
  edges = CFGEdges([[1],[2,5,9],[3],[3,4],[13],[6,7],[4,8],
                   [8,12],[5,13],[10,11],[12],[12],[13],[]])
  dominance_frontier = [set(),set(),{4},{3,4},{13},{12,13,4,5},{8,4},
                        {8,12},{13,5},{12},{12},{12},{13},set()]
  assert edges.getDominanceFrontier()==dominance_frontier

def test_nodesDF():
  edges = CFGEdges([[1],[2,3],[4],[4,5],[1,5],[]])
  set_of_nodes = {2,3,4}
  dominance_frontier = {1,4,5}
  assert edges.nodesDF(set_of_nodes)==dominance_frontier

def test_nodesIteratedDF():
  edges = CFGEdges([[1],[2,3],[4],[4,5],[1,5],[]])
  set_of_nodes = {2,3,4}
  iterated_df = {1,4,5}
  assert edges.nodesIteratedDF(set_of_nodes)==iterated_df

test_getPredecessors()
test_deleteNode()
test_insertNode()
test_getAllDominators()
test_getImmediateDominators()
test_getDominanceFrontier()
test_nodesDF()
test_nodesIteratedDF()
