simply_arm_template = """.global _start

_start:
{}
end:
  MOV R7, #1  // syscall 1 : exit
  SWI 0

.printhexint:
  // number to be printed is in R0.
  // R1 : address to write
  // R2 : counter
  // R3 : tmp char
  // R4 : 4 chars
  MOV R2, #8 // initialize loop counter
  MOV R4, #0 // initialize 4 chars
.loopprintcond:
  CMP R2, #0
  BEQ .loopprintend
  LSL R4, R4, #8
  MOV R3, R0      //
  LSL R3, R3, #28 // Take least significant nibble from R0
  LSR R3, R3, #28 //
  ADD R3, R3, #48 // add '0'
  CMP R3, #58   // did that exceed ASCII '9'?
  BCC .ifdigit09  // if not...
  ADD R3, R3, #7  // add 'A'-('0'+10) if needed
.ifdigit09:
  // put one char in string
  ADD R4, R4, R3
  // half-way
  CMP R2, #5
  BNE .loopprintnext
  LDR R1, =hexint
  ADD R1, #6 // start address (after 0x)
  STR R4, [R1]
  MOV R4, #0 // re-initialize 4 chars
.loopprintnext:
  // prepare next loop
  LSR R0, R0, #4 // >>=4
  SUB R2, R2, #1 // decrement counter
  B .loopprintcond
.loopprintend:
  LDR R1, =hexint
  ADD R1, #2 // start address (after 0x)
  STR R4, [R1]
  // print
  MOV R7, #4      // syscall 4 : write screen R0,R1,R2
  MOV R0, #1      // destination : to screen
  LDR R1, =hexint // pchar
  MOV R2, #11     // len of mess
  SWI 0           // syscall
  //
  BX LR

.data
hexint:
  .ascii "0x________\\n"
keepitsafe:
  .word 0
var0:
  .word 0
var1:
  .word 0
var2:
  .word 0
var3:
  .word 0
var4:
  .word 0
var5:
  .word 0
var6:
  .word 0
var7:
  .word 0
var8:
  .word 0
var9:
  .word 0
var10:
  .word 0
var11:
  .word 0
var12:
  .word 0"""
