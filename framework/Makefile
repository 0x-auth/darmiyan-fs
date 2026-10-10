IMAGE ?= darmiyan:1.1.0

build:
	docker build -t $(IMAGE) .

suite:
	docker run --rm $(IMAGE) suite

verify:
	docker run --rm $(IMAGE) verify

shell:
	docker run --rm -it --entrypoint /bin/bash $(IMAGE)

read:
	docker run --rm $(IMAGE) read $(R)

.PHONY: build suite verify shell read
