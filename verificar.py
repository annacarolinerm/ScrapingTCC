#!/usr/bin/env python3
"""
Verifica palavras-chave e orientações
"""

import json
import sqlite3
from config import DB_NAME

print("\n" + "="*80)
print("🔍 VERIFICANDO PALAVRAS-CHAVE E ORIENTAÇÕES")
print("="*80 + "\n")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# 1. Verifica palavras-chave no banco
print("1️⃣  PALAVRAS-CHAVE NO BANCO:")
print("-" * 80)

cursor.execute("SELECT id, palavras_chave FROM dados_gerais WHERE palavras_chave IS NOT NULL AND palavras_chave != '' LIMIT 5")
resultados = cursor.fetchall()

if resultados:
    print(f"✅ Encontradas {len(resultados)} com palavras-chave preenchidas:\n")
    for doc_id, pk in resultados:
        print(f"   Docente {doc_id}: {pk[:100]}...")
else:
    print("❌ NENHUMA palavra-chave no banco!")
    print("   Vou verificar no JSON...\n")
    
    cursor.execute("SELECT id, nome, data_completa FROM docentes LIMIT 3")
    docs = cursor.fetchall()
    
    for doc_id, nome, data_json in docs:
        data = json.loads(data_json)
        
        print(f"📄 {nome}:")
        
        # Verifica palavrasChave
        pk = data.get('palavrasChave')
        print(f"   palavrasChave no JSON: {type(pk).__name__ if pk is not None else 'None'}")
        
        if pk:
            if isinstance(pk, list):
                print(f"   Lista com {len(pk)} itens")
                if pk:
                    print(f"   Exemplos: {pk[:3]}")
            elif isinstance(pk, dict):
                print(f"   Dict com chaves: {list(pk.keys())[:5]}")
                # Tenta extrair
                palavras = []
                for i in range(1, 10):
                    p = pk.get(f'palavraChave{i}')
                    if p:
                        palavras.append(str(p))
                if palavras:
                    print(f"   Palavras extraídas: {palavras[:3]}")
        
        # Mostra estrutura completa
        print(f"\n   Estrutura completa de palavrasChave:")
        if pk:
            print(json.dumps(pk, indent=6, ensure_ascii=False)[:500])
        print()

# 2. Verifica orientações
print("\n2️⃣  ORIENTAÇÕES:")
print("-" * 80)

cursor.execute("SELECT COUNT(*) FROM orientacoes_concluidas")
count_orient = cursor.fetchone()[0]
print(f"Orientações no banco: {count_orient}")

if count_orient == 0:
    print("\n❌ Nenhuma orientação! Verificando no JSON...\n")
    
    cursor.execute("SELECT id, nome, data_completa FROM docentes LIMIT 10")
    docs = cursor.fetchall()
    
    total_encontradas = 0
    total_ifs = 0
    exemplos_inst = []
    
    for doc_id, nome, data_json in docs:
        try:
            data = json.loads(data_json)
            
            outra = data.get('outraProducao', {})
            if not isinstance(outra, dict):
                continue
            
            orient_list = outra.get('orientacoesConcluidas', [])
            if not isinstance(orient_list, list) or len(orient_list) == 0:
                continue
            
            item = orient_list[0]
            if not isinstance(item, dict):
                continue
            
            # Verifica todos os tipos
            mestrado = item.get('orientacoesConcluidasParaMestrado', [])
            doutorado = item.get('orientacoesConcluidasParaDoutorado', [])
            outras = item.get('outrasOrientacoesConcluidas', [])
            
            total_doc = 0
            if isinstance(mestrado, list):
                total_doc += len(mestrado)
                for ori in mestrado[:2]:
                    if isinstance(ori, dict):
                        inst = ori.get('nomeDoInstituicao') or ori.get('instituicao', '')
                        if inst and inst not in exemplos_inst:
                            exemplos_inst.append(str(inst))
            
            if isinstance(doutorado, list):
                total_doc += len(doutorado)
            
            if isinstance(outras, list):
                total_doc += len(outras)
                for ori in outras[:2]:
                    if isinstance(ori, dict):
                        inst = ori.get('nomeDoInstituicao') or ori.get('instituicao', '')
                        if inst and inst not in exemplos_inst:
                            exemplos_inst.append(str(inst))
            
            if total_doc > 0:
                total_encontradas += total_doc
                print(f"   {nome}: {total_doc} orientações")
        
        except:
            continue
    
    print(f"\n📊 Total encontrado no JSON (10 docentes): {total_encontradas}")
    
    if exemplos_inst:
        print(f"\n📋 Exemplos de instituições:")
        for inst in exemplos_inst[:10]:
            # Verifica se é IF
            inst_upper = inst.upper()
            is_if = any(sigla in inst_upper for sigla in ['IFAC', 'IFAL', 'IFB', 'IFBA', 'IFCE', 'IFC', 'IFES', 'IFG', 'IFMA', 'IFMG', 'IFMS', 'IFPA', 'IFPB', 'IFPE', 'IFPI', 'IFPR', 'IFRJ', 'IFRN', 'IFRO', 'IFRR', 'IFRS', 'IFSC', 'IFSP', 'IFS', 'IFTO', 'CEFET']) or 'INSTITUTO FEDERAL' in inst_upper
            
            emoji = "✅" if is_if else "❌"
            print(f"   {emoji} {inst}")
        
        print(f"\n💡 Se nenhuma é IF, o filtro está bloqueando TUDO!")
        print(f"   Você quer orientações APENAS de IFs ou de TODAS as instituições?")

# 3. Verifica estrutura da tabela dados_gerais
print("\n3️⃣  ESTRUTURA DA TABELA dados_gerais:")
print("-" * 80)

cursor.execute("PRAGMA table_info(dados_gerais)")
colunas = cursor.fetchall()

tem_palavras_chave = False
for col in colunas:
    if col[1] == 'palavras_chave':
        tem_palavras_chave = True
        print(f"✅ Coluna 'palavras_chave' existe!")
        break

if not tem_palavras_chave:
    print(f"❌ Coluna 'palavras_chave' NÃO EXISTE!")
    print(f"\n💡 SOLUÇÃO: Execute novamente:")
    print(f"   python atualizar_banco.py")

conn.close()

print("\n" + "="*80)
print("✅ VERIFICAÇÃO CONCLUÍDA")
print("="*80 + "\n")