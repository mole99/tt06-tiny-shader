BITS := $(patsubst shader/%.shader,binary/%.bit, $(wildcard shader/*.shader))

bits: $(BITS)

binary/%.bit: shader/%.shader
	python3 assembler.py -i $^ -o $@ --image images/$(basename $(notdir $@)).png

clean:
	rm -rf binary/*.bit
	rm -rf images/*.png
