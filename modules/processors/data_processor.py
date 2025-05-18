"""
Processador de dados para unificar informações de múltiplas fontes.
"""

import logging
import random
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Processador responsável por unificar dados de múltiplas fontes.
    """
    
    def __init__(self):
        """Inicializa o processador de dados."""
        # Mapeamento de campos de diferentes fontes para campos padronizados
        self.field_mapping = {
            'linkedin': {
                'name': 'Company Name (Revised)',
                'location': 'Location',
                'size': 'Size',
                'first_name': 'First name',
                'last_name': 'Second Name',
                'position': 'Office',
                'website': 'Domain',
                'linkedin': 'Linkedin',
                'city': 'City',
                'state': 'State'
            },
            'cnpj': {
                'name': 'Company Name (Revised)',
                'fantasy_name': 'Fantasy name',
                'cnpj': 'CNPJ',
                'cnpj_formatted': 'CNPJ',
                'location': 'Location',
                'address': 'Location',
                'email': 'E-mail',
                'phone': 'Telephone',
                'phone2': 'Telephone 2',
                'city': 'City',
                'state': 'State'
            },
            'company_site': {
                'name': 'Company Name (Revised)',
                'website': 'Domain',
                'domain': 'Domain',
                'email': 'E-mail',
                'phone': 'Telephone',
                'phone2': 'Telephone 2',
                'address': 'Location',
                'size': 'Size'
            }
        }
        
        # Dados de fallback para quando o scraping falhar
        self.fallback_data = {
            'domains': ['gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com', 'uol.com.br', 'terra.com.br'],
            'states': ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'DF', 'GO', 'PE'],
            'cities': {
                'SP': ['São Paulo', 'Campinas', 'Santos', 'São José dos Campos', 'Ribeirão Preto'],
                'RJ': ['Rio de Janeiro', 'Niterói', 'Petrópolis', 'Volta Redonda', 'Duque de Caxias'],
                'MG': ['Belo Horizonte', 'Uberlândia', 'Contagem', 'Juiz de Fora', 'Betim'],
                'RS': ['Porto Alegre', 'Caxias do Sul', 'Pelotas', 'Canoas', 'Santa Maria'],
                'PR': ['Curitiba', 'Londrina', 'Maringá', 'Ponta Grossa', 'Cascavel'],
                'SC': ['Florianópolis', 'Joinville', 'Blumenau', 'São José', 'Criciúma'],
                'BA': ['Salvador', 'Feira de Santana', 'Vitória da Conquista', 'Camaçari', 'Itabuna'],
                'DF': ['Brasília', 'Ceilândia', 'Taguatinga', 'Samambaia', 'Plano Piloto'],
                'GO': ['Goiânia', 'Aparecida de Goiânia', 'Anápolis', 'Rio Verde', 'Luziânia'],
                'PE': ['Recife', 'Jaboatão dos Guararapes', 'Olinda', 'Caruaru', 'Petrolina']
            },
            'sizes': ['Pequeno Porte', 'Médio Porte', 'Grande Porte'],
            'positions': ['CEO', 'CTO', 'Diretor', 'Gerente', 'Coordenador', 'Analista', 'Desenvolvedor'],
            'first_names': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Fernanda', 'Lucas', 'Juliana', 'Rafael', 'Mariana'],
            'last_names': ['Silva', 'Santos', 'Oliveira', 'Souza', 'Pereira', 'Lima', 'Costa', 'Ferreira', 'Rodrigues', 'Almeida']
        }
        
        # Importar configurações
        from config import settings
        self.use_fallback = getattr(settings, 'USE_FALLBACK_DATA', False)
        self.export_partial = getattr(settings, 'EXPORT_PARTIAL_DATA', False)
    
    def process(self, raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa e unifica dados de múltiplas fontes.
        
        Args:
            raw_results: Resultados brutos da busca
            
        Returns:
            Lista de resultados processados
        """
        processed_results = []
        
        for company_result in raw_results:
            try:
                # Inicializar dados unificados
                unified_data = {
                    'Company Name (Revised)': '',
                    'Location': '',
                    'CNPJ': '',
                    'Fantasy name': '',
                    'Domain': '',
                    'Size': '',
                    'First name': '',
                    'Second Name': '',
                    'Office': '',
                    'E-mail': '',
                    'Telephone': '',
                    'Telephone 2': '',
                    'City': '',
                    'State': '',
                    'Linkedin': '',
                    'LOTE': 1  # Valor padrão para LOTE
                }
                
                # Processar cada fonte de dados
                for source_data in company_result.get('data_sources', []):
                    source_type = source_data.get('source', '')
                    
                    if source_type in self.field_mapping:
                        # Mapear campos da fonte para campos padronizados
                        for source_field, target_field in self.field_mapping[source_type].items():
                            if source_field in source_data and source_data[source_field]:
                                # Só atualizar se o campo estiver vazio ou a fonte atual for mais confiável
                                if not unified_data[target_field] or self._is_better_source(source_type, target_field, unified_data.get(f"_source_{target_field}", "")):
                                    unified_data[target_field] = source_data[source_field]
                                    unified_data[f"_source_{target_field}"] = source_type
                
                # Verificar se tem dados suficientes
                if self._has_minimum_data(unified_data):
                    # Preencher dados ausentes com fallback se configurado
                    if self.use_fallback:
                        self._fill_missing_data(unified_data)
                    
                    # Remover campos temporários de controle
                    for field in list(unified_data.keys()):
                        if field.startswith('_source_'):
                            del unified_data[field]
                    
                    processed_results.append(unified_data)
                elif self.export_partial and unified_data['Company Name (Revised)']:
                    # Se configurado para exportar dados parciais e tiver pelo menos o nome
                    logger.warning(f"Exportando dados parciais para {unified_data['Company Name (Revised)']}")
                    
                    # Preencher dados ausentes com fallback
                    if self.use_fallback:
                        self._fill_missing_data(unified_data)
                    
                    # Remover campos temporários de controle
                    for field in list(unified_data.keys()):
                        if field.startswith('_source_'):
                            del unified_data[field]
                    
                    processed_results.append(unified_data)
                else:
                    logger.warning(f"Empresa {unified_data.get('Company Name (Revised)', 'Desconhecida')} não tem dados mínimos necessários")
            
            except Exception as e:
                logger.error(f"Erro ao processar dados da empresa: {e}")
        
        # Se não houver resultados e estiver configurado para usar fallback, gerar dados sintéticos
        if not processed_results and self.use_fallback:
            logger.warning("Nenhum resultado processado. Gerando dados sintéticos de fallback.")
            processed_results = self._generate_synthetic_data(10)  # Gerar 10 empresas sintéticas
        
        return processed_results
    
    def _is_better_source(self, new_source: str, field: str, current_source: str) -> bool:
        """
        Verifica se a nova fonte é mais confiável que a atual para um campo específico.
        
        Args:
            new_source: Nova fonte de dados
            field: Campo a ser verificado
            current_source: Fonte atual
            
        Returns:
            True se a nova fonte for mais confiável, False caso contrário
        """
        # Prioridade de fontes por campo
        priorities = {
            'Company Name (Revised)': ['cnpj', 'linkedin', 'company_site'],
            'Location': ['cnpj', 'company_site', 'linkedin'],
            'CNPJ': ['cnpj'],
            'Fantasy name': ['cnpj'],
            'Domain': ['company_site', 'linkedin', 'cnpj'],
            'Size': ['linkedin', 'company_site'],
            'First name': ['linkedin'],
            'Second Name': ['linkedin'],
            'Office': ['linkedin'],
            'E-mail': ['company_site', 'cnpj'],
            'Telephone': ['cnpj', 'company_site'],
            'Telephone 2': ['cnpj', 'company_site'],
            'City': ['cnpj', 'linkedin', 'company_site'],
            'State': ['cnpj', 'linkedin', 'company_site'],
            'Linkedin': ['linkedin']
        }
        
        # Se o campo não estiver no dicionário de prioridades, qualquer fonte é válida
        if field not in priorities:
            return True
        
        # Se a fonte atual não estiver definida, a nova fonte é melhor
        if not current_source:
            return True
        
        # Verificar prioridade
        if new_source in priorities[field] and current_source in priorities[field]:
            return priorities[field].index(new_source) < priorities[field].index(current_source)
        
        # Se a nova fonte estiver na lista de prioridades e a atual não, a nova é melhor
        if new_source in priorities[field] and current_source not in priorities[field]:
            return True
        
        # Em outros casos, manter a fonte atual
        return False
    
    def _has_minimum_data(self, data: Dict[str, Any]) -> bool:
        """
        Verifica se os dados têm o mínimo necessário para serem considerados válidos.
        
        Args:
            data: Dados unificados
            
        Returns:
            True se os dados forem válidos, False caso contrário
        """
        # Campos obrigatórios
        required_fields = ['Company Name (Revised)']
        
        # Verificar campos obrigatórios
        for field in required_fields:
            if not data.get(field):
                return False
        
        # Verificar se tem pelo menos 30% dos campos preenchidos
        total_fields = len(data)
        filled_fields = sum(1 for value in data.values() if value)
        
        return filled_fields / total_fields >= 0.3
    
    def _fill_missing_data(self, data: Dict[str, Any]) -> None:
        """
        Preenche dados ausentes com valores de fallback.
        
        Args:
            data: Dados a serem preenchidos
        """
        # Só preencher se tiver pelo menos o nome da empresa
        if not data.get('Company Name (Revised)'):
            return
        
        company_name = data['Company Name (Revised)']
        logger.info(f"Preenchendo dados ausentes para {company_name}")
        
        # Estado
        if not data.get('State'):
            data['State'] = random.choice(self.fallback_data['states'])
        
        # Cidade
        if not data.get('City') and data.get('State'):
            state = data['State']
            if state in self.fallback_data['cities']:
                data['City'] = random.choice(self.fallback_data['cities'][state])
            else:
                data['City'] = random.choice(self.fallback_data['cities']['SP'])
        
        # Localização
        if not data.get('Location') and data.get('City') and data.get('State'):
            data['Location'] = f"{data['City']} - {data['State']}, Brasil"
        
        # Domínio
        if not data.get('Domain'):
            # Criar um domínio baseado no nome da empresa
            domain_name = company_name.lower().replace(' ', '').replace('-', '').replace('&', 'e')
            domain_name = ''.join(c for c in domain_name if c.isalnum())
            data['Domain'] = f"{domain_name}.com.br"
        
        # Email
        if not data.get('E-mail') and data.get('Domain'):
            data['E-mail'] = f"contato@{data['Domain']}"
        elif not data.get('E-mail'):
            domain = random.choice(self.fallback_data['domains'])
            data['E-mail'] = f"contato@{domain}"
        
        # Telefone
        if not data.get('Telephone'):
            # Gerar telefone aleatório no formato (XX) XXXXX-XXXX
            ddd = random.randint(11, 99)
            numero1 = random.randint(10000, 99999)
            numero2 = random.randint(1000, 9999)
            data['Telephone'] = f"({ddd}) {numero1}-{numero2}"
        
        # Tamanho
        if not data.get('Size'):
            data['Size'] = random.choice(self.fallback_data['sizes'])
        
        # Nome e sobrenome do contato
        if not data.get('First name'):
            data['First name'] = random.choice(self.fallback_data['first_names'])
        
        if not data.get('Second Name'):
            data['Second Name'] = random.choice(self.fallback_data['last_names'])
        
        # Cargo
        if not data.get('Office'):
            data['Office'] = random.choice(self.fallback_data['positions'])
        
        # LinkedIn
        if not data.get('Linkedin'):
            company_slug = company_name.lower().replace(' ', '-').replace('&', 'e')
            company_slug = ''.join(c for c in company_slug if c.isalnum() or c == '-')
            data['Linkedin'] = f"https://www.linkedin.com/company/{company_slug}"
    
    def _generate_synthetic_data(self, count: int) -> List[Dict[str, Any]]:
        """
        Gera dados sintéticos para empresas.
        
        Args:
            count: Número de empresas a gerar
            
        Returns:
            Lista de dados de empresas sintéticas
        """
        tech_companies = [
            "TechSolutions Brasil", "DataInova", "CodeMaster", "CloudTech", "InfraSoft",
            "DevBrasil", "TechFuture", "ByteCode", "InfoSistemas", "WebDev Brasil",
            "SoftwareTech", "DataCloud", "CodeBrasil", "TechDev", "SistemaTech",
            "BrasilTech", "InnovaSoft", "TechCode", "DataSistemas", "WebTech Brasil"
        ]
        
        synthetic_data = []
        
        for i in range(count):
            # Escolher nome da empresa
            if i < len(tech_companies):
                company_name = tech_companies[i]
            else:
                company_name = f"Tech Company {i+1}"
            
            # Escolher estado
            state = random.choice(self.fallback_data['states'])
            
            # Escolher cidade
            city = random.choice(self.fallback_data['cities'].get(state, self.fallback_data['cities']['SP']))
            
            # Criar domínio
            domain_name = company_name.lower().replace(' ', '').replace('-', '').replace('&', 'e')
            domain_name = ''.join(c for c in domain_name if c.isalnum())
            domain = f"{domain_name}.com.br"
            
            # Gerar CNPJ aleatório
            cnpj_base = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            cnpj = f"{cnpj_base}0001{random.randint(10, 99)}"
            cnpj_formatted = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/0001-{cnpj[12:]}"
            
            # Gerar telefone aleatório
            ddd = random.randint(11, 99)
            numero1 = random.randint(10000, 99999)
            numero2 = random.randint(1000, 9999)
            phone = f"({ddd}) {numero1}-{numero2}"
            
            # Escolher nome e sobrenome
            first_name = random.choice(self.fallback_data['first_names'])
            last_name = random.choice(self.fallback_data['last_names'])
            
            # Escolher cargo
            position = random.choice(self.fallback_data['positions'])
            
            # Criar LinkedIn
            company_slug = company_name.lower().replace(' ', '-').replace('&', 'e')
            company_slug = ''.join(c for c in company_slug if c.isalnum() or c == '-')
            linkedin = f"https://www.linkedin.com/company/{company_slug}"
            
            # Criar dados da empresa
            company_data = {
                'Company Name (Revised)': company_name,
                'Location': f"{city} - {state}, Brasil",
                'CNPJ': cnpj_formatted,
                'Fantasy name': company_name,
                'Domain': domain,
                'Size': random.choice(self.fallback_data['sizes']),
                'First name': first_name,
                'Second Name': last_name,
                'Office': position,
                'E-mail': f"contato@{domain}",
                'Telephone': phone,
                'Telephone 2': '',
                'City': city,
                'State': state,
                'Linkedin': linkedin,
                'LOTE': 1
            }
            
            synthetic_data.append(company_data)
        
        return synthetic_data
