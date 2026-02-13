try:
    with open("movies2.txt", "r", encoding="utf-8", errors="ignore") as f:
        for i in range(5):
            print(repr(f.readline()))
except Exception as e:
    print(e)
