"""
Gerenciamento do banco de dados SQLite para o scraping do Portal Integra
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import DB_NAME


class Database:
    """Classe para gerenciar o banco de dados SQLite"""
    
    def __init__(self, db_name: str = DB_NAME):
        """Inicializa conexão com o banco de dados"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Conecta ao banco de dados"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Fecha conexão com o banco"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Cria todas as tabelas necessárias"""
        
        # Tabela principal de docentes
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS docentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sigla TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                campus TEXT,
                cargo TEXT,
                email TEXT,
                url TEXT,
                data_completa TEXT NOT NULL,  -- JSON completo da API
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices para melhor performance
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_docentes_sigla 
            ON docentes(sigla)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_docentes_slug 
            ON docentes(slug)
        """)
        
        # Tabela de dados gerais
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS dados_gerais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_docente INTEGER NOT NULL,
                nome_completo TEXT,
                nome_citacao TEXT,
                orcid TEXT,
                resumo_cv TEXT,
                FOREIGN KEY (id_docente) REFERENCES docentes(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de formações acadêmicas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS formacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_docente INTEGER NOT NULL,
                nivel TEXT,  -- doutorado, mestrado, graduação, etc
                curso TEXT,
                instituicao TEXT,
                ano_inicio INTEGER,
                ano_fim INTEGER,
                titulo TEXT,
                orientador TEXT,
                FOREIGN KEY (id_docente) REFERENCES docentes(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de atuações profissionais
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS atuacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_docente INTEGER NOT NULL,
                instituicao TEXT,
                funcao TEXT,
                tipo_vinculo TEXT,
                ano_inicio INTEGER,
                ano_fim INTEGER,
                FOREIGN KEY (id_docente) REFERENCES docentes(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de produção bibliográfica
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS producao_bibliografica (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_docente INTEGER NOT NULL,
                tipo TEXT,  -- artigo, livro, capítulo, etc
                titulo TEXT,
                ano INTEGER,
                detalhes TEXT,  -- JSON com informações adicionais
                FOREIGN KEY (id_docente) REFERENCES docentes(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de orientações concluídas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orientacoes_concluidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_docente INTEGER NOT NULL,
                nome_orientado TEXT,
                curso TEXT,
                instituicao TEXT,
                titulo TEXT,
                ano INTEGER,
                FOREIGN KEY (id_docente) REFERENCES docentes(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de prêmios e títulos
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS premios_titulos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_docente INTEGER NOT NULL,
                nome TEXT,
                ano INTEGER,
                instituicao TEXT,
                FOREIGN KEY (id_docente) REFERENCES docentes(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de áreas de atuação
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS areas_atuacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_docente INTEGER NOT NULL,
                grande_area TEXT,
                area TEXT,
                subarea TEXT,
                especialidade TEXT,
                FOREIGN KEY (id_docente) REFERENCES docentes(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
        print("✅ Tabelas criadas com sucesso!")
    
    def insert_docente(self, sigla: str, pessoa: Dict, data_completa: Dict) -> Optional[int]:
        """
        Insere ou atualiza um docente no banco
        
        Args:
            sigla: Sigla da instituição (ex: IFB, IFSP)
            pessoa: Dados básicos da pessoa
            data_completa: JSON completo da API de detalhes
        
        Returns:
            ID do docente inserido/atualizado ou None em caso de erro
        """
        try:
            slug = pessoa.get('slug', '')
            nome = pessoa.get('nome', '')
            campus = pessoa.get('campusNome', '')
            cargo = pessoa.get('cargo', '')
            
            # Extrai email se disponível
            email = None
            if 'dadosGerais' in data_completa and 'emails' in data_completa['dadosGerais']:
                emails = data_completa['dadosGerais']['emails']
                if emails and len(emails) > 0:
                    email = emails[0].get('email', '')
            
            url = f"{data_completa.get('baseUrl', '')}/api/portfolio/pessoa/s/{slug}"
            
            # Converte data_completa para JSON string
            data_json = json.dumps(data_completa, ensure_ascii=False)
            
            # Verifica se já existe
            self.cursor.execute("SELECT id FROM docentes WHERE slug = ?", (slug,))
            existing = self.cursor.fetchone()
            
            if existing:
                # Atualiza
                self.cursor.execute("""
                    UPDATE docentes 
                    SET sigla = ?, nome = ?, campus = ?, cargo = ?, 
                        email = ?, url = ?, data_completa = ?, 
                        atualizado_em = CURRENT_TIMESTAMP
                    WHERE slug = ?
                """, (sigla, nome, campus, cargo, email, url, data_json, slug))
                docente_id = existing[0]
            else:
                # Insere novo
                self.cursor.execute("""
                    INSERT INTO docentes (sigla, slug, nome, campus, cargo, email, url, data_completa)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (sigla, slug, nome, campus, cargo, email, url, data_json))
                docente_id = self.cursor.lastrowid
            
            self.conn.commit()
            return docente_id
            
        except Exception as e:
            print(f"❌ Erro ao inserir docente {pessoa.get('nome', 'DESCONHECIDO')}: {e}")
            return None
    
    def get_docentes_by_sigla(self, sigla: str) -> List[Dict]:
        """Retorna todos os docentes de uma instituição"""
        self.cursor.execute("""
            SELECT id, sigla, slug, nome, campus, cargo, email, url, atualizado_em
            FROM docentes
            WHERE sigla = ?
            ORDER BY nome
        """, (sigla,))
        
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_all_siglas(self) -> List[str]:
        """Retorna lista de todas as siglas únicas no banco"""
        self.cursor.execute("""
            SELECT DISTINCT sigla 
            FROM docentes 
            ORDER BY sigla
        """)
        return [row[0] for row in self.cursor.fetchall()]
    
    def count_docentes_by_sigla(self, sigla: str) -> int:
        """Conta quantos docentes existem no banco para uma instituição"""
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM docentes 
            WHERE sigla = ?
        """, (sigla,))
        return self.cursor.fetchone()[0]
    
    def count_all_docentes(self) -> int:
        """Conta total de docentes no banco"""
        self.cursor.execute("SELECT COUNT(*) FROM docentes")
        return self.cursor.fetchone()[0]
    
    def get_docente_data_completa(self, docente_id: int) -> Optional[Dict]:
        """Retorna o JSON completo de um docente"""
        self.cursor.execute("""
            SELECT data_completa 
            FROM docentes 
            WHERE id = ?
        """, (docente_id,))
        
        row = self.cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None
    
    def get_all_docentes_for_normalization(self) -> List[tuple]:
        """Retorna todos os docentes para normalização (id, data_completa)"""
        self.cursor.execute("""
            SELECT id, data_completa 
            FROM docentes 
            ORDER BY id
        """)
        return self.cursor.fetchall()
    
    def clear_normalized_data(self, docente_id: int):
        """Remove dados normalizados de um docente (para re-normalizar)"""
        tables = [
            'dados_gerais', 'formacoes', 'atuacoes', 
            'producao_bibliografica', 'orientacoes_concluidas', 
            'premios_titulos', 'areas_atuacao'
        ]
        
        for table in tables:
            self.cursor.execute(f"DELETE FROM {table} WHERE id_docente = ?", (docente_id,))
        
        self.conn.commit()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais do banco"""
        stats = {}
        
        # Total de docentes
        stats['total_docentes'] = self.count_all_docentes()
        
        # Docentes por instituição
        self.cursor.execute("""
            SELECT sigla, COUNT(*) as total
            FROM docentes
            GROUP BY sigla
            ORDER BY total DESC
        """)
        stats['por_instituicao'] = dict(self.cursor.fetchall())
        
        # Docentes por UF
        self.cursor.execute("""
            SELECT 
                CASE 
                    WHEN sigla LIKE '%MG' OR sigla IN ('IFMG', 'IFNMG', 'IFSUDESTEMG', 'IFSULDEMINAS', 'IFTM', 'CEFET-MG') THEN 'MG'
                    WHEN sigla LIKE '%RJ' OR sigla IN ('IFRJ', 'IFFLUMINENSE', 'CEFET-RJ') THEN 'RJ'
                    WHEN sigla LIKE '%SP' THEN 'SP'
                    WHEN sigla LIKE '%RS' OR sigla IN ('IFRS', 'IFFARROUPILHA', 'IFSUL') THEN 'RS'
                    WHEN sigla LIKE '%GO' OR sigla IN ('IFG', 'IFGOIANO') THEN 'GO'
                    WHEN sigla LIKE '%PE' OR sigla IN ('IFPE', 'IFSertaoPE') THEN 'PE'
                    WHEN sigla LIKE '%SC' OR sigla IN ('IFSC', 'IFC') THEN 'SC'
                    ELSE SUBSTR(sigla, 3)
                END as uf,
                COUNT(*) as total
            FROM docentes
            GROUP BY uf
            ORDER BY total DESC
        """)
        stats['por_uf'] = dict(self.cursor.fetchall())
        
        # Tabelas normalizadas
        tables = [
            'dados_gerais', 'formacoes', 'atuacoes', 
            'producao_bibliografica', 'orientacoes_concluidas', 
            'premios_titulos', 'areas_atuacao'
        ]
        
        stats['tabelas_normalizadas'] = {}
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats['tabelas_normalizadas'][table] = self.cursor.fetchone()[0]
        
        return stats


def init_database():
    """Inicializa o banco de dados criando as tabelas"""
    db = Database()
    db.connect()
    db.create_tables()
    db.close()
    return True


if __name__ == "__main__":
    # Teste: criar banco e mostrar estatísticas
    print("🔧 Inicializando banco de dados...")
    init_database()
    
    db = Database()
    db.connect()
    stats = db.get_statistics()
    db.close()
    
    print(f"\n📊 Estatísticas:")
    print(f"Total de docentes: {stats['total_docentes']}")
    print(f"\nTabelas normalizadas:")
    for table, count in stats['tabelas_normalizadas'].items():
        print(f"  {table}: {count} registros")
