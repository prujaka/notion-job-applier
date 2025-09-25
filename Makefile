clean_raw:
	rm documents/cv_raw/*

clean_renamed:
	rm documents/cv_renamed/*

rename_cvs:
	python jobapplier/main.py -a "rename_cvs"

add_covers:
	python jobapplier/main.py -a "fill_cover_letters"
