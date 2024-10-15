from ofxtools.Parser import OFXTree

parser = OFXTree()

file_name = '/Volumes/GoogleDrive/My Drive/Palhas Perandini/Financeiro/Extratos Bancarios/SICOOB-0002/2024/2024-09.ofx'

# Find MEMO flag, copy entire line
# Find NAME flag, copy entire line
# Change lines order
def fix_ofx(file_path):

    print(f'Fixing OFX file: {file_path}')

    with open(file_path, 'r', encoding='latin1') as file:
        lines = file.readlines()

    # Listas para armazenar o conteúdo das linhas processadas
    processed_lines = []

    # Variáveis para armazenar as linhas com MEMO e NAME
    memo_line = None
    name_line = None

    for line in lines:
        if 'MEMO' in line:
            memo_line = line  # Armazena a linha MEMO
        elif 'NAME' in line:
            name_line = line  # Armazena a linha NAME
        else:
            processed_lines.append(line)  # Mantém linhas sem MEMO e NAME intactas

        # Quando ambos MEMO e NAME forem encontrados, trocamos as linhas
        if memo_line and name_line:
            processed_lines.append(name_line)  # Escreve a linha NAME antes
            processed_lines.append(memo_line)  # Escreve a linha MEMO depois
            memo_line = None
            name_line = None

    # Escreve de volta ao arquivo mantendo todas as linhas
    with open(file_path, 'w') as file:
        for line in processed_lines:
            file.write(line)  
        
        print(f'OFX file fixed: {file_path}')

            
fix_ofx(file_name)

with open(file_name, 'rb') as f: 
    parser.parse(f)

ofx = parser.convert()

print(ofx)