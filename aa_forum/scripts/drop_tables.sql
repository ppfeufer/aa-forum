-- Deletes all AA Forum tables from the database
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS aa_forum_board2;
DROP TABLE IF EXISTS aa_forum_board2_groups;
DROP TABLE IF EXISTS aa_forum_categories;
DROP TABLE IF EXISTS aa_forum_messages;
DROP TABLE IF EXISTS aa_forum_messages_read_by;
DROP TABLE IF EXISTS aa_forum_personalmessages;
DROP TABLE IF EXISTS aa_forum_settings;
DROP TABLE IF EXISTS aa_forum_slugs;
DROP TABLE IF EXISTS aa_forum_topics;
DROP TABLE IF EXISTS aa_forum_topics_read_by;
DROP TABLE IF EXISTS aa_forum_board;
DROP TABLE IF EXISTS aa_forum_board_groups;
DROP TABLE IF EXISTS aa_forum_category;
DROP TABLE IF EXISTS aa_forum_message;
DROP TABLE IF EXISTS aa_forum_message_read_by;
DROP TABLE IF EXISTS aa_forum_personalmessage;
DROP TABLE IF EXISTS aa_forum_setting;
DROP TABLE IF EXISTS aa_forum_slug;
DROP TABLE IF EXISTS aa_forum_topic;
DROP TABLE IF EXISTS aa_forum_topic_read_by;
SET FOREIGN_KEY_CHECKS=1;
