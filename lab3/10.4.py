n = int(input("Введите длину массива\n"))
x = []
for i in range(n):
    print('Введите', i, 'элемент')
    x.append(input())
povtor = []
for i in range(n):
    if x.count(x[i]) > 1:
        povtor.append(x[i])
if len(povtor) > 0:
    print(f"Повторяющийся элемент: {povtor[0]}")
else:
    print("Повторяющиеся элементы отсутствуют")