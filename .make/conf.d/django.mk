# Make targets for Django projects

# Translation files
.PHONY: translations
translations:
	@echo "Creating or updating translation files"
	@django-admin makemessages \
		-l cs_CZ \
		-l de \
		-l es \
		-l fr_FR \
		-l it_IT \
		-l ja \
		-l ko_KR \
		-l nl_NL \
		-l pl_PL \
		-l ru \
		-l sk \
		-l uk \
		-l zh_Hans \
		--keep-pot \
		--ignore 'build/*'

# Compile translation files
.PHONY: compile_translations
compile_translations:
	@echo "Compiling translation files"
	@django-admin compilemessages \
		-l cs_CZ \
		-l de \
		-l es \
		-l fr_FR \
		-l it_IT \
		-l ja \
		-l ko_KR \
		-l nl_NL \
		-l pl_PL \
		-l ru \
		-l sk \
		-l uk \
		-l zh_Hans

# Migrate all database changes
.PHONY: migrate
migrate:
	@echo "Migrating the database"
	@python ../myauth/manage.py migrate $(package)

# Make migrations for the app
.PHONY: migrations
migrations:
	@echo "Creating or updating migrations"
	@python ../myauth/manage.py makemigrations $(package)

# Help message
.PHONY: help
help::
	@echo "  $(TEXT_UNDERLINE)Translation:$(TEXT_UNDERLINE_END)"
	@echo "    migrate                   Migrate all database changes"
	@echo "    migrations                Create or update migrations"
	@echo "    translations              Create or update translation files"
	@echo "    compile_translations      Compile translation files"
	@echo ""
