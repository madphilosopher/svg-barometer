barometer.svg: barometer.py
	./barometer.py

barometer.png: barometer.svg
	inkscape -z -e barometer.png -w 400 -h 400 barometer.svg

README.html: README.md
	pandoc -f markdown_github README.md -o README.html

clean:
	rm -f README.html
