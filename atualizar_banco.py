#!/usr/bin/env python3
"""
Script para atualizar a estrutura do banco de dados
Adiciona os novos campos necessários
"""

import sqlite3
from config import DB_NAME

print("\n" + "="*70)
print("🔧 ATUALIZANDO ESTRUTURA DO BANCO DE DADOS")
print("="*70 + "\n")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# 1. Atualizar tabela dados_gerais
print("1️⃣  Atualizando tabela 'dados_gerais'...")
try:
    cursor.execute("ALTER TABLE dados_gerais ADD COLUMN lattes_url TEXT")
    print("   ✅ Campo 'lattes_url' adicionado")
except:
    print("   ℹ️  Campo 'lattes_url' já existe")

try:
    cursor.execute("ALTER TABLE dados_gerais ADD COLUMN palavras_chave TEXT")
    print("   ✅ Campo 'palavras_chave' adicionado")
except:
    print("   ℹ️  Campo 'palavras_chave' já existe")

# 2. Atualizar tabela producao_bibliografica
print("\n2️⃣  Atualizando tabela 'producao_bibliografica'...")
try:
    cursor.execute("ALTER TABLE producao_bibliografica ADD COLUMN revista_evento_editora TEXT")
    print("   ✅ Campo 'revista_evento_editora' adicionado")
except:
    print("   ℹ️  Campo 'revista_evento_editora' já existe")

try:
    cursor.execute("ALTER TABLE producao_bibliografica ADD COLUMN num_coautores INTEGER")
    print("   ✅ Campo 'num_coautores' adicionado")
except:
    print("   ℹ️  Campo 'num_coautores' já existe")

try:
    cursor.execute("ALTER TABLE producao_bibliografica ADD COLUMN lista_coautores TEXT")
    print("   ✅ Campo 'lista_coautores' adicionado")
except:
    print("   ℹ️  Campo 'lista_coautores' já existe")

# 3. Atualizar tabela orientacoes_concluidas
print("\n3️⃣  Atualizando tabela 'orientacoes_concluidas'...")
try:
    cursor.execute("ALTER TABLE orientacoes_concluidas ADD COLUMN tipo_orientacao TEXT")
    print("   ✅ Campo 'tipo_orientacao' adicionado")
except:
    print("   ℹ️  Campo 'tipo_orientacao' já existe")

# Salvar mudanças
conn.commit()
conn.close()

print("\n" + "="*70)
print("✅ ESTRUTURA ATUALIZADA COM SUCESSO!")
print("="*70)
print("\n💡 Agora execute: python normalizer_completo.py\n")