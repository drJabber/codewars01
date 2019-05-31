import json
from assembler import Assembler
from interpreter import Interpreter

def simple_assembler(operations):
    assembler=Assembler()
    return assembler.execute(operations)            

def assembler_interpreter(program):
    return Interpreter().execute_program(program)


sample_program = """
; My first program
mov  a, 5
inc  a
call function1
msg  '(5+1)/2*4 = ', a    ; output message
cmp a,20
jle label1:
mov b,5
label1:
add b,a
msg a,'+',b,'=',20,' - wrong result'
end

function2:
    mul a,4
    ret

function1:
    div  a, 2
    call function2
    ret
"""

if __name__ == "__main__":
    l=simple_assembler(['mov a 5','inc a','dec a','dec a','jnz a -1','inc a'])
    print(json.dumps(l))

    l=assembler_interpreter(sample_program)
    if type(l) is list:
        for item in l:
            print(item)
    else:        
        print(l)
