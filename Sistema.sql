-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: limpind
-- ------------------------------------------------------
-- Server version	8.0.43-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `compras`
--

DROP TABLE IF EXISTS `compras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras` (
  `id_compra` int NOT NULL AUTO_INCREMENT,
  `id_fornecedor` int NOT NULL,
  `data_compra` date NOT NULL,
  `valor_total` decimal(18,4) NOT NULL DEFAULT '0.0000',
  PRIMARY KEY (`id_compra`),
  KEY `id_fornecedor` (`id_fornecedor`),
  CONSTRAINT `compras_ibfk_1` FOREIGN KEY (`id_fornecedor`) REFERENCES `fornecedores` (`id_fornecedor`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras`
--

LOCK TABLES `compras` WRITE;
/*!40000 ALTER TABLE `compras` DISABLE KEYS */;
/*!40000 ALTER TABLE `compras` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compras_itens`
--

DROP TABLE IF EXISTS `compras_itens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras_itens` (
  `id_item` int NOT NULL AUTO_INCREMENT,
  `id_compra` int NOT NULL,
  `id_peca` int NOT NULL,
  `quantidade` decimal(20,4) NOT NULL,
  `preco_unitario` decimal(18,4) NOT NULL,
  PRIMARY KEY (`id_item`),
  KEY `id_compra` (`id_compra`),
  KEY `id_peca` (`id_peca`),
  CONSTRAINT `compras_itens_ibfk_1` FOREIGN KEY (`id_compra`) REFERENCES `compras` (`id_compra`) ON DELETE CASCADE,
  CONSTRAINT `compras_itens_ibfk_2` FOREIGN KEY (`id_peca`) REFERENCES `pecas` (`id_peca`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras_itens`
--

LOCK TABLES `compras_itens` WRITE;
/*!40000 ALTER TABLE `compras_itens` DISABLE KEYS */;
/*!40000 ALTER TABLE `compras_itens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipamentos`
--

DROP TABLE IF EXISTS `equipamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipamentos` (
  `id_equipamento` int NOT NULL AUTO_INCREMENT,
  `placa` varchar(50) DEFAULT NULL,
  `descricao` varchar(255) NOT NULL,
  `modelo` varchar(100) DEFAULT NULL,
  `ano` int DEFAULT NULL,
  `chassi` varchar(100) DEFAULT NULL,
  `status` enum('ativo','em_manutencao','inativo') DEFAULT 'ativo',
  PRIMARY KEY (`id_equipamento`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipamentos`
--

LOCK TABLES `equipamentos` WRITE;
/*!40000 ALTER TABLE `equipamentos` DISABLE KEYS */;
INSERT INTO `equipamentos` VALUES (1,'JBK3D79','CAVALO MECÂNICO','VW',2022,'984J71J1GDXJ4NV81KTHVU2811B','ativo');
/*!40000 ALTER TABLE `equipamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estoque`
--

DROP TABLE IF EXISTS `estoque`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estoque` (
  `id_estoque` int NOT NULL AUTO_INCREMENT,
  `id_peca` int NOT NULL,
  `quantidade_atual` decimal(20,4) NOT NULL DEFAULT '0.0000',
  `quantidade_minima` decimal(20,4) NOT NULL DEFAULT '0.0000',
  PRIMARY KEY (`id_estoque`),
  UNIQUE KEY `id_peca` (`id_peca`),
  CONSTRAINT `estoque_ibfk_1` FOREIGN KEY (`id_peca`) REFERENCES `pecas` (`id_peca`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estoque`
--

LOCK TABLES `estoque` WRITE;
/*!40000 ALTER TABLE `estoque` DISABLE KEYS */;
/*!40000 ALTER TABLE `estoque` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estoque_movimentacoes`
--

DROP TABLE IF EXISTS `estoque_movimentacoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estoque_movimentacoes` (
  `id_movimentacao` int NOT NULL AUTO_INCREMENT,
  `id_peca` int NOT NULL,
  `tipo` enum('entrada','saida','ajuste') NOT NULL,
  `quantidade` decimal(20,4) NOT NULL,
  `data_movimentacao` datetime NOT NULL,
  `origem` varchar(100) DEFAULT NULL,
  `id_referencia` int DEFAULT NULL,
  `observacao` text,
  PRIMARY KEY (`id_movimentacao`),
  KEY `id_peca` (`id_peca`),
  CONSTRAINT `estoque_movimentacoes_ibfk_1` FOREIGN KEY (`id_peca`) REFERENCES `pecas` (`id_peca`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estoque_movimentacoes`
--

LOCK TABLES `estoque_movimentacoes` WRITE;
/*!40000 ALTER TABLE `estoque_movimentacoes` DISABLE KEYS */;
/*!40000 ALTER TABLE `estoque_movimentacoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fornecedores`
--

DROP TABLE IF EXISTS `fornecedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fornecedores` (
  `id_fornecedor` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(255) NOT NULL,
  `cnpj_cpf` varchar(50) DEFAULT NULL,
  `endereco` varchar(255) DEFAULT NULL,
  `telefone` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `observacoes` text,
  PRIMARY KEY (`id_fornecedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fornecedores`
--

LOCK TABLES `fornecedores` WRITE;
/*!40000 ALTER TABLE `fornecedores` DISABLE KEYS */;
/*!40000 ALTER TABLE `fornecedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `importacoes`
--

DROP TABLE IF EXISTS `importacoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `importacoes` (
  `id_importacao` int NOT NULL AUTO_INCREMENT,
  `arquivo_nome` varchar(255) NOT NULL,
  `arquivo_hash` varchar(255) DEFAULT NULL,
  `tipo_importacao` varchar(50) NOT NULL,
  `data_importacao` datetime NOT NULL,
  `usuario_responsavel` int DEFAULT NULL,
  `status` enum('sucesso','parcial','erro') NOT NULL,
  `mensagem_log` text,
  PRIMARY KEY (`id_importacao`),
  KEY `usuario_responsavel` (`usuario_responsavel`),
  CONSTRAINT `importacoes_ibfk_1` FOREIGN KEY (`usuario_responsavel`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `importacoes`
--

LOCK TABLES `importacoes` WRITE;
/*!40000 ALTER TABLE `importacoes` DISABLE KEYS */;
/*!40000 ALTER TABLE `importacoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `manutencoes`
--

DROP TABLE IF EXISTS `manutencoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `manutencoes` (
  `id_manutencao` int NOT NULL AUTO_INCREMENT,
  `id_equipamento` int NOT NULL,
  `data_inicio` date NOT NULL,
  `data_fim` date DEFAULT NULL,
  `tipo` enum('preventiva','corretiva','revisao','outro') DEFAULT 'outro',
  `descricao_servico` text,
  `custo_total` decimal(18,4) NOT NULL DEFAULT '0.0000',
  `responsavel` int DEFAULT NULL,
  PRIMARY KEY (`id_manutencao`),
  KEY `id_equipamento` (`id_equipamento`),
  KEY `responsavel` (`responsavel`),
  CONSTRAINT `manutencoes_ibfk_1` FOREIGN KEY (`id_equipamento`) REFERENCES `equipamentos` (`id_equipamento`) ON DELETE RESTRICT,
  CONSTRAINT `manutencoes_ibfk_2` FOREIGN KEY (`responsavel`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `manutencoes`
--

LOCK TABLES `manutencoes` WRITE;
/*!40000 ALTER TABLE `manutencoes` DISABLE KEYS */;
/*!40000 ALTER TABLE `manutencoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `manutencoes_pecas`
--

DROP TABLE IF EXISTS `manutencoes_pecas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `manutencoes_pecas` (
  `id_item_manutencao` int NOT NULL AUTO_INCREMENT,
  `id_manutencao` int NOT NULL,
  `id_peca` int NOT NULL,
  `quantidade_usada` decimal(20,4) NOT NULL,
  `preco_unitario` decimal(18,4) NOT NULL,
  PRIMARY KEY (`id_item_manutencao`),
  KEY `id_manutencao` (`id_manutencao`),
  KEY `id_peca` (`id_peca`),
  CONSTRAINT `manutencoes_pecas_ibfk_1` FOREIGN KEY (`id_manutencao`) REFERENCES `manutencoes` (`id_manutencao`) ON DELETE CASCADE,
  CONSTRAINT `manutencoes_pecas_ibfk_2` FOREIGN KEY (`id_peca`) REFERENCES `pecas` (`id_peca`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `manutencoes_pecas`
--

LOCK TABLES `manutencoes_pecas` WRITE;
/*!40000 ALTER TABLE `manutencoes_pecas` DISABLE KEYS */;
/*!40000 ALTER TABLE `manutencoes_pecas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orcamentos`
--

DROP TABLE IF EXISTS `orcamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orcamentos` (
  `id_orcamento` int NOT NULL AUTO_INCREMENT,
  `data_orcamento` datetime NOT NULL,
  `id_usuario` int DEFAULT NULL,
  `observacao` text,
  PRIMARY KEY (`id_orcamento`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `orcamentos_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orcamentos`
--

LOCK TABLES `orcamentos` WRITE;
/*!40000 ALTER TABLE `orcamentos` DISABLE KEYS */;
/*!40000 ALTER TABLE `orcamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orcamentos_itens`
--

DROP TABLE IF EXISTS `orcamentos_itens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orcamentos_itens` (
  `id_orcamento_item` int NOT NULL AUTO_INCREMENT,
  `id_orcamento` int NOT NULL,
  `id_peca` int NOT NULL,
  `id_fornecedor` int NOT NULL,
  `quantidade` decimal(20,4) NOT NULL,
  `preco_unitario` decimal(18,4) NOT NULL,
  PRIMARY KEY (`id_orcamento_item`),
  KEY `id_orcamento` (`id_orcamento`),
  KEY `id_peca` (`id_peca`),
  KEY `id_fornecedor` (`id_fornecedor`),
  CONSTRAINT `orcamentos_itens_ibfk_1` FOREIGN KEY (`id_orcamento`) REFERENCES `orcamentos` (`id_orcamento`) ON DELETE CASCADE,
  CONSTRAINT `orcamentos_itens_ibfk_2` FOREIGN KEY (`id_peca`) REFERENCES `pecas` (`id_peca`) ON DELETE RESTRICT,
  CONSTRAINT `orcamentos_itens_ibfk_3` FOREIGN KEY (`id_fornecedor`) REFERENCES `fornecedores` (`id_fornecedor`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orcamentos_itens`
--

LOCK TABLES `orcamentos_itens` WRITE;
/*!40000 ALTER TABLE `orcamentos_itens` DISABLE KEYS */;
/*!40000 ALTER TABLE `orcamentos_itens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pecas`
--

DROP TABLE IF EXISTS `pecas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pecas` (
  `id_peca` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(255) NOT NULL,
  `descricao` text,
  `codigo_interno` varchar(100) DEFAULT NULL,
  `unidade_medida` varchar(20) DEFAULT 'un',
  PRIMARY KEY (`id_peca`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pecas`
--

LOCK TABLES `pecas` WRITE;
/*!40000 ALTER TABLE `pecas` DISABLE KEYS */;
/*!40000 ALTER TABLE `pecas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pecas_fornecedores`
--

DROP TABLE IF EXISTS `pecas_fornecedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pecas_fornecedores` (
  `id_peca_fornecedor` int NOT NULL AUTO_INCREMENT,
  `id_peca` int NOT NULL,
  `id_fornecedor` int NOT NULL,
  `preco_unitario` decimal(15,4) NOT NULL,
  `data_cotacao` date NOT NULL,
  PRIMARY KEY (`id_peca_fornecedor`),
  KEY `id_peca` (`id_peca`),
  KEY `id_fornecedor` (`id_fornecedor`),
  CONSTRAINT `pecas_fornecedores_ibfk_1` FOREIGN KEY (`id_peca`) REFERENCES `pecas` (`id_peca`) ON DELETE CASCADE,
  CONSTRAINT `pecas_fornecedores_ibfk_2` FOREIGN KEY (`id_fornecedor`) REFERENCES `fornecedores` (`id_fornecedor`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pecas_fornecedores`
--

LOCK TABLES `pecas_fornecedores` WRITE;
/*!40000 ALTER TABLE `pecas_fornecedores` DISABLE KEYS */;
/*!40000 ALTER TABLE `pecas_fornecedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `senha_hash` varchar(255) DEFAULT NULL,
  `perfil` enum('admin','mecanico','gestor') DEFAULT 'gestor',
  `status` enum('ativo','inativo') DEFAULT 'ativo',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (2,'Erivaldo Junior','erivaldosantosjunior81@gmail.com','157c801df2b20e1b28bcf7407e88b22f7e8fabb03d2555453617b76b88af5ddb','admin','ativo');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-01 22:20:52
