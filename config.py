"""
Configurações do sistema de scraping do Portal Integra
"""

# Configurações de coleta
PAGE_SIZE = 50  # Tamanho da página na API
MAX_CONCURRENT_INSTITUTIONS = 5  # Máximo de instituições simultâneas
MAX_CONCURRENT_DETAILS = 50  # Máximo de requisições de detalhes simultâneas por instituição
TIMEOUT = 60  # Timeout em segundos
MAX_RETRIES = 3  # Número máximo de tentativas em caso de falha
RETRY_DELAY = 2  # Delay entre tentativas (segundos)

# Headers HTTP para simular navegador
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Lista completa das 40 instituições da Rede Federal
INSTITUICOES = {
    "IFAC": {"url": "https://integra.ifac.edu.br", "uf": "AC"},
    "IFAL": {"url": "https://integra.ifal.edu.br", "uf": "AL"},
    "IFAP": {"url": "https://integra.ifap.edu.br", "uf": "AP"},
    "IFAM": {"url": "https://integra.ifam.edu.br", "uf": "AM"},
    "IFBA": {"url": "https://integra.ifba.edu.br", "uf": "BA"},
    "IFBAIANO": {"url": "https://integra.ifbaiano.edu.br", "uf": "BA"},
    "IFB": {"url": "https://integra.ifb.edu.br", "uf": "DF"},
    "IFCE": {"url": "https://integra.ifce.edu.br", "uf": "CE"},
    "IFES": {"url": "https://integra.ifes.edu.br", "uf": "ES"},
    "IFG": {"url": "https://integra.ifg.edu.br", "uf": "GO"},
    "IFGOIANO": {"url": "https://integra.ifgoiano.edu.br", "uf": "GO"},
    "IFMA": {"url": "https://integra.ifma.edu.br", "uf": "MA"},
    "IFMG": {"url": "https://integra.ifmg.edu.br", "uf": "MG"},
    "IFNMG": {"url": "https://integra.ifnmg.edu.br", "uf": "MG"},
    "IFSUDESTEMG": {"url": "https://integra.ifsudestemg.edu.br", "uf": "MG"},
    "IFSULDEMINAS": {"url": "https://integra.ifsuldeminas.edu.br", "uf": "MG"},
    "IFTM": {"url": "https://integra.iftm.edu.br", "uf": "MG"},
    "IFMT": {"url": "https://integra.ifmt.edu.br", "uf": "MT"},
    "IFMS": {"url": "https://integra.ifms.edu.br", "uf": "MS"},
    "IFPA": {"url": "https://integra.ifpa.edu.br", "uf": "PA"},
    "IFPB": {"url": "https://integra.ifpb.edu.br", "uf": "PB"},
    "IFPE": {"url": "https://integra.ifpe.edu.br", "uf": "PE"},
    "IFSertaoPE": {"url": "https://integra.ifsertao-pe.edu.br", "uf": "PE"},
    "IFPI": {"url": "https://integra.ifpi.edu.br", "uf": "PI"},
    "IFPR": {"url": "https://integra.ifpr.edu.br", "uf": "PR"},
    "IFRJ": {"url": "https://integra.ifrj.edu.br", "uf": "RJ"},
    "IFFLUMINENSE": {"url": "http://integra.iff.edu.br", "uf": "RJ"},  # HTTP, não HTTPS!
    "IFRN": {"url": "https://integra.ifrn.edu.br", "uf": "RN"},
    "IFRO": {"url": "https://integra.ifro.edu.br", "uf": "RO"},
    "IFRR": {"url": "https://integra.ifrr.edu.br", "uf": "RR"},
    "IFRS": {"url": "https://integra.ifrs.edu.br", "uf": "RS"},
    "IFFARROUPILHA": {"url": "https://integra.iffarroupilha.edu.br", "uf": "RS"},
    "IFSUL": {"url": "https://integra.ifsul.edu.br", "uf": "RS"},
    "IFSC": {"url": "https://integra.ifsc.edu.br", "uf": "SC"},
    "IFC": {"url": "https://integra.ifc.edu.br", "uf": "SC"},
    "IFSP": {"url": "https://integra.ifsp.edu.br", "uf": "SP"},
    "IFS": {"url": "https://integra.ifs.edu.br", "uf": "SE"},
    "IFTO": {"url": "https://integra.ifto.edu.br", "uf": "TO"},
    "CEFET-RJ": {"url": "https://integra.cefet-rj.br", "uf": "RJ"},
    "CEFET-MG": {"url": "https://integra.cefetmg.br", "uf": "MG"},
}

# Termos para filtrar docentes (filtro ABRANGENTE para não perder ninguém)
TERMOS_DOCENTE = [
    "professor",
    "docente",
    "ebtt",
    "magistério",
    "magistério superior",
    "ensino",
    "titular",
    "adjunto",
    "assistente",
    "auxiliar",
    "substituto",
    "temporário",
    "visitante",
    "associado",
    "colaborador",
]

# Nome do banco de dados
DB_NAME = "integra.db"
