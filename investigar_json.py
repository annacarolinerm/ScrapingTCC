#!/usr/bin/env python3
"""
Script para investigar a estrutura dos dados JSON
Mostra como os dados realmente estão organizados
"""

import json
from database import Database


def investigar_estrutura():
    """Investiga a estrutura dos dados de alguns docentes"""
    
    print("\n" + "="*70)
    print("🔍 INVESTIGANDO ESTRUTURA DOS DADOS JSON")
    print("="*70 + "\n")
    
    db = Database()
    db.connect()
    
    # Pega os primeiros 3 docentes
    db.cursor.execute("""
        SELECT id, nome, data_completa 
        FROM docentes 
        LIMIT 3
    """)
    
    docentes = db.cursor.fetchall()
    
    if not docentes:
        print("❌ Nenhum docente encontrado!")
        db.close()
        return
    
    for i, (doc_id, nome, data_json) in enumerate(docentes, 1):
        print(f"\n{'='*70}")
        print(f"📄 DOCENTE {i}: {nome}")
        print(f"{'='*70}\n")
        
        try:
            data = json.loads(data_json)
            
            # Mostra as chaves principais
            print("🔑 CHAVES PRINCIPAIS DO JSON:")
            for key in data.keys():
                print(f"   - {key}")
            
            # Investiga dadosGerais
            if 'dadosGerais' in data:
                print("\n📋 CHAVES DENTRO DE 'dadosGerais':")
                dados_gerais = data['dadosGerais']
                for key in dados_gerais.keys():
                    valor = dados_gerais[key]
                    tipo = type(valor).__name__
                    
                    if isinstance(valor, list):
                        print(f"   - {key} (lista com {len(valor)} itens)")
                        if len(valor) > 0:
                            print(f"      Exemplo do primeiro item: {type(valor[0]).__name__}")
                            if isinstance(valor[0], dict):
                                print(f"      Chaves: {list(valor[0].keys())[:5]}")
                    elif isinstance(valor, dict):
                        print(f"   - {key} (dicionário com {len(valor)} chaves)")
                        print(f"      Chaves: {list(valor.keys())[:5]}")
                    else:
                        print(f"   - {key} ({tipo})")
            
            # Procura por formações
            print("\n🎓 BUSCANDO FORMAÇÕES:")
            formacoes_encontradas = False
            
            # Tenta vários caminhos possíveis
            caminhos_formacoes = [
                ['dadosGerais', 'formacaoAcademicaTitulacao'],
                ['dadosGerais', 'formacaoAcademica'],
                ['formacaoAcademicaTitulacao'],
                ['formacao'],
            ]
            
            for caminho in caminhos_formacoes:
                try:
                    temp = data
                    for key in caminho:
                        temp = temp[key]
                    
                    if temp:
                        print(f"   ✅ Encontrado em: {' -> '.join(caminho)}")
                        if isinstance(temp, list) and len(temp) > 0:
                            print(f"   📊 Total de formações: {len(temp)}")
                            print(f"   📝 Exemplo da primeira:")
                            print(f"      {json.dumps(temp[0], indent=6, ensure_ascii=False)[:500]}")
                        formacoes_encontradas = True
                        break
                except:
                    pass
            
            if not formacoes_encontradas:
                print("   ❌ Não encontrado em nenhum caminho testado")
            
            # Procura por produções
            print("\n📚 BUSCANDO PRODUÇÕES BIBLIOGRÁFICAS:")
            producoes_encontradas = False
            
            caminhos_producoes = [
                ['dadosGerais', 'producaoBibliografica'],
                ['producaoBibliografica'],
                ['producoes'],
            ]
            
            for caminho in caminhos_producoes:
                try:
                    temp = data
                    for key in caminho:
                        temp = temp[key]
                    
                    if temp:
                        print(f"   ✅ Encontrado em: {' -> '.join(caminho)}")
                        if isinstance(temp, dict):
                            print(f"   📊 Categorias encontradas:")
                            for cat, items in temp.items():
                                if isinstance(items, list):
                                    print(f"      - {cat}: {len(items)} itens")
                        producoes_encontradas = True
                        break
                except:
                    pass
            
            if not producoes_encontradas:
                print("   ❌ Não encontrado em nenhum caminho testado")
            
            # Procura orientações
            print("\n👨‍🎓 BUSCANDO ORIENTAÇÕES:")
            orientacoes_encontradas = False
            
            caminhos_orientacoes = [
                ['dadosGerais', 'outraProducao', 'orientacoesConcluidas'],
                ['dadosGerais', 'orientacoes'],
                ['orientacoesConcluidas'],
            ]
            
            for caminho in caminhos_orientacoes:
                try:
                    temp = data
                    for key in caminho:
                        temp = temp[key]
                    
                    if temp:
                        print(f"   ✅ Encontrado em: {' -> '.join(caminho)}")
                        if isinstance(temp, list):
                            print(f"   📊 Total: {len(temp)} orientações")
                        orientacoes_encontradas = True
                        break
                except:
                    pass
            
            if not orientacoes_encontradas:
                print("   ❌ Não encontrado em nenhum caminho testado")
            
            # Salva um exemplo completo
            if i == 1:
                print(f"\n💾 Salvando exemplo completo do JSON no arquivo 'exemplo_json.txt'...")
                with open('exemplo_json.txt', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print("   ✅ Salvo! Abra o arquivo para ver toda a estrutura.")
        
        except Exception as e:
            print(f"❌ Erro ao processar: {e}")
    
    db.close()
    
    print(f"\n{'='*70}")
    print("✅ INVESTIGAÇÃO CONCLUÍDA")
    print(f"{'='*70}\n")
    print("💡 Agora podemos ajustar o normalizer com base na estrutura real!")
    print("")


if __name__ == "__main__":
    investigar_estrutura()