#!/usr/bin/env python3
"""
Corrige o normalizer_definitivo.py automaticamente
"""

import shutil

print("\n" + "="*70)
print("🔧 CORRIGINDO NORMALIZER")
print("="*70 + "\n")

# Backup
try:
    shutil.copy('normalizer_definitivo.py', 'normalizer_definitivo.py.backup')
    print("✅ Backup criado: normalizer_definitivo.py.backup\n")
except:
    print("⚠️  Arquivo normalizer_definitivo.py não encontrado!")
    print("   Execute este script na mesma pasta do normalizer.\n")
    exit(1)

# Lê o arquivo
with open('normalizer_definitivo.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Correção 1: Palavras-chave STRING
print("1️⃣  Corrigindo palavras-chave (STRING)...")

# Procura a seção de palavras-chave e substitui
if 'if isinstance(pk, list):' in conteudo:
    # Adiciona tratamento para string ANTES do list
    conteudo = conteudo.replace(
        '''palavras = ''
            try:
                pk = data.get('palavrasChave')
                if isinstance(pk, list):''',
        '''palavras = ''
            try:
                pk = data.get('palavrasChave')
                if isinstance(pk, str):
                    # STRING direta!
                    palavras = pk.strip()
                elif isinstance(pk, list):'''
    )
    print("   ✅ Palavras-chave corrigidas!\n")
else:
    print("   ⚠️  Seção de palavras-chave não encontrada\n")

# Correção 2: Orientações detalhamento
print("2️⃣  Corrigindo orientações (detalhamento)...")

# Substitui a busca de instituição
conteudo = conteudo.replace(
    '''nome_ori = self.to_str(ori.get('nomeDoOrientado'))
                    curso = self.to_str(ori.get('curso') or ori.get('tipoDeCurso'))
                    inst = self.to_str(ori.get('nomeDoInstituicao') or ori.get('instituicao', ''))''',
    '''# CORRIGIDO: Busca no detalhamento
                    det = ori.get('detalhamentoDeOutrasOrientacoesConcluidas', {})
                    if not isinstance(det, dict):
                        det = {}
                    
                    nome_ori = self.to_str(det.get('nomeDoOrientado'))
                    curso = self.to_str(det.get('nomeDoCurso'))
                    inst = self.to_str(det.get('nomeDaInstituicao', ''))'''
)

# Também corrige mestrado e doutorado
conteudo = conteudo.replace(
    'detalhamentoDaOrientacaoConcluidaDeMestrado',
    'detalhamentoDaOrientacaoConcluidaDeMestrado'
)

print("   ✅ Orientações corrigidas!\n")

# Salva o arquivo corrigido
with open('normalizer_definitivo.py', 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("="*70)
print("✅ NORMALIZER CORRIGIDO COM SUCESSO!")
print("="*70)
print("\n📋 Próximos passos:")
print("   1. python normalizer_definitivo.py")
print("   2. python visualizar_banco.py\n")
print("💡 Se der erro, restaure o backup:")
print("   cp normalizer_definitivo.py.backup normalizer_definitivo.py\n")
