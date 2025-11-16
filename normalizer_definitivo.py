#!/usr/bin/env python3
"""
NORMALIZER DEFINITIVO - Versão Final
Trata TODAS as variações e NUNCA quebra
"""

import json
from database import Database


class NormalizerDefinitivo:
    """Normalizer final - à prova de balas"""
    
    def __init__(self, db: Database):
        self.db = db
        self.stats = {
            'processados': 0,
            'com_dados_gerais': 0,
            'com_formacoes': 0,
            'com_atuacoes': 0,
            'com_producoes': 0,
            'com_orientacoes': 0,
            'com_premios': 0,
            'com_areas': 0,
            'erros_json': 0,
        }
        
        self.siglas_ifs = {
            # 'IFAC', 'IFAL', 'IFAP', 'IFAM', 'IFBA', 'IFBAIANO', 'IFB', 'IFCE', 'IFES',
            # 'IFG', 'IFGOIANO', 'IFMA', 'IFMG', 'IFNMG', 'IFSUDESTEMG', 'IFSULDEMINAS',
            # 'IFTM', 'IFMT', 'IFMS', 'IFPA', 'IFPB', 'IFPE', 'IFSERTAOPE', 'IFPI',
            # 'IFPR', 'IFRJ', 'IFFLUMINENSE', 'IFRN', 'IFRO', 'IFRR', 'IFRS',
            # 'IFFARROUPILHA', 'IFSUL', 'IFSC', 'IFC', 'IFSP', 'IFS', 'IFTO',
            # 'CEFET-RJ', 'CEFET-MG', 'CEFET RJ', 'CEFET MG', 'CEFET'
            'Instituto Federal de Brasília'
        }
    
    def safe_get(self, data, *keys, default=None):
        """Acessa chaves com máxima segurança"""
        if not isinstance(data, dict):
            return default
        
        result = data
        for key in keys:
            if not isinstance(result, dict):
                return default
            result = result.get(key, default)
            if result is None:
                return default
        return result
    
    def to_str(self, value):
        """Converte para string"""
        if value is None or value == '':
            return ''
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value).strip()
    
    def safe_int(self, value):
        """Converte para int com segurança"""
        if value is None:
            return None
        try:
            return int(value)
        except:
            return None
    
    def get_list_safe(self, data, *keys):
        """Retorna lista garantida"""
        result = self.safe_get(data, *keys, default=[])
        if not isinstance(result, list):
            return []
        return result
    
    def is_if(self, instituicao: str) -> bool:
        """Verifica IF/CEFET"""
        if not instituicao:
            return False
        inst_upper = str(instituicao).upper()
        return any(sigla in inst_upper for sigla in self.siglas_ifs) or \
               'Instituto Federal' in inst_upper or 'CENTRO FEDERAL' in inst_upper
    
    def extract_dados_gerais(self, docente_id: int, data: dict):
        """Extrai dados gerais"""
        try:
            dg = self.safe_get(data, 'dadosGerais', default={})
            if not dg:
                return
            
            nome = self.to_str(self.safe_get(dg, 'nomeCompleto'))
            citacao = self.to_str(self.safe_get(dg, 'nomeEmCitacoesBibliograficas'))
            orcid = self.to_str(self.safe_get(dg, 'orcidId'))
            
            resumo_dict = self.safe_get(dg, 'resumoCv', default={})
            if isinstance(resumo_dict, dict):
                resumo = self.to_str(resumo_dict.get('textoResumoCvRh', ''))
            else:
                resumo = self.to_str(resumo_dict)
            
            lattes = self.to_str(self.safe_get(data, 'lattesUrl'))
            
            palavras = ''
            try:
                pk = data.get('palavrasChave')
                if isinstance(pk, str):
                    # STRING direta!
                    palavras = pk.strip()
                elif isinstance(pk, list):
                    palavras = ', '.join([str(p) for p in pk if p])
                elif isinstance(pk, dict):
                    plist = []
                    for i in range(1, 10):
                        p = pk.get(f'palavraChave{i}')
                        if p and str(p).strip():
                            plist.append(str(p).strip())
                    palavras = ', '.join(plist)
            except:
                pass
            
            if nome or citacao:
                try:
                    self.db.cursor.execute("""
                        INSERT INTO dados_gerais 
                        (id_docente, nome_completo, nome_citacao, orcid, resumo_cv, lattes_url, palavras_chave)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (docente_id, nome, citacao, orcid, resumo, lattes, palavras))
                except:
                    try:
                        self.db.cursor.execute("""
                            INSERT INTO dados_gerais 
                            (id_docente, nome_completo, nome_citacao, orcid, resumo_cv)
                            VALUES (?, ?, ?, ?, ?)
                        """, (docente_id, nome, citacao, orcid, resumo))
                    except:
                        pass
                
                self.stats['com_dados_gerais'] += 1
        except:
            pass
    
    def extract_formacoes(self, docente_id: int, data: dict):
        """Extrai formações"""
        try:
            form_dict = self.safe_get(data, 'dadosGerais', 'formacaoAcademicaTitulacao', default={})
            if not isinstance(form_dict, dict):
                return
            
            count = 0
            tipos = {
                'graduacoes': 'Graduação',
                'especializacoes': 'Especialização',
                'mestrados': 'Mestrado',
                'mestradoProfissional': 'Mestrado Profissional',
                'doutorado': 'Doutorado',
                'posDoutorado': 'Pós-Doutorado',
                'livreDocencia': 'Livre-Docência',
            }
            
            for campo, nivel in tipos.items():
                formacoes = self.get_list_safe(form_dict, campo)
                
                for form in formacoes:
                    if not isinstance(form, dict):
                        continue
                    
                    curso = self.to_str(form.get('nomeCurso') or form.get('curso'))
                    inst = self.to_str(form.get('nomeInstituicao') or form.get('instituicao'))
                    ano_i = self.safe_int(form.get('anoDeInicio') or form.get('anoInicio'))
                    ano_f = self.safe_int(form.get('anoDeConclusao') or form.get('anoFim'))
                    tit = self.to_str(form.get('tituloDaMonografia') or form.get('tituloDaDissertacaoTese'))
                    ori = self.to_str(form.get('nomeDoOrientador'))
                    
                    try:
                        self.db.cursor.execute("""
                            INSERT INTO formacoes 
                            (id_docente, nivel, curso, instituicao, ano_inicio, ano_fim, titulo, orientador)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (docente_id, nivel, curso, inst, ano_i, ano_f, tit, ori))
                        count += 1
                    except:
                        pass
            
            if count > 0:
                self.stats['com_formacoes'] += 1
        except:
            pass
    
    def contar_coautores(self, autores) -> tuple:
        """Retorna (num, lista)"""
        try:
            if not isinstance(autores, list):
                return (0, '')
            nomes = []
            for aut in autores:
                if isinstance(aut, dict):
                    nome = aut.get('nomeCompletoDoAutor') or aut.get('nomeParaCitacao', '')
                    if nome:
                        nomes.append(str(nome))
            return (len(nomes), '; '.join(nomes))
        except:
            return (0, '')
    
    def extract_producoes(self, docente_id: int, data: dict):
        """Extrai produções - TODAS as variações"""
        try:
            prod = self.safe_get(data, 'producaoBibliografica', default={})
            if not isinstance(prod, dict):
                return
            
            count = 0
            
            # ARTIGOS
            try:
                artigos_list = self.get_list_safe(prod, 'artigosPublicados')
                
                # Pode ser: [{}] ou [[]] ou []
                for item in artigos_list:
                    if isinstance(item, dict):
                        # Estrutura: [{artigoPublicado: [...]}]
                        arts = self.get_list_safe(item, 'artigoPublicado')
                        for art in arts:
                            if not isinstance(art, dict):
                                continue
                            
                            tit = self.to_str(art.get('tituloDoArtigo'))
                            if not tit:
                                tit = f"[Sem título - ID: {art.get('id', 'N/A')}]"
                            
                            ano = self.safe_int(art.get('anoDoArtigo'))
                            rev = self.to_str(art.get('tituloDoPeriodicoOuRevista'))
                            num, lista = self.contar_coautores(art.get('autores', []))
                            
                            try:
                                self.db.cursor.execute("""
                                    INSERT INTO producao_bibliografica 
                                    (id_docente, tipo, titulo, ano, revista_evento_editora, num_coautores, lista_coautores, detalhes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (docente_id, 'Artigo', tit, ano, rev, num, lista, json.dumps(art, ensure_ascii=False)))
                                count += 1
                            except:
                                try:
                                    self.db.cursor.execute("""
                                        INSERT INTO producao_bibliografica 
                                        (id_docente, tipo, titulo, ano, detalhes)
                                        VALUES (?, ?, ?, ?, ?)
                                    """, (docente_id, 'Artigo', tit, ano, json.dumps(art, ensure_ascii=False)))
                                    count += 1
                                except:
                                    pass
                    
                    elif isinstance(item, list):
                        # Estrutura: [[{...}]] - lista dentro de lista!
                        for art in item:
                            if not isinstance(art, dict):
                                continue
                            
                            tit = self.to_str(art.get('tituloDoArtigo'))
                            if not tit:
                                tit = f"[Sem título - ID: {art.get('id', 'N/A')}]"
                            
                            ano = self.safe_int(art.get('anoDoArtigo'))
                            rev = self.to_str(art.get('tituloDoPeriodicoOuRevista'))
                            num, lista = self.contar_coautores(art.get('autores', []))
                            
                            try:
                                self.db.cursor.execute("""
                                    INSERT INTO producao_bibliografica 
                                    (id_docente, tipo, titulo, ano, revista_evento_editora, num_coautores, lista_coautores, detalhes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (docente_id, 'Artigo', tit, ano, rev, num, lista, json.dumps(art, ensure_ascii=False)))
                                count += 1
                            except:
                                try:
                                    self.db.cursor.execute("""
                                        INSERT INTO producao_bibliografica 
                                        (id_docente, tipo, titulo, ano, detalhes)
                                        VALUES (?, ?, ?, ?, ?)
                                    """, (docente_id, 'Artigo', tit, ano, json.dumps(art, ensure_ascii=False)))
                                    count += 1
                                except:
                                    pass
            except:
                pass
            
            # TRABALHOS EM EVENTOS (mesmo padrão)
            try:
                trab_list = self.get_list_safe(prod, 'trabalhosEmEventos')
                
                for item in trab_list:
                    if isinstance(item, dict):
                        trabs = self.get_list_safe(item, 'trabalhoEmEventos')
                        for trab in trabs:
                            if not isinstance(trab, dict):
                                continue
                            
                            tit = self.to_str(trab.get('tituloDoTrabalho'))
                            if not tit:
                                tit = f"[Sem título - ID: {trab.get('id', 'N/A')}]"
                            
                            ano = self.safe_int(trab.get('anoDoTrabalho'))
                            evt = self.to_str(trab.get('nomeDoEvento'))
                            num, lista = self.contar_coautores(trab.get('autores', []))
                            
                            try:
                                self.db.cursor.execute("""
                                    INSERT INTO producao_bibliografica 
                                    (id_docente, tipo, titulo, ano, revista_evento_editora, num_coautores, lista_coautores, detalhes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (docente_id, 'Trabalho em Evento', tit, ano, evt, num, lista, json.dumps(trab, ensure_ascii=False)))
                                count += 1
                            except:
                                try:
                                    self.db.cursor.execute("""
                                        INSERT INTO producao_bibliografica 
                                        (id_docente, tipo, titulo, ano, detalhes)
                                        VALUES (?, ?, ?, ?, ?)
                                    """, (docente_id, 'Trabalho em Evento', tit, ano, json.dumps(trab, ensure_ascii=False)))
                                    count += 1
                                except:
                                    pass
                    
                    elif isinstance(item, list):
                        for trab in item:
                            if not isinstance(trab, dict):
                                continue
                            
                            tit = self.to_str(trab.get('tituloDoTrabalho'))
                            if not tit:
                                tit = f"[Sem título - ID: {trab.get('id', 'N/A')}]"
                            
                            ano = self.safe_int(trab.get('anoDoTrabalho'))
                            evt = self.to_str(trab.get('nomeDoEvento'))
                            num, lista = self.contar_coautores(trab.get('autores', []))
                            
                            try:
                                self.db.cursor.execute("""
                                    INSERT INTO producao_bibliografica 
                                    (id_docente, tipo, titulo, ano, revista_evento_editora, num_coautores, lista_coautores, detalhes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (docente_id, 'Trabalho em Evento', tit, ano, evt, num, lista, json.dumps(trab, ensure_ascii=False)))
                                count += 1
                            except:
                                try:
                                    self.db.cursor.execute("""
                                        INSERT INTO producao_bibliografica 
                                        (id_docente, tipo, titulo, ano, detalhes)
                                        VALUES (?, ?, ?, ?, ?)
                                    """, (docente_id, 'Trabalho em Evento', tit, ano, json.dumps(trab, ensure_ascii=False)))
                                    count += 1
                                except:
                                    pass
            except:
                pass
            
            # LIVROS E CAPÍTULOS
            try:
                livros_list = self.get_list_safe(prod, 'livrosECapitulos')
                
                for item in livros_list:
                    if isinstance(item, dict):
                        # Livros
                        livros = self.get_list_safe(item, 'livrosPublicadosOuOrganizados')
                        for liv in livros:
                            if not isinstance(liv, dict):
                                continue
                            
                            tit = self.to_str(liv.get('tituloDoLivro'))
                            if not tit:
                                tit = f"[Sem título - ID: {liv.get('id', 'N/A')}]"
                            
                            ano = self.safe_int(liv.get('anoDoLivro'))
                            edit = self.to_str(liv.get('nomeEditora'))
                            num, lista = self.contar_coautores(liv.get('autores', []))
                            
                            try:
                                self.db.cursor.execute("""
                                    INSERT INTO producao_bibliografica 
                                    (id_docente, tipo, titulo, ano, revista_evento_editora, num_coautores, lista_coautores, detalhes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (docente_id, 'Livro', tit, ano, edit, num, lista, json.dumps(liv, ensure_ascii=False)))
                                count += 1
                            except:
                                try:
                                    self.db.cursor.execute("""
                                        INSERT INTO producao_bibliografica 
                                        (id_docente, tipo, titulo, ano, detalhes)
                                        VALUES (?, ?, ?, ?, ?)
                                    """, (docente_id, 'Livro', tit, ano, json.dumps(liv, ensure_ascii=False)))
                                    count += 1
                                except:
                                    pass
                        
                        # Capítulos
                        caps = self.get_list_safe(item, 'capitulosDeLivrosPublicados')
                        for cap in caps:
                            if not isinstance(cap, dict):
                                continue
                            
                            tit = self.to_str(cap.get('tituloDoCapituloDoLivro'))
                            if not tit:
                                tit = f"[Sem título - ID: {cap.get('id', 'N/A')}]"
                            
                            ano = self.safe_int(cap.get('anoDoCapitulo'))
                            edit = self.to_str(cap.get('nomeEditora'))
                            num, lista = self.contar_coautores(cap.get('autores', []))
                            
                            try:
                                self.db.cursor.execute("""
                                    INSERT INTO producao_bibliografica 
                                    (id_docente, tipo, titulo, ano, revista_evento_editora, num_coautores, lista_coautores, detalhes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (docente_id, 'Capítulo de Livro', tit, ano, edit, num, lista, json.dumps(cap, ensure_ascii=False)))
                                count += 1
                            except:
                                try:
                                    self.db.cursor.execute("""
                                        INSERT INTO producao_bibliografica 
                                        (id_docente, tipo, titulo, ano, detalhes)
                                        VALUES (?, ?, ?, ?, ?)
                                    """, (docente_id, 'Capítulo de Livro', tit, ano, json.dumps(cap, ensure_ascii=False)))
                                    count += 1
                                except:
                                    pass
            except:
                pass
            
            if count > 0:
                self.stats['com_producoes'] += 1
        except:
            pass
    
    def extract_atuacoes(self, docente_id: int, data: dict):
        """Extrai atuações"""
        try:
            dg = self.safe_get(data, 'dadosGerais', default={})
            atu_dict = self.safe_get(dg, 'atuacoesProfissionais', default={})
            atuacoes = self.get_list_safe(atu_dict, 'atuacaoProfissional')
            
            count = 0
            for atu in atuacoes:
                if not isinstance(atu, dict):
                    continue
                
                inst = self.to_str(self.safe_get(atu, 'nomeInstituicao'))
                func = self.to_str(self.safe_get(atu, 'atividades'))
                vinc = self.to_str(self.safe_get(atu, 'vinculo'))
                ano_i = self.safe_int(atu.get('anoInicio'))
                ano_f = self.safe_int(atu.get('anoFim'))
                
                try:
                    self.db.cursor.execute("""
                        INSERT INTO atuacoes 
                        (id_docente, instituicao, funcao, tipo_vinculo, ano_inicio, ano_fim)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (docente_id, inst, func, vinc, ano_i, ano_f))
                    count += 1
                except:
                    pass
            
            if count > 0:
                self.stats['com_atuacoes'] += 1
        except:
            pass
    
    def extract_orientacoes(self, docente_id: int, data: dict):
        """Extrai orientações - APENAS IFs"""
        try:
            op = self.safe_get(data, 'outraProducao', default={})
            orient_list = self.get_list_safe(op, 'orientacoesConcluidas')
            
            count = 0
            
            for item in orient_list:
                if not isinstance(item, dict):
                    continue
                
                tipos = {
                    'orientacoesConcluidasParaMestrado': 'Mestrado',
                    'orientacoesConcluidasParaDoutorado': 'Doutorado',
                    'orientacoesConcluidasParaPosDoutorado': 'Pós-Doutorado',
                    'outrasOrientacoesConcluidas': 'Outros',
                }
                
                for campo, tipo_ori in tipos.items():
                    orients = self.get_list_safe(item, campo)
                    
                    for ori in orients:
                        if not isinstance(ori, dict):
                            continue
                        
                        nome_ori = self.to_str(ori.get('nomeDoOrientado'))
                        curso = self.to_str(ori.get('curso') or ori.get('tipoDeCurso'))
                        inst = self.to_str(ori.get('nomeDoInstituicao') or ori.get('instituicao'))
                        
                        # FILTRO: Apenas IFs
                        if not self.is_if(inst):
                            continue
                        
                        tit = self.to_str(ori.get('titulo'))
                        ano = self.safe_int(ori.get('ano'))
                        
                        tipo_final = tipo_ori
                        if tipo_ori == 'Outros':
                            nat = str(ori.get('natureza', '')).lower()
                            if 'iniciacao' in nat:
                                tipo_final = 'Iniciação Científica'
                            elif 'tcc' in nat or 'graduacao' in nat:
                                tipo_final = 'TCC/Graduação'
                        
                        try:
                            self.db.cursor.execute("""
                                INSERT INTO orientacoes_concluidas 
                                (id_docente, nome_orientado, tipo_orientacao, curso, instituicao, titulo, ano)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (docente_id, nome_ori, tipo_final, curso, inst, tit, ano))
                            count += 1
                        except:
                            try:
                                self.db.cursor.execute("""
                                    INSERT INTO orientacoes_concluidas 
                                    (id_docente, nome_orientado, curso, instituicao, titulo, ano)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (docente_id, nome_ori, curso, inst, tit, ano))
                                count += 1
                            except:
                                pass
            
            if count > 0:
                self.stats['com_orientacoes'] += 1
        except:
            pass
    
    def extract_premios(self, docente_id: int, data: dict):
        """Extrai prêmios"""
        try:
            dg = self.safe_get(data, 'dadosGerais', default={})
            prem_dict = self.safe_get(dg, 'premiosTitulos', default={})
            premios = self.get_list_safe(prem_dict, 'premioTitulo')
            
            count = 0
            for prem in premios:
                if not isinstance(prem, dict):
                    continue
                
                nome = self.to_str(prem.get('nomeDoPremioOuTitulo'))
                ano = self.safe_int(prem.get('ano'))
                inst = self.to_str(prem.get('nomeEntidadePromotora'))
                
                if nome:
                    try:
                        self.db.cursor.execute("""
                            INSERT INTO premios_titulos (id_docente, nome, ano, instituicao)
                            VALUES (?, ?, ?, ?)
                        """, (docente_id, nome, ano, inst))
                        count += 1
                    except:
                        pass
            
            if count > 0:
                self.stats['com_premios'] += 1
        except:
            pass
    
    def extract_areas(self, docente_id: int, data: dict):
        """Extrai áreas"""
        try:
            dg = self.safe_get(data, 'dadosGerais', default={})
            areas_dict = self.safe_get(dg, 'areasDeAtuacao', default={})
            areas = self.get_list_safe(areas_dict, 'areaDeAtuacao')
            
            count = 0
            for area in areas:
                if not isinstance(area, dict):
                    continue
                
                grande = self.to_str(area.get('nomeGrandeAreaDoConhecimento'))
                nome_area = self.to_str(area.get('nomeDaAreaDoConhecimento'))
                sub = self.to_str(area.get('nomeDaSubAreaDoConhecimento'))
                esp = self.to_str(area.get('nomeDaEspecialidade'))
                
                try:
                    self.db.cursor.execute("""
                        INSERT INTO areas_atuacao (id_docente, grande_area, area, subarea, especialidade)
                        VALUES (?, ?, ?, ?, ?)
                    """, (docente_id, grande, nome_area, sub, esp))
                    count += 1
                except:
                    pass
            
            if count > 0:
                self.stats['com_areas'] += 1
        except:
            pass
    
    def normalize_docente(self, docente_id: int, data_json: str):
        """Normaliza 1 docente"""
        try:
            data = json.loads(data_json)
            self.db.clear_normalized_data(docente_id)
            
            self.extract_dados_gerais(docente_id, data)
            self.extract_formacoes(docente_id, data)
            self.extract_atuacoes(docente_id, data)
            self.extract_producoes(docente_id, data)
            self.extract_orientacoes(docente_id, data)
            self.extract_premios(docente_id, data)
            self.extract_areas(docente_id, data)
            
            self.db.conn.commit()
            self.stats['processados'] += 1
        except json.JSONDecodeError:
            self.stats['erros_json'] += 1
        except Exception:
            self.stats['erros_json'] += 1
    
    def normalize_all(self):
        """Normaliza todos"""
        print("\n" + "="*70)
        print("🔄 NORMALIZER DEFINITIVO - Versão Final")
        print("="*70 + "\n")
        
        docentes = self.db.get_all_docentes_for_normalization()
        total = len(docentes)
        
        print(f"📊 Total: {total:,} docentes\n")
        
        for i, (doc_id, data_json) in enumerate(docentes, 1):
            self.normalize_docente(doc_id, data_json)
            
            if i % 100 == 0 or i == total:
                print(f"⏳ {i:,}/{total:,} ({(i/total)*100:.1f}%)")
        
        print(f"\n{'='*70}")
        print("✅ NORMALIZAÇÃO CONCLUÍDA")
        print(f"{'='*70}\n")
        
        print("📊 ESTATÍSTICAS:")
        print(f"   Processados: {self.stats['processados']:,}")
        print(f"   Erros JSON: {self.stats['erros_json']:,}")
        print(f"\n   Com dados:")
        print(f"      - Dados gerais: {self.stats['com_dados_gerais']:,}")
        print(f"      - Formações: {self.stats['com_formacoes']:,}")
        print(f"      - Atuações: {self.stats['com_atuacoes']:,}")
        print(f"      - Produções: {self.stats['com_producoes']:,}")
        print(f"      - Orientações (IFs): {self.stats['com_orientacoes']:,}")
        print(f"      - Prêmios: {self.stats['com_premios']:,}")
        print(f"      - Áreas: {self.stats['com_areas']:,}")


def main():
    print("\n🚀 NORMALIZER DEFINITIVO\n")
    
    db = Database()
    db.connect()
    
    try:
        normalizer = NormalizerDefinitivo(db)
        normalizer.normalize_all()
    except KeyboardInterrupt:
        print("\n⚠️  Interrompido!")
    finally:
        db.close()
    
    print("\n✅ Concluído!\n")


if __name__ == "__main__":
    main()