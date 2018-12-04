import logging
logging.basicConfig(filename='log.log',filemode='w',format='%(message)s',level=logging.DEBUG)

class Unit:
    """ Describes a functional unit """
    def __init__(self):
        """ Constructor """
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
        """ Display status """
        logging.debug(str(self.busy)+"\t"+str(self.op)+"\t"+str(self.fi)+"\t"+str(self.fj)+"\t"+str(self.fk)+"\t"+str(self.qj)+"\t"+str(self.qk)+"\t"+str(self.rj)+"\t"+str(self.rk))

class Instruction:
    """ Describes an instruction and its stages """
    def __init__(self, index, op, dst, src1, src2):
        """ Constructor """
        self.index = index
        # operands
        self.op = op
        self.dst = dst
        self.src1 = src1
        self.src2 = src2
        # clock cycles / stages
        # issue, read_op, exec_begin, exec_end, write_back
        self.stages = {1:0,2:0,3:0,4:0,5:0}
        self.current_stage = 1

    def print(self):
        """ Display status """
        logging.debug(self.op + " " + str(self.dst) + " " + str(self.src1) + " " + str(self.src2) + "\t" + str(self.stages))

# clock
clock = 1

# code
instruction_index = 0 # current instruction
instructions = [] # stores all parsed instructions

# operations
memory_operations = ['lw', 'sw']
arithmetic_operations = ['add', 'addi', 'mult', 'div']

# execution delays
delay_ldu = 1 # how long does a memory operation take
delay_alu = 0 # how long does a arithmetic operation take

result = dict.fromkeys(['$2','$3','$4','$5'], False) # results registers

ld_units = [[Unit(), None], [Unit(), None]] # memory units
al_units = [[Unit(), None], [Unit(), None]] # arithmetic units


def status():
    """ Logs the current status of everything """
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
    """ Checks if there's an available functional unit
    
    Arguments:
        instruction {Instruction} -- Instruction object
    
    Returns:
        Unit  -- Reference to the available unit, if it exists
    """
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
    """ Issue an instruction to the pipeline
    
    Arguments:
        instruction {Instruction} -- Instruction to be issued
    
    Returns:
        Boolean -- Issue was successful or not
    """
    # wait until (!Busy[FU] AND !Result[dst])
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
    """ Read operands for an instruction
    
    Arguments:
        unit {[Unit, Instruction]} -- Unit and Instruction to be checked
    
    Returns:
        Boolean -- Read operands was successful or not
    """

    FU = unit[0]
    if ((FU.rj) or (FU.rk)):
        # waiting for results
        return False

    FU.rj = False
    FU.rk = False
    return True


def execute(unit):
    """ Execution stage for instruction, applies
        clock delay if necessary, depending on the
        instruction type
    
    Arguments:
        unit {[Unit, Instruction]} -- Unit and Instruction to be checked
    """
    # store current cycle in current stage
    # of the instruction this FU is handling
    global instruction_index
    global instructions
    
    instruction = unit[1]
    logging.debug("Instruction " + instruction.op + " is at stage " + str(instruction.current_stage))


def write_back(unit):
    """ Write results and removes instruction from pipeline
    
    Arguments:
        unit {[Unit, Instruction] -- Unit and Instruction to be checked
    
    Returns:
        Boolean -- Success
    """
    # wait until (∀f {(Fj[f]≠Fi[FU] OR Rj[f]=No) AND (Fk[f]≠Fi[FU] OR Rk[f]=No)})
    # check all functional units for availability of source operands
    unit = unit[0]
    # check all functional units for availability of source operands
    for functional_unit in (ld_units + al_units):
        FU = functional_unit[0]
        # wait until (∀f {(Fj[f]≠Fi[FU] OR Rj[f]=No) AND (Fk[f]≠Fi[FU] OR Rk[f]=No)})
        if (not ((FU.fj != unit.fi or (not FU.rj)) and (FU.fk != unit.fi or (not FU.rk)))):
            return False
        
        # if ((FU.fj == unit.fi) and (FU.rj)) or ((FU.fk == unit.fi) and (FU.rk)):
            # return False

    # clear all functional units where this one is flagged as being used
    for functional_unit in (ld_units + al_units):
        FU = functional_unit[0]
        if (FU.qj == unit):
            FU.rj = False
        if (FU.qk == unit):
            FU.rk = False
    
    # clear register being written
    result[unit.fi] = False
    # flag unit as free for using
    unit.busy = False
    return True

def loop():
    """ Runs pipeline simulation until stop condition
    
    Returns:
        Boolean -- False if reached end of simulation
    """
    global instruction_index
    global clock

    logging.debug("\n[CLOCK " + str(clock) + "]")

    if (clock > 30):
        print("FINISHED.")
        return False # code finished execution

    # move current executing instructions
    for functional_unit in (ld_units + al_units):
        if (functional_unit[0].busy):
            execute(functional_unit)
    
    clock += 1

    return True


def parse_code(code):
    """ Parses source code to the simulation format
    
    Arguments:
        code {String} -- Source code read from .asm file
    """
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

        logging.debug(str(instruction_index) + " " + str(op) + " " + str(dest) + " " + str(src1) + " " + str(src2))

        instructions.append(Instruction(instruction_index, op, dest, src1, src2))
        instruction_index += 1


def main():
    global clock
    global instruction_index
    global instructions

    logging.debug("Parsing source code...")
    with open('source.asm', 'r') as src:
        code = src.read()
        parse_code(code)

    while(loop()):
        pass

    logging.debug("\nExecution finished.")
    for instruction in instructions:
        instruction.print()

if __name__ == "__main__":
    main()