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

            this.mostrarResultados(data, duracao);
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

    mostrarResultados(data, duracao) {
        const resultados = document.getElementById('resultados');

        // Atualiza metadados
        document.getElementById('duracao').textContent = `${duracao}s`;
        document.getElementById('fontes').textContent = `${data.fontes || 0} fontes`;
        document.getElementById('workflow-id').textContent = data.workflow_id || 'N/A';

        // Atualiza conteúdo
        document.getElementById('resumo').innerHTML = this.formatarTexto(data.resumo || 'N/A');
        document.getElementById('resposta-completa').innerHTML = this.formatarTexto(data.resposta_completa || 'N/A');

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

        // Converte quebras de linha em <br>
        return texto.replace(/\n/g, '<br>');
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
        const consulta = {
            id: Date.now(),
            pergunta: pergunta,
            resposta: resposta.resposta_completa || resposta.resumo || 'N/A',
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

    loadQueryHistory() {
        try {
            const saved = localStorage.getItem('ia_jur_history');
            if (saved) {
                this.queryHistory = JSON.parse(saved);
                this.renderizarHistorico();
            }
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
            this.queryHistory = [];
        }
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
                    <span><i class="fas fa-clock"></i> ${consulta.duracao}s</span>
                    <span><i class="fas fa-database"></i> ${consulta.fontes} fontes</span>
                    <span><i class="fas fa-id-card"></i> ${consulta.workflow_id}</span>
                </div>
                <div class="historico-actions">
                    <button class="btn btn-secondary btn-sm" onclick="app.repetirConsulta(${consulta.id})">
                        <i class="fas fa-redo"></i> Repetir
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="app.copiarConsulta(${consulta.id})">
                        <i class="fas fa-copy"></i> Copiar
                    </button>
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

    clearQueryHistory() {
        if (confirm('Tem certeza que deseja limpar todo o histórico de consultas?')) {
            this.queryHistory = [];
            this.salvarHistorico();
            this.renderizarHistorico();
            this.mostrarNotificacao('Histórico limpo!', 'success');
        }
    }

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
`;
document.head.appendChild(style);

// Inicializa a aplicação quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.app = new IAJURApp();
});
