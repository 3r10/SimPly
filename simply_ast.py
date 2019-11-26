from graphviz import Digraph
import random

def unique_id():
  return("Element"+str(random.randint(0,1000000000000)))


def dict2graph(dot,dictionary):
  string = ""
  for key in dictionary:
    string += str(key)+":"+str(dictionary[key])+"\n"
  if dictionary!={}:
    string = string[:-1]
  env_name = unique_id()
  dot.node(env_name,string,shape="note")
  return env_name

class ASTVariable:
  def __init__(self,name):
    self.name = name
  def __repr__(self):
    return self.name
  def toGraph(self,dot):
    name = unique_id()
    dot.node(name,self.name, shape='box')
    return name
  def getType(self,environment):
    assert self.name in environment, "Variable "+self.name+" referenced before assignment OR initialized locally"
    return environment[self.name]
  def evaluate(self,environment):
    assert self.name in environment, "Variable "+self.name+" referenced before assignment"
    return environment[self.name]

class ASTIntegerConstant:
  def __init__(self,value):
    self.value = value
  def __repr__(self):
    return str(self.value)
  def toGraph(self,dot):
    name = unique_id()
    dot.node(name,str(self.value), shape='box')
    return name
  def getType(self,environment):
    return "int"
  def evaluate(self,environment):
    return self.value

class ASTBooleanConstant:
  def __init__(self,value):
    self.value = value
  def __repr__(self):
    return str(self.value)
  def toGraph(self,dot):
    name = unique_id()
    dot.node(name,str(self.value), shape='box')
    return name
  def getType(self,environment):
    return "bool"
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
    name = unique_id()
    dot.node(name,self.operator, shape='box')
    name_operand1 = self.operand1.toGraph(dot)
    dot.edge(name,name_operand1)
    name_operand2 = self.operand2.toGraph(dot)
    dot.edge(name,name_operand2)
    return name
  def getType(self,environment):
    type1 = self.operand1.getType(environment)
    type2 = self.operand2.getType(environment)
    if self.operator in ["+","-","*","//","%"]:
      assert type1=="int","Expression ("+str(self.operand1)+") should be int"
      assert type2=="int","Expression ("+str(self.operand2)+") should be int"
      return "int"
    if self.operator in ["<",">","<=",">="]:
      assert type1=="int","Expression ("+str(self.operand1)+") should be int"
      assert type2=="int","Expression ("+str(self.operand2)+") should be int"
      return "bool"
    if self.operator in ["==","!="]:
      assert type1==type2,"Expressions ("+str(self.operand1)+") and ("+str(self.operand2)+") should be of same type"
      return "bool"
    assert type1=="bool", "Expression ("+str(self.operand1)+") should be bool"
    assert type2=="bool", "Expression ("+str(self.operand2)+") should be bool"
    return "bool"
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
    name = unique_id()
    dot.node(name,"not", shape='box')
    name_operand = self.operand.toGraph(dot)
    dot.edge(name,name_operand)
    return name
  def getType(self,environment):
    type = self.operand.getType(environment)
    assert type=="bool","Expression ("+str(self.operand)+") should be bool"
    return "bool"
  def evaluate(self,environment):
    return not self.operand.evaluate(environment)

class ASTExpressionGroup:
  def __init__(self,expression):
    self.expression = expression
  def __repr__(self):
    return "("+str(self.expression)+")"
  def toGraph(self,dot):
    name = unique_id()
    dot.node(name,"( )", shape='box')
    name_expression = self.expression.toGraph(dot)
    dot.edge(name,name_expression)
    return name
  def getType(self,environment):
    return self.expression.getType(environment)
  def evaluate(self,environment):
    return self.expression.evaluate(environment)

class ASTNop:
  def __init__(self):
    self.local_environment = {}
  def __repr__(self):
    return ""
  def toGraph(self,dot,is_deep=False):
    name = unique_id()
    dot.node(name,"NOP", shape='box')
    return name
  def checkType(self,environment):
    pass
  def execute(self,environment):
    pass

class ASTAssignment:
  def __init__(self,name,expression):
    self.name = name
    self.expression = expression
    self.local_environment = {}
  def __repr__(self):
    return self.name+" = "+str(self.expression)+"\n"
  def toGraph(self,dot,is_deep=False):
    name = unique_id()
    if is_deep:
      dot.node(name,self.name+" =", shape='box')
      name_expression = self.expression.toGraph(dot)
      dot.edge(name,name_expression)
    else:
      dot.node(name,self.name+" = "+str(self.expression), shape='box')
    if self.local_environment!={}:
      env_name = dict2graph(dot,self.local_environment)
      dot.edge(name,env_name,arrowhead="none")
    return name
  def checkType(self,environment):
    type = self.expression.getType(environment)
    if self.name in environment:
      assert environment[self.name]==type, "Wrong extression type "+type+" for variable "+self.name
    else:
      environment[self.name] = type
  def execute(self,environment):
    value = self.expression.evaluate(environment)
    environment[self.name] = value
    print(self.name,"<-",value)

class ASTWhile:
  def __init__(self,condition,statement):
    self.condition = condition
    self.statement = statement
    self.local_environment = {}
  def __repr__(self):
    return "while "+str(self.condition)+":\n"+str(self.statement)
  def toGraph(self,dot,is_deep=False):
    name = unique_id()
    dot.node(name,"While",shape="diamond")
    if is_deep:
      condition_name = self.condition.toGraph(dot)
    else:
      condition_name = unique_id()
      dot.node(condition_name,str(self.condition),shape='box')
    dot.edge(name,condition_name,"condition")
    statement_name = self.statement.toGraph(dot,is_deep)
    dot.edge(name,statement_name,"block")
    if self.local_environment!={}:
      env_name = dict2graph(dot,self.local_environment)
      dot.edge(name,env_name,arrowhead="none")
    return name
  def checkType(self,environment):
    type = self.condition.getType(environment)
    assert type=="bool", "Condition ("+str(self.condition)+") should be bool"
    environment_copy = environment.copy()
    self.statement.checkType(environment_copy)
    for name in environment_copy:
      if name not in environment:
        print("Warning : variable "+name+" is local to WHILE loop")
        self.statement.local_environment[name] = environment_copy[name]
  def execute(self,environment):
    while self.condition.evaluate(environment):
      print("Condition : T")
      self.statement.execute(environment)
    print("Condition : F")

class ASTBranch:
  def __init__(self,condition,if_statement,else_statement):
    self.condition = condition
    self.if_statement= if_statement
    self.else_statement= else_statement
    self.local_environment = {}
  def __repr__(self):
    string = "if "+str(self.condition)+":\n"+str(self.if_statement)
    string += "else...\n"+str(self.else_statement)
    return string
  def toGraph(self,dot,is_deep=False):
    name = unique_id()
    dot.node(name,"Branch",shape="diamond")
    if is_deep:
      condition_name = self.condition.toGraph(dot)
    else:
      condition_name = unique_id()
      dot.node(condition_name,str(self.condition),shape='box')
    dot.edge(name,condition_name,"condition")
    if_name = self.if_statement.toGraph(dot,is_deep)
    dot.edge(name,if_name,"if")
    else_name = self.else_statement.toGraph(dot,is_deep)
    dot.edge(name,else_name,"else")
    if self.local_environment!={}:
      env_name = dict2graph(dot,self.local_environment)
      dot.edge(name,env_name,arrowhead="none")
    return name
  def checkType(self,environment):
    type = self.condition.getType(environment)
    assert type=="bool", "Condition ("+str(self.condition)+") should be bool"
    if_environment = environment.copy()
    self.if_statement.checkType(if_environment)
    else_environment = environment.copy()
    self.else_statement.checkType(else_environment)
    for name in if_environment:
      if name not in environment:
        # each variable initialized in the IF block
        if name not in else_environment:
          print("Warning : variable "+name+" is local to a IF block")
          self.if_statement.local_environment[name] = if_environment[name]
        elif if_environment[name]!=else_environment[name]:
          print("Warning : variable "+name+" initialized with different types in IF/ELSE blocks\n  -> interpreted as local to each")
          self.if_statement.local_environment[name] = if_environment[name]
          self.else_statement.local_environment[name] = else_environment[name]
        else:
          environment[name] = if_environment[name]
    # variables initialized ONLY in the ELSE block
    for name in else_environment:
      if name not in environment and name not in if_environment:
        print("Warning : variable "+name+" is local to a ELSE block")
        self.else_statement.local_environment[name] = else_environment[name]
  def execute(self,environment):
    condition = self.condition.evaluate(environment)
    print("Condition :",condition)
    if condition:
      self.if_statement.execute(environment)
    else:
      self.else_statement.execute(environment)

class ASTSequence:
  def __init__(self,statement1,statement2):
    self.statement1 = statement1
    self.statement2 = statement2
    self.local_environment = {}
  def __repr__(self):
    string = str(self.statement)
    if self.next:
      string += str(self.next)
    return string
  def toGraph(self,dot,is_deep=False):
    name = unique_id()
    dot.node(name,"Sequence",shape="diamond")
    statement1_name = self.statement1.toGraph(dot,is_deep)
    dot.edge(name,statement1_name)
    statement2_name = self.statement2.toGraph(dot,is_deep)
    dot.edge(name,statement2_name)
    if self.local_environment!={}:
      env_name = dict2graph(dot,self.local_environment)
      dot.edge(name,env_name,arrowhead="none")
    return name
  def checkType(self,environment):
    self.statement1.checkType(environment)
    self.statement2.checkType(environment)
  def execute(self,environment):
    self.statement1.execute(environment)
    self.statement2.execute(environment)
