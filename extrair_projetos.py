import sqlite3
import json

def extrair_projetos_de_json(dados_json, id_docente):
    """
    Extrai projetos do JSON aninhado.
    """
    projetos = []
    
    # Navegar até os projetos (estrutura profunda!)
    atuacoes_prof = dados_json.get('dadosGerais', {}).get('atuacoesProfissionais', {})
    
    if not atuacoes_prof:
        return projetos
    
    atuacoes_lista = atuacoes_prof.get('atuacaoProfissional', [])
    if not isinstance(atuacoes_lista, list):
        atuacoes_lista = [atuacoes_lista] if atuacoes_lista else []
    
    for atuacao in atuacoes_lista:
        # Pegar atividades de participação em projeto
        atividades_proj = atuacao.get('atividadesDeParticipacaoEmProjeto', [])
        if not isinstance(atividades_proj, list):
            atividades_proj = [atividades_proj] if atividades_proj else []
        
        for atividade in atividades_proj:
            participacoes = atividade.get('participacaoEmProjeto', [])
            if not isinstance(participacoes, list):
                participacoes = [participacoes] if participacoes else []
            
            for participacao in participacoes:
                # Aqui estão os projetos!
                projetos_pesq = participacao.get('projetoDePesquisa', [])
                if not isinstance(projetos_pesq, list):
                    projetos_pesq = [projetos_pesq] if projetos_pesq else []
                
                for proj in projetos_pesq:
                    # Verificar se é coordenador
                    equipe = proj.get('equipeDoProjeto', {})
                    integrantes = equipe.get('integrantesDoProjeto', [])
                    if not isinstance(integrantes, list):
                        integrantes = [integrantes] if integrantes else []
                    
                    flag_coordenador = 'NAO'
                    for integrante in integrantes:
                        if integrante.get('flagResponsavel') == 'SIM':
                            flag_coordenador = 'SIM'
                            break
                    
                    # Montar registro
                    projeto = {
                        'id_docente': id_docente,
                        'nome': proj.get('nomeDoProjeto', ''),
                        'natureza': proj.get('natureza', ''),
                        'situacao': proj.get('situacao', ''),
                        'ano_inicio': proj.get('anoInicio', ''),
                        'ano_fim': proj.get('anoFim', ''),
                        'descricao': proj.get('descricaoDoProjeto', ''),
                        'instituicao': participacao.get('nomeOrgao', ''),
                        'orgao': participacao.get('codigoOrgao', ''),
                        'flag_coordenador': flag_coordenador,
                        'num_integrantes': len(integrantes),
                        'num_alunos_graduacao': int(proj.get('numeroGraduacao', 0) or 0),
                        'num_alunos_mestrado': int(proj.get('numeroMestradoAcademico', 0) or 0),
                        'num_alunos_doutorado': int(proj.get('numeroDoutorado', 0) or 0)
                    }
                    
                    projetos.append(projeto)
    
    return projetos


def processar_todos_docentes():
    """
    Processa todos os docentes e extrai projetos.
    """
    conn = sqlite3.connect('integra.db')
    cursor = conn.cursor()
    
    # 1. Criar tabela projetos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_docente INTEGER NOT NULL,
            nome TEXT NOT NULL,
            natureza TEXT,
            situacao TEXT,
            ano_inicio INTEGER,
            ano_fim INTEGER,
            descricao TEXT,
            instituicao TEXT,
            orgao TEXT,
            flag_coordenador TEXT,
            num_integrantes INTEGER,
            num_alunos_graduacao INTEGER,
            num_alunos_mestrado INTEGER,
            num_alunos_doutorado INTEGER,
            FOREIGN KEY (id_docente) REFERENCES docentes(id)
        )
    ''')
    
    # 2. Criar índices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_projetos_docente ON projetos(id_docente)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_projetos_natureza ON projetos(natureza)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_projetos_situacao ON projetos(situacao)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_projetos_ano ON projetos(ano_inicio)')
    
    # 3. Buscar todos os docentes
    cursor.execute("SELECT id, data_completa FROM docentes")
    
    total_projetos = 0
    total_docentes_com_projetos = 0
    
    for row in cursor.fetchall():
        id_docente = row[0]
        data_completa = row[1]
        
        if not data_completa:
            continue
        
        try:
            dados_json = json.loads(data_completa)
            projetos = extrair_projetos_de_json(dados_json, id_docente)
            
            if projetos:
                total_docentes_com_projetos += 1
                
                for projeto in projetos:
                    cursor.execute('''
                        INSERT INTO projetos (
                            id_docente, nome, natureza, situacao, 
                            ano_inicio, ano_fim, descricao,
                            instituicao, orgao, flag_coordenador,
                            num_integrantes, num_alunos_graduacao,
                            num_alunos_mestrado, num_alunos_doutorado
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        projeto['id_docente'],
                        projeto['nome'],
                        projeto['natureza'],
                        projeto['situacao'],
                        projeto['ano_inicio'],
                        projeto['ano_fim'],
                        projeto['descricao'],
                        projeto['instituicao'],
                        projeto['orgao'],
                        projeto['flag_coordenador'],
                        projeto['num_integrantes'],
                        projeto['num_alunos_graduacao'],
                        projeto['num_alunos_mestrado'],
                        projeto['num_alunos_doutorado']
                    ))
                    total_projetos += 1
        
        except Exception as e:
            print(f"Erro ao processar docente {id_docente}: {e}")
            continue
    
    conn.commit()
    
    print(f"\n✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"📊 Total de docentes com projetos: {total_docentes_com_projetos}")
    print(f"📊 Total de projetos extraídos: {total_projetos}")
    
    # 4. Estatísticas
    cursor.execute("SELECT COUNT(*) FROM projetos")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT id_docente) FROM projetos")
    docentes_unicos = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT natureza, COUNT(*) 
        FROM projetos 
        GROUP BY natureza
    """)
    por_natureza = cursor.fetchall()
    
    print(f"\n📈 ESTATÍSTICAS:")
    print(f"Total de registros: {total}")
    print(f"Docentes únicos: {docentes_unicos}")
    print(f"Média de projetos/docente: {total/docentes_unicos:.2f}")
    print(f"\nPor natureza:")
    for natureza, count in por_natureza:
        print(f"  {natureza}: {count}")
    
    conn.close()


if __name__ == "__main__":
    processar_todos_docentes()