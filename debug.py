#!/usr/bin/env python3
"""
DEBUG COMPLETO - Mostra EXATAMENTE onde está falhando
"""

import json
import sqlite3
from config import DB_NAME

print("\n" + "="*80)
print("🔍 DEBUG COMPLETO DE ORIENTAÇÕES")
print("="*80 + "\n")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Siglas IFs
siglas_ifs = {
    'IFAC', 'IFAL', 'IFAP', 'IFAM', 'IFBA', 'IFBAIANO', 'IFB', 'IFCE', 'IFES',
    'IFG', 'IFGOIANO', 'IFMA', 'IFMG', 'IFNMG', 'IFSUDESTEMG', 'IFSULDEMINAS',
    'IFTM', 'IFMT', 'IFMS', 'IFPA', 'IFPB', 'IFPE', 'IFSERTAOPE', 'IFPI',
    'IFPR', 'IFRJ', 'IFFLUMINENSE', 'IFRN', 'IFRO', 'IFRR', 'IFRS',
    'IFFARROUPILHA', 'IFSUL', 'IFSC', 'IFC', 'IFSP', 'IFS', 'IFTO',
    'CEFET-RJ', 'CEFET-MG', 'CEFET RJ', 'CEFET MG', 'CEFET'
}

def is_if(instituicao: str) -> bool:
    if not instituicao:
        return False
    inst_upper = str(instituicao).upper()
    return any(sigla in inst_upper for sigla in siglas_ifs) or \
           'INSTITUTO FEDERAL' in inst_upper or 'CENTRO FEDERAL' in inst_upper

# Pega um docente com orientações
cursor.execute("SELECT id, nome, data_completa FROM docentes WHERE id = 1")
result = cursor.fetchone()

if result:
    doc_id, nome, data_json = result
    print(f"📄 Testando: {nome} (ID: {doc_id})\n")
    
    data = json.loads(data_json)
    
    # PASSO 1: Verifica outraProducao
    print("PASSO 1: Verificando outraProducao")
    print("-" * 80)
    outra = data.get('outraProducao')
    print(f"outraProducao existe? {outra is not None}")
    print(f"Tipo: {type(outra).__name__ if outra else 'None'}")
    
    if not isinstance(outra, dict):
        print("❌ ERRO: outraProducao não é dict!")
        exit()
    
    print("✅ outraProducao é dict\n")
    
    # PASSO 2: Verifica orientacoesConcluidas
    print("PASSO 2: Verificando orientacoesConcluidas")
    print("-" * 80)
    orient_list = outra.get('orientacoesConcluidas')
    print(f"orientacoesConcluidas existe? {orient_list is not None}")
    print(f"Tipo: {type(orient_list).__name__ if orient_list else 'None'}")
    
    if isinstance(orient_list, list):
        print(f"Length: {len(orient_list)}")
    else:
        print("❌ ERRO: orientacoesConcluidas não é lista!")
        exit()
    
    if len(orient_list) == 0:
        print("⚠️  Lista está VAZIA! Este docente não tem orientações.")
        print("   Vou pegar OUTRO docente...\n")
        
        # Pega outro
        cursor.execute("SELECT id, nome, data_completa FROM docentes LIMIT 1 OFFSET 5")
        result = cursor.fetchone()
        doc_id, nome, data_json = result
        print(f"📄 Testando: {nome} (ID: {doc_id})\n")
        data = json.loads(data_json)
        outra = data.get('outraProducao', {})
        orient_list = outra.get('orientacoesConcluidas', [])
    
    print(f"✅ orientacoesConcluidas tem {len(orient_list)} items\n")
    
    # PASSO 3: Pega primeiro item
    print("PASSO 3: Pegando primeiro item da lista")
    print("-" * 80)
    if len(orient_list) > 0:
        item = orient_list[0]
        print(f"Tipo do item: {type(item).__name__}")
        
        if isinstance(item, dict):
            print(f"Chaves do item: {list(item.keys())}\n")
        else:
            print("❌ ERRO: Item não é dict!")
            exit()
    else:
        print("❌ Lista vazia!")
        exit()
    
    # PASSO 4: Verifica outrasOrientacoesConcluidas
    print("PASSO 4: Verificando outrasOrientacoesConcluidas")
    print("-" * 80)
    outras = item.get('outrasOrientacoesConcluidas')
    print(f"outrasOrientacoesConcluidas existe? {outras is not None}")
    print(f"Tipo: {type(outras).__name__ if outras else 'None'}")
    
    if isinstance(outras, list):
        print(f"Length: {len(outras)}")
        
        if len(outras) > 0:
            print(f"✅ Tem {len(outras)} orientações!\n")
            
            # PASSO 5: Analisa PRIMEIRA orientação
            print("PASSO 5: Analisando PRIMEIRA orientação")
            print("-" * 80)
            ori = outras[0]
            print(f"Tipo: {type(ori).__name__}")
            print(f"Chaves: {list(ori.keys())}\n")
            
            # PASSO 6: Busca detalhamento
            print("PASSO 6: Buscando detalhamento")
            print("-" * 80)
            det = ori.get('detalhamentoDeOutrasOrientacoesConcluidas')
            print(f"detalhamentoDeOutrasOrientacoesConcluidas existe? {det is not None}")
            print(f"Tipo: {type(det).__name__ if det else 'None'}")
            
            if isinstance(det, dict):
                print(f"Chaves do detalhamento: {list(det.keys())}\n")
                
                # PASSO 7: Extrai campos
                print("PASSO 7: Extraindo campos")
                print("-" * 80)
                nome_ori = det.get('nomeDoOrientado', '')
                curso = det.get('nomeDoCurso', '')
                inst = det.get('nomeDaInstituicao', '')
                
                print(f"nomeDoOrientado: {nome_ori}")
                print(f"nomeDoCurso: {curso}")
                print(f"nomeDaInstituicao: {inst}\n")
                
                # PASSO 8: Testa filtro IF
                print("PASSO 8: Testando filtro IF")
                print("-" * 80)
                print(f"Instituição: '{inst}'")
                print(f"É IF? {is_if(inst)}")
                
                if is_if(inst):
                    print(f"✅ PASSOU NO FILTRO!")
                    print(f"\n🎉 ESTA ORIENTAÇÃO DEVERIA SER INSERIDA!")
                    print(f"\n⚠️  MAS NÃO FOI! Por que?")
                    print(f"\n💡 POSSÍVEIS CAUSAS:")
                    print(f"   1. Erro na função de inserção (try/except engoliu)")
                    print(f"   2. Coluna 'tipo_orientacao' não existe")
                    print(f"   3. Outro erro no SQL INSERT")
                else:
                    print(f"❌ NÃO PASSOU NO FILTRO!")
                    print(f"   Instituição '{inst}' não é IF")
                    print(f"\n💡 Se TODAS as orientações não passam no filtro,")
                    print(f"   você precisa REMOVER o filtro ou aceitar que terá 0 orientações.")
            else:
                print("❌ detalhamento não é dict!")
        else:
            print("⚠️  Lista vazia!")
    else:
        print("❌ Não é lista!")
    
    # PASSO 9: Verifica estrutura da tabela
    print("\n\nPASSO 9: Verificando estrutura da tabela")
    print("-" * 80)
    cursor.execute("PRAGMA table_info(orientacoes_concluidas)")
    colunas = cursor.fetchall()
    print("Colunas da tabela:")
    for col in colunas:
        print(f"   - {col[1]} ({col[2]})")
    
    tem_tipo_orientacao = any(col[1] == 'tipo_orientacao' for col in colunas)
    if tem_tipo_orientacao:
        print("\n✅ Coluna 'tipo_orientacao' existe!")
    else:
        print("\n❌ Coluna 'tipo_orientacao' NÃO EXISTE!")
        print("   💡 Execute: python atualizar_banco.py")

conn.close()

print("\n" + "="*80)
print("✅ DEBUG CONCLUÍDO")
print("="*80 + "\n")