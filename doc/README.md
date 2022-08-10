# Estrutura dos dados bancários

## Campos obrigatórios:
- id: identificador único do banco de dados 
- date: data do lançamento do extrato bancário
- account: conta bancária
- description_original: descrição original do lançamento no extrato bancário
- type_transaction: tipo de transação (categorizada)
- value: valor da transação no extrato bancário
- balance: saldo atual a transação do extrato bancário

## Campos opcionais:
- category_erp: categoria do lançamento no ERP
- entity_erp: entidade do lançamento no ERP (cliente ou fornecedor)
- description_erp: descrição do lançamento no ERP
- status_erp: status do lançamento no ERP (pago ou não pago, por exemplo)
- document: documento do lançamento no extrato bancário (CPF ou CNPJ) - obtido via método
- name: nome do lançamento (cliente ou fornecedor) no extrato bancário - obtido via método
- is_classified: indica se o lançamento foi classificado no ERP pelo Bot (true ou false)