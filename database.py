import pymysql
from pymysql import Error
from PyQt5.QtWidgets import QMessageBox

class DatabaseConfig:
    def __init__(self):
        self.host = "localhost"
        self.user = "admin"
        self.password = "3r!v4ld0Jun!0r"
        self.database = "teste"
    
db_config = DatabaseConfig()

class DbConect:
    def conectar(self):
         config = db_config
         
         try:
             self.conexao = pymysql.connect(
                 host = config.host,
                 user = config.user,
                 password = config.password,
                 database = config.database
             )
             
             return self.conexao
         
         except Exception:
             raise
    
    def conn_close(self):
        try:
            self.conexao.close()
        except:
            pass
            
####################SELECTS####################

    def get_all_fornecedores(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
                            SELECT f.*, s.*, d.* FROM fornecedores f
                            JOIN fornecedor_setor fs ON fs.id_fornecedor = f.id_fornecedor
                            JOIN setor s ON s.id_setor = fs.id_setor
                            LEFT JOIN documentos_setor d ON d.id_fornecedor = fs.id_fornecedor AND d.id_setor = fs.id_setor
                            ORDER BY f.nome_empresarial, s.atividade, d.data_upload""")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_all_setores(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
                           SELECT s.*, d.* FROM setor s
                           LEFT JOIN documentos_necessarios d ON d.id_setor = s.id_setor
                           ORDER BY s.atividade, d.nome""")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_itens_estoque(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
                            SELECT
                                i.id_item, 
                                i.nome, 
                                i.codigo_interno, 
                                i.unidade_medida, 
                                e.quantidade_atual, 
                                e.quantidade_minima 
                            FROM estoque e 
                            JOIN itens i ON i.id_item = e.id_item""")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_all_movimentacoes(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
                           SELECT
                                me.id_movimentacao,
                                me.tipo,
                                i.nome,
                                i.unidade_medida,
                                im.quantidade,
                                me.origem,
                                me.destino,
                                me.solicitante,
                                me.register_at
                            FROM itens_movimentacao im
                            LEFT JOIN movimentacao_estoque me ON me.id_movimentacao = im.id_movimentacao
                            LEFT JOIN itens i ON i.id_item = im.id_item
                            ORDER BY me.register_at""")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_all_itens(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT * FROM itens")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_all_compras(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
                            SELECT
                                c.id_compra,
                                f.nome_empresarial as fornecedor,
                                vf.nome as vendedor,
                                c.motivo,
                                c.data_solicitacao,
                                c.n_danfe,
                                c.validacao,
                                c.data_validacao,
                                c.valor_total,
                                u.nome as usuario,
                                c.approved_by,
                                i.nome as item,
                                ci.quantidade,
                                ci.valor_unitario
                            FROM compras c
                            JOIN fornecedores f ON f.id_fornecedor = c.id_fornecedor
                            JOIN vendedor_fornecedor vf ON vf.id_vendedor = c.id_vendedor
                            JOIN usuarios u ON u.id_usuario = c.request_by
                            LEFT JOIN compra_itens ci ON ci.id_compra = c.id_compra
                            LEFT JOIN itens i ON i.id_item = ci.id_item
                            ORDER BY c.data_solicitacao""")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_itens_compra(self, id_compra):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT id_item, quantidade, valor_unitario FROM compra_itens WHERE id_compra = %s", (id_compra,))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_all_equipamentos(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT * FROM veiculos")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_all_ordens(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""SELECT
                                os.id_os,
                                os.numero_os,
                                v.placa,
                                os.local_manutencao,
                                os.km_atual,
                                os.tipo,
                                os.oficina,
                                os.responsavel,
                                os.data_saida,
                                os.data_previsao,
                                os.data_retorno,
                                os.custo,
                                os.status_os,
                                os.descricao
                            FROM ordem_servico os
                            JOIN veiculos v ON v.id_veiculo = os.id_veiculo
                            ORDER BY os.numero_os""")
            return cursor.fetchall()
        finally:
            cursor.close()
    
####################LISTAS####################
 
    def listar_setores(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT id_setor, atividade FROM setor ORDER BY atividade")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def listar_fornecedores(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT id_fornecedor, nome_empresarial FROM fornecedores")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def listar_os(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT id_os, numero_os FROM ordem_servico")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def listar_itens(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT id_item, nome FROM itens")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def listar_veiculos(self):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT id_veiculo, placa FROM veiculos")
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def listar_itens_os(self, id_os):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""SELECT
                                io.id_item,
                                i.nome
                            FROM itens_os io
                            JOIN itens i ON i.id_item = io.id_item
                            WHERE io.id_os = %s
                            AND io.status_item = 'NAO_UTILIZADO'""", (id_os,))
            return cursor.fetchall()
        finally:
            cursor.close()
    
####################REGISTROS####################

    def cadastrar_fornecedor(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        
        try:
            cursor.execute("""INSERT INTO fornecedores(cnpj, nome_empresarial, categoria, logradouro, municipio, bairro, uf, numero, complemento, cep, email, telefone, status_aptidao, register_by)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", info)
            self.conexao.commit()
            return cursor.lastrowid
        except Exception:
            raise
        finally:
            cursor.close()

    def cadastrar_vendedor(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        
        try:
            cursor.execute("INSERT INTO vendedor_fornecedor (id_fornecedor, nome, contato, status_vendedor) VALUES (%s, %s, %s, %s)", info)
            self.conexao.commit()
        except Exception:
            raise
        finally:
            cursor.close()
    
    def cadastrar_setor(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
            
        qntd = ("%s, %s, %s")
        
        try:
            cursor.execute(f"INSERT INTO setor (atividade, criticidade, created_by) VALUE ({qntd})", info)
            self.conexao.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
    
    def registrar_documento_necessario(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        qntd = ("%s, %s, %s, %s")
        
        try:
            cursor.execute(f"INSERT INTO documentos_necessarios (id_setor, nome, tipo, created_by) VALUES ({qntd})", info)
            self.conexao.commit()
        finally:
            cursor.close()
    
    def vincular_setor_fornecedor(self, id_fornecedor, id_setor):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("INSERT IGNORE INTO fornecedor_setor (id_fornecedor, id_setor) VALUES (%s, %s)", (id_fornecedor, id_setor))
            self.conexao.commit()
        finally:
            cursor.close()
    
    def vincular_documento_fornecedor(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("INSERT INTO documentos_setor (id_setor, id_fornecedor, nome, caminho, tipo, register_by) VALUES (%s, %s, %s, %s, %s, %s)", info)
            self.conexao.commit()
        finally:
            cursor.close()
    
    def cadastrar_itens(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("INSERT INTO itens (nome, codigo_interno, unidade_medida, created_by) VALUES (%s, %s, %s, %s)", (info))
            self.conexao.commit()
        finally:
            cursor.close()
    
    def cadastrar_compra(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("INSERT INTO compras (id_fornecedor, id_vendedor, motivo, valor_total, request_by) VALUES (%s, %s, %s, %s, %s)", (info))
            self.conexao.commit()
            return cursor.lastrowid
        except Exception:
            raise
        finally:
            cursor.close()

    def registrar_itens_compra(self, id_compra, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("INSERT INTO compra_itens (id_compra, id_item, quantidade, valor_unitario) VALUES (%s, %s, %s, %s)", (id_compra, info["id_item"], info["quantidade"], info["valor_unitario"]))
            self.conexao.commit()
        except Exception:
            raise
        finally:
            cursor.close()
    
    def registrar_estoque_compra(self, info, id_compra):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("INSERT INTO estoque (id_item, quantidade_atual, quantidade_minima, add_by) VALUES (%s, %s, %s, %s)", (info["id_item"], info["quantidade"], info["quantidade"], info["usuario"]))
            cursor.execute("UPDATE compras SET validacao = 'RECEBIDA' WHERE id_compra = %s", id_compra)
            self.conexao.commit()
        finally:
            cursor.close()  
    
    def registrar_movimentacao(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("INSERT INTO movimentacao_estoque(tipo, id_os, origem, solicitante, destino, descricao, register_by) VALUES (%s, %s, %s, %s, %s, %s, %s)", info)
            self.conexao.commit()
            return cursor.lastrowid
        except Exception:
            raise
        finally:
            cursor.close()
    
    def registrar_itens_movimentacao(self, info, id_mov):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("INSERT INTO itens_movimentacao(id_item, id_movimentacao, quantidade) VALUES (%s, %s, %s)", (info["id_item"], id_mov, info["quantidade"]))
            self.conexao.commit()
        finally:
            cursor.close()
    
    def vincular_doc_equipamento(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""INSERT INTO documentos_veiculo (id_veiculo, nome, emissao, validade, caminho, tipo, register_by)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""", (info))
            self.conexao.commit()
        except:
            self.conexao.rollback()
            raise
        finally:
            cursor.close()
    
    def cadastrar_equipamento(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""INSERT INTO veiculos (placa, equipamento, modelo, ano, km_atual, chassi, renavam, regime, status_atividade, km_ultima_revisao, register_by)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", info)
            self.conexao.commit()
        finally:
            cursor.close()
    
    def add_novo_item_os(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("INSERT INTO itens_os (id_os, id_item, quantidade_previsao, valor_unitario_previsto, valor_total_previsto, status_item) VALUES (%s, %s, %s, %s, %s, %s)", (info))
            self.conexao.commit()
        except Exception:
            raise
        finally:
            cursor.close()
    
    def registrar_os(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""INSERT INTO
                           ordem_servico (numero_os, id_veiculo, local_manutencao, km_atual, tipo, oficina, responsavel, data_saida, data_previsao, custo, status_os, descricao, opened_by)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s ,%s, %s, %s ,%s)""", info)
            self.conexao.commit()
            return cursor.lastrowid
        except Exception:
            self.conexao.rollback()
            raise
        finally:
            cursor.close()
    
    def registrar_itens_os(self, id_os, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""INSERT INTO itens_os (id_os, id_item, quantidade_previsao, valor_unitario_previsto, valor_total_previsto, status_item)
                           VALUES (%s, %s, %s, %s, %s, %s)""", (id_os, info["id_item"], info["quantidade"], info["valor_unitario"], float(info["quantidade"]) * float(info["valor_unitario"]), info["status"]))
            self.conexao.commit()
        except Exception:
            self.conexao.rollback()
            raise
        finally:
            cursor.close()
    
####################FILTROS####################

    def login(self, email):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT id_usuario, nome, email, senha_hash, perfil FROM usuarios WHERE email = %s", (email,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def filtro_fornecedores(self, termo = None):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        if not termo:
            return
        
        try:
            cursor.execute("""
                            SELECT f.*, s.*, d.* FROM fornecedores f
                            JOIN fornecedor_setor fs ON fs.id_fornecedor = f.id_fornecedor
                            JOIN setor s ON s.id_setor = fs.id_setor
                            LEFT JOIN documentos_setor d ON d.id_fornecedor = fs.id_fornecedor AND d.id_setor = fs.id_setor
                            WHERE f.nome_empresarial LIKE %s
                            OR f.cnpj LIKE %s
                            OR f.categoria LIKE %s
                            ORDER BY f.nome_empresarial, s.atividade, d.data_upload""", (termo, termo, termo))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def filtro_setores(self, termo = None):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        if not termo:
            return
        
        try:
            cursor.execute("""
                           SELECT s.*, d.* FROM setor s
                           JOIN documentos_necessarios d ON d.id_setor = s.id_setor
                           WHERE atividade = %s
                           OR nome = %s
                           OR tipo = %s
                           ORDER BY s.atividade, d.nome""", (termo, termo, termo))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def vendedor_por_fornecedor(self,id_fornecedor):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT * FROM vendedor_fornecedor WHERE id_fornecedor = %s", (id_fornecedor,))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def setor_fornecedor(self, id_fornecedor):
        cursor  = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""SELECT s.id_setor, s.atividade
                           FROM setor s
                           JOIN fornecedor_setor fs ON s.id_setor = fs.id_setor
                           WHERE fs.id_fornecedor = %s""", (id_fornecedor,))
            return cursor.fetchall()
        finally:
            cursor.close()

    def get_fornecedor(self, id_fornecedor):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT * FROM fornecedores WHERE id_fornecedor = %s", (id_fornecedor,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def buscar_doc_setor(self, id_setor):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""SELECT d.*, s.* FROM documentos_necessarios d
                            LEFT JOIN setor s ON s.id_setor = d.id_setor
                           WHERE d.id_setor = %s""", id_setor)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def filtrar_estoque(self, termo):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
                           SELECT
                            i.id_item,
                            i.nome,
                            i.codigo_interno,
                            i.unidade_medida,
                            e.quantidade_atual,
                            e.quantidade_minima
                        FROM estoque e
                        JOIN itens i ON i.id_item = e.id_item
                        WHERE i.nome = %s
                        OR i.codigo_interno = %s
                        OR i.unidade_medida = %s""", (termo, termo, termo))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def filtrar_movimentacoes(self, termo):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
                           SELECT
                                me.id_movimentacao,
                                me.tipo,
                                i.nome,
                                i.unidade_medida,
                                im.quantidade,
                                me.origem,
                                me.destino,
                                me.solicitante,
                                me.register_at
                            FROM itens_movimentacao im
                            JOIN movimentacao_estoque me ON me.id_movimentacao = im.id_movimentacao
                            JOIN itens i ON i.id_item = im.id_item
                            WHERE me.tipo = %s
                            ORDER BY me.id_movimentacao""", (termo))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def filtrar_movimentacoes_periodo(self, data_1, data_2):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
                           SELECT
                                me.id_movimentacao,
                                me.tipo,
                                i.nome,
                                i.unidade_medida,
                                im.quantidade,
                                me.origem,
                                me.destino,
                                me.solicitante,
                                me.register_at
                            FROM itens_movimentacao im
                            JOIN movimentacao_estoque me ON me.id_movimentacao = im.id_movimentacao
                            JOIN itens i ON i.id_item = im.id_item
                            WHERE me.register_at >= %s AND me.register_at < DATE_ADD(%s, INTERVAL 1 DAY)
                            ORDER BY me.id_movimentacao""", (data_1, data_2))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def buscar_item_por_id(self, id_item):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT nome, codigo_interno, unidade_medida FROM itens WHERE id_item = %s", (id_item,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def verificar_existe_estoque(self, id_item):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT EXISTS( SELECT 1 FROM estoque WHERE id_item = %s) AS existe", (id_item,))
            return cursor.fetchone()["existe"]
        finally:
            cursor.close()
    
    def get_info_itens_estoque(self, id_item):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT quantidade_atual, quantidade_minima FROM estoque WHERE id_item = %s", id_item)
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def get_itens_movimentacao(self, id_item):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
                            SELECT
                                i.nome,
                                i.codigo_interno,
                                i.unidade_medida,
                                e.quantidade_atual
                            FROM itens i
                            LEFT JOIN estoque e ON e.id_item = i.id_item
                            WHERE i.id_item = %s""", id_item)
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def get_equipamento_by_id(self, id_equipamento):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT id_veiculo, placa, equipamento, modelo, ano, chassi, renavam, regime, km_ultima_revisao, km_atual, status_atividade FROM veiculos WHERE id_veiculo = %s", id_equipamento)
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def documentos_equipamento(self, id_equipamento):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT nome, validade FROM documentos_veiculo WHERE id_veiculo = %s", id_equipamento)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def filtrar_equipamento(self, termo):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""SELECT * FROM veiculos 
                           WHERE placa = %s
                           OR equipamento = %s
                           OR modelo = %s
                           OR ano = %s
                           OR regime = %s
                           OR status_atividade = %s""", (termo, termo, termo, termo, termo, termo))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_os_by_id(self, id_os):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""SELECT
                                os.numero_os,
                                v.placa,
                                os.local_manutencao,
                                os.km_atual,
                                os.tipo,
                                os.oficina,
                                os.responsavel,
                                os.data_saida,
                                os.data_previsao,
                                os.custo,
                                os.status_os,
                                os.descricao
                            FROM ordem_servico os
                            JOIN veiculos v ON v.id_veiculo = os.id_veiculo
                            WHERE os.id_os = %s""", id_os)
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def busca_itens_os(self, id_os):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""SELECT
                                io.id_item,
                                i.nome,
                                i.codigo_interno,
                                i.unidade_medida,
                                io.quantidade_previsao as quantidade,
                                io.status_item
                            FROM itens_os io
                            JOIN itens i ON i.id_item = io.id_item
                            WHERE io.id_os = %s""", id_os)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_item_by_id(self, id_item):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT * FROM itens WHERE id_item = %s", (id_item,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def item_os(self, id_item):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT quantidade_previsao, valor_unitario_previsto FROM itens_os WHERE id_item = %s", (id_item,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def get_manutencoes_os(self, id_os):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT * FROM manutencoes WHERE id_os = %s", (id_os,))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def itens_manutencao(self, id_manutencao):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""SELECT
                                im.id_item,
                                i.nome,
                                im.quantidade,
                                im.valor_unitario,
                                im.valor_total
                            FROM itens_manutencao im
                            LEFT JOIN itens i ON im.id_item = i.id_item
                            WHERE id_manutencao = %s""", (id_manutencao))
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def get_doc_setor(self, id_setor, documento):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT nome FROM documentos_necessarios WHERE id_setor = %s AND nome = %s", (id_setor, documento))
            return cursor.fetchone() or 0
        finally:
            cursor.close()
    
    def buscar_item_nome(self, nome):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("SELECT nome FROM itens WHERE nome = %s", (nome,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
####################UPDATES####################

    def edit_fornecedor(self, info, id_fornecedor):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""UPDATE fornecedores SET cnpj = %s, nome_empresarial = %s, categoria = %s, logradouro = %s, numero = %s,
                           complemento = %s, bairro = %s, municipio = %s, uf = %s, cep = %s, telefone = %s, email = %s, status_aptidao = %s
                           WHERE id_fornecedor = %s""", (info["cnpj"], info["nome_empresarial"], info["categoria"], info["logradouro"], info["numero"], info["complemento"],
                                                         info["bairro"], info["municipio"], info["uf"], info["cep"], info["telefone"], info["email"],
                                                         info["status_aptidao"], id_fornecedor))
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            raise e
        finally:
            cursor.close()

    def edit_setor(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE setor SET atividade = %s, criticidade = %s, created_by = %s WHERE id_setor = %s", info)
            self.conexao.commit()
        finally:
            cursor.close()
    
    def edit_item(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE itens SET nome = %s, codigo_interno = %s, unidade_medida = %s, created_by = %s WHERE id_item = %s", (info["nome"], info["codigo"], info["medida"], info["usuario"], info["id_item"]))
            self.conexao.commit()
        except Exception as e:
            self.conexao.rollback()
            raise e
        finally:
            cursor.close()
    
    def entrada_estoque(self, info, id_compra):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE estoque set quantidade_atual = quantidade_atual + %s WHERE id_item = %s", (info["quantidade"], info["id_item"]))
            cursor.execute("UPDATE compras SET validacao = 'RECEBIDA' WHERE id_compra = %s", id_compra)
            self.conexao.commit()
        finally:
            cursor.close()
    
    def set_compra_aprovada(self, id_compra):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE compras SET validacao = 'APROVADA' WHERE id_compra = %s", id_compra)
            self.conexao.commit()
        finally:
            cursor.close()
    
    def set_compra_negada(self, id_compra):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE compras SET validacao = 'NEGADA' WHERE id_compra = %s", id_compra)
            self.conexao.commit()
        finally:
            cursor.close()
    
    def set_compra_cancelada(self, id_compra):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE compras SET validacao = 'CANCELADA' WHERE id_compra = %s", id_compra)
            self.conexao.commit()
        finally:
            cursor.close()
    
    def set_compra_analise(self, id_compra):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE compras SET validacao = 'EM_ANALISE' WHERE id_compra = %s", id_compra)
            self.conexao.commit()
        finally:
            cursor.close()
    
    def vincular_nf(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE compras SET n_danfe = %s WHERE id_compra = %s", info)
            self.conexao.commit()
        finally:
            cursor.close()
    
    def ajustar_estoque(self, info, id_usuario):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE estoque SET quantidade_atual = %s, quantidade_minima = %s WHERE id_item = %s", (info["quantidade"], info["nova_quantidade"], info["id_item"]))
            cursor.execute("INSERT INTO movimentacao_estoque(tipo, origem, destino, solicitante, descricao, register_by) VALUES ('AJUSTE', 'ESTOQUE', 'ESTOQUE', 'ESTOQUE', 'AJUSTE DE ESTOQUE', %s)", (id_usuario,))
            id_mov = cursor.lastrowid
            cursor.execute("INSERT INTO itens_movimentacao(id_item, id_movimentacao, quantidade) VALUES (%s, %s, %s)", (info["id_item"], id_mov, info["quantidade"]))
            self.conexao.commit()
        finally:
            cursor.close()
    
    def saida_estoque_movimentacao(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE estoque SET quantidade_atual = quantidade_atual - %s WHERE id_item = %s", (info["quantidade"], info["id_item"]))
            self.conexao.commit()
        finally:
            cursor.close()

    def entrada_estoque_movimentacao(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE estoque SET quantidade_atual = quantidade_atual + %s WHERE id_item = %s", (info["quantidade"], info["id_item"]))
            self.conexao.commit()
        finally:
            cursor.close()
    
    def edit_equipamento(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE veiculos SET placa = %s, equipamento = %s, modelo = %s, ano = %s, chassi = %s, renavam = %s, regime = %s, km_atual = %s, status_atividade = %s WHERE id_veiculo = %s", info)
            self.conexao.commit()
        finally:
            cursor.close()
    
    def editar_os(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE ordem_servico SET numero_os = %s, id_veiculo = %s, responsavel = %s, tipo = %s, data_saida = %s, data_previsao = %s, descricao = %s, local_manutencao = %s, km_atual = %s, oficina = %s, custo = %s, status_os = %s, opened_by = %s WHERE id_os = %s", info)
            self.conexao.commit()
        except Exception:
            self.conexao.rollback()
            raise
        finally:
            cursor.close()
    
    def edit_qntd_itens_os(self, info):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE itens_os SET quantidade_previsao = %s WHERE id_item = %s", info)
            self.conexao.commit()
        except Exception:
            self.conexao.rollback()
            raise
        finally:
            cursor.close()
    
    def update_custo_os(self, custo):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE ordem_servico SET custo = custo + %s WHERE id_os = %s", custo)
            self.conexao.commit()
        except Exception:
            self.conexao.rollback()
            raise
        finally:
            cursor.close()

    def update_custo_remover_os(self, custo):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE ordem_servico SET custo = custo - %s WHERE id_os = %s", custo)
            self.conexao.commit()
        except Exception:
            self.conexao.rollback()
            raise
        finally:
            cursor.close()

    def set_os_aberta(self, id_os):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE ordem_servico SET status_os = 'ABERTA' WHERE id_os = %s", (id_os,))
            self.conexao.commit()
        finally:
            cursor.close()

    def set_os_em_execucao(self, id_os):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE ordem_servico SET status_os = 'EM_EXECUCAO' WHERE id_os = %s", (id_os,))
            self.conexao.commit()
        finally:
            cursor.close()

    def set_os_finalizada(self, id_os):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE ordem_servico SET data_retorno = CURRENT_TIMESTAMP, status_os = 'FINALIZADA' WHERE id_os = %s", (id_os,))
            self.conexao.commit()
        finally:
            cursor.close()
            
    def set_os_cancelada(self, id_os):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("UPDATE ordem_servico SET status_os = 'CANCELADA' WHERE id_os = %s", (id_os,))
            self.conexao.commit()
        finally:
            cursor.close()

####################DELETES####################

    def remover_setor(self, id_fornecedor, id_setor):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("DELETE FROM fornecedor_setor WHERE id_fornecedor = %s AND id_setor = %s", (id_fornecedor, id_setor))
            self.conexao.commit()
        finally:
            cursor.close()
    
    def remover_documento(self, id_documento):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("DELETE documentos_necessarios WHERE id_doc_necessario = %s", id_documento)
            self.conexao.commit()
        finally:
            cursor.close()

    def remover_item_os(self, id_item):
        cursor = self.conexao.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("DELETE FROM itens_os WHERE id_item = %s", (id_item,))
            self.conexao.commit()
        except Exception:
            self.conexao.rollback()
            raise
        finally:
            cursor.close()
    
