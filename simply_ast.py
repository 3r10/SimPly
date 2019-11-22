from graphviz import Digraph
import random

class ASTEnvironmentVariable:
  def __init__(self,name,state,type):
    self.name = name
    self.state = state
    self.type = type
  def __repr__(self):
    return self.name+" ("+self.state+" "+self.type+")"

class ASTEnvironment:
  def __init__(self):
    self.dictionary = {}
  def __repr__(self):
    string = ""
    for var in self.dictionary:
      string += str(self.dictionary[var])+'\n'
    return string
  def assignVariable(self,name,state,type):
    if name in self.dictionary:
      assert self.dictionary[name].type==type,\
        "Wrong extression type "+type+" for variable "+name
      self.dictionary[name].state = "var"
    else:
      self.dictionary[name] = ASTEnvironmentVariable(name,state,type)
  def getVariable(self,name):
    if name in self.dictionary:
      return self.dictionary[name]
    return None

class ASTVariable:
  def __init__(self,name):
    self.name = name
  def __repr__(self):
    return self.name
  def toGraph(self,dot):
    name = "Element"+str(random.randint(0,1000000000000))
    dot.node(name,self.name, shape='box')
    return name
  def getStateType(self,environment):
    environment_variable = environment.getVariable(self.name)
    assert environment_variable, "Variable "+self.name+" referenced before assignment"
    return environment_variable.state,environment_variable.type
  def evaluate(self,environment):
    assert self.name in environment, self.name+" referenced before assignment"
    return environment[self.name]

class ASTIntegerConstant:
  def __init__(self,value):
    self.value = value
  def __repr__(self):
    return str(self.value)
  def toGraph(self,dot):
    name = "Element"+str(random.randint(0,1000000000000))
    dot.node(name,str(self.value), shape='box')
    return name
  def getStateType(self,environment):
    return "const","int"
  def evaluate(self,environment):
    return self.value

class ASTBooleanConstant:
  def __init__(self,value):
    self.value = value
  def __repr__(self):
    return str(self.value)
  def toGraph(self,dot):
    name = "Element"+str(random.randint(0,1000000000000))
    dot.node(name,str(self.value), shape='box')
    return name
  def getStateType(self,environment):
    return "const","bool"
  def evaluate(self,environment):
    return self.value

class ASTBinaryOperator:
  def __init__(self,operator,operand1,operand2):
    self.operator = operator
    self.operand1 = operand1
    self.operand2 = operand2
  def __repr__(self):
    if self.operator in ["not","and","or"]:
      return str(self.operand1)+" "+str(self.operator)+" "+str(self.operand2)
    else:
      return str(self.operand1)+str(self.operator)+str(self.operand2)
  def toGraph(self,dot):
    name = "Element"+str(random.randint(0,1000000000000))
    dot.node(name,self.operator, shape='box')
    name_operand1 = self.operand1.toGraph(dot)
    dot.edge(name,name_operand1)
    name_operand2 = self.operand2.toGraph(dot)
    dot.edge(name,name_operand2)
    return name
  def getStateType(self,environment):
    state1,type1 = self.operand1.getStateType(environment)
    state2,type2 = self.operand2.getStateType(environment)
    if state1=="const" and state2=="const":
      state = "const"
    else:
      state = "var"
    if self.operator in ["+","-","*","//","%"]:
      assert type1=="int","Expression ("+str(self.operand1)+") should be int"
      assert type2=="int","Expression ("+str(self.operand2)+") should be int"
      return state,"int"
    if self.operator in ["<",">","<=",">="]:
      assert type1=="int","Expression ("+str(self.operand1)+") should be int"
      assert type2=="int","Expression ("+str(self.operand2)+") should be int"
      return state,"bool"
    if self.operator in ["==","!="]:
      assert type1==type2,"Expressions ("+str(self.operand1)+") and ("+str(self.operand2)+") should be of same type"
      return state,"bool"
    assert type1=="bool", "Expression ("+str(self.operand1)+") should be bool"
    assert type2=="bool", "Expression ("+str(self.operand2)+") should be bool"
    return state, "bool"
  def evaluate(self,environment):
    eval1 = self.operand1.evaluate(environment)
    eval2 = self.operand2.evaluate(environment)
    return eval(str(eval1)+" "+self.operator+" "+str(eval2))

class ASTBooleanNot:
  def __init__(self,operand):
    self.operand = operand
  def __repr__(self):
    return "not "+str(self.operand)
  def toGraph(self,dot):
    name = "Element"+str(random.randint(0,1000000000000))
    dot.node(name,"not", shape='box')
    name_operand = self.operand.toGraph(dot)
    dot.edge(name,name_operand)
    return name
  def getStateType(self,environment):
    state,type = self.operand.getStateType(environment)
    assert type=="bool","Expression ("+str(self.operand)+") should be bool"
    return state,"bool"
  def evaluate(self,environment):
    return not self.operand.evaluate(environment)

class ASTExpressionGroup:
  def __init__(self,expression):
    self.expression = expression
  def __repr__(self):
    return "("+str(self.expression)+")"
  def toGraph(self,dot):
    name = "Element"+str(random.randint(0,1000000000000))
    dot.node(name,"( )", shape='box')
    name_expression = self.expression.toGraph(dot)
    dot.edge(name,name_expression)
    return name
  def getStateType(self,environment):
    state,type = self.expression.getStateType(environment)
    return state,type
  def evaluate(self,environment):
    return self.expression.evaluate(environment)

class ASTAssignment:
  def __init__(self,lineno,indent_level,id,expression):
    self.lineno = lineno
    self.indent_level = indent_level
    self.id = id
    self.expression = expression
  def __repr__(self):
    return "\t"*self.indent_level+self.id+" = "+str(self.expression)+"\n"
  def toGraph(self,dot,is_deep=False):
    name = "S"+str(self.lineno)
    if is_deep:
      dot.node(name,self.id+" =", shape='box')
      name_expression = self.expression.toGraph(dot)
      dot.edge(name,name_expression)
    else:
      dot.node(name,self.id+" = "+str(self.expression), shape='box')
    return name
  def checkType(self,environment):
    state,type = self.expression.getStateType(environment)
    environment.assignVariable(self.id,state,type)
    return environment
  def execute(self,environment):
    value = self.expression.evaluate(environment)
    environment[self.id] = value
    print(self.id,"<-",value)

class ASTWhile:
  def __init__(self,lineno,indent_level,condition,sequence):
    self.lineno = lineno
    self.indent_level = indent_level
    self.condition = condition
    self.sequence = sequence
  def __repr__(self):
    return "\t"*self.indent_level+"while "+str(self.condition)+":\n"+str(self.sequence)
  def toGraph(self,dot,is_deep=False):
    name = "W"+str(self.lineno)
    dot.node(name,"While")
    if is_deep:
      condition_name = self.condition.toGraph(dot)
    else:
      condition_name = "C"+str(self.lineno)
      dot.node(condition_name,str(self.condition),shape='box')
    dot.edge(name,condition_name,"condition")
    sequence_name = self.sequence.toGraph(dot,is_deep)
    dot.edge(name,sequence_name,"block")
    return name
  def checkType(self,environment):
    # two times to propagate
    # not enough!!!!
    self.sequence.checkType(environment)
    self.sequence.checkType(environment)
    state,type = self.condition.getStateType(environment)
    assert type=="bool", "Condition ("+str(self.condition)+") should be bool"
    assert state=="var", "Condition ("+str(self.condition)+") should not be const"
    return environment
  def execute(self,environment):
    while self.condition.evaluate(environment):
      print("Condition : T")
      self.sequence.execute(environment)
    print("Condition : F")

class ASTBranch:
  def __init__(self,lineno,indent_level,condition,if_sequence,else_sequence):
    self.lineno = lineno
    self.indent_level = indent_level
    self.condition = condition
    self.if_sequence= if_sequence
    self.else_sequence= else_sequence
  def __repr__(self):
    string = "\t"*self.indent_level+"if "+str(self.condition)+":\n"+str(self.if_sequence)
    if self.else_sequence:
      string += "\t"*self.indent_level+"else...\n"+str(self.else_sequence)
    return string
  def toGraph(self,dot,is_deep=False):
    name = "B"+str(self.lineno)
    dot.node(name,"Branch")
    if is_deep:
      condition_name = self.condition.toGraph(dot)
    else:
      condition_name = "C"+str(self.lineno)
      dot.node(condition_name,str(self.condition),shape='box')
    dot.edge(name,condition_name,"condition")
    if_name = self.if_sequence.toGraph(dot,is_deep)
    dot.edge(name,if_name,"if")
    if self.else_sequence:
      else_name = self.else_sequence.toGraph(dot,is_deep)
      dot.edge(name,else_name,"else")
    return name
  def checkType(self,environment):
    state,type = self.condition.getStateType(environment)
    assert type=="bool", "Condition ("+str(self.condition)+") should be bool"
    self.if_sequence.checkType(environment)
    if self.else_sequence:
      self.else_sequence.checkType(environment)
    return environment
  def execute(self,environment):
    condition = self.condition.evaluate(environment)
    print("Condition :",condition)
    if condition:
      self.if_sequence.execute(environment)
    elif self.else_sequence:
      self.else_sequence.execute(environment)

class ASTSequence:
  def __init__(self,statement,next):
    self.statement = statement
    self.next = next
  def __repr__(self):
    string = str(self.statement)
    if self.next:
      string += str(self.next)
    return string
  def toGraph(self,dot,is_deep=False):
    name = "Seq"+str(self.statement.lineno)
    dot.node(name,"Sequence")
    statement_name = self.statement.toGraph(dot,is_deep)
    dot.edge(name,statement_name)
    if self.next:
      next_name = self.next.toGraph(dot,is_deep)
      dot.edge(name,next_name)
    return name
  def checkType(self,environment=None):
    if not environment:
      environment=ASTEnvironment()
    self.statement.checkType(environment)
    if self.next:
      self.next.checkType(environment)
    return environment
  def execute(self,environment={}):
    self.statement.execute(environment)
    if self.next:
      self.next.execute(environment)
