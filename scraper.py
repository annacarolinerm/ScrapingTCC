"""
Módulo de scraping do Portal Integra com retry automático e paralelização
"""

import asyncio
import aiohttp
import ssl
import time
from typing import Dict, List, Optional, Tuple
from config import (
    INSTITUICOES, PAGE_SIZE, MAX_CONCURRENT_DETAILS, 
    TIMEOUT, MAX_RETRIES, RETRY_DELAY, HEADERS, TERMOS_DOCENTE
)


class IntegraScraper:
    """Scraper assíncrono para o Portal Integra"""
    
    def __init__(self, sigla: str, base_url: str):
        """
        Inicializa o scraper para uma instituição
        
        Args:
            sigla: Sigla da instituição (ex: IFB, IFSP)
            base_url: URL base do Portal Integra
        """
        self.sigla = sigla
        self.base_url = base_url
        self.session = None
        
        # Estatísticas
        self.stats = {
            'total_pessoas': 0,
            'docentes_filtrados': 0,
            'detalhes_coletados': 0,
            'erros': 0,
            'cargos_encontrados': set(),
            'cargos_ignorados': set(),
        }
    
    async def create_session(self):
        """Cria sessão aiohttp com configurações apropriadas"""
        # SSL context que aceita certificados inválidos
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Timeout personalizado
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        
        # Criar connector com SSL desabilitado
        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=100)
        
        self.session = aiohttp.ClientSession(
            headers=HEADERS,
            timeout=timeout,
            connector=connector
        )
    
    async def close_session(self):
        """Fecha a sessão"""
        if self.session:
            await self.session.close()
    
    async def fetch_with_retry(self, url: str, max_retries: int = MAX_RETRIES) -> Optional[Dict]:
        """
        Faz requisição HTTP com retry automático
        
        Args:
            url: URL para fazer a requisição
            max_retries: Número máximo de tentativas
        
        Returns:
            JSON da resposta ou None em caso de falha
        """
        for attempt in range(max_retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"⚠️  {self.sigla}: Status {response.status} - tentativa {attempt + 1}/{max_retries}")
                        
            except asyncio.TimeoutError:
                print(f"⏱️  {self.sigla}: Timeout - tentativa {attempt + 1}/{max_retries}")
            except aiohttp.ClientError as e:
                print(f"🔌 {self.sigla}: Erro de conexão - tentativa {attempt + 1}/{max_retries}: {e}")
            except Exception as e:
                print(f"❌ {self.sigla}: Erro inesperado - tentativa {attempt + 1}/{max_retries}: {e}")
            
            # Aguarda antes de tentar novamente (exceto na última tentativa)
            if attempt < max_retries - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))  # Backoff exponencial
        
        self.stats['erros'] += 1
        return None
    
    def is_docente(self, cargo: str) -> bool:
        """
        Verifica se o cargo é de docente usando filtro ABRANGENTE
        
        Args:
            cargo: Cargo da pessoa
        
        Returns:
            True se for docente, False caso contrário
        """
        if not cargo:
            return False
        
        cargo_lower = cargo.lower()
        
        # Verifica se contém algum termo de docente
        for termo in TERMOS_DOCENTE:
            if termo in cargo_lower:
                self.stats['cargos_encontrados'].add(cargo)
                return True
        
        # Se não é docente, registra o cargo ignorado
        self.stats['cargos_ignorados'].add(cargo)
        return False
    
    async def fetch_pessoas_page(self, start: int) -> Optional[List[Dict]]:
        """
        Busca uma página de pessoas
        
        Args:
            start: Índice inicial
        
        Returns:
            Lista de pessoas ou None em caso de erro
        """
        url = f"{self.base_url}/api/portfolio/pessoa/data?start={start}&length={PAGE_SIZE}"
        data = await self.fetch_with_retry(url)
        
        if data and isinstance(data, list) and len(data) >= 2:
            # Formato: [{"total": N, "length": M}, [...pessoas...]]
            metadata = data[0]
            pessoas = data[1]
            
            # Atualiza total de pessoas na primeira página
            if start == 0:
                self.stats['total_pessoas'] = metadata.get('total', 0)
            
            return pessoas
        
        return None
    
    async def fetch_all_pessoas(self) -> List[Dict]:
        """
        Busca TODAS as pessoas da instituição (paginado)
        
        Returns:
            Lista completa de todas as pessoas
        """
        print(f"🔍 {self.sigla}: Buscando lista de pessoas...")
        
        todas_pessoas = []
        start = 0
        
        while True:
            pessoas = await self.fetch_pessoas_page(start)
            
            if not pessoas:
                # Se falhou e ainda não pegou ninguém, é erro crítico
                if start == 0:
                    print(f"❌ {self.sigla}: Falha ao buscar primeira página!")
                    return []
                # Se já pegou algumas, para por aqui
                break
            
            if len(pessoas) == 0:
                # Fim da paginação
                break
            
            todas_pessoas.extend(pessoas)
            
            # Se pegou menos que PAGE_SIZE, provavelmente é a última página
            if len(pessoas) < PAGE_SIZE:
                break
            
            start += PAGE_SIZE
            
            # Pequeno delay para não sobrecarregar
            await asyncio.sleep(0.1)
        
        print(f"📋 {self.sigla}: {len(todas_pessoas)} pessoas encontradas")
        return todas_pessoas
    
    async def fetch_pessoa_detalhes(self, slug: str) -> Optional[Dict]:
        """
        Busca detalhes completos de uma pessoa
        
        Args:
            slug: Identificador único da pessoa
        
        Returns:
            JSON completo dos detalhes ou None em caso de erro
        """
        url = f"{self.base_url}/api/portfolio/pessoa/s/{slug}"
        data = await self.fetch_with_retry(url)
        
        if data:
            # Adiciona a URL base nos dados para referência
            data['baseUrl'] = self.base_url
            self.stats['detalhes_coletados'] += 1
        
        return data
    
    async def fetch_docentes_detalhes(self, docentes: List[Dict]) -> List[Tuple[Dict, Dict]]:
        """
        Busca detalhes de múltiplos docentes em paralelo (limitado)
        
        Args:
            docentes: Lista de docentes básicos
        
        Returns:
            Lista de tuplas (dados_basicos, dados_completos)
        """
        print(f"📥 {self.sigla}: Coletando detalhes de {len(docentes)} docentes...")
        
        resultados = []
        
        # Divide em lotes para não sobrecarregar
        batch_size = MAX_CONCURRENT_DETAILS
        
        for i in range(0, len(docentes), batch_size):
            batch = docentes[i:i + batch_size]
            
            # Criar tarefas para o lote
            tasks = []
            for pessoa in batch:
                slug = pessoa.get('slug', '')
                if slug:
                    tasks.append(self.fetch_pessoa_detalhes(slug))
            
            # Executar em paralelo
            detalhes_batch = await asyncio.gather(*tasks)
            
            # Combinar com dados básicos
            for pessoa, detalhes in zip(batch, detalhes_batch):
                if detalhes:
                    resultados.append((pessoa, detalhes))
            
            # Progresso
            progress = min(i + batch_size, len(docentes))
            print(f"  ⏳ {self.sigla}: {progress}/{len(docentes)} docentes processados...")
            
            # Pequeno delay entre lotes
            if i + batch_size < len(docentes):
                await asyncio.sleep(0.5)
        
        print(f"✅ {self.sigla}: {len(resultados)} detalhes coletados com sucesso!")
        return resultados
    
    async def scrape(self) -> List[Tuple[Dict, Dict]]:
        """
        Executa o scraping completo da instituição
        
        Returns:
            Lista de tuplas (dados_basicos, dados_completos) dos docentes
        """
        print(f"\n{'='*60}")
        print(f"🎯 Iniciando coleta: {self.sigla}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Cria sessão
            await self.create_session()
            
            # 1. Buscar todas as pessoas
            todas_pessoas = await self.fetch_all_pessoas()
            
            if not todas_pessoas:
                print(f"❌ {self.sigla}: Nenhuma pessoa encontrada!")
                return []
            
            # 2. Filtrar apenas docentes
            docentes = []
            for pessoa in todas_pessoas:
                cargo = pessoa.get('cargo', '')
                if self.is_docente(cargo):
                    docentes.append(pessoa)
            
            self.stats['docentes_filtrados'] = len(docentes)
            
            print(f"👨‍🏫 {self.sigla}: {len(docentes)} docentes identificados (de {len(todas_pessoas)} pessoas)")
            
            if len(docentes) == 0:
                print(f"⚠️  {self.sigla}: ATENÇÃO - Nenhum docente foi filtrado! Verifique os cargos.")
                return []
            
            # 3. Buscar detalhes de todos os docentes
            resultados = await self.fetch_docentes_detalhes(docentes)
            
            # Fecha sessão
            await self.close_session()
            
            elapsed = time.time() - start_time
            print(f"\n✅ {self.sigla}: Coleta concluída em {elapsed:.1f}s")
            print(f"   📊 Estatísticas:")
            print(f"      - Total de pessoas: {self.stats['total_pessoas']}")
            print(f"      - Docentes filtrados: {self.stats['docentes_filtrados']}")
            print(f"      - Detalhes coletados: {self.stats['detalhes_coletados']}")
            print(f"      - Erros: {self.stats['erros']}")
            print(f"      - Cargos de docente encontrados: {len(self.stats['cargos_encontrados'])}")
            print(f"      - Cargos ignorados: {len(self.stats['cargos_ignorados'])}")
            
            return resultados
            
        except Exception as e:
            print(f"❌ {self.sigla}: Erro fatal durante coleta: {e}")
            await self.close_session()
            return []
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas da coleta"""
        return {
            'sigla': self.sigla,
            'total_pessoas': self.stats['total_pessoas'],
            'docentes_filtrados': self.stats['docentes_filtrados'],
            'detalhes_coletados': self.stats['detalhes_coletados'],
            'erros': self.stats['erros'],
            'cargos_encontrados': sorted(list(self.stats['cargos_encontrados'])),
            'cargos_ignorados': sorted(list(self.stats['cargos_ignorados'])),
        }


async def scrape_instituicao(sigla: str, base_url: str) -> Tuple[str, List[Tuple[Dict, Dict]], Dict]:
    """
    Faz scraping de uma instituição específica
    
    Args:
        sigla: Sigla da instituição
        base_url: URL base do Portal Integra
    
    Returns:
        Tupla (sigla, lista_de_docentes, estatísticas)
    """
    scraper = IntegraScraper(sigla, base_url)
    resultados = await scraper.scrape()
    stats = scraper.get_stats()
    
    return sigla, resultados, stats


async def scrape_multiplas_instituicoes(siglas_selecionadas: Optional[List[str]] = None):
    """
    Faz scraping de múltiplas instituições em paralelo (limitado)
    
    Args:
        siglas_selecionadas: Lista de siglas específicas ou None para todas
    
    Returns:
        Dict com resultados por instituição
    """
    # Determina quais instituições processar
    if siglas_selecionadas:
        instituicoes_processar = {
            sigla: INSTITUICOES[sigla] 
            for sigla in siglas_selecionadas 
            if sigla in INSTITUICOES
        }
        
        # Verifica siglas inválidas
        invalidas = set(siglas_selecionadas) - set(INSTITUICOES.keys())
        if invalidas:
            print(f"⚠️  Siglas inválidas ignoradas: {', '.join(invalidas)}")
    else:
        instituicoes_processar = INSTITUICOES
    
    print(f"\n🚀 Iniciando coleta de {len(instituicoes_processar)} instituições")
    print(f"   Instituições: {', '.join(instituicoes_processar.keys())}")
    
    todos_resultados = {}
    todas_stats = {}
    
    # Processar em lotes para não sobrecarregar
    from config import MAX_CONCURRENT_INSTITUTIONS
    
    siglas_lista = list(instituicoes_processar.keys())
    
    for i in range(0, len(siglas_lista), MAX_CONCURRENT_INSTITUTIONS):
        batch_siglas = siglas_lista[i:i + MAX_CONCURRENT_INSTITUTIONS]
        
        print(f"\n📦 Processando lote {i//MAX_CONCURRENT_INSTITUTIONS + 1}: {', '.join(batch_siglas)}")
        
        # Criar tarefas para o lote
        tasks = []
        for sigla in batch_siglas:
            info = instituicoes_processar[sigla]
            tasks.append(scrape_instituicao(sigla, info['url']))
        
        # Executar em paralelo
        resultados_batch = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        for resultado in resultados_batch:
            if isinstance(resultado, Exception):
                print(f"❌ Erro em uma instituição: {resultado}")
                continue
            
            sigla, docentes, stats = resultado
            todos_resultados[sigla] = docentes
            todas_stats[sigla] = stats
    
    return todos_resultados, todas_stats


if __name__ == "__main__":
    # Teste: coletar dados de uma instituição
    import sys
    
    sigla_teste = "IFB" if len(sys.argv) < 2 else sys.argv[1]
    
    if sigla_teste not in INSTITUICOES:
        print(f"❌ Sigla inválida: {sigla_teste}")
        print(f"Siglas disponíveis: {', '.join(sorted(INSTITUICOES.keys()))}")
        sys.exit(1)
    
    print(f"🧪 Teste de scraping: {sigla_teste}")
    
    async def teste():
        info = INSTITUICOES[sigla_teste]
        sigla, resultados, stats = await scrape_instituicao(sigla_teste, info['url'])
        
        print(f"\n📊 Resultados do teste:")
        print(f"   Docentes coletados: {len(resultados)}")
        print(f"\n   Primeiros 3 docentes:")
        for i, (basico, completo) in enumerate(resultados[:3]):
            print(f"      {i+1}. {basico['nome']} - {basico['cargo']}")
    
    asyncio.run(teste())
