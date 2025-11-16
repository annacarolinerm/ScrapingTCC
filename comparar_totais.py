#!/usr/bin/env python3
"""
Script para comparar o total de docentes na API com o total no banco
Ajuda a identificar se a coleta está completa
"""

import asyncio
from config import INSTITUICOES
from database import Database
from diagnostico import diagnosticar_instituicao


async def main():
    """Função principal"""
    print("\n" + "="*80)
    print("🔄 COMPARANDO TOTAIS: API vs BANCO DE DADOS")
    print("="*80 + "\n")
    
    # Conecta ao banco
    db = Database()
    db.connect()
    
    # Busca instituições no banco
    siglas_no_banco = set(db.get_all_siglas())
    
    if len(siglas_no_banco) == 0:
        print("❌ Banco de dados vazio! Execute primeiro: python main.py\n")
        db.close()
        return
    
    print(f"📋 Instituições no banco: {len(siglas_no_banco)}")
    print("⏳ Consultando APIs para comparação...\n")
    
    # Diagnostica todas as instituições que estão no banco
    tasks = []
    for sigla in siglas_no_banco:
        if sigla in INSTITUICOES:
            info = INSTITUICOES[sigla]
            tasks.append(diagnosticar_instituicao(sigla, info['url']))
    
    resultados_api = await asyncio.gather(*tasks)
    
    # Prepara comparação
    print("="*80)
    print("📊 COMPARAÇÃO DETALHADA")
    print("="*80 + "\n")
    
    print(f"{'Sigla':<18} {'API':<12} {'Banco':<12} {'Diferença':<15} {'Status':<15}")
    print("-" * 80)
    
    total_api = 0
    total_banco = 0
    problemas = []
    
    for resultado in sorted(resultados_api, key=lambda x: x['sigla']):
        sigla = resultado['sigla']
        
        if resultado['sucesso']:
            docentes_api = resultado['docentes_filtrados']
            docentes_banco = db.count_docentes_by_sigla(sigla)
            
            diferenca = docentes_banco - docentes_api
            
            total_api += docentes_api
            total_banco += docentes_banco
            
            # Determina status
            if abs(diferenca) == 0:
                status = "✅ Perfeito"
            elif diferenca > 0:
                status = f"⚠️  +{diferenca}"
            else:
                status = f"⚠️  {diferenca}"
                problemas.append((sigla, docentes_api, docentes_banco, diferenca))
            
            print(f"{sigla:<18} {docentes_api:<12,} {docentes_banco:<12,} {diferenca:<15,} {status:<15}")
        else:
            docentes_banco = db.count_docentes_by_sigla(sigla)
            print(f"{sigla:<18} {'ERRO':<12} {docentes_banco:<12,} {'-':<15} {'❌ API falhou':<15}")
    
    print("-" * 80)
    print(f"{'TOTAL':<18} {total_api:<12,} {total_banco:<12,} {total_banco - total_api:<15,} {'':<15}\n")
    
    # Análise
    print("="*80)
    print("📈 ANÁLISE")
    print("="*80 + "\n")
    
    if total_banco == total_api:
        print("✅ Perfeito! O banco contém exatamente o mesmo número de docentes da API.\n")
    elif total_banco > total_api:
        diff = total_banco - total_api
        print(f"ℹ️  O banco tem {diff:,} docentes A MAIS que a API.")
        print("   Isso é NORMAL se:")
        print("   - Você rodou a coleta múltiplas vezes")
        print("   - Alguns docentes foram atualizados\n")
    else:
        diff = total_api - total_banco
        print(f"⚠️  O banco tem {diff:,} docentes A MENOS que a API!")
        print("   Possíveis causas:")
        print("   - A coleta foi interrompida antes de terminar")
        print("   - Algumas requisições falharam durante a coleta")
        print("   - Erros ao salvar no banco\n")
        
        if problemas:
            print("   Instituições com mais diferença:")
            problemas.sort(key=lambda x: x[3])  # Ordena por diferença
            
            for sigla, api, banco, diff in problemas[:10]:
                print(f"      {sigla}: API={api:,}, Banco={banco:,} (faltam {abs(diff):,})")
            print()
    
    # Percentual de completude
    if total_api > 0:
        completude = (total_banco / total_api) * 100
        print(f"📊 Completude: {completude:.1f}%")
        
        if completude >= 99:
            print("   ✅ Excelente! A coleta está praticamente completa.\n")
        elif completude >= 95:
            print("   ✅ Muito bom! A coleta está quase completa.\n")
        elif completude >= 90:
            print("   ⚠️  Bom, mas pode melhorar. Considere rodar novamente as instituições com diferença.\n")
        else:
            print("   ⚠️  A coleta está incompleta. Recomendado rodar novamente.\n")
    
    # Recomendações
    if problemas:
        print("="*80)
        print("💡 RECOMENDAÇÕES")
        print("="*80 + "\n")
        
        siglas_problema = [p[0] for p in problemas if abs(p[3]) > 10]
        
        if siglas_problema:
            print("Para completar a coleta, execute:")
            print(f"   python main.py {' '.join(siglas_problema)}\n")
    
    db.close()


if __name__ == "__main__":
    asyncio.run(main())
