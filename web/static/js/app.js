// IA-JUR - Sistema de Pesquisa Jurídica Inteligente
class IAJURApp {
    constructor() {
        this.currentQuery = '';
        this.queryHistory = [];
        this.metrics = {
            totalConsultas: 0,
            consultasPesquisa: 0,
            tempoMedio: 0,
            fontesTotais: 0
        };

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupNavigation();
        this.loadQueryHistory();
        this.updateMetrics();
    }

    navegarParaConsulta() {
        // Navega para a seção de consulta
        const navLink = document.querySelector('[data-section="consulta"]');
        if (navLink) {
            navLink.click();
        }
    }

    setupEventListeners() {
        // Botões de consulta
        document.getElementById('btn-consulta').addEventListener('click', () => this.processarConsulta());
        document.getElementById('btn-limpar').addEventListener('click', () => this.limparConsulta());
        document.getElementById('btn-copiar').addEventListener('click', () => this.copiarResposta());
        document.getElementById('btn-download-txt').addEventListener('click', () => this.downloadTXT());
        document.getElementById('btn-nova-consulta').addEventListener('click', () => this.novaConsulta());
        // Botão "Limpar Conversa" removido - não é mais necessário
        document.getElementById('btn-tentar-novamente').addEventListener('click', () => this.processarConsulta());

        // Botões de histórico
        document.getElementById('btn-atualizar-historico').addEventListener('click', () => this.loadQueryHistory());
        document.getElementById('btn-limpar-historico').addEventListener('click', () => this.clearQueryHistory());

        // Botões de métricas
        document.getElementById('btn-atualizar-metricas').addEventListener('click', () => this.updateMetrics());

        // Enter no textarea
        document.getElementById('pergunta').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.processarConsulta();
            }
        });
    }

    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('.section');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();

                // Remove active de todos os links e seções
                navLinks.forEach(l => l.classList.remove('active'));
                sections.forEach(s => s.classList.remove('active'));

                // Adiciona active ao link clicado
                link.classList.add('active');

                // Mostra a seção correspondente
                const targetSection = link.getAttribute('data-section');
                document.getElementById(targetSection).classList.add('active');
            });
        });
    }

    async processarConsulta() {
        const pergunta = document.getElementById('pergunta').value.trim();

        if (!pergunta) {
            this.mostrarErro('Por favor, digite sua pergunta jurídica.');
            return;
        }

        this.currentQuery = pergunta;
        this.mostrarLoading();
        this.ocultarResultados();
        this.ocultarErro();

        const startTime = Date.now();

        try {
            const response = await fetch('/api/consulta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pergunta: pergunta })
            });

            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }

            const data = await response.json();
            const endTime = Date.now();
            const duracao = ((endTime - startTime) / 1000).toFixed(2);

            // Verifica se é follow-up baseado na resposta do servidor
            const isFollowup = data.is_followup || false;

            // Apenas mostra a última resposta na página principal
            this.mostrarResultados(data, duracao, isFollowup);
            // Salva no histórico para download posterior
            this.adicionarAoHistorico(pergunta, data, duracao);
            this.atualizarMetricas(duracao, data.fontes || 0);

        } catch (error) {
            console.error('Erro na consulta:', error);
            this.mostrarErro(`Erro ao processar consulta: ${error.message}`);
        } finally {
            this.ocultarLoading();
        }
    }

    mostrarLoading() {
        document.getElementById('loading').classList.remove('hidden');
    }

    ocultarLoading() {
        document.getElementById('loading').classList.add('hidden');
    }

    mostrarResultados(data, duracao, isFollowup = false) {
        const resultados = document.getElementById('resultados');

        // Atualiza metadados
        document.getElementById('duracao').textContent = `${duracao}s`;
        document.getElementById('fontes').textContent = `${data.fontes || 0} fontes`;
        document.getElementById('workflow-id').textContent = data.workflow_id || 'N/A';

        // Indicador de follow-up removido - não é necessário

        // Atualiza conteúdo - verifica se é JSON estruturado
        let conteudoResposta = '';

        if (typeof data.resposta_completa === 'object' && data.resposta_completa !== null) {
            // É JSON estruturado - renderiza de forma organizada
            conteudoResposta = this.renderizarRespostaEstruturada(data.resposta_completa);
        } else {
            // É texto simples - formata normalmente
            conteudoResposta = this.formatarTexto(data.resposta_completa || 'N/A');
        }

        document.getElementById('resposta-completa').innerHTML = conteudoResposta;

        // Seção de fontes removida - agora integrada na estrutura JSON

        resultados.classList.remove('hidden');
    }

    ocultarResultados() {
        document.getElementById('resultados').classList.add('hidden');
    }

    mostrarErro(mensagem) {
        const erro = document.getElementById('erro');
        document.getElementById('erro-mensagem').textContent = mensagem;
        erro.classList.remove('hidden');
    }

    ocultarErro() {
        document.getElementById('erro').classList.add('hidden');
    }

    formatarTexto(texto) {
        if (!texto) return 'N/A';

        // Remove símbolos de markdown e aplica formatação HTML
        let textoFormatado = texto;

        // Converte ## (títulos secundários) em negrito
        textoFormatado = textoFormatado.replace(/^## (.+)$/gm, '<strong>$1</strong>');

        // Converte # (títulos principais) em negrito
        textoFormatado = textoFormatado.replace(/^# (.+)$/gm, '<strong>$1</strong>');

        // Converte *** (negrito triplo) em negrito
        textoFormatado = textoFormatado.replace(/\*\*\*(.+?)\*\*\*/g, '<strong>$1</strong>');

        // Converte ** (negrito duplo) em negrito
        textoFormatado = textoFormatado.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Converte * (negrito simples) em negrito
        textoFormatado = textoFormatado.replace(/\*(.+?)\*/g, '<strong>$1</strong>');

        // Converte quebras de linha em <br>
        textoFormatado = textoFormatado.replace(/\n/g, '<br>');

        return textoFormatado;
    }

    renderizarRespostaEstruturada(jsonResponse) {
        let html = '';

        // Resposta Imediata
        if (jsonResponse.resposta_imediata) {
            html += `
                <div class="resposta-estruturada">
                    <div class="secao-resposta">
                        <h3 class="titulo-secao">${jsonResponse.resposta_imediata.titulo}</h3>
                        <div class="conteudo-secao">${this.formatarTexto(jsonResponse.resposta_imediata.conteudo)}</div>
                    </div>
                </div>
            `;
        }

        // Resumo Explicativo
        if (jsonResponse.resumo_explicativo) {
            html += `
                <div class="secao-resposta">
                    <h3 class="titulo-secao">${jsonResponse.resumo_explicativo.titulo}</h3>
                    <div class="conteudo-secao">${this.formatarTexto(jsonResponse.resumo_explicativo.conteudo)}</div>
                </div>
            `;
        }

        // Detalhamento Jurídico
        if (jsonResponse.detalhamento_juridico && jsonResponse.detalhamento_juridico.topicos) {
            html += `
                <div class="secao-resposta">
                    <h3 class="titulo-secao">${jsonResponse.detalhamento_juridico.titulo}</h3>
                    <div class="conteudo-secao">
            `;

            jsonResponse.detalhamento_juridico.topicos.forEach((topico, index) => {
                html += `
                    <div class="topico-juridico">
                        <h4 class="termo-chave">${topico.termo_chave}</h4>
                        <div class="analise-tecnica">${this.formatarTexto(topico.analise_tecnica)}</div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        }

        // Implicações Práticas
        if (jsonResponse.implicacoes_praticas) {
            html += `
                <div class="secao-resposta">
                    <h3 class="titulo-secao">${jsonResponse.implicacoes_praticas.titulo}</h3>
                    <div class="conteudo-secao">${this.formatarTexto(jsonResponse.implicacoes_praticas.conteudo)}</div>
                </div>
            `;
        }

        // Fontes Consultadas
        if (jsonResponse.fontes_consultadas && jsonResponse.fontes_consultadas.lista) {
            html += `
                <div class="secao-resposta">
                    <h3 class="titulo-secao">${jsonResponse.fontes_consultadas.titulo}</h3>
                    <div class="conteudo-secao">
                        <ul class="lista-fontes">
                            ${jsonResponse.fontes_consultadas.lista.map(fonte => `<li>${fonte}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }

        // Aviso Legal
        if (jsonResponse.aviso_legal) {
            html += `
                <div class="secao-resposta aviso-legal">
                    <div class="conteudo-secao aviso-texto">${this.formatarTexto(jsonResponse.aviso_legal)}</div>
                </div>
            `;
        }

        return html;
    }

    limparConsulta() {
        document.getElementById('pergunta').value = '';
        this.ocultarResultados();
        this.ocultarErro();
    }

    novaConsulta() {
        this.limparConsulta();
        // Foca no textarea
        document.getElementById('pergunta').focus();
    }

    copiarResposta() {
        const resposta = document.getElementById('resposta-completa').textContent;
        if (resposta && resposta !== 'N/A') {
            navigator.clipboard.writeText(resposta).then(() => {
                this.mostrarNotificacao('Resposta copiada para a área de transferência!', 'success');
            }).catch(() => {
                this.mostrarNotificacao('Erro ao copiar resposta', 'error');
            });
        }
    }

    async downloadTXT() {
        const pergunta = this.currentQuery;
        const resposta = document.getElementById('resposta-completa').textContent;

        if (!resposta || resposta === 'N/A') {
            this.mostrarNotificacao('Nenhuma resposta para download', 'error');
            return;
        }

        const conteudo = `IA-JUR - Consulta Jurídica\n` +
                        `========================\n\n` +
                        `Pergunta: ${pergunta}\n\n` +
                        `Resposta:\n${resposta}\n\n` +
                        `Data: ${new Date().toLocaleString('pt-BR')}\n` +
                        `Sistema: IA-JUR - Sistema de Pesquisa Jurídica Inteligente`;

        const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `consulta_ia_jur_${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        this.mostrarNotificacao('Download iniciado!', 'success');
    }

    adicionarAoHistorico(pergunta, resposta, duracao) {
        // Extrai conteúdo textual da resposta (JSON ou string)
        let respostaTexto = 'N/A';
        if (resposta.resposta_completa) {
            if (typeof resposta.resposta_completa === 'object') {
                // Se é JSON estruturado, extrai o conteúdo das seções principais
                const jsonResp = resposta.resposta_completa;
                respostaTexto = `CONSULTA: ${jsonResp.consulta_recebida || pergunta}\n\n`;
                
                if (jsonResp.resposta_imediata?.conteudo) {
                    respostaTexto += `RESPOSTA RÁPIDA:\n${jsonResp.resposta_imediata.conteudo}\n\n`;
                }
                
                if (jsonResp.resumo_explicativo?.conteudo) {
                    respostaTexto += `RESUMO EXPLICATIVO:\n${jsonResp.resumo_explicativo.conteudo}\n\n`;
                }
                
                if (jsonResp.detalhamento_juridico?.topicos) {
                    respostaTexto += `ANÁLISE TÉCNICA DETALHADA:\n`;
                    jsonResp.detalhamento_juridico.topicos.forEach(topico => {
                        respostaTexto += `\n${topico.termo_chave}:\n${topico.analise_tecnica}\n`;
                    });
                    respostaTexto += '\n';
                }
                
                if (jsonResp.implicacoes_praticas?.conteudo) {
                    respostaTexto += `IMPLICAÇÕES PRÁTICAS:\n${jsonResp.implicacoes_praticas.conteudo}\n\n`;
                }
                
                if (jsonResp.fontes_consultadas?.lista) {
                    respostaTexto += `FONTES CONSULTADAS:\n${jsonResp.fontes_consultadas.lista.join('\n')}\n\n`;
                }
                
                if (jsonResp.aviso_legal) {
                    respostaTexto += `AVISO LEGAL:\n${jsonResp.aviso_legal}`;
                }
            } else {
                // Se é string simples
                respostaTexto = resposta.resposta_completa;
            }
        }

        const consulta = {
            id: Date.now(),
            pergunta: pergunta,
            resposta: respostaTexto,
            duracao: duracao,
            fontes: resposta.fontes || 0,
            timestamp: new Date().toISOString(),
            workflow_id: resposta.workflow_id || 'N/A'
        };

        this.queryHistory.unshift(consulta);

        // Limita o histórico a 50 consultas
        if (this.queryHistory.length > 50) {
            this.queryHistory = this.queryHistory.slice(0, 50);
        }

        this.salvarHistorico();
        this.renderizarHistorico();
    }

    salvarHistorico() {
        try {
            localStorage.setItem('ia_jur_history', JSON.stringify(this.queryHistory));
        } catch (error) {
            console.error('Erro ao salvar histórico:', error);
        }
    }

    async loadQueryHistory() {
        try {
            // Carrega histórico do localStorage
            const saved = localStorage.getItem('ia_jur_history');
            if (saved) {
                this.queryHistory = JSON.parse(saved);
            }

            // Carrega arquivos TXT salvos automaticamente
            await this.carregarArquivosTxt();

            this.renderizarHistorico();
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
            this.queryHistory = [];
        }
    }

    async carregarArquivosTxt() {
        try {
            const response = await fetch('/api/arquivos-txt');
            if (response.ok) {
                const data = await response.json();

                // Adiciona arquivos TXT ao histórico
                data.arquivos.forEach(arquivo => {
                    // Verifica se já existe no histórico
                    const existe = this.queryHistory.find(h => h.arquivo_txt === arquivo.nome);
                    if (!existe) {
                        this.queryHistory.push({
                            id: Date.now() + Math.random(), // ID único
                            pergunta: this.extrairPerguntaDoNome(arquivo.nome),
                            resposta: 'Arquivo TXT salvo automaticamente',
                            duracao: 'N/A',
                            fontes: 'N/A',
                            timestamp: arquivo.data_modificacao,
                            workflow_id: 'N/A',
                            arquivo_txt: arquivo.nome,
                            tamanho: arquivo.tamanho,
                            data_criacao: arquivo.data_criacao
                        });
                    }
                });

                // Salva o histórico atualizado
                this.salvarHistorico();
            }
        } catch (error) {
            console.error('Erro ao carregar arquivos TXT:', error);
        }
    }

    extrairPerguntaDoNome(nomeArquivo) {
        // Extrai a pergunta do nome do arquivo
        // Formato: (palavras_chave_YYYYMMDD_HHMMSS).txt
        const match = nomeArquivo.match(/\(([^)]+)\)\.txt/);
        if (match) {
            return match[1].replace(/_/g, ' ').substring(0, 50) + '...';
        }
        return 'Consulta salva automaticamente';
    }

    renderizarHistorico() {
        const historicoLista = document.getElementById('historico-lista');

        if (this.queryHistory.length === 0) {
            historicoLista.innerHTML = '<p class="text-center">Nenhuma consulta no histórico.</p>';
            return;
        }

        const html = this.queryHistory.map(consulta => `
            <div class="historico-item" data-id="${consulta.id}">
                <div class="historico-header">
                    <h4>${this.truncarTexto(consulta.pergunta, 80)}</h4>
                    <span class="historico-timestamp">${new Date(consulta.timestamp).toLocaleString('pt-BR')}</span>
                </div>
                <div class="historico-meta">
                    ${consulta.arquivo_txt ?
                        `<span><i class="fas fa-file-alt"></i> ${(consulta.tamanho / 1024).toFixed(1)} KB</span>
                         <span><i class="fas fa-save"></i> Salvo automaticamente</span>` :
                        `<span><i class="fas fa-clock"></i> ${consulta.duracao}s</span>
                         <span><i class="fas fa-database"></i> ${consulta.fontes} fontes</span>
                         <span><i class="fas fa-id-card"></i> ${consulta.workflow_id}</span>`
                    }
                </div>
                <div class="historico-actions">
                    <button class="btn btn-primary btn-sm" onclick="app.downloadConsulta(${consulta.id})">
                        <i class="fas fa-download"></i> Download TXT
                    </button>
                    ${!consulta.arquivo_txt ?
                        `<button class="btn btn-secondary btn-sm" onclick="app.repetirConsulta(${consulta.id})">
                            <i class="fas fa-redo"></i> Repetir
                        </button>
                        <button class="btn btn-secondary btn-sm" onclick="app.copiarConsulta(${consulta.id})">
                            <i class="fas fa-copy"></i> Copiar
                        </button>` : ''
                    }
                </div>
            </div>
        `).join('');

        historicoLista.innerHTML = html;
    }

    truncarTexto(texto, maxLength) {
        if (texto.length <= maxLength) return texto;
        return texto.substring(0, maxLength) + '...';
    }

    repetirConsulta(id) {
        const consulta = this.queryHistory.find(c => c.id === id);
        if (consulta) {
            document.getElementById('pergunta').value = consulta.pergunta;
            this.processarConsulta();
        }
    }

    copiarConsulta(id) {
        const consulta = this.queryHistory.find(c => c.id === id);
        if (consulta) {
            navigator.clipboard.writeText(consulta.pergunta).then(() => {
                this.mostrarNotificacao('Pergunta copiada!', 'success');
            }).catch(() => {
                this.mostrarNotificacao('Erro ao copiar pergunta', 'error');
            });
        }
    }

    downloadConsulta(id) {
        const consulta = this.queryHistory.find(c => c.id === id);
        if (consulta) {
            // Se é um arquivo TXT salvo automaticamente, usa o endpoint do backend
            if (consulta.arquivo_txt) {
                const link = document.createElement('a');
                link.href = `/api/download-txt/${consulta.arquivo_txt}`;
                link.download = consulta.arquivo_txt;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                this.mostrarNotificacao('Download do arquivo TXT iniciado!', 'success');
            } else {
                // Se é uma consulta do localStorage, gera o arquivo
                const conteudo = `IA-JUR - Consulta Jurídica\n` +
                                `========================\n\n` +
                                `Pergunta: ${consulta.pergunta}\n\n` +
                                `Resposta:\n${consulta.resposta}\n\n` +
                                `Data: ${new Date(consulta.timestamp).toLocaleString('pt-BR')}\n` +
                                `Duração: ${consulta.duracao}s\n` +
                                `Fontes: ${consulta.fontes}\n` +
                                `Workflow ID: ${consulta.workflow_id}\n` +
                                `Sistema: IA-JUR - Sistema de Pesquisa Jurídica Inteligente`;

                const blob = new Blob([conteudo], { type: 'text/plain;charset=utf-8' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `consulta_ia_jur_${new Date(consulta.timestamp).toISOString().slice(0, 10)}_${id}.txt`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                this.mostrarNotificacao('Download iniciado!', 'success');
            }
        }
    }

    clearQueryHistory() {
        if (confirm('Tem certeza que deseja limpar todo o histórico de consultas?')) {
            this.queryHistory = [];
            this.salvarHistorico();
            this.renderizarHistorico();
            this.mostrarNotificacao('Histórico limpo!', 'success');
        }
    }

    // Métodos para gerenciar histórico de conversas
    // Funções de conversa removidas - não são mais necessárias
    // O histórico agora é gerenciado apenas na página Histórico

    atualizarMetricas(duracao, fontes) {
        this.metrics.totalConsultas++;
        this.metrics.consultasPesquisa++;
        this.metrics.fontesTotais += fontes;

        // Calcula tempo médio
        const tempos = this.queryHistory.map(c => parseFloat(c.duracao));
        this.metrics.tempoMedio = (tempos.reduce((a, b) => a + b, 0) / tempos.length).toFixed(2);

        this.renderizarMetricas();
    }

    async updateMetrics() {
        try {
            const response = await fetch('/api/metricas');
            if (response.ok) {
                const data = await response.json();
                this.metrics = { ...this.metrics, ...data };
            }
        } catch (error) {
            console.error('Erro ao atualizar métricas:', error);
        }

        this.renderizarMetricas();
    }

    renderizarMetricas() {
        document.getElementById('total-consultas').textContent = this.metrics.totalConsultas;
        document.getElementById('consultas-pesquisa').textContent = this.metrics.consultasPesquisa;
        document.getElementById('tempo-medio').textContent = `${this.metrics.tempoMedio}s`;
        document.getElementById('fontes-totais').textContent = this.metrics.fontesTotais;
    }

    mostrarNotificacao(mensagem, tipo = 'info') {
        // Cria notificação simples
        const notificacao = document.createElement('div');
        notificacao.className = `notificacao notificacao-${tipo}`;
        notificacao.innerHTML = `
            <i class="fas fa-${tipo === 'success' ? 'check-circle' : tipo === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${mensagem}</span>
        `;

        document.body.appendChild(notificacao);

        // Remove após 3 segundos
        setTimeout(() => {
            if (notificacao.parentNode) {
                notificacao.parentNode.removeChild(notificacao);
            }
        }, 3000);
    }
}

// Estilos para notificações
const style = document.createElement('style');
style.textContent = `
    .notificacao {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    }

    .notificacao-success {
        background: #28a745;
    }

    .notificacao-error {
        background: #dc3545;
    }

    .notificacao-info {
        background: #17a2b8;
    }

    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    .historico-item {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }

    .historico-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .historico-header h4 {
        color: #333;
        margin: 0;
        flex: 1;
    }

    .historico-timestamp {
        color: #666;
        font-size: 0.9rem;
    }

    .historico-resposta {
        margin-bottom: 1rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }

    .historico-resposta strong {
        color: #333;
        display: block;
        margin-bottom: 0.5rem;
    }

    .historico-resposta-texto {
        color: #555;
        line-height: 1.5;
        font-size: 0.95rem;
        max-height: 400px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    .historico-meta {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }

    .historico-meta span {
        color: #666;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    .historico-actions {
        display: flex;
        gap: 0.5rem;
    }

    .btn-sm {
        padding: 8px 16px;
        font-size: 0.9rem;
    }

    .text-center {
        text-align: center;
        color: #666;
        padding: 2rem;
    }

    /* Estilos para histórico de conversas */
    .conversa-historico {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }

    .conversa-historico h3 {
        color: #495057;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .conversa-lista {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .conversa-item {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }

    .conversa-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.12);
    }

    .conversa-item.followup {
        border-left-color: #28a745;
        background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%);
    }

    .conversa-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #e9ecef;
    }

    .conversa-tipo {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        color: #667eea;
        font-size: 0.9rem;
    }

    .conversa-item.followup .conversa-tipo {
        color: #28a745;
    }

    .conversa-timestamp {
        color: #6c757d;
        font-size: 0.85rem;
    }

    .conversa-pergunta {
        margin-bottom: 1rem;
    }

    .conversa-pergunta strong {
        color: #495057;
        font-size: 0.9rem;
        display: block;
        margin-bottom: 0.5rem;
    }

    .conversa-pergunta p {
        color: #6c757d;
        margin: 0;
        font-style: italic;
        line-height: 1.4;
    }

    .conversa-resposta {
        margin-bottom: 1rem;
    }

    .conversa-resposta strong {
        color: #495057;
        font-size: 0.9rem;
        display: block;
        margin-bottom: 0.5rem;
    }

    .conversa-resposta-texto {
        color: #343a40;
        line-height: 1.5;
        background: #f8f9fa;
        padding: 0.75rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }

    .conversa-meta {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .conversa-meta span {
        color: #6c757d;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 5px;
    }

    /* Indicador de follow-up no resultado */
    .meta-item {
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }

    #followup-indicator {
        background: #28a745;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Estilos para textos formatados */
    .resposta-completa strong {
        color: #2c3e50;
        font-weight: 700;
        font-size: 1.05em;
    }

    .resposta-completa {
        line-height: 1.6;
        color: #34495e;
    }

    .resposta-completa strong:first-child {
        color: #1a252f;
        font-size: 1.1em;
        display: block;
        margin-bottom: 0.5rem;
        padding-bottom: 0.25rem;
        border-bottom: 2px solid #e9ecef;
    }
`;
document.head.appendChild(style);

// Inicializa a aplicação quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.app = new IAJURApp();
});
