from pyfiglet import Figlet
import logging
logging.basicConfig(filename='log.log',filemode='w',format='%(message)s',level=logging.DEBUG)

class Unit:
    def __init__(self):
        self.busy = False
        self.op = None
        self.fi = 0
        self.fj = 0
        self.fk = 0
        self.qj = 0
        self.qk = 0
        self.rj = False
        self.rk = False

    def print(self):
        logging.debug(str(self.busy)+"\t"+str(self.op)+"\t"+str(self.fi)+"\t"+str(self.fj)+"\t"+str(self.fk)+"\t"+str(self.qj)+"\t"+str(self.qk)+"\t"+str(self.rj)+"\t"+str(self.rk))

class Instruction:
    def __init__(self, index, op, dst, src1, src2):
        self.index = index
        # operands
        self.op = op
        self.dst = dst
        self.src1 = src1
        self.src2 = src2
        # clock cycles
        self.issue = 0
        self.read = 0
        self.execution = 0
        self.write = 0
        # stages
        # issue, read_op, exec_begin, exec_end, write_back
        self.stages = {1:0,2:0,3:0,4:0,5:0}
        self.current_stage = 1

    def print(self):
        logging.debug(self.op + " " + str(self.dst) + " " + str(self.src1) + " " + str(self.src2) + "\t" + str(self.stages))

# clock
clock = 1

# code
instruction_index = 0
instructions = []

# operations
memory_operations = ['lw', 'sw']
arithmetic_operations = ['add', 'addi', 'mult', 'div']

delay_ldu = 1
delay_alu = 0

result = dict.fromkeys(['$2','$3','$4','$5'], False) # results registers
ld_units = [[Unit(), None], [Unit(), None]] # memory units
al_units = [[Unit(), None], [Unit(), None]] # arithmetic units


def status():
    logging.debug("\nREGISTERS:")
    logging.debug(result)

    logging.debug("\nFUNCTIONAL UNITS:")
    logging.debug("unit\tbusy\top\tfi\tfj\tfk\tqj\tqk\trj\trk")
    for index, unit in enumerate(ld_units):
        logging.debug("LDU" + str(index) + "\t")
        unit[0].print()
    for index, unit in enumerate(al_units):
        logging.debug("ALU" + str(index) + "\t")
        unit[0].print()

def unit_available(instruction):
    global ld_units
    global al_units

    if (instruction.op in memory_operations):
        for unit in ld_units:
            FU = unit[0]
            if (not FU.busy):
                return unit
    elif (instruction.op in arithmetic_operations):
        for unit in al_units:
            FU = unit[0]
            if (not FU.busy):
                return unit
    return None


def issue(instruction):
    # check if unit is available
    unit = unit_available(instruction)
    if (unit == None):
        return False
    # check if result register is available (WAW)
    if (instruction.dst != None):
        if (result[instruction.dst]):
            return False
    
    FU = unit[0]
    # issue instruction to functional unit
    FU.busy = True
    FU.op = instruction.op
    FU.fi = instruction.dst
    FU.fj = instruction.src1
    FU.fk = instruction.src2
    
    if (instruction.src1 not in result.keys()):
        FU.qj = False
    else:
        FU.qj = result[instruction.src1]
    
    if (instruction.src2 not in result.keys()):
        FU.qk = False
    else:
        FU.qk = result[instruction.src2]

    FU.rj = (FU.qj == 1)
    FU.rk = (FU.qk == 1)
    unit[1] = instruction

    result[instruction.dst] = unit

    return True


def read_operands(unit):
    FU = unit[0]
    if ((FU.rj) or (FU.rk)):
        # waiting for results
        return False

    FU.rj = False
    FU.rk = False
    return True


def execute(unit):
    # store current cycle in current stage
    # of the instruction this FU is handling
    global instruction_index
    global instructions
    
    instruction = unit[1]
    logging.debug("Instruction " + instruction.op + " is at stage " + str(instruction.current_stage))

    # check if execution is complete
    if (instruction.current_stage == 6):
        # instruction finished, write back and clear 
        logging.debug("Write back for " + instruction.op)
        if (write_back(unit)):
            logging.debug("Successful write-back for " + instruction.op)
            instruction.current_stage += 1
            # try to issue a new instruction
            if (instruction_index < len(instructions)):
                instruction = instructions[instruction_index]
                if (issue(instruction)):
                    logging.debug("Issued " + instruction.op)
                    instruction_index += 1
                else:
                    logging.debug("Can't issue " + instruction.op)
        else:
            logging.debug("NOT Successful write-back for " + instruction.op)
    elif (instruction.current_stage == 2):
        if (read_operands(unit)):
            logging.debug("Read operands for " + instruction.op)
            # only advance if no RAW is detected
            instruction.stages[instruction.current_stage] = clock
            instruction.current_stage += 1
        else:
            logging.debug("Can't read operands for " + instruction.op)
        # try to issue a new instruction
        if (instruction_index < len(instructions)):
            instruction = instructions[instruction_index]
            if (issue(instruction)):
                logging.debug("Issued " + instruction.op)
                instruction_index += 1
            else:
                logging.debug("Can't issue " + instruction.op)
    elif (instruction.current_stage == 3):
        logging.debug("Executing " + instruction.op)
        # arithmetic operations start/finish on same clock cycle
        if (instruction.op in arithmetic_operations):
            instruction.stages[instruction.current_stage] = clock
            instruction.current_stage += 1
            instruction.stages[instruction.current_stage] = clock
            instruction.current_stage += 1
        else:
            # memory operations advance one clock cycle
            instruction.stages[instruction.current_stage] = clock
            instruction.current_stage += 1
    elif (instruction.current_stage == 4):
        logging.debug("Executing " + instruction.op)
        instruction.stages[instruction.current_stage] = clock
        if (instruction.op in memory_operations):
            # check delay for memory operations
            if (instruction.stages[instruction.current_stage] - instruction.stages[3] == delay_ldu):
                instruction.current_stage += 1
        else:
            # check delay for arithmetic operations
            if (instruction.stages[instruction.current_stage] - instruction.stages[3] == delay_alu):
                instruction.current_stage += 1
    else:
        # advance clock cycle
        logging.debug("Advancing " + instruction.op)
        instruction.stages[instruction.current_stage] = clock
        instruction.current_stage += 1


def write_back(unit):
    # wait until (∀f {(Fj[f]≠Fi[FU] OR Rj[f]=No) AND (Fk[f]≠Fi[FU] OR Rk[f]=No)})
    # check all functional units for availability of source operands
    unit = unit[0]

    for functional_unit in (ld_units + al_units):
        FU = functional_unit[0]
        if ((FU.fj == unit.fi) and (FU.rj)) or ((FU.fk != unit.fi) and (FU.rk)):
            return False

    for functional_unit in (ld_units + al_units):
        FU = functional_unit[0]
        if (FU.qj == unit):
            FU.rj = True
        if (FU.qk == unit):
            FU.rk = True
    
    result[unit.fi] = False
    unit.busy = False
    return True

def loop():
    global instruction_index
    global clock

    logging.debug("\n[CLOCK " + str(clock) + "]")

    # if (instruction_index >= len(instructions)):
    if (instructions[len(instructions)-1].current_stage >= 7):
        print("FINISHED.")
        return False # code finished execution

    # move current executing instructions
    for functional_unit in (ld_units + al_units):
        if (functional_unit[0].busy):
            execute(functional_unit)
    
    clock += 1
    if (clock > 25):
        exit()

    return True


def parse_code(code):
    global instructions
    global instruction_index

    code = code.replace(",", "")
    for instruction in code.splitlines():
        instruction = instruction.split()
        op = instruction[0]
        arg1 = instruction[1]
        arg2 = instruction[2]
        if (len(instruction) > 3):
            arg3 = instruction[3]
        else:
            arg3 = None

        if (op == 'lw'):
            dest = arg1
            src1 = arg2.split('(')[1].replace(")", "")
            src2 = None
        elif (op == 'sw'):
            dest = None
            src1 = arg1
            src2 = arg2.split('(')[1].replace(")", "")
        else:
            dest = arg1
            src1 = arg2
            src2 = arg3

        instructions.append(Instruction(instruction_index, op, dest, src1, src2))
        instruction_index += 1


def main():
    global clock
    global instruction_index
    global instructions

    figlet = Figlet(font='slant')

    with open('source.asm', 'r') as src:
        code = src.read()
        parse_code(code)

    print(figlet.renderText('Scoreboarding'))

    instruction_index = 0
    # issue first instruction
    if (instruction_index < len(instructions)):
        instruction = instructions[instruction_index]
        if (issue(instruction)):
            logging.debug("Issued " + instruction.op)
            instruction_index += 1
        else:
            logging.debug("Can't issue " + instruction.op)

    while(loop()):
        pass

    for instruction in instructions:
        instruction.print()

if __name__ == "__main__":
    main()