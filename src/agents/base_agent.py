#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Agent - Classe base para agentes customizados
Arquitetura sem CrewAI para análises jurídicas profundas
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentMessage:
    """Estrutura para mensagens entre agentes"""
    sender: str
    recipient: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    message_type: str  # 'query', 'response', 'context', 'error'

@dataclass
class AgentContext:
    """Contexto compartilhado entre agentes"""
    session_id: str
    original_query: str
    current_stage: str
    accumulated_context: Dict[str, Any]
    messages_history: List[AgentMessage]
    metadata: Dict[str, Any]

class BaseAgent(ABC):
    """Classe base para todos os agentes"""
    
    def __init__(self, 
                 name: str, 
                 role: str, 
                 llm_config: Dict[str, Any],
                 tools: Optional[List] = None):
        self.name = name
        self.role = role
        self.llm_config = llm_config
        self.tools = tools or []
        self.context: Optional[AgentContext] = None
        self.logger = logging.getLogger(f"Agent.{name}")
        
    def set_context(self, context: AgentContext):
        """Define o contexto compartilhado"""
        self.context = context
        
    def send_message(self, recipient: str, content: str, 
                    message_type: str = 'response', 
                    metadata: Optional[Dict] = None) -> AgentMessage:
        """Envia mensagem para outro agente"""
        message = AgentMessage(
            sender=self.name,
            recipient=recipient,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now(),
            message_type=message_type
        )
        
        if self.context:
            self.context.messages_history.append(message)
            
        return message
    
    def update_context(self, key: str, value: Any):
        """Atualiza o contexto compartilhado"""
        if self.context:
            self.context.accumulated_context[key] = value
            self.logger.info(f"Contexto atualizado: {key}")
    
    def get_context_value(self, key: str, default: Any = None) -> Any:
        """Recupera valor do contexto"""
        if self.context:
            return self.context.accumulated_context.get(key, default)
        return default
    
    @abstractmethod
    async def process(self, input_data: Union[str, Dict]) -> Dict[str, Any]:
        """Método principal de processamento do agente"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Retorna lista de capacidades do agente"""
        pass
    
    def log_activity(self, activity: str, details: Optional[Dict] = None):
        """Registra atividade do agente"""
        log_entry = {
            'agent': self.name,
            'activity': activity,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.logger.info(f"Atividade: {activity}")
        
        # Adiciona ao contexto se disponível
        if self.context:
            if 'activity_log' not in self.context.accumulated_context:
                self.context.accumulated_context['activity_log'] = []
            self.context.accumulated_context['activity_log'].append(log_entry)

class AgentOrchestrator:
    """Orquestrador para coordenar múltiplos agentes"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.context: Optional[AgentContext] = None
        self.logger = logging.getLogger("AgentOrchestrator")
        
    def register_agent(self, agent: BaseAgent):
        """Registra um agente no orquestrador"""
        self.agents[agent.name] = agent
        if self.context:
            agent.set_context(self.context)
        self.logger.info(f"Agente registrado: {agent.name}")
    
    def create_session(self, query: str, session_id: Optional[str] = None) -> str:
        """Cria uma nova sessão de trabalho"""
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        self.context = AgentContext(
            session_id=session_id,
            original_query=query,
            current_stage="initialization",
            accumulated_context={},
            messages_history=[],
            metadata={}
        )
        
        # Propaga contexto para todos os agentes
        for agent in self.agents.values():
            agent.set_context(self.context)
            
        self.logger.info(f"Sessão criada: {session_id}")
        return session_id
    
    async def execute_workflow(self, workflow_steps: List[Dict]) -> Dict[str, Any]:
        """Executa um workflow definido"""
        results = {}
        
        for step in workflow_steps:
            agent_name = step['agent']
            input_data = step.get('input', {})
            
            if agent_name not in self.agents:
                raise ValueError(f"Agente não encontrado: {agent_name}")
                
            agent = self.agents[agent_name]
            
            # Atualiza estágio atual
            if self.context:
                self.context.current_stage = step.get('stage', agent_name)
            
            self.logger.info(f"Executando: {agent_name}")
            
            try:
                result = await agent.process(input_data)
                results[agent_name] = result
                
                # Atualiza contexto com resultado
                agent.update_context(f"{agent_name}_result", result)
                
            except Exception as e:
                self.logger.error(f"Erro em {agent_name}: {e}")
                results[agent_name] = {'error': str(e)}
                
        return results
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Retorna resumo da sessão atual"""
        if not self.context:
            return {}
            
        return {
            'session_id': self.context.session_id,
            'original_query': self.context.original_query,
            'current_stage': self.context.current_stage,
            'messages_count': len(self.context.messages_history),
            'context_keys': list(self.context.accumulated_context.keys()),
            'agents_involved': list(self.agents.keys())
        }