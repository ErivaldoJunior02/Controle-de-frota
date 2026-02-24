CREATE TABLE IF NOT EXISTS usuarios(
	id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    perfil ENUM("ADMINISTRADOR", "GERENTE", "MECANICO", "SQSMS", "RH", "SUPERVISOR", "ALMOXARIFADO", "USUARIO") DEFAULT "USUARIO",
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_login DATETIME
);

CREATE TABLE IF NOT EXISTS setor (
	id_setor INT PRIMARY KEY AUTO_INCREMENT,
    atividade VARCHAR(255) NOT NULL UNIQUE,
    criticidade ENUM("CRITICO", "MODERADO", "NAO_CRITICO") DEFAULT "MODERADO",
    
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS documentos_necessarios (
	id_doc_necessario INT AUTO_INCREMENT PRIMARY KEY,
    id_setor INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(255),
    obrigatorio BOOLEAN DEFAULT TRUE,
    
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_setor) REFERENCES setor(id_setor),
    FOREIGN KEY (created_by) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS fornecedores (
	id_fornecedor INT AUTO_INCREMENT PRIMARY KEY,
    cnpj VARCHAR(255) NOT NULL UNIQUE,
    nome_empresarial VARCHAR(255),
    categoria ENUM("MECANICA", "PINTURA", "SIDERURGICA", "ABASTECIMENTO", "LIMPEZA", "ADMINISTRATIVO"),
    logradouro VARCHAR(255),
    numero VARCHAR(255),
    complemento VARCHAR(255),
    bairro VARCHAR(255),
    municipio VARCHAR(255),
    uf VARCHAR(255),
    cep VARCHAR(255),
    telefone VARCHAR(255),
    email VARCHAR(255),
    status_aptidao ENUM("APTO", "SEM_DOCUMENTACAO", "NAO_APTO", "INATIVO") DEFAULT "NAO_APTO",
    
    register_by INT NOT NULL,
    register_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (register_by) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS fornecedor_setor (
	id_fornecedor INT NOT NULL,
    id_setor INT NOT NULL,
    
    PRIMARY KEY (id_fornecedor, id_setor),
    
    FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE CASCADE,
    FOREIGN KEY (id_setor) REFERENCES setor(id_setor) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS documentos_setor (
	id_documento INT AUTO_INCREMENT PRIMARY KEY,
    id_setor INT NOT NULL,
    id_fornecedor INT NOT NULL,
    nome VARCHAR(255),
    caminho VARCHAR(500),
    tipo VARCHAR(255),
    data_upload DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    register_by INT NOT NULL,
    FOREIGN KEY (id_fornecedor, id_setor) REFERENCES fornecedor_setor(id_fornecedor, id_setor) ON DELETE CASCADE,
    FOREIGN KEY (register_by) REFERENCES usuarios(id_usuario)
);

SELECT d.*, s.* FROM documentos_necessarios d JOIN setor s ON s.id_setor = d.id_setor WHERE d.id_setor = 1;

CREATE TABLE IF NOT EXISTS vendedor_fornecedor (
	id_vendedor INT AUTO_INCREMENT PRIMARY KEY,
    id_fornecedor INT NOT NULL,
    nome VARCHAR(255),
    contato VARCHAR(255),
    status_vendedor ENUM("ATIVO", "FERIAS", "DESLIGADO"),
    
    FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS itens (
	id_item INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    codigo_interno VARCHAR(255) UNIQUE NOT NULL,
    unidade_medida ENUM("METROS", "PAR", "LITROS", "UNIDADE", "CAIXA", "RESMA") DEFAULT "UNIDADE",
    ultimo_preco DECIMAL(10, 2),
    
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES usuarios(id_usuario)
);

SELECT * FROM itens;

SET SQL_SAFE_UPDATES = 0;
UPDATE itens
SET ultimo_preco = ROUND(5 + (RAND() * 95), 2)
WHERE ultimo_preco IS NULL;
SET SQL_SAFE_UPDATES = 1;

CREATE TABLE IF NOT EXISTS item_fornecedor (
	id_item INT NOT NULL,
    id_fornecedor INT NOT NULL,
    valor_unitario DECIMAL(10, 2) NOT NULL,
    
    PRIMARY KEY (id_item, id_fornecedor),
    
    FOREIGN KEY (id_item) REFERENCES itens(id_item) ON DELETE RESTRICT,
    FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS estoque (
    id_item INT PRIMARY KEY,
    quantidade_atual FLOAT,
    quantidade_minima FLOAT,
    
    add_by INT NOT NULL,
    add_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_item) REFERENCES itens(id_item) ON DELETE RESTRICT,
    FOREIGN KEY (add_by) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS movimentacao_estoque (
	id_movimentacao INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM("ENTRADA", "SAIDA", "AJUSTE", "TROCA"),
    id_os INT NULL,
    origem VARCHAR(255),
    destino VARCHAR(255),
    solicitante VARCHAR(255),
    descricao TEXT,
    
    register_by INT NOT NULL,
    register_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (register_by) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    FOREIGN KEY (id_os) REFERENCES ordem_servico (id_os)
);

SELECT * FROM movimentacao_estoque;

CREATE TABLE IF NOT EXISTS itens_movimentacao (
	id_item INT NOT NULL,
    id_movimentacao INT NOT NULL,
    quantidade FLOAT NOT NULL,
    
    PRIMARY KEY(id_item, id_movimentacao),
	
    FOREIGN KEY (id_item) REFERENCES itens(id_item) ON DELETE RESTRICT,
    FOREIGN KEY (id_movimentacao) REFERENCES movimentacao_estoque(id_movimentacao) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS veiculos (
	id_veiculo INT AUTO_INCREMENT PRIMARY KEY,
    placa VARCHAR(255) NOT NULL UNIQUE,
    equipamento ENUM("MUNCK", "CAVALO_MECANICO", "CAVALO_MUNCK", "GUINDASTE", "POLIGUINDASTE", "TANQUE", "VACUO", "PIPA", "CARRETA", "EMPILHADEIRA", "PA_CARREGADEIRA", "PTA", "VAN", "GOL", "SPIN", "MOBI") NOT NULL,
    modelo VARCHAR(255),
    ano INT NOT NULL,
    chassi VARCHAR(255) NOT NULL UNIQUE,
    renavam VARCHAR(255) NOT NULL UNIQUE,
    regime VARCHAR(255) NOT NULL,
    km_ultima_revisao FLOAT NULL,
    km_atual FLOAT DEFAULT 0,
    status_atividade ENUM("EM_OPERACAO", "FORA_DE_OPERACAO", "EM_MANUTENCAO") DEFAULT "EM_OPERACAO",
    
    register_by INT NOT NULL,
    register_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (register_by) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);

INSERT INTO veiculos (placa, equipamento, modelo, ano, chassi, renavam, regime, km_ultima_revisao, km_atual, status_atividade, register_by) VALUES ("SRF7G85", "MUNCK", "VW", 2025, "12391238123", "ma2m51sm12m31m", "720", 25000, "35000", "EM_OPERACAO", 1);

CREATE TABLE IF NOT EXISTS documentos_veiculo (
	id_documento INT AUTO_INCREMENT PRIMARY KEY,
    id_veiculo INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    emissao DATE,
    validade DATE NOT NULL,
    caminho VARCHAR(500),
    tipo ENUM("CERTIFICADO", "VISTORIA", "LICENCA", "SEGURO", "OUTRO") DEFAULT "CERTIFICADO",
    data_upload DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    register_by INT NOT NULL,
    
    FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo) ON DELETE RESTRICT,
    FOREIGN KEY (register_by) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ordem_servico (
	id_os INT AUTO_INCREMENT PRIMARY KEY,
    numero_os VARCHAR(255) NOT NULL UNIQUE,
    id_veiculo INT NOT NULL,
    local_manutencao VARCHAR(255),
    km_atual FLOAT,
    tipo ENUM("PREVENTIVA", "CORRETIVA_PLANEJADA", "CORRETIVA_NAO_PLANEJADA", "ABASTECIMENTO", "REVISAO"),
    oficina ENUM("OFICINA_INTERNA", "OFICINA_EXTERNA"),
    responsavel VARCHAR(255),
    data_saida DATETIME NOT NULL,
    data_previsao DATETIME NOT NULL,
    data_retorno DATETIME,
    custo DECIMAL (10, 2),
    status_os ENUM("ABERTA", "EM_EXECUCAO", "FINALIZADA", "CANCELADA"),
    descricao TEXT,
    
    opened_by INT NOT NULL,
    
    FOREIGN KEY (id_veiculo) REFERENCES veiculos(id_veiculo),
    FOREIGN KEY (opened_by) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS itens_os (
	id_os INT NOT NULL,
	id_item INT NOT NULL,
	quantidade_previsao FLOAT NOT NULL,
    valor_unitario_previsto DECIMAL (10, 2) NOT NULL,
    valor_total_previsto DECIMAL (10, 2) NOT NULL,
    status_item ENUM("UTILIZADO", "NAO_UTILIZADO"),
    
    PRIMARY KEY (id_item, id_os),
    
    FOREIGN KEY (id_os) REFERENCES ordem_servico (id_os),
    FOREIGN KEY (id_item) REFERENCES itens(id_item)
);

ALTER TABLE itens_os ADD PRIMARY KEY(id_item, id_os);

SELECT * FROM itens_os;

CREATE TABLE IF NOT EXISTS manutencoes (
	id_manutencao INT AUTO_INCREMENT PRIMARY KEY,
    id_os INT NOT NULL,
    servico VARCHAR(255) NOT NULL,
    data_inicio DATETIME NOT NULL,
    data_fim DATETIME NOT NULL,
    custo_total DECIMAL (10, 2) NOT NULL,
    
    created_by INT NOT NULL,
    
    FOREIGN KEY (id_os) REFERENCES ordem_servico(id_os) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS itens_manutencao (
	id_item INT NOT NULL,
    id_manutencao INT NOT NULL,
    quantidade FLOAT NOT NULL,
    valor_unitario DECIMAL (10, 2) NOT NULL,
    valor_total DECIMAL (10, 2) NOT NULL,
    
    PRIMARY KEY(id_item, id_manutencao),
    
    FOREIGN KEY (id_item) REFERENCES itens(id_item),
    FOREIGN KEY (id_manutencao) REFERENCES manutencoes(id_manutencao)
);

INSERT INTO manutencoes (id_os, servico, data_inicio, data_fim, custo_total, created_by)
VALUES
(1, 'Troca de óleo', '2026-02-20 08:00:00', '2026-02-20 10:00:00', 250.00, 2),
(1, 'Troca de filtro de ar', '2026-02-20 10:30:00', '2026-02-20 11:30:00', 120.00, 2),
(2, 'Revisão preventiva básica', '2025-12-12 08:00:00', '2025-12-12 11:00:00', 47.46, 2);

INSERT INTO itens_manutencao (id_item, id_manutencao, quantidade, valor_unitario, valor_total)
VALUES
-- Manutenção 1 (Troca de óleo - OS 1)
(1, 1, 4, 35.00, 140.00),  -- Óleo
(2, 1, 1, 45.00, 45.00),   -- Filtro óleo

-- Manutenção 2 (Filtro de ar - OS 1)
(3, 2, 1, 120.00, 120.00),

-- Manutenção 3 (OS 2)
(1, 3, 2, 35.00, 70.00);



DROP TABLE itens_manutencao;

CREATE TABLE IF NOT EXISTS compras (
	id_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_fornecedor INT NOT NULL,
    id_vendedor INT NULL,
    n_danfe VARCHAR(255) NULL,
    motivo VARCHAR(255),
    data_solicitacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    validacao ENUM("EM_ANALISE", "APROVADA", "NEGADA", "RECEBIDA", "CANCELADA", "SOLICITADA") DEFAULT "SOLICITADA",
    data_validacao DATETIME,
    valor_total DECIMAL(10, 2),
    
    request_by INT NOT NULL,
    approved_by INT,
    received_at DATETIME,
    FOREIGN KEY (request_by) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    FOREIGN KEY (approved_by) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id_fornecedor) ON DELETE RESTRICT,
    FOREIGN KEY (id_vendedor) REFERENCES vendedor_fornecedor(id_vendedor) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS compra_itens (
	id_item_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_compra INT NOT NULL,
    id_item INT NOT NULL,
    quantidade FLOAT NOT NULL,
    valor_unitario DECIMAL(10, 2) NOT NULL,
    
    FOREIGN KEY (id_compra) REFERENCES compras(id_compra) ON DELETE CASCADE,
    FOREIGN KEY (id_item) REFERENCES itens(id_item) ON DELETE CASCADE
);

INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES ("Usuario teste", "teste@gmail.com", "123456", "USUARIO");
SELECT id_usuario, nome, email, senha_hash FROM usuarios WHERE email = "erivaldosantosjunior81@gmail.com";

INSERT INTO fornecedores (
    cnpj,
    nome_empresarial,
    categoria,
    logradouro,
    numero,
    complemento,
    bairro,
    municipio,
    uf,
    cep,
    telefone,
    email,
    status_aptidao,
    register_by
) VALUES
(
    '12.345.678/0001-01',
    'Auto Mecânica Silva LTDA',
    'MECANICA',
    'Rua das Oficinas',
    '120',
    'Galpão A',
    'Centro',
    'Maceió',
    'AL',
    '57000-001',
    '(82) 99999-1001',
    'contato@silvamecanica.com',
    'APTO',
    1
),
(
    '23.456.789/0001-02',
    'Pinturas Alagoanas ME',
    'PINTURA',
    'Av. Industrial',
    '450',
    NULL,
    'Tabuleiro',
    'Maceió',
    'AL',
    '57000-002',
    '(82) 99999-1002',
    'vendas@pinturasal.com',
    'SEM_DOCUMENTACAO',
    1
),
(
    '34.567.890/0001-03',
    'Siderúrgica Nordeste SA',
    'SIDERURGICA',
    'Rod. BR-101',
    'KM 18',
    'Bloco 3',
    'Zona Rural',
    'Rio Largo',
    'AL',
    '57100-000',
    '(82) 99999-1003',
    'financeiro@siderne.com',
    'APTO',
    1
),
(
    '45.678.901/0001-04',
    'Posto Boa Viagem',
    'ABASTECIMENTO',
    'Av. Fernandes Lima',
    '890',
    NULL,
    'Farol',
    'Maceió',
    'AL',
    '57050-000',
    '(82) 99999-1004',
    'posto@boaviagem.com',
    'APTO',
    1
),
(
    '56.789.012/0001-05',
    'Limpeza Total Serviços',
    'LIMPEZA',
    'Rua da Higiene',
    '55',
    'Sala 02',
    'Jatiúca',
    'Maceió',
    'AL',
    '57035-000',
    '(82) 99999-1005',
    'contato@limpezatotal.com',
    'NAO_APTO',
    1
),
(
    '67.890.123/0001-06',
    'Admin Pro Consultoria',
    'ADMINISTRATIVO',
    'Rua dos Escritórios',
    '300',
    'Andar 5',
    'Pajuçara',
    'Maceió',
    'AL',
    '57030-000',
    '(82) 99999-1006',
    'admin@adminpro.com',
    'APTO',
    1
),
(
    '78.901.234/0001-07',
    'Mecânica Rápida Express',
    'MECANICA',
    'Av. Rotary',
    '77',
    NULL,
    'Serraria',
    'Maceió',
    'AL',
    '57046-000',
    '(82) 99999-1007',
    'rapida@express.com',
    'SEM_DOCUMENTACAO',
    1
),
(
    '89.012.345/0001-08',
    'Tintas & Cores LTDA',
    'PINTURA',
    'Rua das Cores',
    '210',
    'Loja 4',
    'Mangabeiras',
    'Maceió',
    'AL',
    '57038-000',
    '(82) 99999-1008',
    'vendas@tintasecores.com',
    'APTO',
    1
),
(
    '90.123.456/0001-09',
    'Aço Forte Distribuidora',
    'SIDERURGICA',
    'Distrito Industrial',
    'Lote 9',
    NULL,
    'Industrial',
    'Marechal Deodoro',
    'AL',
    '57160-000',
    '(82) 99999-1009',
    'contato@acoforte.com',
    'NAO_APTO',
    1
),
(
    '01.234.567/0001-10',
    'Posto Via Norte',
    'ABASTECIMENTO',
    'Av. Norte',
    '1500',
    NULL,
    'Antares',
    'Maceió',
    'AL',
    '57048-000',
    '(82) 99999-1010',
    'posto@vianorte.com',
    'APTO',
    1
);

INSERT INTO setor (atividade, criticidade, created_by) VALUES
('Carga e Recarga de Extintores', 'CRITICO', 1),
('Certificação de Eslingas e Contêineres', 'CRITICO', 1),
('Certificação de Veículos (CIV / CIPP)', 'CRITICO', 1),
('Calibração / Inspeção de END', 'CRITICO', 1),
('Consumíveis de Soldagem', 'MODERADO', 1),
('Calibração de Equipamentos', 'MODERADO', 1),
('Dedetização e Limpeza de Caixas D´água', 'CRITICO', 1),
('EPI – Equipamento de Proteção Individual', 'MODERADO', 1),
('Equipamentos Operacionais', 'MODERADO', 1),
('Lavanderia', 'MODERADO', 1),
('Lavadora / Higienizadora de Veículos', 'MODERADO', 1),
('Medicina do Trabalho', 'CRITICO', 1),
('Oficina Automotiva', 'MODERADO', 1),
('Opacidade de Veículos', 'MODERADO', 1),
('Postos de Combustível', 'CRITICO', 1),
('Produtos de Limpeza', 'MODERADO', 1),
('Empresas Receptoras de Resíduos', 'CRITICO', 1),
('Requisitos Legais', 'CRITICO', 1),
('Subcontratação', 'MODERADO', 1),
('Teste de Carga e Hidrostático', 'CRITICO', 1),
('Aquisição de Veículos e Equipamentos', 'MODERADO', 1);

INSERT INTO fornecedor_setor (id_fornecedor, id_setor) VALUES
-- Auto Mecânica Silva
(1, 1), -- Oficina Automotiva
(1, 6), -- Requisitos Legais

-- Pinturas Alagoanas
(2, 2), -- Pintura Automotiva
(2, 6), -- Requisitos Legais

-- Siderúrgica Nordeste
(3, 5), -- Consumíveis de Soldagem
(3, 6), -- Requisitos Legais

-- Posto Boa Viagem
(4, 3), -- Postos de Combustível
(4, 6), -- Requisitos Legais

-- Limpeza Total
(5, 4), -- Dedetização e Limpeza
(5, 6); -- Requisitos Legais

INSERT INTO documentos_setor (
    id_fornecedor, id_setor, nome, caminho, tipo, register_by
) VALUES
(1, 1, 'Alvará de Funcionamento', 'docs/1/oficina/alvara.pdf', 'ALVARA', 1),
(1, 1, 'Cartão CNPJ', 'docs/1/oficina/cnpj.pdf', 'CNPJ', 1);

INSERT INTO documentos_setor (
    id_fornecedor, id_setor, nome, caminho, tipo, register_by
) VALUES
(2, 2, 'Alvará de Funcionamento', 'docs/2/pintura/alvara.pdf', 'ALVARA', 1),
(2, 2, 'Licença Ambiental', 'docs/2/pintura/licenca.pdf', 'LICENCA_AMBIENTAL', 1);

INSERT INTO documentos_setor (
    id_fornecedor, id_setor, nome, caminho, tipo, register_by
) VALUES
(3, 5, 'Certificação FBTS', 'docs/3/soldagem/fbts.pdf', 'CERTIFICACAO', 1);

INSERT INTO documentos_setor (
    id_fornecedor, id_setor, nome, caminho, tipo, register_by
) VALUES
(4, 3, 'Cadastro ANP', 'docs/4/posto/anp.pdf', 'ANP', 1),
(4, 3, 'Licença Ambiental', 'docs/4/posto/licenca.pdf', 'LICENCA_AMBIENTAL', 1);

INSERT INTO documentos_setor (
    id_fornecedor, id_setor, nome, caminho, tipo, register_by
) VALUES
(5, 4, 'CRV – Controle de Vetores', 'docs/5/limpeza/crv.pdf', 'CRV', 1),
(5, 4, 'Certificado Limpeza Caixa D’água', 'docs/5/limpeza/caixa.pdf', 'CERTIFICADO', 1);

SELECT
    f.nome_empresarial,
    s.atividade,
    d.nome,
    d.caminho
FROM documentos_setor d
JOIN fornecedores f ON f.id_fornecedor = d.id_fornecedor
JOIN setor s ON s.id_setor = d.id_setor
ORDER BY f.nome_empresarial, s.atividade;

SELECT f.*, s.*, d.* FROM fornecedores f
JOIN fornecedor_setor fs ON fs.id_fornecedor = f.id_fornecedor
JOIN setor s ON s.id_setor = fs.id_setor
LEFT JOIN documentos_setor d ON d.id_fornecedor = fs.id_fornecedor AND d.id_setor = fs.id_setor
ORDER BY f.nome_empresarial, s.atividade, d.data_upload;

INSERT INTO vendedor_fornecedor (id_fornecedor, nome, contato, status_vendedor) VALUES (1, "Lana", "876797657855678", "ATIVO");

SELECT * FROM documentos_necessarios;

SELECT * FROM fornecedores;

ALTER TABLE fornecedores
MODIFY COLUMN register_by INT NOT NULL;

ALTER TABLE compras MODIFY COLUMN validacao ENUM("EM_ANALISE", "APROVADA", "NEGADA", "CANCELADA", "RECEBIDA", "SOLICITADA") DEFAULT "SOLICITADA";

ALTER TABLE compras MODIFY COLUMN n_danfe VARCHAR(255) NULL;

SELECT * FROM setor;

SELECT s.*, d.* FROM setor s LEFT JOIN documentos_necessarios d ON d.id_setor = s.id_setor ORDER BY s.atividade, d.nome;



INSERT INTO documentos_necessarios (id_setor, nome, tipo, created_by) VALUES (1, "Certificado 2", "Certificado", 1);

UPDATE fornecedores SET cnpj = "teste", nome_empresarial = "teste", categoria = "PINTURA", logradouro = "teste", numero = "teste",
                           complemento = "teste", bairro = "teste", municipio = "teste", uf = "teste", cep = "teste", telefone = "teste", email = "teste", status_aptidao = "NAO_APTO"
                           WHERE id_fornecedor = 1;
          
SELECT * FROM documentos_necessarios;          

SELECT s.*, d.* FROM setor s
                           LEFT JOIN documentos_necessarios d ON d.id_setor = s.id_setor
                           ORDER BY s.atividade, d.nome;
                           
INSERT INTO itens (nome, codigo_interno, unidade_medida, created_by) VALUES ("Cabeçote", "MEC002", "UNIDADE", 1);
INSERT INTO estoque(id_item, quantidade_atual, quantidade_minima, add_by) VALUES(2, 5, 2, 1);

SELECT i.id_item, i.nome, i.codigo_interno, i.unidade_medida, e.quantidade_atual, e.quantidade_minima FROM estoque e JOIN itens i ON i.id_item = e.id_item;

ALTER TABLE itens ADD COLUMN ultimo_preco DECIMAL (10, 2);

INSERT INTO movimentacao_estoque (tipo, origem, destino, solicitante, register_by) VALUES ("SAIDA", "ESTOQUE", "MECANICA", "ROBERTO", 1);
INSERT INTO itens_movimentacao (id_item, id_movimentacao, quantidade) VALUES (2, 1, 5);

ALTER TABLE compras ADD COLUMN received_at DATETIME;

SELECT * FROM itens;

SELECT * FROM documentos_setor;

INSERT INTO compras (id_fornecedor, id_vendedor, motivo, validacao, valor_total, request_by) VALUES (1, 1, "AJUSTE DE VÁLVULA", "APROVADA", "857.56", 1); 

INSERT INTO compra_itens(id_compra, id_item, quantidade, valor_unitario) VALUES (2, 4, 2, "85.47");

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE itens_movimentacao;
TRUNCATE TABLE movimentacao_estoque;
TRUNCATE TABLE estoque;
TRUNCATE TABLE itens;

SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO itens (nome, codigo_interno, unidade_medida, created_by)
WITH RECURSIVE seq AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 100
)
SELECT 
    CONCAT('Item ', n),
    CONCAT('COD', LPAD(n, 4, '0')),
    ELT(1 + FLOOR(RAND()*6), 'METROS','PAR','LITROS','UNIDADE','CAIXA','RESMA'),
    1
FROM seq;

INSERT INTO estoque (id_item, quantidade_atual, quantidade_minima, add_by)
SELECT 
    id_item,
    FLOOR(10 + RAND()*100),
    FLOOR(5 + RAND()*20),
    1
FROM itens;

INSERT INTO movimentacao_estoque (tipo, id_os, origem, destino, solicitante, descricao, register_by)
SELECT 
    ELT(1 + FLOOR(RAND()*4), 'ENTRADA','SAIDA','AJUSTE','TROCA'),
    FLOOR(1 + RAND()*5),
    'Almoxarifado',
    'Oficina',
    'Sistema',
    'Movimentação automática teste',
    1
FROM (
    SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
    UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
    UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
    UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
    UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
    UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30
    UNION SELECT 31 UNION SELECT 32 UNION SELECT 33 UNION SELECT 34 UNION SELECT 35
    UNION SELECT 36 UNION SELECT 37 UNION SELECT 38 UNION SELECT 39 UNION SELECT 40
    UNION SELECT 41 UNION SELECT 42 UNION SELECT 43 UNION SELECT 44 UNION SELECT 45
    UNION SELECT 46 UNION SELECT 47 UNION SELECT 48 UNION SELECT 49 UNION SELECT 50
) AS temp;

INSERT INTO itens_movimentacao (id_item, id_movimentacao, quantidade)
SELECT 
    FLOOR(1 + RAND()*100),
    id_movimentacao,
    FLOOR(1 + RAND()*20)
FROM movimentacao_estoque;

INSERT INTO movimentacao_estoque 
(tipo, id_os, origem, destino, solicitante, descricao, register_by, register_at)
SELECT 
    ELT(1 + FLOOR(RAND()*4), 'ENTRADA','SAIDA','AJUSTE','TROCA'),
    FLOOR(1 + RAND()*5),
    'Almoxarifado',
    'Oficina',
    'Sistema',
    'Movimentação automática período teste',
    1,
    
    -- Datas distribuídas nos últimos 12 meses
    DATE_SUB(
        NOW(),
        INTERVAL FLOOR(RAND()*365) DAY
    )
FROM (
    SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
    UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10
    UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15
    UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20
    UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25
    UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30
    UNION SELECT 31 UNION SELECT 32 UNION SELECT 33 UNION SELECT 34 UNION SELECT 35
    UNION SELECT 36 UNION SELECT 37 UNION SELECT 38 UNION SELECT 39 UNION SELECT 40
    UNION SELECT 41 UNION SELECT 42 UNION SELECT 43 UNION SELECT 44 UNION SELECT 45
    UNION SELECT 46 UNION SELECT 47 UNION SELECT 48 UNION SELECT 49 UNION SELECT 50
) AS temp;

INSERT INTO itens_movimentacao (id_item, id_movimentacao, quantidade)
SELECT 
    FLOOR(1 + RAND()*100),  -- considerando 100 itens
    id_movimentacao,
    FLOOR(1 + RAND()*20)
FROM movimentacao_estoque
ORDER BY id_movimentacao DESC
LIMIT 50;

ALTER TABLE ordem_servico MODIFY COLUMN status_os ENUM("ABERTA", "EM_EXECUCAO", "FINALIZADA", "CANCELADA");





