context = {}
context["tasks"] = {}
context["tasks"]["pk1"] = 1
context["tasks"]["pk1"] = 2
context["tasks"]["pk2"] = 2
context["tasks"]["pk3"] = 3
for i in context.values():
    print(i)
    for j in i.values():
            print(j)