class Assembler:
    def parse_op(self,operation):
        tokens=operation.split()
        op={}
        op['code']=tokens[0]
        op['x']=None
        if len(tokens)>1:
            x=tokens[1]
            if x.lstrip('+-').isdigit():
                op['x']=int(x)
            else:
                op['x']=x

        op['y']=None
        if len(tokens)>2:
            y=tokens[2]
            if y.lstrip('+-').isdigit():
                op['y']=int(y)
            else:
                op['y']=y

        return op

    def exec_internal(self, op):
        op_func=getattr(self,'op_'+op['code'],None)
        op_func(op['x'],op['y'])

    def execute_op(self,operation):
        op=self.parse_op(operation)
        self.exec_internal(op)

    def init_program(self):
        self.results={}
        self.ep=0

    def execute(self,operations):
        self.init_program()
        while self.ep<len(operations):
            self.execute_op(operations[self.ep])
        return self.results

    def set_register_value(self,x,value):
        self.results[x]=value

    def get_register_or_const(self,y):
        if y in self.results:
            return self.results[y]
        else:
            return y    

    def op_mov(self,x,y):
        self.set_register_value(x,self.get_register_or_const(y))
        self.ep+=1

    def op_inc(self,x,y):
        self.set_register_value(x,self.get_register_or_const(x)+1)
        self.ep+=1

    def op_dec(self,x,y):
        self.set_register_value(x,self.get_register_or_const(x)-1)
        self.ep+=1

    def op_jnz(self,x,y):
        if self.results[x]!=0:
            self.ep+=self.get_register_or_const(y)
        else:
            self.ep+=1    

