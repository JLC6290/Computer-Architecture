import sys

SP = 7

HLT = 0b00000001

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""


        self.ram = [0] * 256     
        self.reg = [0] * 8     
        self.pc = 0     
        self.reg[SP] = 0xF4
        self.flags = 0b00000000
        self.hlt: HLT
        

    
    def ram_read(self, MAR): 
        return self.ram[MAR]
    
    def ram_write(self, MAR, MDR):      
        self.ram[MAR] = MDR 

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("usage: cpu.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    try:
                        line = line.split("#",1)[0]
                        line = int(line, 2)  
                        self.ram[address] = line
                        address += 1
                    except ValueError:
                        pass

        except FileNotFoundError:
            print(f"Couldn't find file {sys.argv[1]}")
            sys.exit(1)


    def alu(self, op, reg_a, reg_b):       
        """ALU operations.  
        Arithmetic logic unit- responsible for math"""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
 

        elif op == "MUL": 
            self.reg[reg_a] *= self.reg[reg_b]
        

        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flags = 0b00000001  

            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flags =  0b00000010 

            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flags = 0b00000100      
   
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]

        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]    

        elif op == "XOR":
           self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]

      
        elif op == "NOT":
            register = self.reg[reg_a]
           
            value = self.reg[register]
            self.reg[register] = ~value 

        elif op == "SHL":
            self.reg[reg_a] << self.reg[reg_b] 

        elif op == "SHR":
            self.reg[reg_a] >> self.reg[reg_b]

        elif op == "MOD":
            if self.reg[reg_b] == 0: 
                print("Cannot perform MOD")
                self.hlt(reg_a, reg_b)
            else:
                self.reg[reg_a] %= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        running = True

        instructions ={
             0b10000010: 'LDI',
             0b01000111: 'PRN',
             0b00000001: 'HLT',
             0b10100010: 'MUL',
             0b01000110: 'POP',
             0b01000101: 'PUSH',
             0b01010000: 'CALL',
             0b00010001: 'RET' ,
             0b10100000: 'ADD',
             0b10100111: 'CMP',
             0b01010100: 'JMP',
             0b01010101: 'JEQ',
             0b01010110: 'JNE',
             0b10101000: 'AND',
             0b10101010: 'OR',
             0b10101011: 'XOR',
             0b01101001: 'NOT',
             0b10101100: 'SHL',
             0b10101101: 'SHR',
             0b10100100: 'MOD'
        }

        while running: 
            i = self.ram[self.pc]   

            if instructions[i] == 'LDI':
                reg_num = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                self.reg[reg_num] = value

                self.pc +=3
            
            elif instructions[i] == 'PRN':
                reg_num = self.ram[self.pc +1]
                print(self.reg[reg_num])

                self.pc +=2
            
            elif instructions[i] == 'HLT':
                running = False
            
            elif instructions[i] == 'MUL':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('MUL', reg_a, reg_b)

                self.pc +=3
            
            elif instructions[i] == 'ADD':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('ADD', reg_a, reg_b)

                self.pc +=3
            
            elif instructions[i] == 'POP':
                address_to_pop_from = self.reg[SP]
                value = self.ram[address_to_pop_from]

                reg_num = self.ram[self.pc + 1]
                self.reg[reg_num] = value

                self.reg[SP] += 1

                self.pc += 2
            
            elif instructions[i] == 'PUSH':
                self.reg[SP] -= 1
                self.reg[SP] &= 0xff

                reg_num = self.ram[self.pc + 1]
                value = self.reg[reg_num]

                address_to_push_from = self.reg[SP]
            
                self.ram[address_to_push_from] = value

                self.pc += 2
            
            elif instructions[i] == 'CALL':
                return_addr = self.pc + 2 
                self.reg[SP] -= 1
                address_to_push_to = self.reg[SP]
                self.ram[address_to_push_to] = return_addr
                reg_num = self.ram[self.pc + 1]
                subroutine_addr = self.reg[reg_num]

                self.pc = subroutine_addr

            elif instructions[i] == 'RET':
                address_to_pop_from = self.reg[SP]
                return_addr = self.ram[address_to_pop_from]
                self.reg[SP] += 1
                self.pc = return_addr
            
            elif instructions[i] == 'CMP':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('CMP', reg_a, reg_b)
                self.pc +=3

            elif instructions[i] == 'JMP':
                reg_a = self.ram[self.pc + 1]
                self.pc = self.reg[reg_a]
                return True

            elif instructions[i] == 'JEQ':
                reg_a = self.ram[self.pc + 1]
                if (self.flags & 0b00000001) == 1: 
                    self.pc = self.reg[reg_a]
                else:
                    self.pc +=2

            elif instructions[i] == 'JNE':
                reg_a = self.ram[self.pc + 1]  
                if (self.flags & 0b00000001) == 0: 
                    self.pc = self.reg[reg_a]
                else:
                    self.pc +=2

            elif instructions[i] == 'AND':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('AND', reg_a, reg_b)
                self.pc +=3

            elif instructions[i] == 'OR':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('OR', reg_a, reg_b)
                self.pc +=3

            elif instructions[i] == 'XOR':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('XOR', reg_a, reg_b)
                self.pc +=3

            elif instructions[i] == 'NOT':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('NOT', reg_a, reg_b)
                self.pc +=3

            elif instructions[i] == 'SHL':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('SHL', reg_a, reg_b)
                self.pc +=3

            elif instructions[i] == 'SHR':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('SHR', reg_a, reg_b)
                self.pc +=3

            elif instructions[i] == 'MOD':
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]

                self.alu('MOD', reg_a, reg_b)
                self.pc +=3

            else: 
                print(f"Unknown instruction {i}")



