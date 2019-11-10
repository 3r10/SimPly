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
  def toHtml(self):
    return str(self.name)
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
  def toHtml(self):
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
  def toHtml(self):
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
  def toHtml(self):
    html = self.operand1.toHtml()
    if self.operator in ["not","and","or"]:
      html +=' <span style="color:blue">'+self.operator+'</span> '
    else:
      html +=self.operator.replace(">","&gt;").replace("<","&lt;")
    html += self.operand2.toHtml()
    return html
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
  def toHtml(self):
    return '<span style="color:blue">not</span> '+self.expression.toHtml()
  def toGraph(self,dot):
    name = "Element"+str(random.randint(0,1000000000000))
    dot.node(name,self.operator, shape='box')
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
  def toHtml(self):
    return "("+self.expression.toHtml()+")"
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

class ASTNode:
  def setLine(self,number):
    self.line_number = number
    self.indent = 0
  def doIndent(self):
    self.indent += 1
  def __repr__(self):
    return str(self.line_number)+"\t"*(self.indent+1)
  def toHtml(self):
    return '<span style="color:grey; font-style: italic">'+str(self.line_number)+"</span>\t"+"  "*self.indent
  def execute(self,environment):
    print("Line ",self.line_number,": ",end="")

class ASTStatement(ASTNode):
  def __init__(self,id,expression):
    self.type = "statement"
    self.id = id
    self.expression = expression
  def __repr__(self):
    return ASTNode.__repr__(self)+self.id+" = "+str(self.expression)+"\n"
  def toHtml(self):
    return ASTNode.toHtml(self)+self.id+" = "+str(self.expression)+"\n"
  def toGraph(self,dot,is_deep=False):
    name = "S"+str(self.line_number)
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
    ASTNode.execute(self,environment)
    value = self.expression.evaluate(environment)
    environment[self.id] = value
    print(self.id,"<-",value)

class ASTWhile(ASTNode):
  def __init__(self,condition):
    self.type = "while"
    self.condition = condition
    self.sequence = ASTSequence()
  def addNode(self,node):
    self.sequence.addNode(node)
  def __repr__(self):
    return ASTNode.__repr__(self)+"while "+str(self.condition)+":\n"+str(self.sequence)
  def toHtml(self):
    return ASTNode.toHtml(self)+'<span style="color:blue">while</span> '+self.condition.toHtml()+":\n"+self.sequence.toHtml()
  def toGraph(self,dot,is_deep=False):
    name = "W"+str(self.line_number)
    dot.node(name,"While")
    if is_deep:
      condition_name = self.condition.toGraph(dot)
    else:
      condition_name = "C"+str(self.line_number)
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
      ASTNode.execute(self,environment)
      print("Condition : T")
      self.sequence.execute(environment)
    ASTNode.execute(self,environment)
    print("Condition : F")

class ASTIf(ASTNode):
  def __init__(self,type,condition):
    self.type = type
    self.condition = condition
    self.sequence = ASTSequence()
    self.next = None
  def addNode(self,node):
    if self.next:
      self.next.addNode(node)
    else:
      self.sequence.addNode(node)
  def setNext(self,node):
    if self.next:
      self.next.setNext(node)
    else:
      self.next = node
  def __repr__(self):
    string = ASTNode.__repr__(self)+self.type+" "+str(self.condition)+":\n"
    string += str(self.sequence)
    if self.next:
      string += str(self.next)
    return string
  def toHtml(self):
    string = ASTNode.toHtml(self)+'<span style="color:blue">'+self.type+'</span> '+self.condition.toHtml()+":\n"
    string += self.sequence.toHtml()
    if self.next:
      string += self.next.toHtml()
    return string
  def toGraph(self,dot,is_deep=False):
    name = "B"+str(self.line_number)
    dot.node(name,"Branch")
    if is_deep:
      condition_name = self.condition.toGraph(dot)
    else:
      condition_name = "C"+str(self.line_number)
      dot.node(condition_name,str(self.condition),shape='box')
    dot.edge(name,condition_name,"condition")
    if_name = self.sequence.toGraph(dot,is_deep)
    dot.edge(name,if_name,"if")
    if self.next:
      else_name = self.next.toGraph(dot,is_deep)
      dot.edge(name,else_name,"else")
    return name
  def checkType(self,environment):
    state,type = self.condition.getStateType(environment)
    assert type=="bool", "Condition ("+str(self.condition)+") should be bool"
    self.sequence.checkType(environment)
    if self.next:
      self.next.checkType(environment)
    return environment
  def execute(self,environment):
    ASTNode.execute(self,environment)
    condition = self.condition.evaluate(environment)
    print(self.type,condition)
    if condition:
      self.sequence.execute(environment)
    elif self.next:
      self.next.execute(environment)

class ASTElse(ASTNode):
  def __init__(self):
    self.type = "else"
    self.sequence = ASTSequence()
  def addNode(self,node):
    self.sequence.addNode(node)
  def __repr__(self):
    return ASTNode.__repr__(self)+'else:\n'+str(self.sequence)
  def toHtml(self):
    string = ASTNode.toHtml(self)+'<span style="color:blue">else</span>:\n'
    string += self.sequence.toHtml()
    return string
  def toGraph(self,dot,is_deep=False):
    sequence_name = self.sequence.toGraph(dot,is_deep)
    return sequence_name
  def checkType(self,environment):
    self.sequence.checkType(environment)
    return environment
  def execute(self,environment):
    ASTNode.execute(self,environment)
    print("Else")
    self.sequence.execute(environment)

class ASTSequence:
  def __init__(self):
    self.nodes = []
  def addNode(self,node):
    if self.nodes==[]:
      self.nodes.append(node)
    elif self.nodes[-1].indent==node.indent:
      if node.type in ["elif", "else"] and self.nodes[-1].type in ["if","elif"]:
        self.nodes[-1].setNext(node)
      else:
        self.nodes.append(node)
    else:
      self.nodes[-1].addNode(node)
  def __repr__(self):
    repr = ""
    for node in self.nodes:
      repr += str(node)
    return repr
  def toHtml(self):
    string = ""
    for node in self.nodes:
      string += node.toHtml()
    return string
  def toGraph(self,dot,is_deep=False):
    name = "Seq"+str(self.nodes[0].line_number)
    dot.node(name,"Sequence")
    for node in self.nodes:
      node_name = node.toGraph(dot,is_deep)
      dot.edge(name,node_name)
    return name
  def checkType(self,environment=ASTEnvironment()):
    for node in self.nodes:
      node.checkType(environment)
    return environment
  def execute(self,environment={}):
    for node in self.nodes:
      node.execute(environment)
