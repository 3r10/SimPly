simply_arm_template = """/*************************
 * Generated with SimPly *
 *************************/

/************************
 * Original source code *
 ************************/
// File : {}

{}
/************************
 * Abstract Syntax Tree *
 ************************/
{}
/*********************
 * ARM assembly code *
 *********************/

.global _start

_start:
/* Start of compiled part */
{}
/* End of compiled part */
end:
  MOV R7, #1  // syscall 1 : exit
  SWI 0

/* print "Functions" */
.printbool:
  CMP R0, #0
  BEQ .printfalse
  // print
  MOV R7, #4    // syscall 4 : write screen R0,R1,R2
  MOV R0, #1    // dest
  LDR R1, =true // pchar
  MOV R2, #5    // len of mess
  SWI 0         // syscall
  BX LR
.printfalse:
  // print
  MOV R7, #4    // syscall 4 : write screen R0,R1,R2
  MOV R0, #1    // dest
  LDR R1, =false // pchar
  MOV R2, #6    // len of mess
  SWI 0         // syscall
  BX LR

.printint:
  // zero case
  CMP R0, #0
  BNE .nonzero
  // print 0
  MOV R0, #48 // '0'
  LDR R1, =char
  STR R0, [R1]
  // print
  MOV R7, #4    // syscall 4 : write screen R0,R1,R2
  MOV R0, #1    // dest
  LDR R1, =char // pchar
  MOV R2, #1    // len of mess
  SWI 0         // syscall
  B .loopprintend
.nonzero:
  CMP R0, #0
  BPL .positive
  MOV R1, #-1
  MUL R0, R1
  PUSH {{R0}}
  // print -
  MOV R0, #45 // '-'
  LDR R1, =char
  STR R0, [R1]
  // print
  MOV R7, #4    // syscall 4 : write screen R0,R1,R2
  MOV R0, #1    // dest
  LDR R1, =char // pchar
  MOV R2, #1    // len of mess
  SWI 0         // syscall
  POP {{R0}}
.positive:
  // R1 : max n so 10^n<=R0
  // R2 : corresponding 10^n
  // R3 : 10^(n+1)
  MOV R1, #0
  MOV R2, #1
  MOV R3, #10
.loopexpcond:
  CMP R0, R3
  BMI .loopexpend
  // next candidate is OK :
  ADD R1, #1
  MOV R2, R3
  // R3 <- R3*10
  LSL R3, #2
  ADD R3, R2
  LSL R3, #1
  B .loopexpcond
.loopexpend:
.loopprintcond:
  CMP R1, #0
  BMI .loopprintend
  // R3 : next digit
  MOV R3, #0
.loopdigitcond:
  CMP R0, R2
  BMI .loopdigitend
  SUB R0, R2
  ADD R3, #1
  B .loopdigitcond
.loopdigitend:
  PUSH {{R0,R1}}
  // R3 is computed, put it in char
  ADD R3, #48 // add '0'
  LDR R1, =char
  STR R3, [R1]
  // print
  MOV R7, #4    // syscall 4 : write screen R0,R1,R2
  MOV R0, #1    // dest
  LDR R1, =char // pchar
  MOV R2, #1    // len of mess
  SWI 0         // syscall
  POP {{R0,R1}}
  SUB R1, #1
  MOV R2, #1
  MOV R3, #0
.loopreexpcond:
  CMP R3, R1
  BPL .loopreexpend
  // R2 <- R2*10
  MOV R4, R2
  LSL R2, #2
  ADD R2, R4
  LSL R2, #1
  ADD R3, #1
  B .loopreexpcond
.loopreexpend:
  B .loopprintcond
.loopprintend:
  MOV R0, #10 // newline
  LDR R1, =char
  STR R0, [R1]
  // print
  MOV R7, #4    // syscall 4 : write screen R0,R1,R2
  MOV R0, #1    // dest
  LDR R1, =char // pchar
  MOV R2, #1    // len of mess
  SWI 0         // syscall
  BX LR

/* Data zone (to improve) */
.data
char:
  .ascii "    "
zero:
  .ascii "0\\n  "
true:
  .ascii "True\\n"
false:
  .ascii "False\\n"
{}"""
