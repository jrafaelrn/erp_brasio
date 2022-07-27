import os


def get_cpf_cnpj(text):
  
  try:

    cnpj = int(text[:14])
    cnpj = str(cnpj)
    nome = text[14:]
    return cnpj, nome
  
  except:

    cpf = text[:12]
    nome = text[12:]
    return cpf, nome

  else:
    return '', ''
      


def extract_cpf_cnpj_cliente_fornecedor_from_description(description):
  
  description = description.upper()

  # Clear the description
  if description.find('RECEBIMENTO PIX ') != -1:
    description = description.replace('RECEBIMENTO PIX ', '')
    return get_cpf_cnpj(description)

  elif description.find('PAGAMENTO PIX ') != -1:
    description = description.replace('PAGAMENTO PIX ', '')
    return get_cpf_cnpj(description)

  elif description.find('COMPRAS NACIONAIS ') != -1:
    description = description.replace('COMPRAS NACIONAIS ', '')
    return '', description
  
  elif description.find('CDB PAGBANK') != -1:
    return '', 'Investimentos - PagBank'
  
  else:
    return '', ''


def extract_type(description, type):

  description = description.upper()
  type = type.upper()
  MY_CNPJ = os.environ.get('MY_CNPJ')
  
  if description.find('COMPRAS NACIONAIS') != -1:
    return 'CARTAO DEB'
  elif description.find('GETNET') != -1:
    return 'GETNET'
  elif description.find(MY_CNPJ) != -1:
    return 'INTERNO'
  elif description.find('SUB ') != -1:
    return 'IFOOD'
  elif description.find('CONVENIO') != -1 or description.find('CONVENIOS') != -1:
    return 'DEB AUTOMATICO'
  elif description.find('FATURA') != -1:
    return 'CARTAO CRED'
  elif type.find('PIX ENVIADO') != -1:
    return 'PIX_DEB'
  elif type.find('PIX RECEBIDO') != -1:
    return 'PIX_CRED'
  elif description.find('PIX') != -1:
    return type
  elif description.find('PLANO DE RECEBIMENTO') != -1:
    return 'LINK'
  else:
    return "OUTROS"

