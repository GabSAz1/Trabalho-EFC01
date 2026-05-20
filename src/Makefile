. PHONY : test lint type cov complexity all
test :
	pytest -v
cov :
	pytest -- cov =. -- cov - report = term - missing -- cov - report = html
lint :
	ruff check .
type :
	mypy -- strict src /
complexity :
	radon cc src / -s -a
all : lint type test cov complexity