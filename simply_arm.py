simply_arm_template = """/*************************
 * Generated with SimPly *
 *************************/

/************************
 * Original source code *
 ************************/
// File : {filename:}

{source:}
/************************
 * Abstract Syntax Tree *
 ************************/
{ast:}
/*********************
 * ARM assembly code *
 *********************/

.global _start

_start:
/* Start of compiled part */
{arm_code:}
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

.printstr:
  // len(str) in R0
  // &str in R1
  MOV R2, R0
  MOV R7, #4    // syscall 4 : write screen R0,R1,R2
  MOV R0, #1    // dest
  SWI 0         // syscall
  BX LR

/* Data zone */
.data
char:
  .ascii "    "
true:
  .ascii "True\\n"
false:
  .ascii "False\\n"
zerodivisionerror:
  .ascii "ZeroDivisionError: integer division or modulo by zero\\n"
{arm_data:}"""

arm_fast_multiplication_template = """
  // Fast multiplication
  // R0 : result
  // R1 : operand 1 (a)
  // R2 : operand 2 (b)
  MOV R0, #0   // z
  // test b>=0
  CMP R2, #0
  BPL .{label:}_mul_loop_condition
  // if b<0, a=-a and b=-b
  SUB R1, R0, R1
  SUB R2, R0, R2
.{label:}_mul_loop_condition:
  CMP R2, #0   // while b!=0
  BEQ .{label:}_mul_loop_end
  MOV R3, R2  // cpy b
  AND R3, #1  // b%2
  CMP R3, #1
  BEQ .{label:}_mul_branch_else_odd // b is odd
  LSR R2, #1 // b = b//2
  LSL R1, #1 // a = a*2
  B .{label:}_mul_branch_end_even
.{label:}_mul_branch_else_odd:
  SUB R2, #1 // b = b-1
  ADD R0, R1 // z = z+a
.{label:}_mul_branch_end_even:
  B .{label:}_mul_loop_condition
.{label:}_mul_loop_end:
"""

arm_fast_division_template = """
  // Fast division
  // R0 : result
  // R1 : operand 1 (a) -> will become the remainder
  // R2 : operand 2 (b)
  MOV R0, #0   // z
  // Testing div/0 error
  CMP R2, #0
  BNE .{label:}_div_nonzero
  MOV R0, #54
  LDR R1, =zerodivisionerror
  BL .printstr
  B end
.{label:}_div_nonzero:
  // b negative?
  CMP R2, #0
  BPL .{label:}_div_b_positive
  SUB R1, R0, R1 // still z=0
  SUB R2, R0, R2 // for -()
.{label:}_div_b_positive:
  // a negative?
  MOV R4, #1 // R4 = both_positive
  CMP R1, #0
  BPL .{label:}_div_a_positive
  MOV R4, #0 // R4 = must be inverted
  SUB R1, R0, R1
.{label:}_div_a_positive:
  MOV R3, R2 // c = b
.{label:}_div_loop1_condition:
  CMP R1, R3 // a >= c?
  BMI .{label:}_div_loop1_end // a<c
  LSL R3, #1 // c <<= 1
  B .{label:}_div_loop1_condition
.{label:}_div_loop1_end:
  LSR R3, #1 // c >>= 1
.{label:}_div_loop2_condition:
  CMP R3, R2 // c>=b?
  BMI .{label:}_div_loop2_end // c<b
  LSL R0, #1 // z <<=1
  CMP R1, R3 // if a>=c?
  BMI .{label:}_div_else // a<c
  SUB R1, R3 // a = a-c
  ADD R0, #1 // z = z+1
.{label:}_div_else:
  LSR R3, #1 // c >>=1
  B .{label:}_div_loop2_condition
.{label:}_div_loop2_end:
  CMP R4, #1
  BEQ .{label:}_div_both_positive
  SUB R0, R4, R0 // R4 is 0, so...
.{label:}_div_both_positive:
"""
