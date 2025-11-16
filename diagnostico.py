#python test_sistema.py#!/usr/bin/env python3
"""
Script de diagnóstico para testar conexão com as APIs do Portal Integra
Mostra quantas pessoas existem, quantos docentes são filtrados e exemplos de cargos
"""

import asyncio
import aiohttp
import ssl
from typing import Dict, List
from config import INSTITUICOES, HEADERS, TERMOS_DOCENTE, PAGE_SIZE


async def diagnosticar_instituicao(sigla: str, base_url: str) -> Dict:
    """
    Diagnostica uma instituição específica
    
    Args:
        sigla: Sigla da instituição
        base_url: URL base do Portal Integra
    
    Returns:
        Dicionário com resultados do diagnóstico
    """
    # SSL context que aceita certificados inválidos
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Criar connector com SSL desabilitado
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    timeout = aiohttp.ClientTimeout(total=30)
    
    resultado = {
        'sigla': sigla,
        'sucesso': False,
        'total_pessoas': 0,
        'docentes_filtrados': 0,
        'cargos_docentes': set(),
        'cargos_ignorados': set(),
        'erro': None,
    }
    
    try:
        async with aiohttp.ClientSession(headers=HEADERS, connector=connector, timeout=timeout) as session:
            # Testa a API buscando primeira página
            url = f"{base_url}/api/portfolio/pessoa/data?start=0&length={PAGE_SIZE}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data and isinstance(data, list) and len(data) >= 2:
                        # Extrai metadata e pessoas
                        metadata = data[0]
                        pessoas = data[1]
                        
                        resultado['sucesso'] = True
                        resultado['total_pessoas'] = metadata.get('total', 0)
                        
                        # Analisa cargos
                        for pessoa in pessoas:
                            cargo = pessoa.get('cargo', '')
                            if cargo:
                                # Verifica se é docente
                                cargo_lower = cargo.lower()
                                is_docente = any(termo in cargo_lower for termo in TERMOS_DOCENTE)
                                
                                if is_docente:
                                    resultado['cargos_docentes'].add(cargo)
                                    resultado['docentes_filtrados'] += 1
                                else:
                                    resultado['cargos_ignorados'].add(cargo)
                    else:
                        resultado['erro'] = "Formato de resposta inesperado"
                else:
                    resultado['erro'] = f"Status HTTP {response.status}"
                    
    except asyncio.TimeoutError:
        resultado['erro'] = "Timeout"
    except aiohttp.ClientError as e:
        resultado['erro'] = f"Erro de conexão: {e}"
    except Exception as e:
        resultado['erro'] = f"Erro: {e}"
    
    return resultado


async def diagnosticar_todas():
    """Diagnostica todas as instituições"""
    print("\n" + "="*80)
    print("🔍 DIAGNÓSTICO COMPLETO DAS APIs DO PORTAL INTEGRA")
    print("="*80 + "\n")
    
    print(f"📋 Total de instituições: {len(INSTITUICOES)}\n")
    
    # Criar tarefas para todas as instituições
    tasks = []
    for sigla, info in INSTITUICOES.items():
        tasks.append(diagnosticar_instituicao(sigla, info['url']))
    
    print("⏳ Testando conexões (pode levar alguns minutos)...\n")
    
    # Executar em paralelo
    resultados = await asyncio.gather(*tasks)
    
    # Análise dos resultados
    sucesso_count = sum(1 for r in resultados if r['sucesso'])
    falha_count = len(resultados) - sucesso_count
    
    # Agrupa por status
    instituicoes_ok = []
    instituicoes_com_problemas = []
    instituicoes_sem_docentes = []
    instituicoes_falha = []
    
    for resultado in resultados:
        if not resultado['sucesso']:
            instituicoes_falha.append(resultado)
        elif resultado['docentes_filtrados'] == 0:
            instituicoes_sem_docentes.append(resultado)
        elif resultado['total_pessoas'] > 100 and resultado['docentes_filtrados'] < 50:
            instituicoes_com_problemas.append(resultado)
        else:
            instituicoes_ok.append(resultado)
    
    # Exibe resultados
    print("="*80)
    print("📊 RESUMO GERAL")
    print("="*80 + "\n")
    
    print(f"✅ Conexões bem-sucedidas: {sucesso_count}/{len(resultados)}")
    print(f"❌ Conexões com falha: {falha_count}/{len(resultados)}")
    print(f"⚠️  Instituições com possíveis problemas: {len(instituicoes_com_problemas)}")
    print(f"⚠️  Instituições sem docentes filtrados: {len(instituicoes_sem_docentes)}\n")
    
    # Total de pessoas e docentes
    total_pessoas = sum(r['total_pessoas'] for r in resultados)
    total_docentes = sum(r['docentes_filtrados'] for r in resultados)
    
    print(f"👥 Total de pessoas nas APIs: {total_pessoas:,}")
    print(f"👨‍🏫 Total de docentes filtrados: {total_docentes:,}")
    
    if total_pessoas > 0:
        percentual = (total_docentes / total_pessoas) * 100
        print(f"📊 Percentual de docentes: {percentual:.1f}%\n")
    
    # Detalhes por instituição
    print("="*80)
    print("📋 DETALHES POR INSTITUIÇÃO")
    print("="*80 + "\n")
    
    print(f"{'Sigla':<18} {'Status':<15} {'Pessoas':<10} {'Docentes':<10} {'% Doc':<10}")
    print("-" * 80)
    
    for resultado in sorted(resultados, key=lambda x: x['sigla']):
        sigla = resultado['sigla']
        
        if resultado['sucesso']:
            status = "✅ OK"
            pessoas = resultado['total_pessoas']
            docentes = resultado['docentes_filtrados']
            
            if pessoas > 0:
                perc_doc = (docentes / pessoas) * 100
                perc_str = f"{perc_doc:.1f}%"
            else:
                perc_str = "N/A"
            
            # Marca instituições com problemas
            if docentes == 0:
                status = "⚠️  SEM DOCENTES"
            elif pessoas > 100 and docentes < 50:
                status = "⚠️  POUCOS DOCS"
            
            print(f"{sigla:<18} {status:<15} {pessoas:<10,} {docentes:<10,} {perc_str:<10}")
        else:
            erro = resultado['erro'][:30] if resultado['erro'] else "Erro desconhecido"
            print(f"{sigla:<18} {'❌ FALHA':<15} {'-':<10} {'-':<10} {erro:<10}")
    
    print("-" * 80)
    
    # Instituições com falha
    if instituicoes_falha:
        print("\n" + "="*80)
        print("❌ INSTITUIÇÕES COM FALHA DE CONEXÃO")
        print("="*80 + "\n")
        
        for resultado in instituicoes_falha:
            print(f"   {resultado['sigla']}: {resultado['erro']}")
    
    # Instituições sem docentes
    if instituicoes_sem_docentes:
        print("\n" + "="*80)
        print("⚠️  INSTITUIÇÕES SEM DOCENTES FILTRADOS")
        print("="*80 + "\n")
        
        for resultado in instituicoes_sem_docentes:
            print(f"   {resultado['sigla']}: {resultado['total_pessoas']} pessoas no total")
            
            if resultado['cargos_ignorados']:
                print(f"      Cargos ignorados:")
                for cargo in sorted(resultado['cargos_ignorados'])[:10]:
                    print(f"         - {cargo}")
    
    # Instituições com problemas no filtro
    if instituicoes_com_problemas:
        print("\n" + "="*80)
        print("⚠️  INSTITUIÇÕES COM POSSÍVEL PROBLEMA NO FILTRO")
        print("="*80 + "\n")
        
        for resultado in instituicoes_com_problemas:
            pessoas = resultado['total_pessoas']
            docentes = resultado['docentes_filtrados']
            perc = (docentes / pessoas) * 100 if pessoas > 0 else 0
            
            print(f"   {resultado['sigla']}: {docentes} docentes de {pessoas} pessoas ({perc:.1f}%)")
            
            print(f"      Cargos de docentes encontrados:")
            for cargo in sorted(resultado['cargos_docentes'])[:5]:
                print(f"         ✅ {cargo}")
            
            print(f"      Cargos ignorados (amostra):")
            for cargo in sorted(resultado['cargos_ignorados'])[:10]:
                print(f"         ❌ {cargo}")
    
    # Cargos de docentes mais comuns
    print("\n" + "="*80)
    print("👔 CARGOS DE DOCENTES MAIS COMUNS")
    print("="*80 + "\n")
    
    todos_cargos_docentes = {}
    for resultado in resultados:
        if resultado['sucesso']:
            for cargo in resultado['cargos_docentes']:
                todos_cargos_docentes[cargo] = todos_cargos_docentes.get(cargo, 0) + 1
    
    cargos_ordenados = sorted(todos_cargos_docentes.items(), key=lambda x: x[1], reverse=True)
    
    for i, (cargo, freq) in enumerate(cargos_ordenados[:20], 1):
        print(f"   {i:2d}. {cargo} (em {freq} instituições)")
    
    # Cargos ignorados mais comuns
    print("\n" + "="*80)
    print("❌ CARGOS IGNORADOS MAIS COMUNS")
    print("="*80 + "\n")
    
    todos_cargos_ignorados = {}
    for resultado in resultados:
        if resultado['sucesso']:
            for cargo in resultado['cargos_ignorados']:
                todos_cargos_ignorados[cargo] = todos_cargos_ignorados.get(cargo, 0) + 1
    
    cargos_ignorados_ordenados = sorted(todos_cargos_ignorados.items(), key=lambda x: x[1], reverse=True)
    
    for i, (cargo, freq) in enumerate(cargos_ignorados_ordenados[:20], 1):
        print(f"   {i:2d}. {cargo} (em {freq} instituições)")
    
    # Recomendações
    print("\n" + "="*80)
    print("💡 RECOMENDAÇÕES")
    print("="*80 + "\n")
    
    if falha_count > 0:
        print("⚠️  Algumas instituições falharam:")
        print("   - Verifique conexão com internet")
        print("   - Alguns servidores podem estar temporariamente indisponíveis")
        print("   - O sistema tem retry automático que deve resolver a maioria dos problemas\n")
    
    if len(instituicoes_sem_docentes) > 0:
        print("⚠️  Algumas instituições não tiveram docentes filtrados:")
        print("   - Verifique se os termos de filtro em config.py estão adequados")
        print("   - Analise os 'Cargos ignorados' para identificar padrões\n")
    
    if len(instituicoes_com_problemas) > 0:
        print("⚠️  Algumas instituições têm poucos docentes filtrados:")
        print("   - Pode ser necessário adicionar mais termos ao filtro")
        print("   - Verifique os cargos ignorados dessas instituições\n")
    
    if falha_count == 0 and len(instituicoes_sem_docentes) == 0 and len(instituicoes_com_problemas) == 0:
        print("✅ Tudo certo! Todas as instituições estão respondendo adequadamente.")
        print("   Você pode prosseguir com a coleta executando: python main.py\n")
    
    print("="*80 + "\n")


def main():
    """Função principal"""
    asyncio.run(diagnosticar_todas())


if __name__ == "__main__":
    main()
