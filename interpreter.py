import csv
import json
from io import StringIO as sio

class Interpreter:
    def parse_csv(self, text):
        return list(csv.reader(sio(text), skipinitialspace=True))

    def isquoted(self, text):
        return text.startswith('\'') and text.endswith('\'')

    def isinteger(self,text):
        return text.lstrip('+-').isdigit()
    def stripcomments(self, text):
        l=text.split(';')
        return l[0]

    def parse_operands(self,text,op):
        lines=self.parse_csv(text)
        operands=[]
        if lines and lines[0]:
            for line in lines[0]:
                l=line.strip()
                if l.strip():
                    if self.isquoted(l):
                        operands.append({'value':l.strip('\''), 'type':'str'})
                    else:
                        l=self.stripcomments(l)        
                        if self.isinteger(l): 
                            operands.append({'value':int(l), 'type':'int'})
                        else:    
                            operands.append({'value':l, 'type':'reg'})

        if len(operands)<2:
            for index in range(len(operands),2):
                operands.append(None)

        op['operands']=operands        

    # def parse_operands(self, text,op):
    #     tokens=text.split(',')
    #     op['x']=None
    #     if len(tokens>0):
    #         x=tokens[0].strip()
    #         if x.lstrip('+-').isdigit():
    #             op['x']=int(x)
    #         else:
    #             op['x']=x

    #     op['y']=None
    #     if len(tokens)>1:
    #         y=tokens[1].strip()
    #         if y.lstrip('+-').isdigit():
    #             op['y']=int(y)
    #         else:
    #             op['y']=y

    def parse_op(self,operation):
        tokens=operation.split(' ')
        op={}
        code=tokens[0]
        op['code']=code
        operands=''
        if len(tokens)>0:
            operands="".join(tokens[1:])

        self.parse_operands(operands,op)
        print(json.dumps(op))
        return op

    def exec_internal(self, op):
        op_func=getattr(self,'op_'+op['code'],None)
        op_func(op['operands'])

    def execute_op(self,operation):
        op=self.parse_op(operation)
        self.exec_internal(op)

    def init_program(self,operations):
        self.results={}
        self.stack=[]
        self.messages=[]
        self.ep=0
        self.eop=len(operations)
        self.sf=False
        self.zf=False

    def execute(self,operations):
        self.init_program(operations)
        while self.ep<self.eop:
            self.execute_op(operations[self.ep])
        if self.ep==self.eop:
            return -1
        else:
            return self.messages    

    def parse_program(self,program):
        self.labels={}
        lines=program.splitlines()
        plist=[]
        ep=0
        for line in lines:
            l=line.strip()
            if l:
                if not l.startswith(';'):
                    if l.endswith(':'):
                        self.labels[l.rstrip(':').strip()]=ep
                    else:
                        plist.append(l) 
                        ep+=1
        return plist    

    def execute_program(self,program):
        l=self.parse_program(program)
        return self.execute(l)    

    def set_flags(self,value):
        zf=value==0
        sf=value>0


    def set_register_value(self,x,value):
        self.results[x]=value

    def get_register_or_const(self,operand):
        op_type=operand['type']
        op_value=operand['value']
        if op_type=='int':
            return op_value
        elif op_type=='reg':    
            return self.results[op_value]
        else:
            return None    


    def op_mov(self,operands):
        self.set_register_value(operands[0]['value'],self.get_register_or_const(operands[1]))
        self.ep+=1

    def op_add(self,operands):
        self.set_register_value(operands[0]['value'],self.get_register_or_const(operands[0])+self.get_register_or_const(operands[1]))
        self.ep+=1

    def op_sub(self,operands):
        self.set_register_value(operands[0]['value'],self.get_register_or_const(operands[0])-self.get_register_or_const(operands[1]))
        self.ep+=1

    def op_cmp(self,operands):
        self.set_flags(self.get_register_or_const(operands[0])-self.get_register_or_const(operands[1]))
        self.ep+=1

    def op_mul(self,operands):
        self.set_register_value(operands[0]['value'],self.get_register_or_const(operands[0])*self.get_register_or_const(operands[1]))
        self.ep+=1

    def op_div(self,operands):
        self.set_register_value(operands[0]['value'],self.get_register_or_const(operands[0])//self.get_register_or_const(operands[1]))
        self.ep+=1

    def op_inc(self,operands):
        self.set_register_value(operands[0]['value'],self.get_register_or_const(operands[0])+1)
        self.ep+=1

    def op_dec(self,operands):
        self.set_register_value(operands[0]['value'],self.get_register_or_const(operands[0])-1)
        self.ep+=1

    def op_msg(self,operands):
        msg=''
        for operand in operands:
            if operand:
                op_type=operand['type']
                op_value=operand['value']
                if op_type=='int': 
                    msg+=str(op_value)
                elif op_type=='str':    
                    msg+=op_value
                elif op_type=='reg':
                    msg+=str(self.results[op_value])
        
        self.messages.append(msg)
        self.ep+=1

    def op_end(self, operands):
        self.ep=self.eop+100

    def op_jnz(self,operands):
        if self.results[operands[0]['value']]!=0:
            self.ep+=self.get_register_or_const(operands[0])
        else:
            self.ep+=1    

    def op_jmp(self,operands):
        label=operands[0]['value']
        if label in self.labels:
            self.ep=self.labels[label]

    def op_jne(self,operands):
        if not zf:
            self.op_jmp(operands)
        else:
            self.ep+=1

    def op_je(self,operands):
        if zf:
            self.op_jmp(operands)
        else:
            self.ep+=1

    def op_jge(self,operands):
        if zf or sf:
            self.op_jmp(operands)
        else:
            self.ep+=1

    def op_jg(self,operands):
        if not zf and sf:
            self.op_jmp(operands)
        else:
            self.ep+=1

    def op_jle(self,operands):
        if zf or not sf:
            self.op_jmp(operands)
        else:
            self.ep+=1

    def op_jl(self,operands):
        if not zf and not sf:
            self.op_jmp(operands)
        else:
            self.ep+=1

                

    def stack_push(self,value):
        self.stack.append(value)

    def stack_pop(self):
        return self.stack.pop()

    def op_call(self,operands):
        self.stack_push(self.ep+1)
        self.op_jmp(operands)

    def op_ret(self,operands):
        self.ep=self.stack_pop()
