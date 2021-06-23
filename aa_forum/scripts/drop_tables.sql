-- Deletes all AA Forum tables from the database
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS aa_forum_board;
DROP TABLE IF EXISTS aa_forum_board_groups;
DROP TABLE IF EXISTS aa_forum_category;
DROP TABLE IF EXISTS aa_forum_lastmessageseen;
DROP TABLE IF EXISTS aa_forum_message;
DROP TABLE IF EXISTS aa_forum_personalmessage;
DROP TABLE IF EXISTS aa_forum_setting;
DROP TABLE IF EXISTS aa_forum_slug;
DROP TABLE IF EXISTS aa_forum_topic;
SET FOREIGN_KEY_CHECKS=1;
