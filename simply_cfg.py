from simply_arm import simply_arm_template, arm_fast_multiplication_template, arm_fast_division_template
from simply_df import *

class CFGBlock:
  def __init__(self,root,index):
    self.root = root
    self.index = index
    self.quadruplets = []
    self.tmp_counter = 0
    self.test = None
  def __repr__(self):
    string = ""
    for quadruplet in self.quadruplets:
      string += "{}\n".format(quadruplet)
    if self.test:
      string += "test {} ?\n".format(self.test)
    return string[:-1]
  def isEmpty(self):
    return len(self.quadruplets)==0
  def whileBlocks(self):
    return self.root.whileBlocks(self.index)
  def branchBlocks(self):
    return self.root.branchBlocks(self.index)
  def logicalBlocks(self,operator):
    return self.root.logicalBlocks(self.index,operator)
  def addTmp(self):
    assert not self.test, "CFGBlock : test should be the last quadruplet"
    self.tmp_counter += 1
    return "tmp_"+str(self.tmp_counter)
  def addBool(self):
    return self.root.addBool()
  def addQuadruplet(self,quadruplet):
    assert len(quadruplet)==4, "CFGBlock : quadruplet should be of length 4"

    assert self.quadruplets==[] or self.quadruplets[-1][0]!='test', "CFGBlock : test should be the last quadruplet"
    self.quadruplets.append(quadruplet)
  def resolveTmp(self):
    i = 0
    while i<len(self.quadruplets):
      action,op0,op1,op2 = self.quadruplets[i]
      if action=="mov" and op0[:4]=="tmp_":
        for j in range(i+1,len(self.quadruplets)):
          assert self.quadruplets[j]!=op0, "CFGBlock : tmp variables should not be reassigned!!!"
          if self.quadruplets[j][2]==op0:
            self.quadruplets[j][2]=op1
          if self.quadruplets[j][3]==op0:
            self.quadruplets[j][3]=op1
        del self.quadruplets[i]
      else:
        i += 1
  def compile(self,successors):
    string = ".block_{}:\n".format(self.index)
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
        string += "  CMP R0, #1\n  BEQ .block_{}\n  B .block_{}\n".format(successors[0],successors[1])
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
      string += "  B .block_{}\n".format(successors[0])
    elif len(successors)==0:
      string += "  B end\n"
    return string


class CFGRoot:
  def __init__(self):
    self.blocks = []
    self.edges = CFGEdges([])
    self.names = {}
    self.bool_counter = 0
  def __repr__(self):
    return self.toString("")
  def toString(self,prepend):
    contents = []
    for i in range(len(self.blocks)):
      contents.append(str(self.blocks[i]))
    return self.edges.toString(prepend,contents)
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
      if block.index>=index:
        block.index +=1
    self.blocks.insert(index,CFGBlock(self,index))
  def deleteBlock(self,index):
    block = self.blocks[index]
    assert block.isEmpty(), "CFGRoot : non empty blocks should not be deleted"
    assert len(self.edges.successors[index])==1, "CFGRoot : blocks with conditional branching should not be empty"
    self.edges.deleteNode(index)
    for block in self.blocks:
      if block.index>index:
        block.index -=1
    del self.blocks[index]
  def compile(self):
    # Optimizations????
    i = 0
    while i<len(self.blocks):
      block = self.blocks[i]
      block.resolveTmp()
      if block.isEmpty() and len(self.edges.successors[i])==1:
        self.deleteBlock(i)
      else:
        i += 1
    # Compilation
    string = ""
    for i in range(len(self.blocks)):
      block = self.blocks[i]
      successors = self.edges.successors[i]
      string += block.compile(successors)
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
