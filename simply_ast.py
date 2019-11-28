import random
from simply_arm import simply_arm_template

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
    self.address = -1
  def toString(self,prepend):
    return self.name+" (*"+str(self.address)+")\n"
  def getType(self,environment):
    assert self.name in environment, "Variable "+self.name+" referenced before assignment OR initialized locally"
    return environment[self.name]
  def assignMemory(self,environment,address):
    self.address = environment[self.name]
  def compile(self):
    return ""
  def evaluate(self,environment):
    assert self.name in environment, "Variable "+self.name+" referenced before assignment"
    return environment[self.name]

class ASTIntegerConstant:
  def __init__(self,value):
    self.value = value
    self.address = -1
  def toString(self,prepend):
    return str(self.value)+" (*"+str(self.address)+")\n"
  def getType(self,environment):
    return "int"
  def assignMemory(self,environment,address):
    self.address = address
  def compile(self):
    return "  MOV R0, #{:d}\n  LDR R1, =var{:d}\n  STR R0, [R1]\n".format(self.value,self.address)
  def evaluate(self,environment):
    return self.value

class ASTBooleanConstant:
  def __init__(self,value):
    self.value = value
    self.address = -1
  def toString(self,prepend):
    return str(self.value)+" (*"+str(self.address)+")\n"
  def getType(self,environment):
    return "bool"
  def assignMemory(self,environment,address):
    self.address = address
  def compile(self):
    return "  MOV R0, #{:d}\n  LDR R1, =var{:d}\n  STR R0, [R1]\n".format(int(self.value),self.address)
  def evaluate(self,environment):
    return self.value

class ASTBinaryOperator:
  def __init__(self,operator,operand1,operand2):
    self.operator = operator
    self.operand1 = operand1
    self.operand2 = operand2
    self.address = -1
  def toString(self,prepend):
    string = "{} (*{})\n".format(self.operator,self.address)
    string += prepend+"├─"+self.operand1.toString(prepend+"│ ")
    string += prepend+"└─"+self.operand2.toString(prepend+"  ")
    return string
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
  def assignMemory(self,environment,address):
    self.address = address
    self.operand1.assignMemory(environment,address+1)
    self.operand2.assignMemory(environment,address+2)
  def compile(self):
    id = unique_id()
    if self.operator in ["+","-","*","//","%","<",">","<=",">=","==","!="]:
      # both operands must be evaluated
      string = self.operand1.compile()
      string += self.operand2.compile()
      string += "  LDR R1, =var{:d}\n  LDR R1, [R1]\n".format(self.operand1.address)
      string += "  LDR R2, =var{:d}\n  LDR R2, [R2]\n".format(self.operand2.address)
      if self.operator=="+":
        string += "  ADD R0, R1, R2\n"
      elif self.operator=="-":
        string += "  SUB R0, R1, R2\n"
      elif self.operator=="*":
        string += "  MOV R0, #0\n.loopmulcond{}:\n  CMP R2, #0\n  BEQ .loopmulend{}\n  ADD R0, R0, R1\n  SUB R2, #1\n  B .loopmulcond{}\n.loopmulend{}:\n".format(id,id,id,id)
      elif self.operator in ["//","%"]:
        string += "  MOV R0, #0\n.loopdivcond{}:\n  CMP R1, R2\n  BMI .loopdivend{}\n  SUB R1, R1, R2\n  ADD R0, #1\n  B .loopdivcond{}\n.loopdivend{}:\n".format(id,id,id,id)
        if self.operator=="%":
          string += "  MOV R0, R1\n"
      elif self.operator=="==":
        string += "  MOV R0, #1\n  CMP R1, R2\n  BEQ .true{}\n  MOV R0, #0\n.true{}:\n".format(id,id)
      elif self.operator=="!=":
        string += "  MOV R0, #0\n  CMP R1, R2\n  BEQ .false{}\n  MOV R0, #1\n.false{}:\n".format(id,id)
      elif self.operator=="<":
        string += "  MOV R0, #1\n  CMP R1, R2\n  BMI .true{}\n  MOV R0, #0\n.true{}:\n".format(id,id)
      elif self.operator==">":
        string += "  MOV R0, #1\n  CMP R2, R1\n  BMI .true{}\n  MOV R0, #0\n.true{}:\n".format(id,id)
      elif self.operator=="<=":
        string += "  MOV R0, #1\n  CMP R2, R1\n  BPL .true{}\n  MOV R0, #0\n.true{}:\n".format(id,id)
      elif self.operator==">=":
        string += "  MOV R0, #1\n  CMP R1, R2\n  BPL .true{}\n  MOV R0, #0\n.true{}:\n".format(id,id)
      else:
        string += "  TODOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO\n"
    elif self.operator in ["and","or"]:
      # first operand must be evaluated
      string = self.operand1.compile()
      string += "  LDR R0, =var{:d}\n  LDR R0, [R0]\n".format(self.operand1.address)
      if self.operator=="and":
        string += "  CMP R0, #0\n  BEQ .onlyone{}\n".format(id)
      else:
        string += "  CMP R0, #1\n  BEQ .onlyone{}\n".format(id)
      string += self.operand2.compile()
      string += "  LDR R0, =var{:d}\n  LDR R0, [R0]\n".format(self.operand2.address)
      string += ".onlyone{}:\n".format(id)
    else:
      assert False, "unknown operator "+self.operator
    string += "  LDR R3, =var{:d}\n  STR R0, [R3]\n".format(self.address)
    return string

  def evaluate(self,environment):
    eval1 = self.operand1.evaluate(environment)
    eval2 = self.operand2.evaluate(environment)
    return eval(str(eval1)+" "+self.operator+" "+str(eval2))

class ASTBooleanNot:
  def __init__(self,operand):
    self.operand = operand
    self.address = -1
  def toString(self,prepend):
    string = "not\n"
    string += prepend+"└─"+self.operand.toString(prepend+"  ")
    return string
  def getType(self,environment):
    type = self.operand.getType(environment)
    assert type=="bool","Expression ("+str(self.operand)+") should be bool"
    return "bool"
  def assignMemory(self,environment,address):
    self.address = address
    self.operand.assignMemory(environment,address+1)
  def compile(self):
    string = self.operand.compile()
    string += "  LDR R0, =var{}\n  LDR R0, [R0]\n".format(self.operand.address)
    string += "  MOV R1, #1\n  SUB R0, R1, R0\n"
    string += "  LDR R1, =var{}\n  STR R0, [R1]\n".format(self.address)
    return string
  def evaluate(self,environment):
    return not self.operand.evaluate(environment)

class ASTNop:
  def __init__(self):
    self.local_environment = {}
  def toString(self,prepend):
    return "Nop\n"
  def checkType(self,environment):
    if environment=={}:
      self.local_environment = environment
  def assignMemory(self,environment,address=0):
    if environment=={}:
      assert address==0, "incoherent adress for empty environment"
  def compile(self):
    return ""
  def execute(self,environment):
    pass

class ASTAssignment:
  def __init__(self,name,expression):
    self.name = name
    self.expression = expression
    self.local_environment = {}
    self.address = -1
  def toString(self,prepend):
    string = "Assignment\n"
    string += prepend+"├i─{} (*{})\n".format(str(self.name),self.address)
    string += prepend+"└─"+self.expression.toString(prepend+"  ")
    return string
  def checkType(self,environment):
    type = self.expression.getType(environment)
    if self.name in environment:
      assert environment[self.name]==type, "Wrong extression type "+type+" for variable "+self.name
    else:
      environment[self.name] = type
  def assignMemory(self,environment,address=0):
    if environment=={}:
      assert address==0, "incoherent adress for empty environment"
    if self.local_environment!={}:
      environment = environment.copy()
      for name in self.local_environment:
        environment[name] = address
        address += 1
    self.expression.assignMemory(environment,address)
    self.address = environment[self.name]
  def compile(self):
    string = self.expression.compile()
    string += "  LDR R0, =var{}\n  LDR R0, [R0]\n".format(self.expression.address)
    string += "  LDR R1, =var{}\n  STR R0, [R1]\n".format(self.address)
    return string
  def execute(self,environment):
    value = self.expression.evaluate(environment)
    environment[self.name] = value
    print(self.name,"<-",value)

class ASTPrint:
  def __init__(self,expression):
    self.expression = expression
    self.local_environment = {}
  def toString(self,prepend):
    string = "Print\n"
    string += prepend+"└─"+self.expression.toString(prepend+"  ")
    return string
  def checkType(self,environment):
    self.type = self.expression.getType(environment)
  def assignMemory(self,environment,address=0):
    if environment=={}:
      assert address==0, "incoherent adress for empty environment"
    if self.local_environment!={}:
      environment = environment.copy()
      for name in self.local_environment:
        environment[name] = address
        address += 1
    self.expression.assignMemory(environment,address)
  def compile(self):
    string = self.expression.compile()
    string += "  LDR R0, =var{}\n  LDR R0, [R0]\n  BL .print{}\n".format(self.expression.address,self.type)
    return string
  def execute(self,environment):
    value = self.expression.evaluate(environment)
    print("Affichage :",value)

class ASTWhile:
  def __init__(self,condition,statement):
    self.condition = condition
    self.statement = statement
    self.local_environment = {}
  def toString(self,prepend):
    string = "While\n"
    string += prepend+"├c─"+self.condition.toString(prepend+"│  ")
    string += prepend+"└─"+self.statement.toString(prepend+"  ")
    return string
  def checkType(self,environment):
    type = self.condition.getType(environment)
    assert type=="bool", "Condition ("+self.condition.toString("")+") should be bool"
    environment_copy = environment.copy()
    self.statement.checkType(environment_copy)
    for name in environment_copy:
      if name not in environment:
        print("Warning : variable "+name+" is local to WHILE loop")
        self.statement.local_environment[name] = environment_copy[name]
  def assignMemory(self,environment,address=0):
    if environment=={}:
      assert address==0, "incoherent adress for empty environment"
    if self.local_environment!={}:
      environment = environment.copy()
      for name in self.local_environment:
        environment[name] = address
        address += 1
    self.condition.assignMemory(environment,address)
    self.statement.assignMemory(environment,address)
  def compile(self):
    id = unique_id()
    string = ".loopcond"+id+":\n"
    string += self.condition.compile()
    string += "  LDR R0, =var{}\n  LDR R0, [R0]\n".format(self.condition.address)
    string += "  CMP R0, #0\n"
    string += "  BEQ .loopend"+id+"\n"
    string += self.statement.compile()
    string += "  B .loopcond"+id+"\n"
    string += ".loopend"+id+":\n"
    return string
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
  def toString(self,prepend):
    string = "Branch\n"
    string += prepend+"├c─"+self.condition.toString(prepend+"│  ")
    string += prepend+"├i─"+self.if_statement.toString(prepend+"│  ")
    string += prepend+"└e─"+self.else_statement.toString(prepend+"   ")
    return string
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
  def assignMemory(self,environment,address=0):
    if environment=={}:
      assert address==0, "incoherent adress for empty environment"
    if self.local_environment!={}:
      environment = environment.copy()
      for name in self.local_environment:
        environment[name] = address
        address += 1
    self.condition.assignMemory(environment,address)
    self.if_statement.assignMemory(environment,address)
    self.else_statement.assignMemory(environment,address)
  def compile(self):
    id = unique_id()
    string = self.condition.compile()
    string += "  LDR R0, =var{}\n  LDR R0, [R0]\n".format(self.condition.address)
    string += "  CMP R0, #0\n"
    string += "  BEQ .branchelse"+id+"\n"
    string += self.if_statement.compile()
    string += "  B .branchend"+id+"\n"
    string += ".branchelse"+id+":\n"
    string += self.else_statement.compile()
    string += ".branchend"+id+":\n"
    return string
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
  def toString(self,prepend):
    string = "Sequence\n"
    prepend = prepend[:-2]
    string += prepend+"┌─┘\n"
    string += prepend+"├─"+self.statement1.toString(prepend+"│ ")
    string += prepend+"└─"+self.statement2.toString(prepend+"  ")
    return string
  def checkType(self,environment):
    if environment=={}:
      self.local_environment = environment
    self.statement1.checkType(environment)
    self.statement2.checkType(environment)
  def assignMemory(self,environment,address=0):
    if environment=={}:
      assert address==0, "incoherent adress for empty environment"
    if self.local_environment!={}:
      environment = environment.copy()
      for name in self.local_environment:
        environment[name] = address
        address += 1
    self.statement1.assignMemory(environment,address)
    self.statement2.assignMemory(environment,address)
  def compile(self):
    string = self.statement1.compile()
    string += self.statement2.compile()
    return string
  def execute(self,environment):
    self.statement1.execute(environment)
    self.statement2.execute(environment)

class ASTRoot:
  def __init__(self,root):
    self.root = root
    self.py_filename = "<unknown.py>"
    self.py_code = "<not given>"
  def __repr__(self):
    return self.toString("")
  def process(self):
    self.root.checkType({})
    self.root.assignMemory({})
    return simply_arm_template.format(self.py_filename,
                                      "// "+self.py_code.replace("\n","\n// "),
                                      self.toString("// "),
                                      self.root.compile())
  def toString(self,prepend):
    string = prepend+"Root\n"
    string += prepend+"└─"
    string += self.root.toString(prepend+"  ")
    return string
