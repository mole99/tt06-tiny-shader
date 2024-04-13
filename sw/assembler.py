import os
import sys
import math
import argparse

instructions = {

    'SETRGB' : {'format': 'single_operand', 'opcode': '00_0000', 'short': 'RGB <= RA', 'description': 'Set the output color to the value of the specified register.', 'category': 'Output'},
    'SETR' : {'format': 'single_operand', 'opcode': '00_0001', 'short': 'R <= RA[1:0]', 'description': 'Set the red channel of the output color to the lower two bits of the specified register.', 'category': 'Output'},
    'SETG' : {'format': 'single_operand', 'opcode': '00_0010', 'short': 'G <= RA[1:0]', 'description': 'Set the green channel of the output color to the lower two bits of the specified register.', 'category': 'Output'},
    'SETB' : {'format': 'single_operand', 'opcode': '00_0011', 'short': 'B <= RA[1:0]', 'description': 'Set the blue channel of the output color to the lower two bits of the specified register.', 'category': 'Output'},
    
    'GETX' : {'format': 'single_operand', 'opcode': '00_0100', 'short': 'RA <= X', 'description': 'Set the specified register to the x position of the current pixel.', 'category': 'Input'},
    'GETY' : {'format': 'single_operand', 'opcode': '00_0101', 'short': 'RA <= Y', 'description': 'Set the specified register to the y position of the current pixel.', 'category': 'Input'},
    'GETTIME' : {'format': 'single_operand', 'opcode': '00_0110', 'short': 'RA <= TIME', 'description': 'Set the specified register to the current time value, increases with each frame.', 'category': 'Input'},
    'GETUSER' : {'format': 'single_operand', 'opcode': '00_0111', 'short': 'RA <= USER', 'description': 'Set the specified register to the user value, can be set via the SPI interface.', 'category': 'Input'},
    
    'IFEQ' : {'format': 'single_operand', 'opcode': '00_1000', 'short': 'TAKE <= RA == REG0', 'description': 'Execute the next instruction if RA equals REG0.', 'category': 'Branches'},
    'IFNE' : {'format': 'single_operand', 'opcode': '00_1001', 'short': 'TAKE <= RA != REG0', 'description': 'Execute the next instruction if RA does not equal REG0.', 'category': 'Branches'},
    'IFGE' : {'format': 'single_operand', 'opcode': '00_1010', 'short': 'TAKE <= RA >= REG0', 'description': 'Execute the next instruction if RA is greater then or equal REG0.', 'category': 'Branches'},
    'IFLT' : {'format': 'single_operand', 'opcode': '00_1011', 'short': 'TAKE <= RA < REG0', 'description': 'Execute the next instruction if RA is less than REG0.', 'category': 'Branches'},
    
    'DOUBLE' : {'format': 'single_operand', 'opcode': '00_1100', 'short': 'RA <= RA * 2', 'description': 'Double the value of RA.', 'category': 'Arithmetic'},
    'HALF' : {'format': 'single_operand', 'opcode': '00_1101', 'short': 'RA <= RA / 2', 'description': 'Half the value of RA.', 'category': 'Arithmetic'},
    'CLEAR' : {'format': 'single_operand', 'opcode': '00_1110', 'short': 'RA <= 0', 'description': 'Clear RA by writing 0.', 'category': 'Load'},
    'SINE' : {'format': 'single_operand', 'opcode': '00_1111', 'short': 'RA <= SINE[REG0[5:2]] TODO', 'description': 'Get the sine value for REG0 and write into RA.', 'category': 'Special'},
    
    # Boolean operations
    'AND' : {'format': 'dual_operand', 'opcode': '01_00', 'short': 'RA <= RA & RB', 'description': 'Boolean AND of RA and RB, result written into RA.', 'category': 'Boolean'},
    'OR'  : {'format': 'dual_operand', 'opcode': '01_01', 'short': 'RA <= RA | RB', 'description': 'Boolean OR of RA and RB, result written into RA.', 'category': 'Boolean'},
    'NOT' : {'format': 'dual_operand', 'opcode': '01_10', 'short': 'RA <= ~RB', 'description': 'Boolean NOT of RB, result written into RA.', 'category': 'Boolean'},
    'XOR' : {'format': 'dual_operand', 'opcode': '01_11', 'short': 'RA <= RA ^ RB', 'description': 'Boolean XOR of RA and RB, result written into RA.', 'category': 'Boolean'},
    
    # Various
    'MOV' : {'format': 'dual_operand', 'opcode': '10_00', 'short': 'RA <= RB', 'description': 'Move value of RB into RA.', 'category': 'Move'},
    'ADD' : {'format': 'dual_operand', 'opcode': '10_01', 'short': 'RA <= RA + RB', 'description': 'Add RA and RB, result written into RA.', 'category': 'Arithmetic'},
    'SHIFTL' : {'format': 'dual_operand', 'opcode': '10_10', 'short': 'RA <= RA << RB', 'description': 'Shift RA with RB to the left, result written into RA.', 'category': 'Shift'},
    'SHIFTR' : {'format': 'dual_operand', 'opcode': '10_11', 'short': 'RA <= RA >> RB', 'description': 'Shift RA with RB to the right, result written into RA.', 'category': 'Shift'},

    # Load immediate
    'LDI' : {'format': 'immediate', 'opcode': '11', 'short': 'RA <= IMMEDIATE', 'description': 'Load an immediate value into RA.', 'category': 'Load'},
    
    # No operation
    'NOP' : {'format': 'pseudo', 'opcode': '01_00_00_00', 'short': 'R0 <= R0 & R0', 'description': 'No operation.', 'category': 'Pseudo'}
}


def get_syntax(fmt):

    if fmt == 'immediate':
        return 'IMMEDIATE'
    elif fmt == 'single_operand':
        return 'RA'
    elif fmt == 'dual_operand':
        return 'RA RB'
    else:
        return 'UNKNOWN'

def summary():
    categories = {}

    for name, instruction in instructions.items():
        if not instruction['category'] in categories:
            categories[instruction['category']] = {}
        
        categories[instruction['category']][name] = instruction
    
    for name, category in categories.items():
        print(f'### {name}')
        
        print(f'|Instruction|Operation|Description|')
        print(f'|-----------|---------|-----------|')
        
        for name, instruction in category.items():
        
            print(f'|{name} {get_syntax(instruction["format"])}|{instruction["short"]}|{instruction["description"]}|')

def get_register(string):
    if string[0] != 'R':
        print('Register operand must start with "R"')
        sys.exit()
    
    return int(string[1:])

def assemble(program, verbose=False):
    assembled = ''

    # Remove all comments
    program = os.linesep.join([s.split('#', 1)[0] for s in program.splitlines()])

    # Remove all empty lines
    program = os.linesep.join([s for s in program.splitlines() if s.strip()])

    # Process lines
    for line in program.splitlines():
        if verbose:
            print(f"Processing line: {line}")
        
        token = line.split()
        
        if token[0] in instructions:
            instr = instructions[token[0]]
            
            if instr['format'] == 'pseudo':
                assembled += f'{instr["opcode"]} // {line}\n'
            
            elif instr['format'] == 'immediate':
                if (len(token) != 2):
                    print(f'Instruction {token[0]} expects one immediate')
                imm = int(token[1])
                assembled += f'{instr["opcode"]}_{imm:06b} // {line}\n'

            elif instr['format'] == 'dual_operand':
                if (len(token) != 3):
                    print(f'Instruction {token[0]} expects two operand')

                op0 = get_register(token[1])
                op1 = get_register(token[2])

                assembled += f'{instr["opcode"]}_{op1:02b}_{op0:02b} // {line}\n'

            elif instr['format'] == 'single_operand':
                if (len(token) != 2):
                    print(f'Instruction {token[0]} expects one operand')

                op0 = get_register(token[1])

                assembled += f'{instr["opcode"]}_{op0:02b} // {line}\n'
            
            else:
                print(f'Instruction format unknown: {instr["format"]}')
        else:
            print(f'Unknown instruction: {token[0]}')
            sys.exit()

    return assembled

def simulate(program, x_pos=0, y_pos=0, cur_time=0, user=0, verbose=False):

    register = [0, 0, 0, 0]
    rgb = [0, 0, 0]
    skip = 0
    sine_lut = [int(0x3F*math.sin(math.radians(90.0/15*i))) for i in range(16)]

    # Remove all comments
    program = os.linesep.join([s.split('#', 1)[0] for s in program.splitlines()])

    # Remove all empty lines
    program = os.linesep.join([s for s in program.splitlines() if s.strip()])

    # Process lines
    for line in program.splitlines():
        #print(f"Processing line: {line}")
        
        token = line.split()
        
        if token[0] in instructions:
            instr = instructions[token[0]]
            
            if skip:
                if verbose:
                    print(f'Skipping instruction {token[0]}')
                skip = 0
                continue

            if instr['format'] == 'immediate':
                if (len(token) != 2):
                    print(f'Instruction {token[0]} expects one immediate')
                imm = int(token[1])
                
                if imm < 0 or imm > 0x3F:
                    print('Warning: immediate out of range')
                
                if token[0] == 'LDI':
                    register[0] = imm & 0x3F

            if instr['format'] == 'dual_operand':
                if (len(token) != 3):
                    print(f'Instruction {token[0]} expects two operand')

                op0 = get_register(token[1])
                op1 = get_register(token[2])

                if token[0] == 'AND':
                    register[op0] = register[op0] & register[op1] & 0x3F
                if token[0] == 'OR':
                    register[op0] = register[op0] | register[op1] & 0x3F
                if token[0] == 'NOT':
                    register[op0] = ~register[op1] & 0x3F
                if token[0] == 'XOR':
                    register[op0] = register[op0] ^ register[op1] & 0x3F

                if token[0] == 'MOV':
                    register[op0] = register[op1] & 0x3F
                if token[0] == 'ADD':
                    register[op0] = register[op0] + register[op1] & 0x3F
                if token[0] == 'SHIFTL':
                    register[op0] = register[op0] << register[op1] & 0x3F
                if token[0] == 'SHIFTR':
                    register[op0] = register[op0] >> register[op1] & 0x3F

            if instr['format'] == 'single_operand':
                if (len(token) != 2):
                    print(f'Instruction {token[0]} expects one operand')

                op0 = get_register(token[1])

                if token[0] == 'SETRGB':
                    rgb[2] = register[op0] >> 4 & 0x3
                    rgb[1] = register[op0] >> 2 & 0x3
                    rgb[0] = register[op0] >> 0 & 0x3
                if token[0] == 'SETR':
                    rgb[2] = register[op0] & 0x3
                if token[0] == 'SETG':
                    rgb[1] = register[op0] & 0x3
                if token[0] == 'SETB':
                    rgb[0] = register[op0] & 0x3

                if token[0] == 'GETX':
                    register[op0] = x_pos & 0x3F
                if token[0] == 'GETY':
                    register[op0] = y_pos & 0x3F
                if token[0] == 'GETTIME':
                    register[op0] = cur_time & 0x3F
                if token[0] == 'GETUSER':
                    register[op0] = user & 0x3F

                if token[0] == 'IFEQ':
                    skip = not (register[op0] == register[0])
                if token[0] == 'IFNE':
                    skip = not (register[op0] != register[0])
                if token[0] == 'IFGE':
                    skip = not (register[op0] >= register[0])
                if token[0] == 'IFLT':
                    skip = not (register[op0] < register[0])

                if token[0] == 'DOUBLE':
                    register[op0] = register[op0] << 1 & 0x3F
                if token[0] == 'HALF':
                    register[op0] = register[op0] >> 1 & 0x3F
                if token[0] == 'CLEAR':
                    register[op0] = 0
    
                if token[0] == 'SINE':
                    if register[0] & (1<<4):
                        register[op0] = sine_lut[15 - (register[0] & 0xF)]
                    else:
                        register[op0] = sine_lut[register[0] & 0xF]
                    if verbose:
                        print(f'register[0] {register[0]}')


            if verbose:
                print(f'Current state:')
                print(f'register: {register}')
                print(f'rgb: {rgb}')
            
        else:
            print(f'Unknown instruction: {token[0]}')
            sys.exit()
        
    return rgb

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='.shader file to assemble', type=str, required=False)
    parser.add_argument('-o', '--output', help='output name of the result', type=str, required=False, default='shader.bit')
    parser.add_argument('--image', help='simulate the shader and save an image of the result', type=str, required=False)
    parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
    parser.add_argument('-s', '--summary', help='summary about all instructions', action='store_true')
    args = parser.parse_args()
    
    if args.summary:
        summary()
        return
    
    if not args.input:
        shader = """
        # Example Shader
        SETRGB R0

        GETX R1
        GETY R2
        
        LDI 10
        
        IFEQ R1
        SETRGB R1
        
        IFEQ R2
        SETRGB R2
        """
    
        print('No input specfified! Using example shader:')
        print(program)
    
    else:
        with open(args.input, 'r') as f:
            shader = f.read()
    
    if args.image:
        WIDTH = 640//10
        HEIGHT = 480//10
        
        from PIL import Image
        
        img = Image.new(mode="RGB", size=(WIDTH, HEIGHT))
        pixels = img.load()
        
        for y_pos in range(HEIGHT):
            for x_pos in range(WIDTH):
                rgb = simulate(shader, x_pos, y_pos, verbose=args.verbose)
                
                if args.verbose:
                    #print(rgb)
                    pass
                
                red = (rgb[2]&0x3)<<6
                if rgb[2] & 0x1:
                    red |= 63
                
                green = (rgb[1]&0x3)<<6
                if rgb[1] & 0x1:
                    green |= 63
                
                blue = (rgb[0]&0x3)<<6
                if rgb[0] & 0x1:
                    blue |= 63
                
                pixels[x_pos,y_pos] = (red, green, blue)
                
        #img.show()
        img.save(args.image)

    assembled = assemble(shader, args.verbose)
    
    if args.verbose:
        print(assembled)
    
    with open(args.output, 'w') as f:
        f.write(assembled)

if __name__ == "__main__":
    main()
