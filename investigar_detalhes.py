#!/usr/bin/env python3
"""
Investiga a estrutura interna de produções e orientações
"""

import json

print("\n" + "="*70)
print("🔍 INVESTIGANDO PRODUÇÕES E ORIENTAÇÕES")
print("="*70 + "\n")

data = json.load(open('exemplo_json.txt', encoding='utf-8'))

# 1. PRODUÇÕES BIBLIOGRÁFICAS
print("📚 PRODUÇÕES BIBLIOGRÁFICAS:")
print("-" * 70)

producoes = data.get('producaoBibliografica', {})

# Verifica trabalhosEmEventos
trabalhos = producoes.get('trabalhosEmEventos', [])
print(f"\n📄 trabalhosEmEventos ({len(trabalhos)} itens):")
if trabalhos and len(trabalhos) > 0:
    print("   Chaves do primeiro item:")
    for key in trabalhos[0].keys():
        print(f"      - {key}")
    print("\n   Exemplo completo:")
    print(json.dumps(trabalhos[0], indent=6, ensure_ascii=False)[:800])

# Verifica artigosPublicados
artigos = producoes.get('artigosPublicados', [])
print(f"\n📄 artigosPublicados ({len(artigos)} itens):")
if artigos and len(artigos) > 0:
    print("   Chaves do primeiro item:")
    for key in artigos[0].keys():
        print(f"      - {key}")

# Verifica livrosECapitulos
livros = producoes.get('livrosECapitulos', [])
print(f"\n📄 livrosECapitulos ({len(livros)} itens):")
if livros and len(livros) > 0:
    print("   Chaves do primeiro item:")
    for key in livros[0].keys():
        print(f"      - {key}")

# 2. ORIENTAÇÕES
print("\n\n👨‍🎓 ORIENTAÇÕES:")
print("-" * 70)

outra_producao = data.get('outraProducao', {})
orientacoes = outra_producao.get('orientacoesConcluidas', [])

print(f"\n📄 orientacoesConcluidas ({len(orientacoes)} itens):")
if orientacoes and len(orientacoes) > 0:
    print("   Chaves do primeiro item:")
    for key in orientacoes[0].keys():
        print(f"      - {key}")
    print("\n   Exemplo completo:")
    print(json.dumps(orientacoes[0], indent=6, ensure_ascii=False)[:800])
else:
    # Tenta outras chaves
    print("   ⚠️  Array vazio ou não encontrado")
    print("\n   Tentando outras estruturas...")
    
    for tipo_key in ['orientacoesEmAndamento', 'orientacoesConcluidas']:
        items = outra_producao.get(tipo_key, [])
        if items:
            print(f"\n   ✅ Encontrado: {tipo_key} ({len(items)} itens)")
            if len(items) > 0:
                print(f"   Chaves: {list(items[0].keys())}")

print("\n" + "="*70)
print("✅ INVESTIGAÇÃO CONCLUÍDA")
print("="*70 + "\n")