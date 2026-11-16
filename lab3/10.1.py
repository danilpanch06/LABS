print ("Введите оценки по очереди :")
sum = 0
for a in range(20):
    ocenka = 0
    while ocenka < 1 or ocenka > 5:
        try:
            ocenka = int(input(f"Ученик  {a + 1}: "))
            if ocenka < 1 or ocenka > 5:
                print("Ошибка! Оценка должна быть от 1 до 5.")
        except ValueError:
            print("Ошибка! Введите число.")
    sum = sum + ocenka
sred = sum/20 
print (sred)