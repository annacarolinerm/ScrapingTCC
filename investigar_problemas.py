#!/usr/bin/env python3
"""
Investigação: Por que produções e orientações deram 0%?
E onde estão os PROJETOS?
"""

import json

print("\n" + "="*80)
print("🔍 INVESTIGAÇÃO COMPLETA")
print("="*80)

data = json.load(open('exemplo_json.txt', encoding='utf-8'))

# 1. PRODUÇÕES BIBLIOGRÁFICAS
print("\n1️⃣  PRODUÇÕES BIBLIOGRÁFICAS:")
print("-" * 80)

producao = data.get('producaoBibliografica', {})
print(f"Chaves em producaoBibliografica: {list(producao.keys())}")

# Artigos
artigos = producao.get('artigosPublicados', [])
print(f"\n📄 artigosPublicados: tipo={type(artigos)}, len={len(artigos) if isinstance(artigos, list) else 'N/A'}")
if artigos and isinstance(artigos, list):
    print(f"   Primeiro item: tipo={type(artigos[0])}")
    if isinstance(artigos[0], dict):
        print(f"   Chaves: {list(artigos[0].keys())}")
        print(f"\n   Estrutura completa:")
        print(json.dumps(artigos[0], indent=3, ensure_ascii=False)[:1000])

# 2. ORIENTAÇÕES
print("\n\n2️⃣  ORIENTAÇÕES:")
print("-" * 80)

outra_prod = data.get('outraProducao', {})
print(f"Chaves em outraProducao: {list(outra_prod.keys())}")

orientacoes = outra_prod.get('orientacoesConcluidas', [])
print(f"\n📄 orientacoesConcluidas: tipo={type(orientacoes)}, len={len(orientacoes) if isinstance(orientacoes, list) else 'N/A'}")
if orientacoes and isinstance(orientacoes, list):
    print(f"   Primeiro item: tipo={type(orientacoes[0])}")
    if isinstance(orientacoes[0], dict):
        print(f"   Chaves: {list(orientacoes[0].keys())}")

# 3. PROCURAR PROJETOS!
print("\n\n3️⃣  PROCURANDO PROJETOS:")
print("-" * 80)

def buscar_projetos(obj, caminho="", nivel=0):
    """Busca recursiva por projetos"""
    if nivel > 3:  # Limita profundidade
        return
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_lower = key.lower()
            novo_caminho = f"{caminho}.{key}" if caminho else key
            
            # Palavras-chave de projetos
            if any(palavra in key_lower for palavra in ['projeto', 'participacao', 'natureza']):
                print(f"\n✅ ENCONTRADO: {novo_caminho}")
                print(f"   Tipo: {type(value).__name__}")
                
                if isinstance(value, list):
                    print(f"   Lista com {len(value)} itens")
                    if value and isinstance(value[0], dict):
                        print(f"   Chaves do item: {list(value[0].keys())[:15]}")
                        print(f"\n   EXEMPLO DO PRIMEIRO PROJETO:")
                        print(json.dumps(value[0], indent=6, ensure_ascii=False)[:1500])
                        return True  # Encontrou!
                elif isinstance(value, dict):
                    print(f"   Dict com {len(value)} chaves")
                    print(f"   Sub-chaves: {list(value.keys())[:15]}")
                    buscar_projetos(value, novo_caminho, nivel + 1)
            else:
                buscar_projetos(value, novo_caminho, nivel + 1)

buscar_projetos(data)

# 4. VERIFICAR dadosComplementares especificamente
print("\n\n4️⃣  VERIFICANDO dadosComplementares:")
print("-" * 80)

dados_compl = data.get('dadosComplementares', {})
if dados_compl:
    for key in dados_compl.keys():
        valor = dados_compl[key]
        print(f"\n📁 {key}:")
        print(f"   Tipo: {type(valor).__name__}")
        
        if isinstance(valor, list) and valor:
            print(f"   Lista com {len(valor)} itens")
            if isinstance(valor[0], dict):
                print(f"   Chaves: {list(valor[0].keys())[:10]}")
        elif isinstance(valor, dict):
            print(f"   Dict com chaves: {list(valor.keys())[:10]}")

# 5. ÁREAS DE ATUAÇÃO
print("\n\n5️⃣  ÁREAS DE ATUAÇÃO:")
print("-" * 80)

areas_dict = data.get('dadosGerais', {}).get('areasDeAtuacao', {})
print(f"Tipo: {type(areas_dict)}")
print(f"Chaves: {list(areas_dict.keys()) if isinstance(areas_dict, dict) else 'N/A'}")

if isinstance(areas_dict, dict):
    areas = areas_dict.get('areaDeAtuacao', [])
    print(f"\nareaDeAtuacao: tipo={type(areas)}, len={len(areas) if isinstance(areas, list) else 'N/A'}")
    if areas and isinstance(areas, list):
        print(f"Primeiro item:")
        print(json.dumps(areas[0], indent=3, ensure_ascii=False)[:500])

print("\n" + "="*80)
print("✅ INVESTIGAÇÃO CONCLUÍDA")
print("="*80 + "\n")