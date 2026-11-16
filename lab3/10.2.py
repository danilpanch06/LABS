a = 0
while a <= 1:
    try:
        a = float(input("Введите число А (больше 1): "))
        if a <= 1:
            print("Ошибка! Число А должно быть строго больше 1.")
    except ValueError:
        print("Ошибка! Нужно ввести число.")

summ = 0
k = 0
while summ + (1 / (k + 1)) < a:
    k = k + 1
    summ = summ + (1 / k)
print (f"Наибольшее целое число k: {k}")
print (f"Сумма: {summ} ")