#!/usr/bin/env python3
"""
Script para visualizar estatísticas detalhadas do banco de dados
"""

from database import Database
from config import INSTITUICOES


def main():
    """Função principal"""
    print("\n" + "="*80)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS - PORTAL INTEGRA")
    print("="*80 + "\n")
    
    db = Database()
    db.connect()
    
    # Estatísticas gerais
    stats = db.get_statistics()
    
    total_docentes = stats['total_docentes']
    
    if total_docentes == 0:
        print("⚠️  Banco de dados vazio!")
        print("💡 Execute: python main.py\n")
        db.close()
        return
    
    print(f"👥 DADOS GERAIS:")
    print(f"   Total de docentes: {total_docentes:,}\n")
    
    # Por instituição
    print("="*80)
    print("📋 DOCENTES POR INSTITUIÇÃO")
    print("="*80 + "\n")
    
    print(f"{'Sigla':<18} {'UF':<5} {'Docentes':<12} {'% do Total':<12}")
    print("-" * 80)
    
    por_instituicao = stats['por_instituicao']
    
    for sigla in sorted(por_instituicao.keys()):
        count = por_instituicao[sigla]
        uf = INSTITUICOES.get(sigla, {}).get('uf', '??')
        percentual = (count / total_docentes) * 100
        
        print(f"{sigla:<18} {uf:<5} {count:<12,} {percentual:>6.2f}%")
    
    print("-" * 80)
    print(f"{'TOTAL':<18} {'':<5} {total_docentes:<12,} {'100.00%':>12}\n")
    
    # Por UF
    print("="*80)
    print("🗺️  DOCENTES POR ESTADO")
    print("="*80 + "\n")
    
    print(f"{'UF':<5} {'Docentes':<12} {'% do Total':<12}")
    print("-" * 80)
    
    # Agrupa por UF manualmente para ter controle total
    por_uf = {}
    for sigla, count in por_instituicao.items():
        uf = INSTITUICOES.get(sigla, {}).get('uf', '??')
        por_uf[uf] = por_uf.get(uf, 0) + count
    
    # Ordena por quantidade
    for uf in sorted(por_uf.keys(), key=lambda x: por_uf[x], reverse=True):
        count = por_uf[uf]
        percentual = (count / total_docentes) * 100
        print(f"{uf:<5} {count:<12,} {percentual:>6.2f}%")
    
    print("-" * 80)
    print(f"{'TOTAL':<5} {total_docentes:<12,} {'100.00%':>12}\n")
    
    # Tabelas normalizadas
    print("="*80)
    print("📊 DADOS NORMALIZADOS")
    print("="*80 + "\n")
    
    tabelas_normalizadas = stats['tabelas_normalizadas']
    
    total_registros_normalizados = sum(tabelas_normalizadas.values())
    
    print(f"{'Tabela':<30} {'Registros':<15} {'Média/Docente':<15}")
    print("-" * 80)
    
    for tabela, count in sorted(tabelas_normalizadas.items()):
        media = count / total_docentes if total_docentes > 0 else 0
        print(f"{tabela:<30} {count:<15,} {media:>10.2f}")
    
    print("-" * 80)
    print(f"{'TOTAL':<30} {total_registros_normalizados:<15,} {'':<15}\n")
    
    # Análise de cobertura dos dados normalizados
    print("="*80)
    print("📈 COBERTURA DOS DADOS NORMALIZADOS")
    print("="*80 + "\n")
    
    # Verifica quantos docentes têm cada tipo de dado
    tabelas_info = {
        'dados_gerais': 'Dados Gerais',
        'formacoes': 'Formações Acadêmicas',
        'atuacoes': 'Atuações Profissionais',
        'producao_bibliografica': 'Produção Bibliográfica',
        'orientacoes_concluidas': 'Orientações Concluídas',
        'premios_titulos': 'Prêmios e Títulos',
        'areas_atuacao': 'Áreas de Atuação',
    }
    
    print(f"{'Tipo de Dado':<35} {'Docentes':<12} {'Cobertura':<12}")
    print("-" * 80)
    
    for tabela, nome in tabelas_info.items():
        # Conta quantos docentes únicos têm registros nessa tabela
        db.cursor.execute(f"""
            SELECT COUNT(DISTINCT id_docente) 
            FROM {tabela}
        """)
        count = db.cursor.fetchone()[0]
        cobertura = (count / total_docentes) * 100 if total_docentes > 0 else 0
        
        print(f"{nome:<35} {count:<12,} {cobertura:>6.2f}%")
    
    print()
    
    # Estatísticas adicionais interessantes
    print("="*80)
    print("🔍 ESTATÍSTICAS ADICIONAIS")
    print("="*80 + "\n")
    
    # Docentes com ORCID
    db.cursor.execute("""
        SELECT COUNT(*) 
        FROM dados_gerais 
        WHERE orcid IS NOT NULL AND orcid != ''
    """)
    com_orcid = db.cursor.fetchone()[0]
    perc_orcid = (com_orcid / total_docentes) * 100 if total_docentes > 0 else 0
    print(f"👤 Docentes com ORCID: {com_orcid:,} ({perc_orcid:.1f}%)")
    
    # Docentes com email
    db.cursor.execute("""
        SELECT COUNT(*) 
        FROM docentes 
        WHERE email IS NOT NULL AND email != ''
    """)
    com_email = db.cursor.fetchone()[0]
    perc_email = (com_email / total_docentes) * 100 if total_docentes > 0 else 0
    print(f"📧 Docentes com email: {com_email:,} ({perc_email:.1f}%)")
    
    # Total de produções bibliográficas
    db.cursor.execute("SELECT COUNT(*) FROM producao_bibliografica")
    total_producoes = db.cursor.fetchone()[0]
    media_producoes = total_producoes / total_docentes if total_docentes > 0 else 0
    print(f"📚 Total de produções: {total_producoes:,} (média: {media_producoes:.1f}/docente)")
    
    # Produções por tipo
    db.cursor.execute("""
        SELECT tipo, COUNT(*) as count 
        FROM producao_bibliografica 
        GROUP BY tipo 
        ORDER BY count DESC
    """)
    producoes_por_tipo = db.cursor.fetchall()
    
    if producoes_por_tipo:
        print(f"\n   Produções por tipo:")
        for tipo, count in producoes_por_tipo:
            perc = (count / total_producoes) * 100 if total_producoes > 0 else 0
            print(f"      {tipo}: {count:,} ({perc:.1f}%)")
    
    # Total de orientações
    db.cursor.execute("SELECT COUNT(*) FROM orientacoes_concluidas")
    total_orientacoes = db.cursor.fetchone()[0]
    media_orientacoes = total_orientacoes / total_docentes if total_docentes > 0 else 0
    print(f"\n🎓 Total de orientações: {total_orientacoes:,} (média: {media_orientacoes:.1f}/docente)")
    
    # Formações mais comuns
    db.cursor.execute("""
        SELECT nivel, COUNT(*) as count 
        FROM formacoes 
        WHERE nivel IS NOT NULL AND nivel != ''
        GROUP BY nivel 
        ORDER BY count DESC 
        LIMIT 10
    """)
    formacoes_comuns = db.cursor.fetchall()
    
    if formacoes_comuns:
        print(f"\n🎓 Níveis de formação mais comuns:")
        for nivel, count in formacoes_comuns:
            print(f"      {nivel}: {count:,}")
    
    # Áreas de conhecimento mais comuns
    db.cursor.execute("""
        SELECT grande_area, COUNT(*) as count 
        FROM areas_atuacao 
        WHERE grande_area IS NOT NULL AND grande_area != ''
        GROUP BY grande_area 
        ORDER BY count DESC 
        LIMIT 10
    """)
    areas_comuns = db.cursor.fetchall()
    
    if areas_comuns:
        print(f"\n🔬 Grandes áreas de conhecimento mais comuns:")
        for area, count in areas_comuns:
            print(f"      {area}: {count:,}")
    
    print()
    
    # Qualidade dos dados
    print("="*80)
    print("✅ QUALIDADE DOS DADOS")
    print("="*80 + "\n")
    
    # Verifica docentes sem dados normalizados
    db.cursor.execute("""
        SELECT COUNT(*) 
        FROM docentes d
        WHERE NOT EXISTS (
            SELECT 1 FROM dados_gerais WHERE id_docente = d.id
        )
    """)
    sem_normalizacao = db.cursor.fetchone()[0]
    
    if sem_normalizacao > 0:
        perc = (sem_normalizacao / total_docentes) * 100
        print(f"⚠️  {sem_normalizacao:,} docentes sem dados normalizados ({perc:.1f}%)")
        print("   💡 Execute: python normalizer.py\n")
    else:
        print("✅ Todos os docentes têm dados normalizados!\n")
    
    # Tamanho do banco
    db.cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    tamanho_bytes = db.cursor.fetchone()[0]
    tamanho_mb = tamanho_bytes / (1024 * 1024)
    tamanho_gb = tamanho_mb / 1024
    
    if tamanho_gb >= 1:
        print(f"💾 Tamanho do banco: {tamanho_gb:.2f} GB")
    else:
        print(f"💾 Tamanho do banco: {tamanho_mb:.2f} MB")
    
    print()
    
    db.close()
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
