lw $2, BASEA($4)
addi $2, $2, INC1
lw $3, BASEB($4)
addi $3, $3, INC2
add $5, $2, $3
sw $5, BASEC($4)
addi $4, $4, 4 
