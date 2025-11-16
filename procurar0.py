#!/usr/bin/env python3
"""
Procura projetos em vários docentes até achar
"""

import json
import sqlite3
from config import DB_NAME

print("\n" + "="*80)
print("🔍 PROCURANDO PROJETOS EM MÚLTIPLOS DOCENTES")
print("="*80 + "\n")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Busca em vários docentes
cursor.execute("SELECT id, nome, data_completa FROM docentes LIMIT 50")
docentes = cursor.fetchall()

encontrou_projeto = False

for doc_id, nome, data_json in docentes:
    try:
        data = json.loads(data_json)
        
        # Procura em todas as chaves possíveis
        def procurar_recursivo(obj, caminho="", nivel=0):
            global encontrou_projeto
            
            if nivel > 5 or encontrou_projeto:
                return
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    # Palavras-chave de projetos
                    if any(palavra in key.lower() for palavra in ['projeto', 'PESQUISA', 'EXTENSAO']):
                        if isinstance(value, list) and value:
                            # Verifica se tem campos de projeto
                            primeiro = value[0]
                            if isinstance(primeiro, dict):
                                # Verifica se tem campos típicos de projeto
                                campos_projeto = ['nomeDoProjeto', 'natureza', 'situacao', 'anoInicio']
                                if any(campo in primeiro for campo in campos_projeto):
                                    print(f"✅ PROJETO ENCONTRADO em: {nome}")
                                    print(f"   Localização: {caminho}.{key}")
                                    print(f"   Total de projetos: {len(value)}")
                                    print(f"\n   📋 ESTRUTURA DO PROJETO:")
                                    print(json.dumps(primeiro, indent=6, ensure_ascii=False)[:1500])
                                    encontrou_projeto = True
                                    return
                    
                    procurar_recursivo(value, f"{caminho}.{key}" if caminho else key, nivel + 1)
        
        procurar_recursivo(data)
        
        if encontrou_projeto:
            break
            
    except:
        continue

if not encontrou_projeto:
    print("⚠️  Projetos não encontrados nos primeiros 50 docentes")
    print("   Vou verificar a estrutura completa de dadosComplementares...\n")
    
    # Pega primeiro docente e mostra dadosComplementares
    cursor.execute("SELECT data_completa FROM docentes LIMIT 1")
    data_json = cursor.fetchone()[0]
    data = json.loads(data_json)
    
    dados_compl = data.get('dadosComplementares', {})
    if dados_compl:
        print("📋 Chaves em dadosComplementares:")
        for key in dados_compl.keys():
            print(f"   - {key}")

conn.close()

print("\n" + "="*80)
print("✅ BUSCA CONCLUÍDA")
print("="*80 + "\n")