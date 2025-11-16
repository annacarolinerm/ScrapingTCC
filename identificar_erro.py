#!/usr/bin/env python3
"""
Identifica EXATAMENTE onde está o erro no normalizer
"""

import json
import sqlite3
from config import DB_NAME
import traceback

print("\n" + "="*80)
print("🔍 IDENTIFICANDO ERRO EXATO DO NORMALIZER")
print("="*80 + "\n")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Pega um docente que deu erro
cursor.execute("SELECT id, nome, data_completa FROM docentes WHERE id = 697")
result = cursor.fetchone()

if result:
    doc_id, nome, data_json = result
    print(f"📄 Testando docente com erro: {nome} (ID: {doc_id})\n")
    
    data = json.loads(data_json)
    
    # Testa cada extração separadamente
    print("1️⃣  Testando extract_producao_bibliografica:")
    print("-" * 80)
    try:
        producao = data.get('producaoBibliografica', {})
        print(f"   producaoBibliografica: {type(producao).__name__}")
        
        # ARTIGOS
        artigos_pub = producao.get('artigosPublicados', [])
        print(f"   artigosPublicados: {type(artigos_pub).__name__}, len={len(artigos_pub) if isinstance(artigos_pub, list) else 'N/A'}")
        
        if isinstance(artigos_pub, list) and len(artigos_pub) > 0:
            primeiro = artigos_pub[0]
            print(f"   Primeiro item: {type(primeiro).__name__}")
            print(f"   Chaves: {list(primeiro.keys()) if isinstance(primeiro, dict) else 'N/A'}")
            
            if isinstance(primeiro, dict):
                artigos = primeiro.get('artigoPublicado', [])
                print(f"   artigoPublicado: {type(artigos).__name__}")
                
                if isinstance(artigos, list):
                    print(f"   ✅ É lista com {len(artigos)} artigos")
                else:
                    print(f"   ❌ NÃO É LISTA! É {type(artigos).__name__}")
            elif isinstance(primeiro, list):
                print(f"   ❌ ERRO: Primeiro item é LISTA (esperava dict)")
                print(f"   Lista com {len(primeiro)} itens")
                if primeiro:
                    print(f"   Primeiro da lista: {type(primeiro[0])}")
        
        # TRABALHOS
        trabalhos_pub = producao.get('trabalhosEmEventos', [])
        print(f"\n   trabalhosEmEventos: {type(trabalhos_pub).__name__}, len={len(trabalhos_pub) if isinstance(trabalhos_pub, list) else 'N/A'}")
        
        if isinstance(trabalhos_pub, list) and len(trabalhos_pub) > 0:
            primeiro = trabalhos_pub[0]
            print(f"   Primeiro item: {type(primeiro).__name__}")
            
            if isinstance(primeiro, list):
                print(f"   ❌ ERRO ENCONTRADO! Primeiro item é LISTA")
                print(f"   Lista tem {len(primeiro)} itens")
                if primeiro:
                    print(f"   Tipo do primeiro: {type(primeiro[0])}")
                    if isinstance(primeiro[0], dict):
                        print(f"   Chaves: {list(primeiro[0].keys())[:10]}")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        traceback.print_exc()
    
    print("\n2️⃣  Testando extract_orientacoes:")
    print("-" * 80)
    try:
        outra_prod = data.get('outraProducao', {})
        orient_container = outra_prod.get('orientacoesConcluidas', [])
        print(f"   orientacoesConcluidas: {type(orient_container).__name__}, len={len(orient_container) if isinstance(orient_container, list) else 'N/A'}")
        
        if isinstance(orient_container, list) and len(orient_container) > 0:
            primeiro = orient_container[0]
            print(f"   Primeiro item: {type(primeiro).__name__}")
            
            if isinstance(primeiro, dict):
                mestrado = primeiro.get('orientacoesConcluidasParaMestrado', [])
                print(f"   Mestrado: {type(mestrado).__name__}")
                
                if isinstance(mestrado, list):
                    print(f"   ✅ Mestrado é lista com {len(mestrado)} itens")
                else:
                    print(f"   ❌ Mestrado NÃO é lista!")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        traceback.print_exc()
    
    print("\n3️⃣  Estrutura COMPLETA de producaoBibliografica:")
    print("-" * 80)
    print(json.dumps(producao, indent=3, ensure_ascii=False)[:2000])

conn.close()

print("\n" + "="*80)
print("✅ DIAGNÓSTICO CONCLUÍDO")
print("="*80 + "\n")