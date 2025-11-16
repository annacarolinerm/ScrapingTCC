#!/usr/bin/env python3
"""
Script para verificar quais instituições ainda não foram coletadas
"""

from config import INSTITUICOES
from database import Database


def main():
    """Função principal"""
    print("\n" + "="*70)
    print("🔍 VERIFICANDO INSTITUIÇÕES FALTANTES NO BANCO")
    print("="*70 + "\n")
    
    db = Database()
    db.connect()
    
    # Busca instituições no banco
    siglas_no_banco = set(db.get_all_siglas())
    
    # Todas as instituições possíveis
    todas_siglas = set(INSTITUICOES.keys())
    
    # Instituições faltantes
    faltantes = todas_siglas - siglas_no_banco
    
    # Instituições presentes
    presentes = todas_siglas & siglas_no_banco
    
    print(f"📊 RESUMO:")
    print(f"   Total de instituições: {len(todas_siglas)}")
    print(f"   No banco: {len(presentes)}")
    print(f"   Faltantes: {len(faltantes)}\n")
    
    if len(faltantes) == 0:
        print("✅ Todas as 40 instituições estão no banco!\n")
    else:
        print(f"⚠️  {len(faltantes)} instituições faltando:\n")
        
        for sigla in sorted(faltantes):
            info = INSTITUICOES[sigla]
            print(f"   ❌ {sigla:<18} (UF: {info['uf']}, URL: {info['url']})")
        
        print(f"\n💡 Para coletar as instituições faltantes, execute:")
        print(f"   python main.py {' '.join(sorted(faltantes))}\n")
    
    # Mostra quantos docentes por instituição presente
    if len(presentes) > 0:
        print("="*70)
        print("📋 DOCENTES POR INSTITUIÇÃO NO BANCO")
        print("="*70 + "\n")
        
        print(f"{'Sigla':<18} {'UF':<5} {'Docentes':<10}")
        print("-" * 70)
        
        total_docentes = 0
        for sigla in sorted(presentes):
            count = db.count_docentes_by_sigla(sigla)
            uf = INSTITUICOES[sigla]['uf']
            print(f"{sigla:<18} {uf:<5} {count:<10,}")
            total_docentes += count
        
        print("-" * 70)
        print(f"{'TOTAL':<18} {'':<5} {total_docentes:<10,}\n")
    
    db.close()


if __name__ == "__main__":
    main()
