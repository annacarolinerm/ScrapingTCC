#!/usr/bin/env python3
"""
Script principal para coleta de dados dos docentes da Rede Federal via Portal Integra

Uso:
    python main.py                    # Coleta TODAS as 40 instituições
    python main.py IFB IFSP IFRJ      # Coleta apenas instituições específicas
"""

import asyncio
import sys
import time
from datetime import datetime
from typing import List, Optional

from config import INSTITUICOES
from database import Database, init_database
from scraper import scrape_multiplas_instituicoes


def print_banner():
    """Imprime banner do sistema"""
    print("\n" + "="*70)
    print("🎓 SCRAPER PORTAL INTEGRA - REDE FEDERAL DE ENSINO")
    print("="*70)
    print("📚 Sistema de coleta de dados de docentes dos IFs e CEFETs")
    print("🔧 Versão 1.0 - Robusto com retry automático e paralelização")
    print("="*70 + "\n")


def parse_arguments() -> Optional[List[str]]:
    """
    Processa argumentos da linha de comando
    
    Returns:
        Lista de siglas para processar ou None para todas
    """
    if len(sys.argv) > 1:
        siglas = [s.upper() for s in sys.argv[1:]]
        
        # Valida siglas
        siglas_validas = []
        siglas_invalidas = []
        
        for sigla in siglas:
            if sigla in INSTITUICOES:
                siglas_validas.append(sigla)
            else:
                siglas_invalidas.append(sigla)
        
        if siglas_invalidas:
            print(f"⚠️  Siglas inválidas ignoradas: {', '.join(siglas_invalidas)}")
            print(f"💡 Siglas disponíveis: {', '.join(sorted(INSTITUICOES.keys()))}\n")
        
        if not siglas_validas:
            print("❌ Nenhuma sigla válida fornecida!")
            return None
        
        return siglas_validas
    
    return None  # Processar todas


def salvar_resultados_no_banco(db: Database, todos_resultados: dict, todas_stats: dict):
    """
    Salva os resultados coletados no banco de dados
    
    Args:
        db: Instância do banco de dados
        todos_resultados: Dicionário com resultados por instituição
        todas_stats: Dicionário com estatísticas por instituição
    """
    print(f"\n{'='*70}")
    print("💾 SALVANDO DADOS NO BANCO DE DADOS")
    print(f"{'='*70}\n")
    
    total_salvos = 0
    total_erros = 0
    
    for sigla, docentes in todos_resultados.items():
        print(f"💾 {sigla}: Salvando {len(docentes)} docentes...")
        
        salvos_instituicao = 0
        erros_instituicao = 0
        
        for pessoa_basica, pessoa_completa in docentes:
            docente_id = db.insert_docente(sigla, pessoa_basica, pessoa_completa)
            
            if docente_id:
                salvos_instituicao += 1
            else:
                erros_instituicao += 1
        
        print(f"   ✅ {sigla}: {salvos_instituicao} salvos, {erros_instituicao} erros")
        
        total_salvos += salvos_instituicao
        total_erros += erros_instituicao
    
    print(f"\n📊 RESUMO DO SALVAMENTO:")
    print(f"   ✅ Total salvos: {total_salvos}")
    print(f"   ❌ Total com erro: {total_erros}")


def exibir_estatisticas_finais(todas_stats: dict, db: Database):
    """
    Exibe estatísticas finais da coleta
    
    Args:
        todas_stats: Estatísticas de coleta
        db: Instância do banco de dados
    """
    print(f"\n{'='*70}")
    print("📊 ESTATÍSTICAS FINAIS DA COLETA")
    print(f"{'='*70}\n")
    
    # Estatísticas gerais
    total_instituicoes = len(todas_stats)
    total_pessoas = sum(s['total_pessoas'] for s in todas_stats.values())
    total_docentes_filtrados = sum(s['docentes_filtrados'] for s in todas_stats.values())
    total_detalhes = sum(s['detalhes_coletados'] for s in todas_stats.values())
    total_erros = sum(s['erros'] for s in todas_stats.values())
    
    print(f"🎯 Instituições processadas: {total_instituicoes}")
    print(f"👥 Total de pessoas na API: {total_pessoas:,}")
    print(f"👨‍🏫 Docentes identificados: {total_docentes_filtrados:,}")
    print(f"✅ Detalhes coletados: {total_detalhes:,}")
    print(f"❌ Erros durante coleta: {total_erros}")
    
    # Taxa de sucesso
    if total_docentes_filtrados > 0:
        taxa_sucesso = (total_detalhes / total_docentes_filtrados) * 100
        print(f"📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
    
    # Estatísticas do banco
    print(f"\n💾 ESTATÍSTICAS DO BANCO DE DADOS:")
    total_banco = db.count_all_docentes()
    print(f"   Total no banco: {total_banco:,} docentes")
    
    # Por instituição
    print(f"\n📋 DETALHES POR INSTITUIÇÃO:")
    print(f"{'Sigla':<15} {'Pessoas':<10} {'Docentes':<10} {'Coletados':<10} {'No Banco':<10}")
    print("-" * 70)
    
    for sigla in sorted(todas_stats.keys()):
        stats = todas_stats[sigla]
        no_banco = db.count_docentes_by_sigla(sigla)
        
        print(f"{sigla:<15} {stats['total_pessoas']:<10,} {stats['docentes_filtrados']:<10,} "
              f"{stats['detalhes_coletados']:<10,} {no_banco:<10,}")
    
    print("-" * 70)
    print(f"{'TOTAL':<15} {total_pessoas:<10,} {total_docentes_filtrados:<10,} "
          f"{total_detalhes:<10,} {total_banco:<10,}")
    
    # Identifica possíveis problemas
    print(f"\n⚠️  ANÁLISE DE POSSÍVEIS PROBLEMAS:")
    problemas_encontrados = False
    
    for sigla, stats in todas_stats.items():
        # Instituição com muitos erros
        if stats['erros'] > 10:
            print(f"   ⚠️  {sigla}: {stats['erros']} erros durante coleta")
            problemas_encontrados = True
        
        # Instituição com muito poucos docentes (possível filtro ruim)
        if stats['total_pessoas'] > 100 and stats['docentes_filtrados'] < 50:
            print(f"   ⚠️  {sigla}: Apenas {stats['docentes_filtrados']} docentes de {stats['total_pessoas']} pessoas - verificar filtro")
            problemas_encontrados = True
        
        # Taxa de coleta de detalhes muito baixa
        if stats['docentes_filtrados'] > 0:
            taxa = (stats['detalhes_coletados'] / stats['docentes_filtrados']) * 100
            if taxa < 90:
                print(f"   ⚠️  {sigla}: Taxa de coleta {taxa:.1f}% - alguns detalhes não foram coletados")
                problemas_encontrados = True
    
    if not problemas_encontrados:
        print("   ✅ Nenhum problema significativo detectado!")
    
    # Cargos mais comuns
    print(f"\n👔 CARGOS DE DOCENTES MAIS FREQUENTES:")
    todos_cargos = {}
    for stats in todas_stats.values():
        for cargo in stats.get('cargos_encontrados', []):
            todos_cargos[cargo] = todos_cargos.get(cargo, 0) + 1
    
    cargos_ordenados = sorted(todos_cargos.items(), key=lambda x: x[1], reverse=True)
    for i, (cargo, freq) in enumerate(cargos_ordenados[:15], 1):
        print(f"   {i:2d}. {cargo} (encontrado em {freq} instituições)")


async def main():
    """Função principal do sistema"""
    print_banner()
    
    # Timestamp de início
    inicio = time.time()
    timestamp_inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"🕐 Início: {timestamp_inicio}\n")
    
    # Parse argumentos
    siglas_selecionadas = parse_arguments()
    
    if siglas_selecionadas:
        print(f"🎯 Modo: Coleta SELETIVA")
        print(f"📋 Instituições: {', '.join(siglas_selecionadas)}")
    else:
        print(f"🎯 Modo: Coleta COMPLETA")
        print(f"📋 Instituições: Todas as {len(INSTITUICOES)} da Rede Federal")
    
    print(f"\n⏳ Iniciando coleta...\n")
    
    # Inicializa banco de dados
    print("💾 Inicializando banco de dados...")
    init_database()
    
    # Executa scraping
    try:
        todos_resultados, todas_stats = await scrape_multiplas_instituicoes(siglas_selecionadas)
        
        # Salva no banco
        db = Database()
        db.connect()
        
        salvar_resultados_no_banco(db, todos_resultados, todas_stats)
        
        # Exibe estatísticas finais
        exibir_estatisticas_finais(todas_stats, db)
        
        db.close()
        
        # Tempo total
        fim = time.time()
        tempo_total = fim - inicio
        timestamp_fim = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{'='*70}")
        print(f"✅ COLETA CONCLUÍDA COM SUCESSO!")
        print(f"{'='*70}")
        print(f"🕐 Início: {timestamp_inicio}")
        print(f"🕐 Fim: {timestamp_fim}")
        print(f"⏱️  Tempo total: {tempo_total/60:.1f} minutos ({tempo_total:.0f} segundos)")
        print(f"{'='*70}\n")
        
        print("💡 Próximos passos:")
        print("   1. Execute 'python normalizer.py' para extrair dados estruturados")
        print("   2. Execute 'python visualizar_banco.py' para ver estatísticas detalhadas")
        print("   3. Execute 'python comparar_totais.py' para validar a coleta")
        print("")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Coleta interrompida pelo usuário!")
        print("💾 Dados já coletados foram salvos no banco.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Executa o sistema
    asyncio.run(main())
