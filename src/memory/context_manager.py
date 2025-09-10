#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Memória Modular
Gerencia contexto de conversas de forma independente
"""

import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import deque
import logging


class ContextManager:
    """Gerenciador de contexto modular e independente"""

    def __init__(self, max_interactions: int = 10, memory_file: str = ".cursor/memory/chat_history.json"):
        self.max_interactions = max_interactions
        self.memory_file = memory_file
        self.logger = logging.getLogger(f"Memory.{self.__class__.__name__}")
        self._lock = asyncio.Lock()

        # Cria diretório se não existir
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)

        # Carrega histórico existente
        self._interactions = deque(maxlen=max_interactions)
        self._load_memory()

        self.logger.info(f"ContextManager inicializado (max: {max_interactions} interações)")

    def _load_memory(self):
        """Carrega memória do arquivo"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    interactions = data.get('interactions', [])

                    # Converte para deque
                    for interaction in interactions:
                        self._interactions.append(interaction)

                    self.logger.info(f"Memória carregada: {len(self._interactions)} interações")
        except Exception as e:
            self.logger.warning(f"Erro ao carregar memória: {e}")

    async def _save_memory(self):
        """Salva memória no arquivo"""
        try:
            async with self._lock:
                data = {
                    'interactions': list(self._interactions),
                    'last_updated': datetime.now().isoformat(),
                    'max_interactions': self.max_interactions
                }

                with open(self.memory_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                self.logger.debug(f"Memória salva: {len(self._interactions)} interações")
        except Exception as e:
            self.logger.error(f"Erro ao salvar memória: {e}")

    async def add_interaction(self, query: str, response: str, metadata: Optional[Dict] = None):
        """Adiciona nova interação ao contexto"""
        try:
            async with self._lock:
                interaction = {
                    'timestamp': datetime.now().isoformat(),
                    'query': query,
                    'response': response,
                    'metadata': metadata or {}
                }

                self._interactions.append(interaction)
                await self._save_memory()

                self.logger.info(f"Interação adicionada: {query[:50]}...")
        except Exception as e:
            self.logger.error(f"Erro ao adicionar interação: {e}")

    def get_context(self, current_query: str) -> Dict[str, Any]:
        """Retorna contexto relevante para a query atual"""
        try:
            if not self._interactions:
                return {'is_followup': False, 'context': None}

            # Verifica se é follow-up
            is_followup = self._is_followup_query(current_query)

            if is_followup:
                # Retorna contexto das últimas interações
                context = {
                    'is_followup': True,
                    'previous_interactions': list(self._interactions)[-3:],  # Últimas 3
                    'context_summary': self._generate_context_summary()
                }
                self.logger.info("Contexto de follow-up detectado")
                return context
            else:
                return {'is_followup': False, 'context': None}

        except Exception as e:
            self.logger.error(f"Erro ao obter contexto: {e}")
            return {'is_followup': False, 'context': None}

    def _is_followup_query(self, query: str) -> bool:
        """Detecta se a query é um follow-up"""
        followup_indicators = [
            'mais', 'detalhes', 'explicar', 'fundamentar', 'como', 'quando', 'onde',
            'por que', 'porque', 'qual', 'quais', 'isso', 'aquilo', 'sobre isso',
            'a respeito', 'relacionado', 'conexo', 'similar', 'parecido'
        ]

        query_lower = query.lower()

        # Verifica indicadores de follow-up
        for indicator in followup_indicators:
            if indicator in query_lower:
                return True

        # Verifica se a query é muito curta (possível follow-up)
        if len(query.split()) <= 3:
            return True

        return False

    def _generate_context_summary(self) -> str:
        """Gera resumo do contexto"""
        if not self._interactions:
            return ""

        summary = "Contexto das conversas anteriores:\n"
        for i, interaction in enumerate(list(self._interactions)[-3:], 1):
            summary += f"\n{i}. Pergunta: {interaction['query']}\n"
            summary += f"   Resposta: {interaction['response'][:200]}...\n"

        return summary

    async def clear_memory(self):
        """Limpa toda a memória"""
        try:
            async with self._lock:
                self._interactions.clear()
                await self._save_memory()
                self.logger.info("Memória limpa")
        except Exception as e:
            self.logger.error(f"Erro ao limpar memória: {e}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da memória"""
        return {
            'total_interactions': len(self._interactions),
            'max_interactions': self.max_interactions,
            'memory_file': self.memory_file,
            'last_interaction': self._interactions[-1]['timestamp'] if self._interactions else None
        }
