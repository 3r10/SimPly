import random
from simply_arm import simply_arm_template, arm_fast_multiplication_template, arm_fast_division_template

class ASTEnvironment:
  def __init__(self,parent=None):
    self.parent = parent
    self.children = []
    self.variables = {}
    self.constants = {}
    self.nb_tmp = 0
    self.tmp_counter = 0
    self.label_counter = 0
  def __repr__(self):
    return str(self.variables)
  def getVariableType(self,name):
    if name in self.variables:
      return self.variables[name]
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
  def setConstant(self,value):
    if self.parent:
      return self.parent.setConstant(value)
    if value not in self.constants:
      self.constants[value] = "const_"+str(value)
    return self.constants[value]
  def increaseTmpCounter(self):
    if self.parent:
      return self.parent.increaseTmpCounter()
    self.tmp_counter += 1
    if self.tmp_counter>self.nb_tmp:
      self.nb_tmp = self.tmp_counter
    return self.tmp_counter
  def decreaseTmpCounter(self):
    if self.parent:
      return self.parent.decreaseTmpCounter()
    self.tmp_counter -= 1
    return self.tmp_counter
  def resetTmpCounter(self):
    if self.parent:
      return self.parent.resetTmpCounter()
    self.tmp_counter = 0
  def increaseLabelCounter(self):
    if self.parent:
      return self.parent.increaseLabelCounter()
    self.label_counter += 1
    return self.label_counter
  def getAllVariables(self):
    variables = []
    for variable in self.variables:
      variables.append(variable)
    for child in self.children:
      child_variables = child.getAllVariables()
      for variable in child_variables:
        if variable not in variables:
          variables.append(variable)
    return variables
  def toArmData(self):
    data = ""
    for variable in self.getAllVariables():
      data += "var_"+variable+":\n  .word 0\n"
    for tmp in range(1,self.nb_tmp+1):
      data += "tmp_"+str(tmp)+":\n  .word 0\n"
    for constant in self.constants:
      if isinstance(constant,int):
        data += "{}:\n  .word {:d}\n".format(self.constants[constant],constant)
      else:
        data += "{}:\n  .word {:d}\n".format(self.constants[constant],[0,1][constant])
    return data

class ASTVariable:
  def __init__(self,name):
    self.name = name
  def toString(self,prepend):
    return "{}\t\tid:{}\n".format(self.name,self.id)
  def getType(self,environment):
    type = environment.getVariableType(self.name)
    assert type!=None, "Variable "+self.name+" referenced before assignment OR initialized locally"
    return type
  def setId(self,environment):
    self.id = 'var_'+self.name
  def compile(self):
    return ""

class ASTIntegerConstant:
  def __init__(self,value):
    self.value = value
  def toString(self,prepend):
    return "{}\t\tid:{}\n".format(self.value,self.id)
  def getType(self,environment):
    return "int"
  def setId(self,environment):
    self.id = environment.setConstant(self.value)
  def compile(self):
    return ""

class ASTBooleanConstant:
  def __init__(self,value):
    self.value = value
  def toString(self,prepend):
    return "{}\t\tid:{}\n".format(self.value,self.id)
  def getType(self,environment):
    return "bool"
  def setId(self,environment):
    self.id = environment.setConstant(self.value)
  def compile(self):
    return ""

class ASTBinaryOperator:
  def __init__(self,operator,operand1,operand2):
    self.operator = operator
    self.operand1 = operand1
    self.operand2 = operand2
  def toString(self,prepend):
    string = "{}\t\tid:{},label:{}\n".format(self.operator,self.id,self.label)
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
  def setId(self,environment):
    self.label = 'op_'+str(environment.increaseLabelCounter())
    self.id = 'tmp_'+str(environment.increaseTmpCounter())
    self.operand1.setId(environment)
    self.operand2.setId(environment)
  def compile(self):
    if self.operator in ["+","-","*","//","%","<",">","<=",">=","==","!="]:
      # both operands must be evaluated
      string = self.operand1.compile()
      string += self.operand2.compile()
      string += "  LDR R1, ={}\n  LDR R1, [R1]\n".format(self.operand1.id)
      string += "  LDR R2, ={}\n  LDR R2, [R2]\n".format(self.operand2.id)
      if self.operator=="+":
        string += "  ADD R0, R1, R2\n"
      elif self.operator=="-":
        string += "  SUB R0, R1, R2\n"
      elif self.operator=="*":
        string += arm_fast_multiplication_template.format(label=self.label)
      elif self.operator in ["//","%"]:
        string += arm_fast_division_template.format(label=self.label)
        if self.operator=="%":
          string += "  MOV R0, R1\n"
      elif self.operator=="==":
        string += "  MOV R0, #1\n  CMP R1, R2\n  BEQ .{}_true\n  MOV R0, #0\n.{}_true:\n".format(self.label,self.label)
      elif self.operator=="!=":
        string += "  MOV R0, #0\n  CMP R1, R2\n  BEQ .{}_false\n  MOV R0, #1\n.{}_false:\n".format(self.label,self.label)
      elif self.operator=="<":
        string += "  MOV R0, #1\n  CMP R1, R2\n  BMI .{}_true\n  MOV R0, #0\n.{}_true:\n".format(self.label,self.label)
      elif self.operator==">":
        string += "  MOV R0, #1\n  CMP R2, R1\n  BMI .{}_true\n  MOV R0, #0\n.{}_true:\n".format(self.label,self.label)
      elif self.operator=="<=":
        string += "  MOV R0, #1\n  CMP R2, R1\n  BPL .{}_true\n  MOV R0, #0\n.{}_true:\n".format(self.label,self.label)
      elif self.operator==">=":
        string += "  MOV R0, #1\n  CMP R1, R2\n  BPL .{}_true\n  MOV R0, #0\n.{}_true:\n".format(self.label,self.label)
      else:
        assert False, "unknown operator "+self.operator
    elif self.operator in ["and","or"]:
      # first operand must be evaluated
      string = self.operand1.compile()
      string += "  LDR R0, ={}\n  LDR R0, [R0]\n".format(self.operand1.id)
      if self.operator=="and":
        string += "  CMP R0, #0\n  BEQ .onlyone_{}\n".format(self.label)
      else:
        string += "  CMP R0, #1\n  BEQ .onlyone_{}\n".format(self.label)
      string += self.operand2.compile()
      string += "  LDR R0, ={}\n  LDR R0, [R0]\n".format(self.operand2.id)
      string += ".onlyone_{}:\n".format(self.label)
    else:
      assert False, "unknown operator "+self.operator
    string += "  LDR R3, ={}\n  STR R0, [R3]\n".format(self.id)
    return string

class ASTBooleanNot:
  def __init__(self,operand):
    self.operand = operand
  def toString(self,prepend):
    string = "not\t\tid:{}\n".format(self.id)
    string += prepend+"└─"+self.operand.toString(prepend+"  ")
    return string
  def getType(self,environment):
    type = self.operand.getType(environment)
    assert type=="bool","Expression ("+str(self.operand)+") should be bool"
    return "bool"
  def setId(self,environment):
    self.id = 'tmp_'+str(environment.increaseTmpCounter())
    self.operand.setId(environment)
  def compile(self):
    string = self.operand.compile()
    string += "  LDR R0, ={}\n  LDR R0, [R0]\n".format(self.operand.id)
    string += "  MOV R1, #1\n  SUB R0, R1, R0\n"
    string += "  LDR R1, ={}\n  STR R0, [R1]\n".format(self.id)
    return string

class ASTNop:
  def __init__(self):
    pass
  def toString(self,prepend):
    return "Nop\n"
  def checkType(self,environment):
    pass
  def setId(self,environment):
    pass
  def compile(self):
    return ""

class ASTAssignment:
  def __init__(self,name,expression):
    self.name = name
    self.expression = expression
  def toString(self,prepend):
    string = "Assignment\n"
    string += prepend+"├i─{}\t\tid:{}\n".format(str(self.name),self.id)
    string += prepend+"└─"+self.expression.toString(prepend+"  ")
    return string
  def checkType(self,environment):
    expression_type = self.expression.getType(environment)
    name_type = environment.getVariableType(self.name)
    if name_type:
      assert expression_type==name_type, "Wrong extression type "+expression_type+" for variable "+self.name
    else:
      environment.setVariableType(self.name,expression_type)
  def setId(self,environment):
    self.id = 'var_'+self.name
    environment.resetTmpCounter()
    self.expression.setId(environment)
  def compile(self):
    string = self.expression.compile()
    string += "  LDR R0, ={}\n  LDR R0, [R0]\n".format(self.expression.id)
    string += "  LDR R1, ={}\n  STR R0, [R1]\n".format(self.id)
    return string

class ASTPrint:
  def __init__(self,expression):
    self.expression = expression
  def toString(self,prepend):
    string = "Print\n"
    string += prepend+"└─"+self.expression.toString(prepend+"  ")
    return string
  def checkType(self,environment):
    self.type = self.expression.getType(environment)
  def setId(self,environment):
    environment.resetTmpCounter()
    self.expression.setId(environment)
  def compile(self):
    string = self.expression.compile()
    string += "  LDR R0, ={}\n  LDR R0, [R0]\n  BL .print{}\n".format(self.expression.id,self.type)
    return string

class ASTWhile:
  def __init__(self,condition,statement):
    self.condition = condition
    self.statement = statement
    self.environment = None
  def toString(self,prepend):
    string = "While\t\tlabel:{},localvars:{}\n".format(self.label,self.environment)
    string += prepend+"├c─"+self.condition.toString(prepend+"│  ")
    string += prepend+"└─"+self.statement.toString(prepend+"  ")
    return string
  def checkType(self,environment):
    type = self.condition.getType(environment)
    assert type=="bool", "Condition ("+self.condition.toString("")+") should be bool"
    self.environment = environment.fork()
    self.statement.checkType(self.environment)
    for name in self.environment.variables:
      print("Warning : variable "+name+" is local to WHILE loop")
  def setId(self,environment):
    self.label = 'while_'+str(environment.increaseLabelCounter())
    environment.resetTmpCounter()
    self.condition.setId(environment)
    self.statement.setId(self.environment)
  def compile(self):
    string = ".{}_condition:\n".format(self.label)
    string += self.condition.compile()
    string += "  LDR R0, ={}\n  LDR R0, [R0]\n".format(self.condition.id)
    string += "  CMP R0, #0\n"
    string += "  BEQ .{}_end\n".format(self.label)
    string += self.statement.compile()
    string += "  B .{}_condition\n".format(self.label)
    string += ".{}_end:\n".format(self.label)
    return string

class ASTBranch:
  def __init__(self,condition,if_statement,else_statement):
    self.condition = condition
    self.if_statement = if_statement
    self.else_statement = else_statement
    self.if_environment = None
    self.else_environment = None
  def toString(self,prepend):
    string = "Branch\t\tlabel:{},localvars:{},{}\n".format(self.label,self.if_environment,self.else_environment)
    string += prepend+"├c─"+self.condition.toString(prepend+"│  ")
    string += prepend+"├i─"+self.if_statement.toString(prepend+"│  ")
    string += prepend+"└e─"+self.else_statement.toString(prepend+"   ")
    return string
  def checkType(self,environment):
    type = self.condition.getType(environment)
    assert type=="bool", "Condition ("+str(self.condition)+") should be bool"
    self.if_environment = environment.fork()
    self.if_statement.checkType(self.if_environment)
    self.else_environment = environment.fork()
    self.else_statement.checkType(self.else_environment)
    self.if_environment.merge(self.else_environment)
  def setId(self,environment):
    self.label = 'branch_'+str(environment.increaseLabelCounter())
    environment.resetTmpCounter()
    self.condition.setId(environment)
    self.if_statement.setId(self.if_environment)
    self.else_statement.setId(self.else_environment)
  def compile(self):
    string = self.condition.compile()
    string += "  LDR R0, ={}\n  LDR R0, [R0]\n".format(self.condition.id)
    string += "  CMP R0, #0\n"
    string += "  BEQ .{}_else\n".format(self.label)
    string += self.if_statement.compile()
    string += "  B .{}_end\n".format(self.label)
    string += ".{}_else:\n".format(self.label)
    string += self.else_statement.compile()
    string += ".{}_end:\n".format(self.label)
    return string

class ASTSequence:
  def __init__(self,statement1,statement2):
    self.statement1 = statement1
    self.statement2 = statement2
  def toString(self,prepend):
    string = "Sequence\n"
    prepend = prepend[:-2]
    string += prepend+"┌─┘\n"
    string += prepend+"├─"+self.statement1.toString(prepend+"│ ")
    string += prepend+"└─"+self.statement2.toString(prepend+"  ")
    return string
  def checkType(self,environment):
    self.statement1.checkType(environment)
    self.statement2.checkType(environment)
  def setId(self,environment):
    self.statement1.setId(environment)
    self.statement2.setId(environment)
  def compile(self):
    string = self.statement1.compile()
    string += self.statement2.compile()
    return string

class ASTRoot:
  def __init__(self,root):
    self.root = root
    self.py_filename = "<unknown.py>"
    self.py_code = "<not given>"
    self.environment = ASTEnvironment()
  def __repr__(self):
    return self.toString("")
  def process(self):
    self.root.checkType(self.environment)
    self.root.setId(self.environment)
    arm_code = self.root.compile()
    arm_data = self.environment.toArmData()
    return simply_arm_template.format(filename=self.py_filename,
                                      source="// "+self.py_code.replace("\n","\n// "),
                                      ast=self.toString("// "),
                                      arm_code=arm_code,
                                      arm_data=arm_data)
  def toString(self,prepend):
    string = prepend+"Root\t\tlocalvars:{}\n".format(self.environment)
    string += prepend+"└─"
    string += self.root.toString(prepend+"  ")
    return string
