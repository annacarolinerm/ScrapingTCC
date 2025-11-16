#!/usr/bin/env python3
"""
INSERIR ORIENTAÇÕES - Com nome do banco CORRETO
"""

import json
import sqlite3
import os
import glob

print("\n" + "="*70)
print("🔍 PROCURANDO BANCO DE DADOS")
print("="*70 + "\n")

# Procura arquivo .db na pasta atual
bancos = glob.glob("*.db")

if not bancos:
    print("❌ NENHUM banco .db encontrado na pasta atual!")
    print("   Arquivos na pasta:")
    for arquivo in os.listdir('.'):
        print(f"   - {arquivo}")
    exit(1)

print(f"📁 Bancos encontrados:")
for i, banco in enumerate(bancos, 1):
    tamanho = os.path.getsize(banco) / (1024*1024)
    print(f"   {i}. {banco} ({tamanho:.1f} MB)")

# Usa o primeiro (ou o que tiver 'integra' no nome)
banco_escolhido = None
for banco in bancos:
    if 'integra' in banco.lower():
        banco_escolhido = banco
        break

if not banco_escolhido:
    banco_escolhido = bancos[0]

print(f"\n✅ Usando: {banco_escolhido}\n")

# Conecta
conn = sqlite3.connect(banco_escolhido)
cursor = conn.cursor()

# Verifica se tabelas existem
print("📊 Verificando tabelas...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = [t[0] for t in cursor.fetchall()]
print(f"   Tabelas: {', '.join(tabelas)}\n")

if 'orientacoes_concluidas' not in tabelas:
    print("❌ Tabela 'orientacoes_concluidas' não existe!")
    print("   Execute: python atualizar_banco.py")
    exit(1)

if 'docentes' not in tabelas:
    print("❌ Tabela 'docentes' não existe!")
    exit(1)

# Conta docentes
cursor.execute("SELECT COUNT(*) FROM docentes")
total_docentes = cursor.fetchone()[0]
print(f"✅ Banco OK! {total_docentes} docentes encontrados\n")

# Verifica estrutura da tabela orientacoes_concluidas
print("📋 Estrutura da tabela orientacoes_concluidas:")
cursor.execute("PRAGMA table_info(orientacoes_concluidas)")
colunas = cursor.fetchall()
for col in colunas:
    print(f"   - {col[1]} ({col[2]})")
print()

# LIMPA tabela
print("🗑️  Limpando tabela orientacoes_concluidas...")
cursor.execute("DELETE FROM orientacoes_concluidas")
conn.commit()
print("   ✅ Tabela limpa!\n")

# FUNÇÕES
def to_str(val):
    return str(val).strip() if val else ''

def safe_int(val):
    try:
        return int(val) if val else None
    except:
        return None

# PROCESSA
print("="*70)
print("🔄 PROCESSANDO ORIENTAÇÕES")
print("="*70 + "\n")

cursor.execute("SELECT id, nome, data_completa FROM docentes")
docentes = cursor.fetchall()

total = len(docentes)
inseridos = 0
erros = 0
docentes_com_orientacoes = 0

for i, (doc_id, nome, data_json) in enumerate(docentes, 1):
    try:
        data = json.loads(data_json)
        
        outra = data.get('outraProducao', {})
        orient_list = outra.get('orientacoesConcluidas', [])
        
        if not orient_list or not isinstance(orient_list, list) or len(orient_list) == 0:
            continue
        
        item = orient_list[0]
        if not isinstance(item, dict):
            continue
        
        teve_orientacao_neste_docente = False
        
        # Mestrado
        mestrados = item.get('orientacoesConcluidasParaMestrado', [])
        if isinstance(mestrados, list):
            for ori in mestrados:
                if not isinstance(ori, dict):
                    continue
                
                det = ori.get('detalhamentoDaOrientacaoConcluidaDeMestrado', {})
                basicos = ori.get('dadosBasicosDaOrientacaoConcluidaDeMestrado', {})
                
                if not isinstance(det, dict):
                    det = {}
                if not isinstance(basicos, dict):
                    basicos = {}
                
                nome_ori = to_str(det.get('nomeDoOrientado'))
                curso = to_str(det.get('nomeDoCurso'))
                inst = to_str(det.get('nomeDaInstituicao'))
                tit = to_str(basicos.get('titulo'))
                ano = safe_int(basicos.get('ano'))
                
                cursor.execute("""
                    INSERT INTO orientacoes_concluidas 
                    (id_docente, nome_orientado, tipo_orientacao, curso, instituicao, titulo, ano)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (doc_id, nome_ori, 'Mestrado', curso, inst, tit, ano))
                inseridos += 1
                teve_orientacao_neste_docente = True
        
        # Doutorado
        doutorados = item.get('orientacoesConcluidasParaDoutorado', [])
        if isinstance(doutorados, list):
            for ori in doutorados:
                if not isinstance(ori, dict):
                    continue
                
                det = ori.get('detalhamentoDaOrientacaoConcluidaDeDoutorado', {})
                basicos = ori.get('dadosBasicosDaOrientacaoConcluidaDeDoutorado', {})
                
                if not isinstance(det, dict):
                    det = {}
                if not isinstance(basicos, dict):
                    basicos = {}
                
                nome_ori = to_str(det.get('nomeDoOrientado'))
                curso = to_str(det.get('nomeDoCurso'))
                inst = to_str(det.get('nomeDaInstituicao'))
                tit = to_str(basicos.get('titulo'))
                ano = safe_int(basicos.get('ano'))
                
                cursor.execute("""
                    INSERT INTO orientacoes_concluidas 
                    (id_docente, nome_orientado, tipo_orientacao, curso, instituicao, titulo, ano)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (doc_id, nome_ori, 'Doutorado', curso, inst, tit, ano))
                inseridos += 1
                teve_orientacao_neste_docente = True
        
        # Pós-Doutorado
        pos_docs = item.get('orientacoesConcluidasParaPosDoutorado', [])
        if isinstance(pos_docs, list):
            for ori in pos_docs:
                if not isinstance(ori, dict):
                    continue
                
                det = ori.get('detalhamentoDaOrientacaoConcluidaDePosDoutorado', {})
                basicos = ori.get('dadosBasicosDaOrientacaoConcluidaDePosDoutorado', {})
                
                if not isinstance(det, dict):
                    det = {}
                if not isinstance(basicos, dict):
                    basicos = {}
                
                nome_ori = to_str(det.get('nomeDoOrientado'))
                curso = to_str(det.get('nomeDoCurso'))
                inst = to_str(det.get('nomeDaInstituicao'))
                tit = to_str(basicos.get('titulo'))
                ano = safe_int(basicos.get('ano'))
                
                cursor.execute("""
                    INSERT INTO orientacoes_concluidas 
                    (id_docente, nome_orientado, tipo_orientacao, curso, instituicao, titulo, ano)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (doc_id, nome_ori, 'Pós-Doutorado', curso, inst, tit, ano))
                inseridos += 1
                teve_orientacao_neste_docente = True
        
        # Outras Orientações
        outras = item.get('outrasOrientacoesConcluidas', [])
        if isinstance(outras, list):
            for ori in outras:
                if not isinstance(ori, dict):
                    continue
                
                det = ori.get('detalhamentoDeOutrasOrientacoesConcluidas', {})
                basicos = ori.get('dadosBasicosDeOutrasOrientacoesConcluidas', {})
                
                if not isinstance(det, dict):
                    det = {}
                if not isinstance(basicos, dict):
                    basicos = {}
                
                nome_ori = to_str(det.get('nomeDoOrientado'))
                curso = to_str(det.get('nomeDoCurso'))
                inst = to_str(det.get('nomeDaInstituicao'))
                tit = to_str(basicos.get('titulo'))
                ano = safe_int(basicos.get('ano'))
                
                natureza = str(basicos.get('natureza', '')).lower()
                if 'iniciacao' in natureza:
                    tipo = 'Iniciação Científica'
                elif 'tcc' in natureza or 'graduacao' in natureza:
                    tipo = 'TCC/Graduação'
                else:
                    tipo = 'Outros'
                
                cursor.execute("""
                    INSERT INTO orientacoes_concluidas 
                    (id_docente, nome_orientado, tipo_orientacao, curso, instituicao, titulo, ano)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (doc_id, nome_ori, tipo, curso, inst, tit, ano))
                inseridos += 1
                teve_orientacao_neste_docente = True
        
        if teve_orientacao_neste_docente:
            docentes_com_orientacoes += 1
    
    except Exception as e:
        erros += 1
        if erros <= 3:
            print(f"❌ Erro docente {doc_id}: {e}")
    
    if i % 100 == 0 or i == total:
        print(f"⏳ {i}/{total} - Inseridos: {inseridos}")
        conn.commit()

# Commit final
conn.commit()

print(f"\n{'='*70}")
print("✅ INSERÇÃO CONCLUÍDA!")
print(f"{'='*70}\n")

print(f"📊 RESULTADO:")
print(f"   Total de orientações inseridas: {inseridos}")
print(f"   Docentes com orientações: {docentes_com_orientacoes}")
print(f"   Erros: {erros}\n")

# Verifica se realmente inseriu
cursor.execute("SELECT COUNT(*) FROM orientacoes_concluidas")
count_verificacao = cursor.fetchone()[0]

print(f"🔍 VERIFICAÇÃO:")
print(f"   Registros na tabela: {count_verificacao}")

if count_verificacao == inseridos:
    print(f"   ✅ CONFIRMADO! Dados foram salvos!\n")
else:
    print(f"   ⚠️  Divergência! Verificar...\n")

# TOP instituições
cursor.execute("""
    SELECT instituicao, COUNT(*) as total
    FROM orientacoes_concluidas
    WHERE instituicao != ''
    GROUP BY instituicao
    ORDER BY total DESC
    LIMIT 15
""")

instituicoes = cursor.fetchall()

if instituicoes:
    print("🏛️  TOP 15 INSTITUIÇÕES:")
    for inst, count in instituicoes:
        is_if = 'INSTITUTO FEDERAL' in inst.upper() or 'CEFET' in inst.upper() or any(s in inst.upper() for s in ['IFAC', 'IFAL', 'IFB', 'IFBA', 'IFCE', 'IFC'])
        emoji = "✅" if is_if else "  "
        print(f"   {emoji} {count:4d}x - {inst[:60]}")

conn.close()

print(f"\n{'='*70}")
print(f"✅ BANCO SALVO: {banco_escolhido}")
print(f"✅ Total de orientações: {inseridos}")
print(f"{'='*70}\n")