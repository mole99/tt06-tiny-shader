import os
import sys
import math
import argparse

instructions = {

    'SETRGB' : {'format': 'single_operand', 'opcode': '00_0000'},
    'SETR' : {'format': 'single_operand', 'opcode': '00_0001'},
    'SETG' : {'format': 'single_operand', 'opcode': '00_0010'},
    'SETB' : {'format': 'single_operand', 'opcode': '00_0011'},
    
    'GETX' : {'format': 'single_operand', 'opcode': '00_0100'},
    'GETY' : {'format': 'single_operand', 'opcode': '00_0101'},
    'GETTIME' : {'format': 'single_operand', 'opcode': '00_0110'},
    'GETUSER' : {'format': 'single_operand', 'opcode': '00_0111'},
    
    'IFEQ' : {'format': 'single_operand', 'opcode': '00_1000'},
    'IFNE' : {'format': 'single_operand', 'opcode': '00_1001'},
    'IFGE' : {'format': 'single_operand', 'opcode': '00_1010'},
    'IFLT' : {'format': 'single_operand', 'opcode': '00_1011'},
    
    'TODO0' : {'format': 'single_operand', 'opcode': '00_1100'},
    'TODO1' : {'format': 'single_operand', 'opcode': '00_1101'},
    'TODO2' : {'format': 'single_operand', 'opcode': '00_1110'},
    'SINE' : {'format': 'single_operand', 'opcode': '00_1111'},
    
    # Logical operations
    'AND' : {'format': 'dual_operand', 'opcode': '01_00'},
    'OR'  : {'format': 'dual_operand', 'opcode': '01_01'},
    'NOT' : {'format': 'dual_operand', 'opcode': '01_10'},
    'XOR' : {'format': 'dual_operand', 'opcode': '01_11'},
    
    # Various
    'MOV' : {'format': 'dual_operand', 'opcode': '10_00'},
    'ADD' : {'format': 'dual_operand', 'opcode': '10_01'},
    'SHIFTL' : {'format': 'dual_operand', 'opcode': '10_10'},
    'SHIFTR' : {'format': 'dual_operand', 'opcode': '10_11'},
    
    # Load immediate
    'LDI' : {'format': 'immediate', 'opcode': '11'}
}

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
            
            if instr['format'] == 'immediate':
                if (len(token) != 2):
                    print(f'Instruction {token[0]} expects one immediate')
                imm = int(token[1])
                assembled += f'{instr["opcode"]}_{imm:06b} // {line}\n'

            if instr['format'] == 'dual_operand':
                if (len(token) != 3):
                    print(f'Instruction {token[0]} expects two operand')

                op0 = get_register(token[1])
                op1 = get_register(token[2])

                assembled += f'{instr["opcode"]}_{op1:02b}_{op0:02b} // {line}\n'

            if instr['format'] == 'single_operand':
                if (len(token) != 2):
                    print(f'Instruction {token[0]} expects one operand')

                op0 = get_register(token[1])

                assembled += f'{instr["opcode"]}_{op0:02b} // {line}\n'
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

                if token[0] == 'SINE':
                    if verbose:
                        print(f'register[0] {register[0]}')
                        print(f'sine_lut[register[0] >> 2] {sine_lut[register[0] >> 2]}')
                    register[op0] = sine_lut[register[0] >> 2]

            if verbose:
                print(f'Current state:')
                print(f'register: {register}')
                print(f'rgb: {rgb}')
            
        else:
            print(f'Unknown instruction: {token[0]}')
            sys.exit()
        
    return rgb

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='.shader file to assemble', type=str, required=False)
    parser.add_argument('-o', '--output', help='output name of the result', type=str, required=False, default='shader.bit')
    parser.add_argument('--image', help='simulate the shader and save an image of the result', type=str, required=False)
    parser.add_argument('-v', '--verbose', help='verbose output', action='store_true')
    args = parser.parse_args()
    
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
        WIDTH = 40
        HEIGHT = 30    
        
        from PIL import Image
        
        img = Image.new(mode="RGB", size=(WIDTH, HEIGHT))
        pixels = img.load()
        
        for y_pos in range(HEIGHT):
            for x_pos in range(WIDTH):
                rgb = simulate(shader, x_pos, y_pos, verbose=args.verbose)
                
                if args.verbose:
                    #print(rgb)
                    pass
                
                pixels[x_pos,y_pos] = (rgb[2]<<6, rgb[1]<<6, rgb[0]<<6)
                
        #img.show()
        img.save(args.image)

    assembled = assemble(shader, args.verbose)
    
    if args.verbose:
        print(assembled)
    
    with open(args.output, 'w') as f:
        f.write(assembled)
