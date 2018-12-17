-- MySQL dump 10.13  Distrib 5.7.11, for Linux (x86_64)
--
-- Host: 192.168.1.100    Database: elo7_datascience
-- ------------------------------------------------------
-- Server version	5.7.24-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `genome_scores`
--

DROP TABLE IF EXISTS `genome_scores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `genome_scores` (
  `idmovie` int(11) NOT NULL,
  `idtag` int(11) NOT NULL,
  `relevance` double DEFAULT NULL,
  PRIMARY KEY (`idmovie`,`idtag`),
  KEY `fk_genome_scores_1_idx` (`idtag`),
  CONSTRAINT `fk_genome_scores_1` FOREIGN KEY (`idtag`) REFERENCES `genome_tags` (`idtag`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_genome_scores_2` FOREIGN KEY (`idmovie`) REFERENCES `movie` (`idmovie`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `genome_scores_at_one_line`
--

DROP TABLE IF EXISTS `genome_scores_at_one_line`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `genome_scores_at_one_line` (
  `idmovie` int(11) NOT NULL,
  `valuesdata` mediumtext,
  `idrand` int(11) NOT NULL,
  PRIMARY KEY (`idmovie`,`idrand`),
  CONSTRAINT `fk_genome_scores_at_one_line_1` FOREIGN KEY (`idmovie`) REFERENCES `movie` (`idmovie`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `genome_scores_pca`
--

DROP TABLE IF EXISTS `genome_scores_pca`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `genome_scores_pca` (
  `idmovie` int(11) NOT NULL,
  `component` int(11) NOT NULL,
  `value_component` double DEFAULT NULL,
  `pca_group` int(11) DEFAULT NULL,
  PRIMARY KEY (`idmovie`,`component`),
  CONSTRAINT `fk_genome_score_pca_1` FOREIGN KEY (`idmovie`) REFERENCES `movie` (`idmovie`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `genome_scores_pca_at_one_line`
--

DROP TABLE IF EXISTS `genome_scores_pca_at_one_line`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `genome_scores_pca_at_one_line` (
  `idmovie` int(11) NOT NULL,
  `valuesdata` mediumtext,
  PRIMARY KEY (`idmovie`),
  CONSTRAINT `fk_genome_scores_pca_at_one_1` FOREIGN KEY (`idmovie`) REFERENCES `movie` (`idmovie`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `genome_tags`
--

DROP TABLE IF EXISTS `genome_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `genome_tags` (
  `idtag` int(11) NOT NULL,
  `tag` varchar(255) DEFAULT NULL,
  `avg` double DEFAULT NULL,
  `std` double DEFAULT NULL,
  PRIMARY KEY (`idtag`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `genre`
--

DROP TABLE IF EXISTS `genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `genre` (
  `idgenre` int(11) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idgenre`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `movie`
--

DROP TABLE IF EXISTS `movie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `movie` (
  `idmovie` int(11) NOT NULL,
  `tittle` varchar(255) DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `cluster` int(11) DEFAULT NULL,
  PRIMARY KEY (`idmovie`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `number_of_votes_for_a_genre_from_a_user`
--

DROP TABLE IF EXISTS `number_of_votes_for_a_genre_from_a_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `number_of_votes_for_a_genre_from_a_user` (
  `number_of_votes` int(11) DEFAULT NULL,
  `idgenre` int(11) NOT NULL,
  `iduser` int(11) NOT NULL,
  PRIMARY KEY (`iduser`,`idgenre`),
  KEY `fk_number_of_votes_for_a_genre_from_a_user_1_idx` (`idgenre`),
  CONSTRAINT `fk_number_of_votes_for_a_genre_from_a_user_1` FOREIGN KEY (`idgenre`) REFERENCES `genre` (`idgenre`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_number_of_votes_for_a_genre_from_a_user_2` FOREIGN KEY (`iduser`) REFERENCES `user` (`iduser`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ratings`
--

DROP TABLE IF EXISTS `ratings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratings` (
  `iduser` int(11) NOT NULL,
  `idmovie` int(11) NOT NULL,
  `rating` float DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT NULL,
  `idrand` int(11) DEFAULT NULL,
  PRIMARY KEY (`iduser`,`idmovie`),
  KEY `fk_ratings_1_idx` (`idmovie`),
  KEY `indexrand` (`idrand`) USING BTREE,
  CONSTRAINT `fk_ratings_1` FOREIGN KEY (`idmovie`) REFERENCES `movie` (`idmovie`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_ratings_2` FOREIGN KEY (`iduser`) REFERENCES `user` (`iduser`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `relation_movie_genre`
--

DROP TABLE IF EXISTS `relation_movie_genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `relation_movie_genre` (
  `idmovie` int(11) NOT NULL,
  `idgenre` int(11) NOT NULL,
  PRIMARY KEY (`idmovie`,`idgenre`),
  KEY `fk_relation_movie_genre_1_idx` (`idgenre`),
  CONSTRAINT `fk_relation_movie_genre_1` FOREIGN KEY (`idgenre`) REFERENCES `genre` (`idgenre`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_relation_movie_genre_2` FOREIGN KEY (`idmovie`) REFERENCES `movie` (`idmovie`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `iduser` int(11) NOT NULL,
  PRIMARY KEY (`iduser`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `votes_computed_for_movies`
--

DROP TABLE IF EXISTS `votes_computed_for_movies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `votes_computed_for_movies` (
  `idmovie` int(11) NOT NULL,
  `number_of_votes_greater_or_equal_three` int(11) DEFAULT NULL,
  PRIMARY KEY (`idmovie`),
  KEY `index2` (`number_of_votes_greater_or_equal_three`) USING BTREE,
  CONSTRAINT `fk_new_table_1` FOREIGN KEY (`idmovie`) REFERENCES `movie` (`idmovie`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-12-16 17:35:10