#!/usr/bin/env python3
"""
Procura por PROJETOS (pesquisa, extensão, ensino) no JSON
"""

import json

print("\n" + "="*80)
print("🔍 PROCURANDO PROJETOS NO JSON")
print("="*80 + "\n")

data = json.load(open('exemplo_json.txt', encoding='utf-8'))

# Palavras-chave relacionadas a projetos
palavras_projeto = ['projeto', 'pesquisa', 'extensao', 'ensino', 'participacao']

print("📌 BUSCANDO SEÇÕES RELACIONADAS A PROJETOS...\n")

# 1. Busca na raiz
print("1️⃣  CHAVES NA RAIZ DO JSON:")
print("-" * 80)
for key in data.keys():
    key_lower = key.lower()
    if any(palavra in key_lower for palavra in palavras_projeto):
        print(f"   ✅ ENCONTRADO: {key}")
        valor = data[key]
        if isinstance(valor, dict):
            print(f"      Sub-chaves: {list(valor.keys())[:10]}")
        elif isinstance(valor, list):
            print(f"      Lista com {len(valor)} itens")
            if valor and isinstance(valor[0], dict):
                print(f"      Campos do item: {list(valor[0].keys())[:10]}")

# 2. Busca em dadosGerais
print("\n2️⃣  DENTRO DE 'dadosGerais':")
print("-" * 80)
dados_gerais = data.get('dadosGerais', {})
for key in dados_gerais.keys():
    key_lower = key.lower()
    if any(palavra in key_lower for palavra in palavras_projeto):
        print(f"   ✅ ENCONTRADO: dadosGerais -> {key}")
        valor = dados_gerais[key]
        if isinstance(valor, dict):
            print(f"      Sub-chaves: {list(valor.keys())[:10]}")

# 3. Busca em dadosComplementares
print("\n3️⃣  DENTRO DE 'dadosComplementares':")
print("-" * 80)
dados_compl = data.get('dadosComplementares', {})
if dados_compl:
    print(f"   Chaves encontradas: {list(dados_compl.keys())}")
    for key in dados_compl.keys():
        print(f"\n   📁 {key}:")
        valor = dados_compl[key]
        if isinstance(valor, dict):
            print(f"      Sub-chaves: {list(valor.keys())[:15]}")
        elif isinstance(valor, list):
            print(f"      Lista com {len(valor)} itens")
            if valor and isinstance(valor[0], dict):
                print(f"      Campos do primeiro item:")
                for campo in list(valor[0].keys())[:15]:
                    print(f"         - {campo}")
else:
    print("   ⚠️  Seção vazia ou não encontrada")

# 4. Busca em outraProducao
print("\n4️⃣  DENTRO DE 'outraProducao':")
print("-" * 80)
outra_prod = data.get('outraProducao', {})
if outra_prod:
    print(f"   Chaves encontradas: {list(outra_prod.keys())}")
    for key in outra_prod.keys():
        key_lower = key.lower()
        if any(palavra in key_lower for palavra in palavras_projeto):
            print(f"\n   ✅ ENCONTRADO: {key}")
            valor = outra_prod[key]
            if isinstance(valor, list) and valor:
                print(f"      Lista com {len(valor)} itens")
                if isinstance(valor[0], dict):
                    print(f"      Campos: {list(valor[0].keys())[:15]}")

# 5. Busca em producaoTecnica
print("\n5️⃣  DENTRO DE 'producaoTecnica':")
print("-" * 80)
prod_tec = data.get('producaoTecnica', {})
if prod_tec:
    print(f"   Chaves encontradas: {list(prod_tec.keys())}")
    for key in prod_tec.keys():
        print(f"\n   📁 {key}:")
        valor = prod_tec[key]
        if isinstance(valor, dict):
            print(f"      Sub-chaves: {list(valor.keys())[:15]}")
        elif isinstance(valor, list):
            print(f"      Lista com {len(valor)} itens")

# 6. Procura específica por "participacaoEmProjetos"
print("\n6️⃣  PROCURANDO 'participacaoEmProjetos' ESPECIFICAMENTE:")
print("-" * 80)

def buscar_projetos_recursivo(obj, caminho=""):
    """Busca recursivamente por projetos"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            novo_caminho = f"{caminho}.{key}" if caminho else key
            if 'projeto' in key.lower():
                print(f"   ✅ {novo_caminho}")
                if isinstance(value, dict):
                    print(f"      Tipo: dicionário com {len(value)} chaves")
                    print(f"      Chaves: {list(value.keys())[:10]}")
                elif isinstance(value, list):
                    print(f"      Tipo: lista com {len(value)} itens")
                    if value and isinstance(value[0], dict):
                        print(f"      Campos do item: {list(value[0].keys())[:10]}")
            else:
                buscar_projetos_recursivo(value, novo_caminho)

buscar_projetos_recursivo(data)

# 7. Exemplo completo se encontrar
print("\n7️⃣  EXEMPLO COMPLETO (se houver projetos):")
print("-" * 80)

# Tenta acessar caminhos comuns
caminhos_possiveis = [
    ('dadosComplementares', 'participacaoEmProjetos'),
    ('dadosComplementares', 'participacaoEmProjetosDePesquisa'),
    ('dadosGerais', 'participacaoEmProjetos'),
    ('outraProducao', 'participacaoEmProjetos'),
]

for caminho in caminhos_possiveis:
    try:
        temp = data
        for key in caminho:
            temp = temp[key]
        
        if temp:
            print(f"\n   ✅ ENCONTRADO em: {' -> '.join(caminho)}")
            if isinstance(temp, dict):
                print(f"      Sub-chaves: {list(temp.keys())}")
                # Pega a primeira sub-chave que seja lista
                for sub_key, sub_value in temp.items():
                    if isinstance(sub_value, list) and sub_value:
                        print(f"\n      Exemplo do primeiro projeto em '{sub_key}':")
                        print(json.dumps(sub_value[0], indent=6, ensure_ascii=False)[:1000])
                        break
            elif isinstance(temp, list) and temp:
                print(f"      Total de projetos: {len(temp)}")
                print(f"\n      Exemplo do primeiro projeto:")
                print(json.dumps(temp[0], indent=6, ensure_ascii=False)[:1000])
            break
    except:
        pass

print("\n" + "="*80)
print("✅ BUSCA CONCLUÍDA")
print("="*80)
print("\n💡 Agora sabemos onde estão os projetos!\n")