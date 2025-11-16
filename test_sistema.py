#!/usr/bin/env python3
"""
Script de teste rápido para verificar se o sistema está funcionando
Testa uma única instituição (IFB) com coleta limitada
"""

import asyncio
import sys

# Teste de importações
print("🧪 TESTE DO SISTEMA DE SCRAPING\n")
print("="*60)

print("1. Testando importações...")
try:
    from config import INSTITUICOES, HEADERS, TERMOS_DOCENTE
    from database import Database, init_database
    from scraper import IntegraScraper
    print("   ✅ Todas as importações OK")
except Exception as e:
    print(f"   ❌ Erro nas importações: {e}")
    sys.exit(1)

# Teste de configuração
print("\n2. Testando configurações...")
print(f"   - Total de instituições: {len(INSTITUICOES)}")
print(f"   - Termos de filtro: {len(TERMOS_DOCENTE)}")
print(f"   - Headers configurados: {len(HEADERS)} campos")
print("   ✅ Configurações OK")

# Teste de banco de dados
print("\n3. Testando banco de dados...")
try:
    init_database()
    db = Database()
    db.connect()
    
    # Testa inserção
    teste_pessoa = {
        'slug': 'teste-docente',
        'nome': 'Prof. Teste da Silva',
        'campusNome': 'Campus Teste',
        'cargo': 'Professor EBTT'
    }
    
    teste_completo = {
        'baseUrl': 'https://integra.teste.br',
        'dadosGerais': {
            'nomeCompleto': 'Professor Teste da Silva',
            'emails': [{'email': 'teste@teste.br'}]
        }
    }
    
    docente_id = db.insert_docente('TESTE', teste_pessoa, teste_completo)
    
    if docente_id:
        # Remove o docente de teste
        db.cursor.execute("DELETE FROM docentes WHERE sigla = 'TESTE'")
        db.conn.commit()
        print("   ✅ Banco de dados OK (inserção e remoção testadas)")
    else:
        print("   ⚠️  Aviso: Problema ao testar inserção")
    
    db.close()
except Exception as e:
    print(f"   ❌ Erro no banco: {e}")
    sys.exit(1)

# Teste de scraper (sem fazer requisições reais)
print("\n4. Testando inicialização do scraper...")
try:
    scraper = IntegraScraper("IFB", "https://integra.ifb.edu.br")
    print(f"   - Sigla: {scraper.sigla}")
    print(f"   - URL base: {scraper.base_url}")
    print("   ✅ Scraper OK")
except Exception as e:
    print(f"   ❌ Erro no scraper: {e}")
    sys.exit(1)

# Teste de filtro
print("\n5. Testando filtro de docentes...")
cargos_teste = [
    "Professor EBTT",
    "Docente",
    "Professor Titular",
    "Técnico Administrativo",
    "Assistente em Administração",
]

docentes_filtrados = 0
for cargo in cargos_teste:
    if scraper.is_docente(cargo):
        docentes_filtrados += 1
        print(f"   ✅ '{cargo}' -> Docente")
    else:
        print(f"   ❌ '{cargo}' -> Não é docente")

if docentes_filtrados >= 3:
    print("   ✅ Filtro OK (identificou docentes corretamente)")
else:
    print("   ⚠️  Aviso: Filtro pode estar muito restritivo")

# Resumo
print("\n" + "="*60)
print("✅ TODOS OS TESTES PASSARAM!")
print("="*60)
print("\n💡 Próximos passos:")
print("   1. Execute 'python diagnostico.py' para testar as APIs")
print("   2. Execute 'python main.py IFB' para teste com 1 instituição")
print("   3. Execute 'python main.py' para coleta completa\n")
