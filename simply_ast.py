import random
from simply_arm import simply_arm_template, arm_fast_multiplication_template, arm_fast_division_template
from simply_cfg import *

class ASTEnvironment:
  def __init__(self,parent=None):
    self.parent = parent
    if not self.parent:
      self.id = 0
      self.last_id = 0
    else:
      self.id = self.parent.newId()
    self.children = []
    self.variables = {}
  def __repr__(self):
    return str(self.variables)
  def getVariableType(self,name):
    if name in self.variables:
      return self.id,self.variables[name]
    if self.parent:
      return self.parent.getVariableType(name)
    return None #not found
  def setVariableType(self,name,type):
    assert not self.getVariableType(name), "Variable "+name+" already in environment"
    self.variables[name] = type
  def fork(self):
    new = ASTEnvironment(self)
    self.children.append(new)
    return new
  def newId(self):
    if self.parent:
      return self.parent.newId()
    self.last_id += 1
    return self.last_id
  def merge(self,other):
    assert self.parent==other.parent, "trying to merge environments with no common parent"
    assert self.parent!=None, "trying to merge environments with 'None' parent"
    for name in self.variables:
      if name not in other.variables:
        print("Warning : variable "+name+" is local")
      elif self.variables[name]!=other.variables[name]:
        print("Warning : variable "+name+" initialized with different types")
        print("  ->interpreted as local to each")
      else:
        self.parent.variables[name] = self.variables[name]
        del self.variables[name]
        del other.variables[name]
    # variables initialized ONLY in the ELSE block
    for name in other.variables:
      print("Warning : variable "+name+" is local")

class ASTBooleanNot:
  def __init__(self,operand):
    self.operand = operand
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.operand.setEnvironment(environment)
    self.environment = environment
  def toString(self,prepend):
    string = "not\n"
    string += prepend+"└─"+self.operand.toString(prepend+"  ")
    return string
  def checkType(self):
    self.operand,type = self.operand.checkType()
    assert type=="bool","Expression ("+str(self.operand)+") should be bool"
    return self,"bool"
  def booleanCleanup(self,invert):
    return self.operand.booleanCleanup(not invert)
  def toCFG(self,block,name):
    operand_name = block.addTmp()
    block = self.operand.toCFG(block,operand_name)
    block.addQuadruplet(['not',name,operand_name,None])
    return block

class ASTVariable:
  def __init__(self,name):
    self.name = name
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.environment = environment
  def toString(self,prepend):
    return "{}\n".format(self.name)
  def checkType(self):
    id,type = self.environment.getVariableType(self.name)
    assert type!=None, "Variable "+self.name+" referenced before assignment OR initialized locally"
    return self,type
  def booleanCleanup(self,invert):
    if invert:
       return ASTBooleanNot(self)
    return self
  def toCFG(self,block,name):
    environment_id,type = self.environment.getVariableType(self.name)
    id = "var_{}_{}".format(environment_id,self.name)
    block.addQuadruplet(['mov',name,id,None])
    return block

class ASTIntegerConstant:
  def __init__(self,value):
    self.value = value
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.environment = environment
  def toString(self,prepend):
    return "{}\n".format(self.value)
  def checkType(self):
    return self,"int"
  def booleanCleanup(self,invert):
    return self
  def toCFG(self,block,name):
    id = "const_{}".format(self.value)
    block.root.addArmData(id,self.value)
    block.addQuadruplet(['mov',name,id,None])
    return block

class ASTBooleanConstant:
  def __init__(self,value):
    self.value = value
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.environment = environment
  def toString(self,prepend):
    return "{}\n".format(self.value)
  def checkType(self):
    return self,"bool"
  def booleanCleanup(self,invert):
    if invert:
      self.value = not self.value
    return self
  def toCFG(self,block,name):
    id = "const_{}".format(self.value)
    block.root.addArmData(id,[0,1][self.value])
    block.addQuadruplet(['mov',name,id,None])
    return block

class ASTIntegerOperator:
  def __init__(self,operator,operand1,operand2):
    self.operator = operator
    self.operand1 = operand1
    self.operand2 = operand2
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.operand1.setEnvironment(environment)
    self.operand2.setEnvironment(environment)
    self.environment = environment
  def toString(self,prepend):
    string = "{}\n".format(self.operator)
    string += prepend+"├─"+self.operand1.toString(prepend+"│ ")
    string += prepend+"└─"+self.operand2.toString(prepend+"  ")
    return string
  def checkType(self):
    return self,"int"
  def booleanCleanup(self,invert):
    return self
  def toCFG(self,block,name):
    operand1_name = block.addTmp()
    operand2_name = block.addTmp()
    block = self.operand1.toCFG(block,operand1_name)
    block = self.operand2.toCFG(block,operand2_name)
    block.addQuadruplet([self.operator,name,operand1_name,operand2_name])
    return block

class ASTIntegerComparator:
  def __init__(self,operator,operand1,operand2):
    self.operator = operator
    self.operand1 = operand1
    self.operand2 = operand2
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.operand1.setEnvironment(environment)
    self.operand2.setEnvironment(environment)
    self.environment = environment
  def toString(self,prepend):
    string = "{}\n".format(self.operator)
    string += prepend+"├─"+self.operand1.toString(prepend+"│ ")
    string += prepend+"└─"+self.operand2.toString(prepend+"  ")
    return string
  def booleanCleanup(self,invert):
    self.operand1 = self.operand1.booleanCleanup(invert)
    self.operand2 = self.operand2.booleanCleanup(invert)
    if invert:
      inverse_operators = {"<":">=",">":"<=","<=":">",">=":"<","==":"!=","!=":"=="}
      self.operator = inverse_operators[self.operator]
    return self
  def toCFG(self,block,name):
    operand1_name = block.addTmp()
    operand2_name = block.addTmp()
    block = self.operand1.toCFG(block,operand1_name)
    block = self.operand2.toCFG(block,operand2_name)
    block.addQuadruplet([self.operator,name,operand1_name,operand2_name])
    return block

class ASTLogicalOperator:
  def __init__(self,operator,operand1,operand2):
    self.operator = operator
    self.operand1 = operand1
    self.operand2 = operand2
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.operand1.setEnvironment(environment)
    self.operand2.setEnvironment(environment)
    self.environment = environment
  def toString(self,prepend):
    string = "{}\n".format(self.operator)
    string += prepend+"├─"+self.operand1.toString(prepend+"│ ")
    string += prepend+"└─"+self.operand2.toString(prepend+"  ")
    return string
  def booleanCleanup(self,invert):
    self.operand1 = self.operand1.booleanCleanup(invert)
    self.operand2 = self.operand2.booleanCleanup(invert)
    if invert:
      logical_inverses = {"or":"and","and":"or","==":"!=","!=":"=="}
      self.operator = logical_inverses[self.operator]
    return self
  def toCFG(self,block,name):
    operand1_name = block.addBool()
    block = self.operand1.toCFG(block,operand1_name)
    block.addQuadruplet(['mov',name,operand1_name,None])
    block.addQuadruplet(['test',name,None,None])
    right_block,next_block = block.logicalBlocks(self.operator)
    operand2_name = right_block.addBool()
    right_block = self.operand2.toCFG(right_block,operand2_name)
    right_block.addQuadruplet(['mov',name,operand2_name,None])
    return next_block

class ASTBinaryOperator:
  def __init__(self,operator,operand1,operand2):
    self.operator = operator
    self.operand1 = operand1
    self.operand2 = operand2
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.environment = environment
    self.operand1.setEnvironment(environment)
    self.operand2.setEnvironment(environment)
  def checkType(self):
    self.operand1,type1 = self.operand1.checkType()
    self.operand2,type2 = self.operand2.checkType()
    if self.operator in ["+","-","*","//","%"]:
      assert type1=="int","Expression ("+str(self.operand1)+") should be int"
      assert type2=="int","Expression ("+str(self.operand2)+") should be int"
      new =  ASTIntegerOperator(self.operator,self.operand1,self.operand2)
      type = "int"
    elif self.operator in ["<",">","<=",">="]:
      assert type1=="int","Expression ("+str(self.operand1)+") should be int"
      assert type2=="int","Expression ("+str(self.operand2)+") should be int"
      new = ASTIntegerComparator(self.operator,self.operand1,self.operand2)
      type = "bool"
    elif self.operator in ["==","!="]:
      assert type1==type2,"Expressions ("+str(self.operand1)+") and ("+str(self.operand2)+") should be of same type"
      new = ASTIntegerComparator(self.operator,self.operand1,self.operand2)
      type = "bool"
    else: # not,or
      assert type1=="bool", "Expression ("+str(self.operand1)+") should be bool"
      assert type2=="bool", "Expression ("+str(self.operand2)+") should be bool"
      new = ASTLogicalOperator(self.operator,self.operand1,self.operand2)
      type = "bool"
    new.setEnvironment(self.environment)
    return new,type

class ASTNop:
  def __init__(self):
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.environment = environment
  def toString(self,prepend):
    return "Nop\n"
  def checkType(self):
    pass
  def booleanCleanup(self):
    return self
  def toCFG(self,block):
    return block

class ASTAssignment:
  def __init__(self,name,expression):
    self.name = name
    self.expression = expression
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.expression.setEnvironment(environment)
    self.environment = environment
  def toString(self,prepend):
    string = "Assignment\n"
    string += prepend+"├i─{}\n".format(str(self.name))
    string += prepend+"└─"+self.expression.toString(prepend+"  ")
    return string
  def checkType(self):
    self.expression,expression_type = self.expression.checkType()
    answer = self.environment.getVariableType(self.name)
    if answer:
      id,name_type = answer
      assert expression_type==name_type, "Wrong extression type {} for {} variable {}".format(expression_type,variable_type,self.name)
    else:
      self.environment.setVariableType(self.name,expression_type)
  def booleanCleanup(self):
    self.expression = self.expression.booleanCleanup(False)
    return self
  def toCFG(self,block):
    environment_id,type = self.environment.getVariableType(self.name)
    id = "var_{}_{}".format(environment_id,self.name)
    return self.expression.toCFG(block,id)

class ASTPrint:
  def __init__(self,expression):
    self.expression = expression
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.expression.setEnvironment(environment)
    self.environment = environment
  def toString(self,prepend):
    string = "Print\n"
    string += prepend+"└─"+self.expression.toString(prepend+"  ")
    return string
  def checkType(self):
    self.expression,self.type = self.expression.checkType()
  def booleanCleanup(self):
    self.expression.booleanCleanup(False)
    return self
  def toCFG(self,block):
    if self.type=="bool":
      name = block.addBool()
    else:
      name = block.addTmp()
    block = self.expression.toCFG(block,name)
    block.addQuadruplet(['call','print'+self.type,name,None])
    return block

class ASTWhile:
  def __init__(self,condition,statement):
    self.condition = condition
    self.statement = statement
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.environment = environment
    self.condition.setEnvironment(environment)
    self.statement.setEnvironment(environment.fork())
  def toString(self,prepend):
    string = "While\n"
    string += prepend+"├c─"+self.condition.toString(prepend+"│  ")
    string += prepend+"└─"+self.statement.toString(prepend+"  ")
    return string
  def checkType(self):
    self.condition,type = self.condition.checkType()
    assert type=="bool", "Condition ("+self.condition.toString("")+") should be bool"
    self.statement.checkType()
    for name in self.statement.environment.variables:
      print("Warning : variable "+name+" is local to WHILE loop")
  def booleanCleanup(self):
    self.condition = self.condition.booleanCleanup(False)
    self.statement = self.statement.booleanCleanup()
    return self
  def toCFG(self,block):
    condition_block,statement_block,next_block = block.whileBlocks()
    name = condition_block.addBool()
    condition_block = self.condition.toCFG(condition_block,name)
    condition_block.addQuadruplet(['test',name,None,None])
    self.statement.toCFG(statement_block)
    return next_block

class ASTBranch:
  def __init__(self,condition,if_statement,else_statement):
    self.condition = condition
    self.if_statement = if_statement
    self.else_statement = else_statement
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.environment = environment
    self.condition.setEnvironment(environment)
    self.if_statement.setEnvironment(environment.fork())
    self.else_statement.setEnvironment(environment.fork())
  def toString(self,prepend):
    string = "Branch\n"
    string += prepend+"├c─"+self.condition.toString(prepend+"│  ")
    string += prepend+"├i─"+self.if_statement.toString(prepend+"│  ")
    string += prepend+"└e─"+self.else_statement.toString(prepend+"   ")
    return string
  def checkType(self):
    self.condition,type = self.condition.checkType()
    assert type=="bool", "Condition should be bool"
    self.if_statement.checkType()
    self.else_statement.checkType()
    self.if_statement.environment.merge(self.else_statement.environment)
  def booleanCleanup(self):
    self.condition = self.condition.booleanCleanup(False)
    self.if_statement = self.if_statement.booleanCleanup()
    self.else_statement = self.else_statement.booleanCleanup()
    return self
  def toCFG(self,block):
    if_block,else_block,next_block = block.branchBlocks()
    name = block.addBool()
    block = self.condition.toCFG(block,name)
    block.addQuadruplet(['test',name,None,None])
    self.if_statement.toCFG(if_block)
    self.else_statement.toCFG(else_block)
    return next_block

class ASTSequence:
  def __init__(self,statement1,statement2):
    self.statement1 = statement1
    self.statement2 = statement2
    self.environment = None
  def __repr__(self):
    return self.toString("")
  def setEnvironment(self,environment):
    self.environment = environment
    self.statement1.setEnvironment(environment)
    self.statement2.setEnvironment(environment)
  def toString(self,prepend):
    string = "Sequence\n"
    prepend = prepend[:-2]
    string += prepend+"┌─┘\n"
    string += prepend+"├─"+self.statement1.toString(prepend+"│ ")
    string += prepend+"└─"+self.statement2.toString(prepend+"  ")
    return string
  def checkType(self):
    self.statement1.checkType()
    self.statement2.checkType()
  def booleanCleanup(self):
    self.statement1 = self.statement1.booleanCleanup()
    self.statement2 = self.statement2.booleanCleanup()
    return self
  def toCFG(self,block):
    block = self.statement1.toCFG(block)
    block = self.statement2.toCFG(block)
    return block

class ASTRoot:
  def __init__(self,root):
    self.root = root
    self.root.setEnvironment(ASTEnvironment())
    self.py_filename = "<unknown.py>"
    self.py_code = "<not given>"
  def __repr__(self):
    return self.toString("")
  def process(self):
    self.root.checkType()
    self.root = self.root.booleanCleanup()
    # print(self)
    cfg = CFGRoot()
    self.root.toCFG(cfg.addBlock())
    arm_code = cfg.compile()
    arm_data = cfg.toArmData()
    return simply_arm_template.format(filename=self.py_filename,
                                      source="// "+self.py_code.replace("\n","\n// "),
                                      ast=self.toString("// "),
                                      cfg=cfg.toString("// "),
                                      arm_code=arm_code,
                                      arm_data=arm_data)
  def toString(self,prepend):
    string = prepend+"Root\n"
    string += prepend+"└─"
    string += self.root.toString(prepend+"  ")
    return string
