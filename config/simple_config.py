# -*- coding: utf-8 -*-
"""
Configuração Simples - Sistema de Agentes Jurídicos
Configurações essenciais para o novo sistema simples e eficaz
"""

# Palavras-chave para detecção de intenção
TRIAGE_KEYWORDS = [
    'similar', 'precedente', 'já analisado', 'existe', 'verificar',
    'consultar', 'checar', 'conferir', 'validar', 'confirmar'
]

PRECEDENT_KEYWORDS = [
    'precedente', 'entendimento', 'posicionamento', 'AGU', 'SIPEC',
    'consolidado', 'pacificado', 'sedimentado', 'firmado'
]

# Configurações de LLM
LLM_CONFIGS = {
    'default': {
        'provider': 'gemini',
        'model': 'gemini-2.5-flash',
        'temperature': 0.1,
        'max_tokens': 4000
    },
    'triage': {
        'provider': 'gemini',
        'model': 'gemini-2.5-flash',
        'temperature': 0.0,  # Mais determinístico
        'max_tokens': 2000
    },
    'research': {
        'provider': 'gemini',
        'model': 'gemini-2.5-flash',
        'temperature': 0.1,
        'max_tokens': 6000
    },
    'drafting': {
        'provider': 'gemini',
        'model': 'gemini-2.5-flash',
        'temperature': 0.2,  # Mais criativo
        'max_tokens': 8000
    },
    'precedent_analysis': {
        'provider': 'gemini',
        'model': 'gemini-2.5-flash',
        'temperature': 0.1,
        'max_tokens': 5000
    }
}

# Configurações de busca
SEARCH_CONFIG = {
    'initial_match_count': 5,
    'final_result_count': 3,
    'similarity_threshold': 0.3,
    'diversity_factor': 0.7
}

# Configurações de sistema
SYSTEM_CONFIG = {
    'output_dir': './respostas',
    'test_dir': './testes',
    'log_level': 'INFO',
    'max_workflow_time': 300  # 5 minutos
}

# Configurações de formatação
FORMAT_CONFIG = {
    'include_metadata': True,
    'include_confidence': True,
    'include_sources': True,
    'include_recommendations': True
}
