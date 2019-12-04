from simply_arm import simply_arm_template, arm_fast_multiplication_template, arm_fast_division_template
from simply_df import *

class CFGPhi:
  def __init__(self,name):
    self.name = name
    self.version = 0
    self.is_undefined = False
    self.selector = {}
    self.max_predecessor = -1
  def __repr__(self):
    return "{} <-- {}".format(self.getFullName(),self.selector)
  def setVersion(self,version):
    self.version = version
  def getFullName(self):
    return "{}_{}".format(self.name,self.version)
  def blockInsertedAt(self,index):
    for i in range(max_predecessor,index-1,-1):
      if i in self.selector:
        assert i+1 not in self.selector, "CFGPhi : trying to overwrite existing selection"
        self.selector[i+1] = self.selector[i]
        del self.selector[i]
  def blockDeletedAt(self,index):
    if index in self.selector:
      del self.selector[index]
    for i in range(index+1,max_predecessor+1):
      if i in self.selector:
        assert i-1 not in self.selector, "CFGPhi : trying to overwrite existing selection"
        self.selector[i-1] = self.selector[i]
        del self.selector[i]
  def addSelection(self,predecessor,version):
    if version==0:
      self.is_undefined = True
    self.selector[predecessor] = "{}_{}".format(self.name,version)
    self.max_predecessor = max(self.max_predecessor,predecessor)
  def replaceAlias(self,alias):
    for predecessor in self.selector:
      if self.selector[predecessor]==alias[0]:
        self.selector[predecessor] = alias[1]
  def getUsedVariables(self):
    used = set()
    for predecessor in self.selector:
      used.add(self.selector[predecessor])
    return used

class CFGBlock:
  def __init__(self,root,index):
    self.root = root
    self.index = index
    self.phis = {}
    self.quadruplets = []
    self.quadruplets_cpy = None
    self.tmp_counter = 0
  def __repr__(self):
    string = ""
    if self.phis:
      string += "Phi:\n"
      for name in self.phis:
        string += str(self.phis[name])+"\n"
      string += "────────────\n"
    for quadruplet in self.quadruplets:
      string += "{}\n".format(quadruplet)
    return string[:-1]
  def blockInsertedAt(self,index):
    if self.index>=index:
      self.index += 1
    for name in self.phis:
      self.phis[name].blockInsertedAt(index)
  def blockDeletedAt(self,index):
    if self.index>index:
      self.index -= 1
    for name in self.phis:
      self.phis[name].blockDeletedAt(index)
  def isEmpty(self):
    return len(self.quadruplets)==0 and len(self.phis)==0
  def whileBlocks(self):
    return self.root.whileBlocks(self.index)
  def branchBlocks(self):
    return self.root.branchBlocks(self.index)
  def logicalBlocks(self,operator):
    return self.root.logicalBlocks(self.index,operator)
  def addTmp(self):
    return self.root.addTmp()
  def addBool(self):
    return self.root.addBool()
  def addQuadruplet(self,quadruplet):
    assert len(quadruplet)==4, "CFGBlock : quadruplet should be of length 4"
    assert self.quadruplets==[] or self.quadruplets[-1][0]!='test', "CFGBlock : test should be the last quadruplet"
    self.quadruplets.append(quadruplet)
  def popAlias(self):
    i = 0
    while i<len(self.quadruplets):
      action,op0,op1,op2 = self.quadruplets[i]
      if action=="mov":
        del self.quadruplets[i]
        return [op0,op1]
      else:
        i += 1
  def replaceAlias(self,alias):
    for name in self.phis:
      self.phis[name].replaceAlias(alias)
    for quadruplet in self.quadruplets:
      action,op0,op1,op2 = quadruplet
      if action=='test':
        if op0==alias[0]:
          quadruplet[1] = alias[1]
      else:
        if op1==alias[0]:
          quadruplet[2] = alias[1]
        if op2==alias[0]:
          quadruplet[3] = alias[1]
  def getAssignedVariables(self):
    assigned = set()
    for key in self.phis:
      assigned.add(self.phis[key].getFullName())
    for action,op0,op1,op2 in self.quadruplets:
      if action not in ['call','test']:
        assigned.add(op0)
    return assigned
  def getUsedVariables(self):
    used = set()
    for name in self.phis:
      used = used.union(self.phis[name].getUsedVariables())
    for quadruplet in self.quadruplets:
      action,op0,op1,op2 = quadruplet
      if action=='test':
        used.add(op0)
      else:
        if op1:
          used.add(op1)
        if op2:
          used.add(op2)
    return used
  def deleteUnused(self,unused):
    todelete = []
    for name in unused:
      for key in self.phis:
        if self.phis[key].getFullName()==name:
          todelete.append(key)
    for key in todelete:
      del self.phis[key]
  def addPhiFunction(self,name):
    self.phis[name] = CFGPhi(name)
  def addPhiSelection(self,name,predecessor,version):
    if name in self.phis:
      self.phis[name].addSelection(predecessor,version)
  def removeUndefinedPhiFunctions(self):
    todelete = []
    for key in self.phis:
      if self.phis[key].is_undefined:
        todelete.append(key)
    for key in todelete:
      del self.phis[key]
  def renameVariable(self,name,def_version,use_version):
    use_name = "{}_{}".format(name,use_version)
    if name in self.phis:
      def_version += 1
      self.phis[name].setVersion(def_version)
      use_version = def_version
      use_name = "{}_{}".format(name,use_version)
    for quadruplet in self.quadruplets:
      action,op0,op1,op2 = quadruplet
      if action=='test':
        if op0==name:
          quadruplet[1] = use_name
      else:
        if op1==name:
          quadruplet[2] = use_name
        if op2==name:
          quadruplet[3] = use_name
      if action not in ['call','test'] and op0==name:
        def_version += 1
        use_version = def_version
        use_name = "{}_{}".format(name,use_version)
        quadruplet[1] = use_name
    return def_version,use_version
  def compile(self,successors,predecessors):
    string = ""
    for name in self.phis:
      self.root.addArmData(self.phis[name].getFullName())
    for pred in predecessors:
      string += ".block_{}_to_{}:\n".format(pred,self.index)
      i_register = 0
      for name in self.phis:
        assert i_register<10, "CFGBlock: max register number for phi functions"
        string += "  LDR R10, ={}\n  LDR R{}, [R10]\n".format(
          self.phis[name].selector[pred],
          i_register)
        i_register += 1
      i_register = 0
      for name in self.phis:
        string += "  LDR R10, ={}\n  STR R{}, [R10]\n".format(
          self.phis[name].getFullName(),
          i_register)
        i_register += 1
      string += "  B .block_{}\n".format(self.index)
    string += ".block_{}:\n".format(self.index)
    for i in range(len(self.quadruplets)):
      string += "  // {}\n".format(self.quadruplets[i])
      action,op0,op1,op2 = self.quadruplets[i]
      label = "block_{}_quadruplet_{}".format(self.index,i)
      if action=='call':
        string += "  LDR R0, ={}\n  LDR R0, [R0]\n".format(op1)
        string += "  BL .{}\n".format(op0)
      elif action=='mov':
        self.root.addArmData(op0)
        string += "  LDR R1, ={}\n  LDR R1, [R1]\n".format(op1)
        string += "  MOV R0, R1\n"
        string += "  LDR R2, ={}\n  STR R0, [R2]\n".format(op0)
      elif action=='test':
        string += "  LDR R0, ={}\n  LDR R0, [R0]\n".format(op0)
        string += "  CMP R0, #1\n  BEQ .block_{}_to_{}\n  B .block_{}_to_{}\n".format(
          self.index,successors[0],self.index,successors[1])
      elif action in ["+","-","*","//","%","<",">","<=",">=","==","!="]:
        self.root.addArmData(op0)
        string += "  LDR R1, ={}\n  LDR R1, [R1]\n".format(op1)
        string += "  LDR R2, ={}\n  LDR R2, [R2]\n".format(op2)
        if action=="+":
          string += "  ADD R0, R1, R2\n"
        elif action=="-":
          string += "  SUB R0, R1, R2\n"
        elif action=="*":
          string += arm_fast_multiplication_template.format(label=label)
        elif action in ["//","%"]:
          string += arm_fast_division_template.format(label=label)
          if action=="%":
            string += "  MOV R0, R1\n"
        elif action=="==":
          string += "  MOV R0, #1\n  CMP R1, R2\n  BEQ .{label:}_true\n  MOV R0, #0\n.{label:}_true:\n".format(label=label)
        elif action=="!=":
          string += "  MOV R0, #0\n  CMP R1, R2\n  BEQ .{label:}_false\n  MOV R0, #1\n.{label:}_false:\n".format(label=label)
        elif action=="<":
          string += "  MOV R0, #1\n  CMP R1, R2\n  BMI .{label:}_true\n  MOV R0, #0\n.{label:}_true:\n".format(label=label)
        elif action==">":
          string += "  MOV R0, #1\n  CMP R2, R1\n  BMI .{label:}_true\n  MOV R0, #0\n.{label:}_true:\n".format(label=label)
        elif action=="<=":
          string += "  MOV R0, #1\n  CMP R2, R1\n  BPL .{label:}_true\n  MOV R0, #0\n.{label:}_true:\n".format(label=label)
        elif action==">=":
          string += "  MOV R0, #1\n  CMP R1, R2\n  BPL .{label:}_true\n  MOV R0, #0\n.{label:}_true:\n".format(label=label)
        string += "  LDR R3, ={}\n  STR R0, [R3]\n".format(op0)
      elif action== "not":
        self.root.addArmData(op0)
        string += "  LDR R0, ={}\n  LDR R0, [R0]\n".format(op1)
        string += "  MOV R1, #1\n  SUB R0, R1, R0\n"
        string += "  LDR R1, ={}\n  STR R0, [R1]\n".format(op0)
      else:
        assert False, "CFGBlock : Unknown action "+action
    if len(successors)==1:
      string += "  B .block_{}_to_{}\n".format(self.index,successors[0])
    elif len(successors)==0:
      string += "  B end\n"
    return string


class CFGRoot:
  def __init__(self):
    self.blocks = []
    self.edges = CFGEdges([])
    self.names = {}
    self.tmp_counter = 0
    self.bool_counter = 0
  def __repr__(self):
    return self.toString("")
  def toString(self,prepend):
    contents = []
    for i in range(len(self.blocks)):
      contents.append(str(self.blocks[i]))
    return self.edges.toString(prepend,contents)
  def addTmp(self):
    self.tmp_counter += 1
    return "tmp_"+str(self.tmp_counter)
  def addBool(self):
    self.bool_counter += 1
    return "bool_"+str(self.bool_counter)
  def addBlock(self):
    block = CFGBlock(self,len(self.blocks))
    self.blocks.append(block)
    self.edges.insertNode(0)
    return block
  def whileBlocks(self,index):
    i_condition = index+1
    i_statement = index+2
    i_next = index+3
    self.insertBlock(i_condition)
    self.insertBlock(i_statement)
    self.insertBlock(i_next)
    self.edges.connectNode(i_condition,[i_statement,i_next])
    self.edges.connectNode(i_statement,[i_condition])
    self.edges.connectNode(i_next,self.edges.successors[index])
    self.edges.connectNode(index,[i_condition])
    return self.blocks[i_condition],self.blocks[i_statement],self.blocks[i_next]
  def branchBlocks(self,index):
    i_if = index+1
    i_else = index+2
    i_next = index+3
    self.insertBlock(i_if)
    self.insertBlock(i_else)
    self.insertBlock(i_next)
    self.edges.connectNode(i_if,[i_next])
    self.edges.connectNode(i_else,[i_next])
    self.edges.connectNode(i_next,self.edges.successors[index])
    self.edges.connectNode(index,[i_if,i_else])
    return self.blocks[i_if],self.blocks[i_else],self.blocks[i_next]
  def logicalBlocks(self,index,operator):
    i_right = index+1
    i_next = index+2
    self.insertBlock(i_right)
    self.insertBlock(i_next)
    self.edges.connectNode(i_right,[i_next])
    self.edges.connectNode(i_next,self.edges.successors[index])
    if operator=="or":
      self.edges.connectNode(index,[i_next,i_right])
    else:
      self.edges.connectNode(index,[i_right,i_next])
    return self.blocks[i_right],self.blocks[i_next]
  def insertBlock(self,index):
    self.edges.insertNode(index)
    for block in self.blocks:
      block.blockInsertedAt(index)
    self.blocks.insert(index,CFGBlock(self,index))
  def deleteBlock(self,index):
    block = self.blocks[index]
    assert block.isEmpty(), "CFGRoot : non empty blocks should not be deleted"
    assert len(self.edges.successors[index])==1, "CFGRoot : blocks with conditional branching should not be empty"
    self.edges.deleteNode(index)
    del self.blocks[index]
    for block in self.blocks:
      block.blockDeletedAt(index)
  def renameVariable(self,name,i_block=0,def_version=1,use_version=0):
    def_version,use_version = self.blocks[i_block].renameVariable(name,def_version,use_version)
    for i_successor in self.edges.successors[i_block]:
      self.blocks[i_successor].addPhiSelection(name,i_block,use_version)
    for child in self.edges.getDominatedChildren(i_block):
      # siblings use the same use_version
      # but may increment def_version
      def_version,dummy = self.renameVariable(name,child,def_version,use_version)
    return def_version,use_version
  def toSSA(self):
    assigned_set = set()
    assigned_per_block = []
    for block in self.blocks:
      assigned = block.getAssignedVariables()
      assigned_per_block.append(assigned)
      assigned_set = assigned_set.union(assigned)
    for name in assigned_set:
      set_of_blocks = set()
      for i in range(len(self.blocks)):
        if name in assigned_per_block[i]:
          set_of_blocks.add(i)
      iterated_df = self.edges.nodesIteratedDF(set_of_blocks)
      for i in iterated_df:
        self.blocks[i].addPhiFunction(name)
      self.renameVariable(name)
    # iterated_df is an over-approximation :
    # the algorithm assumes an implicit definition of every variable
    # some phis une undefined version (0)
    # but undefined variables have been checked by AST
    # so we may remove any phi with use of version 0
    # TODO : verify theory!!!!
    for block in self.blocks:
      block.removeUndefinedPhiFunctions()
  def compile(self):
    # SSA-based optimizations : work in progress
    optimize = True
    if optimize:
      self.toSSA()
      found = True
      while found:
        i = 0
        found = False
        while i<len(self.blocks) and not found:
          alias = self.blocks[i].popAlias()
          found = alias!=None
          i += 1
        if found:
          for block in self.blocks:
            block.replaceAlias(alias)
      found = True
      while found:
        used = set()
        assigned = set()
        for block in self.blocks:
          assigned = assigned.union(block.getAssignedVariables())
          used = used.union(block.getUsedVariables())
        unused = set()
        for name in assigned:
          if name not in used:
            unused.add(name)
        found = unused!=set()
        for block in self.blocks:
          block.deleteUnused(unused)
    # Compilation
    string = ""
    for i in range(len(self.blocks)):
      block = self.blocks[i]
      successors = self.edges.successors[i]
      predecessors = self.edges.getPredecessors()[i]
      string += block.compile(successors,predecessors)
    return string
  def addArmData(self,name,value=0):
    if name in self.names:
      return
    self.names[name] = value
  def toArmData(self):
    string = ""
    for name in self.names:
      string += "{}:\n  .word {}\n".format(name,self.names[name])
    return string
