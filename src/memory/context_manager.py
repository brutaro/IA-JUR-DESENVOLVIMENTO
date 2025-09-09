#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Manager - Gerenciador de Contexto e Memória
Implementa sistema de memória para preservar contexto entre interações
"""

import json
import logging
import threading
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re

class ContextManager:
    """Gerenciador de contexto com memória de conversação"""

    def __init__(self, max_context_size: int = 10, memory_file: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.max_context_size = max_context_size

        # Usa deque para eficiência em operações de append/popleft
        self.context_window = deque(maxlen=max_context_size)

        # Thread lock para operações thread-safe
        self._lock = threading.Lock()

        # Arquivo de persistência
        self.memory_file = memory_file or Path(".cursor/memory/chat_history.json")
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        # Carrega histórico existente
        self._load_memory()

        # Padrões para detectar follow-ups
        self.followup_patterns = [
            r'\b(e|mas|porém|contudo|entretanto|no entanto)\b',
            r'\b(também|além disso|adicionalmente|outro|outra)\b',
            r'\b(como|quando|onde|por que|porque)\b',
            r'\b(qual|quais|quem|o que|que)\b',
            r'\b(pode|deve|é possível|é permitido)\b',
            r'\b(exemplo|exemplos|caso|casos)\b',
            r'\b(detalhe|detalhes|mais|maior|menor)\b',
            r'\b(sobre|acerca|relativo|relacionado)\b'
        ]

        self.logger.info(f"ContextManager inicializado com janela de {max_context_size} interações")

    def _load_memory(self) -> None:
        """Carrega memória persistente do arquivo"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)

                # Carrega as últimas interações no contexto
                for entry in history[-self.max_context_size:]:
                    self.context_window.append({
                        'user': entry.get('user', ''),
                        'assistant': entry.get('assistant', ''),
                        'timestamp': entry.get('timestamp', ''),
                        'context_keywords': self._extract_context_keywords(entry.get('user', ''))
                    })

                self.logger.info(f"Memória carregada: {len(self.context_window)} interações")
        except Exception as e:
            self.logger.error(f"Erro ao carregar memória: {e}")

    def _save_memory(self) -> None:
        """Salva memória atual no arquivo"""
        try:
            with self._lock:
                # Converte deque para lista para serialização
                history = list(self.context_window)

                with open(self.memory_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)

                self.logger.debug(f"Memória salva: {len(history)} interações")
        except Exception as e:
            self.logger.error(f"Erro ao salvar memória: {e}")

    def _extract_context_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave relevantes para contexto"""
        # Remove pontuação e converte para minúsculas
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())

        # Stopwords jurídicas
        stopwords = {
            'sobre', 'acerca', 'quanto', 'como', 'quando', 'onde', 'por', 'para',
            'em', 'de', 'da', 'do', 'das', 'dos', 'na', 'no', 'nas', 'nos',
            'a', 'o', 'as', 'os', 'e', 'ou', 'mas', 'que', 'se', 'é', 'foi',
            'será', 'pode', 'deve', 'tem', 'há', 'sua', 'seu', 'suas', 'seus',
            'qual', 'quais', 'quem', 'o', 'a', 'um', 'uma', 'uns', 'umas'
        }

        # Extrai palavras significativas
        words = clean_text.split()
        keywords = [word for word in words if len(word) > 2 and word not in stopwords]

        return keywords[:10]  # Limita a 10 palavras-chave

    def is_followup_question(self, new_query: str) -> Tuple[bool, float]:
        """
        Detecta se a nova query é um follow-up baseado em:
        1. Padrões linguísticos
        2. Palavras-chave em comum com contexto anterior
        3. Referências implícitas
        """
        if not self.context_window:
            return False, 0.0

        new_query_lower = new_query.lower()
        new_keywords = set(self._extract_context_keywords(new_query))

        # Verifica padrões de follow-up
        followup_score = 0.0

        # 1. Padrões linguísticos (peso: 0.4)
        pattern_matches = 0
        for pattern in self.followup_patterns:
            if re.search(pattern, new_query_lower):
                pattern_matches += 1

        if pattern_matches > 0:
            followup_score += 0.4 * min(pattern_matches / 3, 1.0)

        # 2. Palavras-chave em comum (peso: 0.4)
        if new_keywords:
            # Compara com as últimas 3 interações
            recent_keywords = set()
            for entry in list(self.context_window)[-3:]:
                recent_keywords.update(entry.get('context_keywords', []))

            if recent_keywords:
                keyword_overlap = len(new_keywords.intersection(recent_keywords))
                keyword_ratio = keyword_overlap / len(new_keywords)
                followup_score += 0.4 * keyword_ratio

        # 3. Referências implícitas (peso: 0.2)
        implicit_refs = [
            'isso', 'isto', 'aquilo', 'ele', 'ela', 'eles', 'elas',
            'o mesmo', 'a mesma', 'os mesmos', 'as mesmas',
            'anterior', 'anteriormente', 'antes', 'depois'
        ]

        implicit_matches = sum(1 for ref in implicit_refs if ref in new_query_lower)
        if implicit_matches > 0:
            followup_score += 0.2 * min(implicit_matches / 2, 1.0)

        is_followup = followup_score >= 0.3
        return is_followup, followup_score

    def get_context_for_query(self, query: str) -> Dict[str, Any]:
        """
        Retorna contexto relevante para a query atual
        """
        is_followup, followup_score = self.is_followup_question(query)

        context = {
            'is_followup': is_followup,
            'followup_score': followup_score,
            'context_window_size': len(self.context_window),
            'relevant_history': []
        }

        if is_followup and self.context_window:
            # Retorna as últimas 3 interações como contexto
            recent_entries = list(self.context_window)[-3:]
            context['relevant_history'] = [
                {
                    'user': entry['user'],
                    'assistant': entry['assistant'][:500] + '...' if len(entry['assistant']) > 500 else entry['assistant'],
                    'timestamp': entry['timestamp']
                }
                for entry in recent_entries
            ]

            self.logger.info(f"Follow-up detectado (score: {followup_score:.2f}) - contexto de {len(recent_entries)} interações")

        return context

    def add_interaction(self, user_query: str, assistant_response: str) -> None:
        """
        Adiciona nova interação ao contexto
        """
        try:
            with self._lock:
                # Cria entrada da interação
                entry = {
                    'user': user_query,
                    'assistant': assistant_response,
                    'timestamp': datetime.now().isoformat(),
                    'context_keywords': self._extract_context_keywords(user_query)
                }

                # Adiciona ao contexto (deque automaticamente remove o mais antigo se exceder maxlen)
                self.context_window.append(entry)

                self.logger.info(f"Interação adicionada ao contexto (total: {len(self.context_window)})")

            # Salva no arquivo fora do lock para evitar deadlock
            self._save_memory()

        except Exception as e:
            self.logger.error(f"Erro ao adicionar interação: {e}")

    def get_context_summary(self) -> Dict[str, Any]:
        """Retorna resumo do contexto atual"""
        return {
            'total_interactions': len(self.context_window),
            'max_context_size': self.max_context_size,
            'memory_file': str(self.memory_file),
            'recent_topics': [
                entry['context_keywords'][:3]
                for entry in list(self.context_window)[-3:]
            ]
        }

    def clear_context(self) -> None:
        """Limpa todo o contexto"""
        with self._lock:
            self.context_window.clear()
            self._save_memory()
            self.logger.info("Contexto limpo")

    def get_recent_queries(self, limit: int = 5) -> List[str]:
        """Retorna as queries mais recentes"""
        return [entry['user'] for entry in list(self.context_window)[-limit:]]
