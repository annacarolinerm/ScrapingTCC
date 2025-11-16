#!/usr/bin/env python3
"""
Busca ONDE estão os projetos no JSON
"""

import json
import sqlite3
from config import DB_NAME

print("\n" + "="*80)
print("🔍 BUSCANDO PROJETOS NO JSON")
print("="*80 + "\n")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("SELECT id, nome, data_completa FROM docentes LIMIT 1")
result = cursor.fetchone()

if result:
    doc_id, nome, data_json = result
    print(f"📄 Analisando: {nome}\n")
    
    data = json.loads(data_json)
    
    def buscar_projetos(obj, caminho="", nivel=0):
        """Busca recursiva por projetos"""
        if nivel > 4:
            return
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                novo_caminho = f"{caminho}.{key}" if caminho else key
                
                # Procura por campos relacionados a projetos
                if any(palavra in key.lower() for palavra in ['projeto', 'natureza', 'sequenciaprojeto']):
                    print(f"✅ ENCONTRADO: {novo_caminho}")
                    print(f"   Tipo: {type(value).__name__}")
                    
                    if isinstance(value, list) and value:
                        print(f"   Lista com {len(value)} itens")
                        if isinstance(value[0], dict):
                            print(f"   Chaves do item: {list(value[0].keys())[:10]}")
                            
                            # Se tiver natureza, mostra exemplo
                            if 'natureza' in value[0]:
                                print(f"\n   📋 EXEMPLO DE PROJETO:")
                                print(json.dumps(value[0], indent=6, ensure_ascii=False)[:1000])
                                return True
                    elif isinstance(value, dict):
                        print(f"   Dict com {len(value)} chaves: {list(value.keys())[:10]}")
                        buscar_projetos(value, novo_caminho, nivel + 1)
                else:
                    buscar_projetos(value, novo_caminho, nivel + 1)
    
    print("🔍 Procurando projetos...\n")
    achou = buscar_projetos(data)
    
    if not achou:
        print("\n⚠️  Não encontrei projetos neste docente específico.")
        print("   Vou verificar em outro docente...\n")
        
        # Tenta outro docente
        cursor.execute("SELECT id, nome, data_completa FROM docentes LIMIT 1 OFFSET 10")
        result2 = cursor.fetchone()
        
        if result2:
            doc_id2, nome2, data_json2 = result2
            print(f"📄 Tentando com: {nome2}\n")
            data2 = json.loads(data_json2)
            buscar_projetos(data2)

conn.close()

print("\n" + "="*80)
print("✅ BUSCA CONCLUÍDA")
print("="*80 + "\n")