#!/usr/bin/env python3
"""
Verifica EXATAMENTE quais instituições aparecem nas orientações
"""

import json
import sqlite3
from config import DB_NAME

print("\n" + "="*80)
print("🔍 VERIFICANDO INSTITUIÇÕES DAS ORIENTAÇÕES")
print("="*80 + "\n")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("SELECT id, nome, data_completa FROM docentes LIMIT 20")
docs = cursor.fetchall()

instituicoes_count = {}
total_orientacoes = 0
total_com_instituicao = 0
total_sem_instituicao = 0

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
        
        # Todos os tipos
        todos_tipos = {
            'orientacoesConcluidasParaMestrado': item.get('orientacoesConcluidasParaMestrado', []),
            'orientacoesConcluidasParaDoutorado': item.get('orientacoesConcluidasParaDoutorado', []),
            'orientacoesConcluidasParaPosDoutorado': item.get('orientacoesConcluidasParaPosDoutorado', []),
            'outrasOrientacoesConcluidas': item.get('outrasOrientacoesConcluidas', [])
        }
        
        for tipo_nome, orients in todos_tipos.items():
            if not isinstance(orients, list):
                continue
            
            for ori in orients:
                if not isinstance(ori, dict):
                    continue
                
                total_orientacoes += 1
                
                # Tenta todos os campos possíveis
                inst = ori.get('nomeDoInstituicao') or ori.get('instituicao') or ori.get('nomeInstituicao', '')
                inst = str(inst).strip()
                
                if inst and inst != 'None':
                    total_com_instituicao += 1
                    instituicoes_count[inst] = instituicoes_count.get(inst, 0) + 1
                else:
                    total_sem_instituicao += 1
                    # Mostra o que tem no dict
                    if total_sem_instituicao <= 3:
                        print(f"⚠️  Orientação sem instituição (exemplo {total_sem_instituicao}):")
                        print(f"   Chaves disponíveis: {list(ori.keys())[:10]}")
                        print(f"   Exemplo de valores:")
                        for k in list(ori.keys())[:5]:
                            v = ori.get(k)
                            if isinstance(v, str):
                                print(f"      {k}: {v[:50]}")
                            elif isinstance(v, dict):
                                print(f"      {k}: (dict com {len(v)} chaves)")
                        print()
    
    except:
        continue

conn.close()

print("="*80)
print("📊 RESULTADO:")
print("="*80)
print(f"Total de orientações: {total_orientacoes}")
print(f"Com instituição preenchida: {total_com_instituicao}")
print(f"SEM instituição: {total_sem_instituicao}")

if instituicoes_count:
    print(f"\n📋 INSTITUIÇÕES ENCONTRADAS ({len(instituicoes_count)}):")
    print("-" * 80)
    
    # Ordena por quantidade
    instituicoes_ordenadas = sorted(instituicoes_count.items(), key=lambda x: x[1], reverse=True)
    
    # Separa IFs de não-IFs
    siglas_ifs = ['IFAC', 'IFAL', 'IFAP', 'IFAM', 'IFBA', 'IFBAIANO', 'IFB', 'IFCE', 'IFES',
                  'IFG', 'IFGOIANO', 'IFMA', 'IFMG', 'IFNMG', 'IFSUDESTEMG', 'IFSULDEMINAS',
                  'IFTM', 'IFMT', 'IFMS', 'IFPA', 'IFPB', 'IFPE', 'IFSERTAOPE', 'IFPI',
                  'IFPR', 'IFRJ', 'IFFLUMINENSE', 'IFRN', 'IFRO', 'IFRR', 'IFRS',
                  'IFFARROUPILHA', 'IFSUL', 'IFSC', 'IFC', 'IFSP', 'IFS', 'IFTO',
                  'CEFET-RJ', 'CEFET-MG', 'CEFET RJ', 'CEFET MG', 'CEFET']
    
    ifs_encontrados = []
    nao_ifs = []
    
    for inst, count in instituicoes_ordenadas:
        inst_upper = inst.upper()
        is_if = any(sigla in inst_upper for sigla in siglas_ifs) or 'INSTITUTO FEDERAL' in inst_upper or 'CENTRO FEDERAL' in inst_upper
        
        if is_if:
            ifs_encontrados.append((inst, count))
        else:
            nao_ifs.append((inst, count))
    
    if ifs_encontrados:
        print(f"\n✅ INSTITUIÇÕES IFs ({len(ifs_encontrados)} tipos, {sum(c for _, c in ifs_encontrados)} orientações):")
        for inst, count in ifs_encontrados[:15]:
            print(f"   {count:3d}x - {inst}")
    
    if nao_ifs:
        print(f"\n❌ OUTRAS INSTITUIÇÕES ({len(nao_ifs)} tipos, {sum(c for _, c in nao_ifs)} orientações):")
        for inst, count in nao_ifs[:15]:
            print(f"   {count:3d}x - {inst}")
    
    if not ifs_encontrados:
        print("\n⚠️  PROBLEMA IDENTIFICADO:")
        print("   NENHUMA orientação é de IF!")
        print("   O filtro está bloqueando 100% das orientações.")
        print("\n💡 DECISÃO NECESSÁRIA:")
        print("   1. REMOVER o filtro → Incluir TODAS as orientações")
        print("   2. MANTER o filtro → Tabela continuará vazia")
else:
    print("\n⚠️  Nenhuma instituição encontrada!")
    print("   O campo 'nomeDoInstituicao' / 'instituicao' está vazio ou não existe.")

print("\n" + "="*80)
print("✅ VERIFICAÇÃO CONCLUÍDA")
print("="*80 + "\n")